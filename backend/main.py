import os
import sys
sys.path.append(os.path.dirname(__file__))
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from google import genai
from dotenv import load_dotenv
load_dotenv()
import json

# Import our AI modules
from ai_engine import emotion, cliffhanger
from ai_engine.aggregator import NarrativeDNAAggregator
from models.schemas import (
    StoryRequest, ArcResponse, AnalysisRequest, AnalyticsResponse,
    Episode, ImprovementRequest, ImprovementResponse,
    StyleSuggestionRequest, StyleSuggestionResponse, SuggestedStyle,
    VideoGenerationRequest, VideoGenerationResponse,
)

load_dotenv(override=True)

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None
    print("WARNING: GOOGLE_API_KEY not found in .env")

app = FastAPI(title="Narrative DNA Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate_arc", response_model=ArcResponse)
async def generate_arc(request: StoryRequest):
    from fastapi import HTTPException
    import time

    if not client:
        raise HTTPException(status_code=503, detail="GOOGLE_API_KEY is not configured on the server. Please add it to backend/.env and restart.")

    prompt = f"""
    Act as a master screenwriter. Create a 5-episode arc for a {request.genre} show based on this idea: "{request.idea}".
    For each episode, provide a Title, a 1-sentence Synopsis, and a 'Script Segment' (approx 150 words of dialogue/action from the climax).
    Return ONLY valid JSON in this format:
    [
        {{"title": "Ep 1 Title", "synopsis": "...", "script_segment": "..."}},
        ...
    ]
    """

    last_error = None
    for attempt in range(4): # Increased to 4 attempts
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
            )
            text = response.text.replace("```json", "").replace("```", "")
            data = json.loads(text)
            episodes = [Episode(**ep) for ep in data]
            return ArcResponse(episodes=episodes)
        except Exception as e:
            last_error = e
            err_str = str(e).upper()
            print(f"Attempt {attempt+1} failed: {err_str[:200]}")
            
            # Quota / Rate limit handling
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str:
                if attempt < 3:
                    wait = 30 * (attempt + 1) # 30s, 60s, 90s backoff
                    print(f"Rate limited or Quota exceeded. Waiting {wait}s before retry...")
                    await asyncio.sleep(wait) # USE ASYNC SLEEP
                    continue
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API quota exceeded. The free-tier rate limit has been reached. Please wait a minute and try again, or upgrade your API key at https://ai.google.dev."
                )
            
            # Generic error mapping
            if "API_KEY_INVALID" in err_str or "400" in err_str and "EXPIRED" in err_str:
                raise HTTPException(status_code=401, detail="API Key appears to be invalid or expired. Please check backend/.env.")
                
            raise HTTPException(status_code=500, detail=f"Gemini API error: {err_str[:300]}")
    
    raise HTTPException(status_code=429, detail="Gemini API rate limit hit after multiple retries. Please wait a few minutes.")

@app.post("/analyze_story", response_model=AnalyticsResponse)
async def analyze_story(request: AnalysisRequest):
    script = request.script_text
    
    aggregator = NarrativeDNAAggregator()
    analysis_data = aggregator.analyze_story(script)

    return AnalyticsResponse(**analysis_data)

@app.post("/improve_cliffhanger", response_model=ImprovementResponse)
async def improve_cliffhanger(request: ImprovementRequest):
    script = request.script_text
    
    # 1. Calculate current metrics
    emotion_arc = emotion.analyze_emotional_arc(script)
    current_score = cliffhanger.calculate_score(script, emotion_arc)
    
    if not client:
        return ImprovementResponse(
            original_score=current_score,
            analysis="Demo Mode: LLM not connected.",
            suggestions=["Add a question mark at the end.", "Include high-stakes keywords like 'trap' or 'secret'.", "Create a sudden sentiment shift."],
            rewritten_segment=script + "\n\nSuddenly, the lights went out. A voice whispered, 'It's a trap.'",
            predicted_score=min(current_score + 30, 100)
        )

    # 2. Construct Prompt for Gemini
    prompt = f"""
    Act as a master script doctor. Analyze this scene ending and improve its cliffhanger potential.
    
    Current Script:
    "{script}"
    
    Current Cliffhanger Score: {current_score}/100.
    
    The scoring algorithm looks for:
    1. Sentiment Shift (emotional volatility at the end)
    2. Information Gaps (unanswered questions, mysteries)
    3. High Stakes (danger, secrets, urgency keywords like 'die', 'kill', 'secret', 'trap')
    
    Task:
    1. Analyze why the score might be low.
    2. Provide 3 specific bullet points on how to fix it.
    3. Rewrite the last few lines to drastically increase the tension and curiosity.
    
    Return ONLY valid JSON in this format:
    {{
        "analysis": "...",
        "suggestions": ["fix 1", "fix 2", "fix 3"],
        "rewritten_segment": "..."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        text = response.text.replace("```json", "").replace("```", "")
        data = json.loads(text)
        
        # 3. Re-score the new segment to verify improvement
        new_script = data.get("rewritten_segment", "")
        new_emotion_arc = emotion.analyze_emotional_arc(new_script)
        new_score = cliffhanger.calculate_score(new_script, new_emotion_arc)
        
        return ImprovementResponse(
            original_score=current_score,
            analysis=data.get("analysis", "Analysis failed"),
            suggestions=data.get("suggestions", []),
            rewritten_segment=new_script,
            predicted_score=new_score
        )
    except Exception as e:
        print(f"Error improving cliffhanger: {e}")
        return ImprovementResponse(
            original_score=current_score,
            analysis="Error generating improvement.",
            suggestions=[],
            rewritten_segment=script,
            predicted_score=current_score
        )




# ── Video Generation Endpoints ────────────────────────────────────────────────

STYLE_OPTIONS = {
    "shot_styles": ["close_up", "wide_shot", "tracking_shot", "drone", "dutch_angle", "over_shoulder"],
    "cinematic_styles": ["neon_noir", "golden_hour", "desaturated", "high_contrast_bw", "vibrant_pop", "earth_tones", "teal_orange"],
    "moods": ["thriller", "drama", "action", "romance", "mystery", "sci_fi"],
    "resolutions": ["480p", "720p"],
}

@app.get("/video_style_options")
async def get_video_style_options():
    """Return the available style options for the video generator."""
    return STYLE_OPTIONS


@app.post("/suggest_style", response_model=StyleSuggestionResponse)
async def suggest_style(request: StyleSuggestionRequest):
    """Use Gemini to predict the best cinematic style for the given script."""
    if not client:
        # Demo fallback
        fallback = SuggestedStyle(
            shot_style="wide_shot",
            cinematic_style="teal_orange",
            mood="drama",
            resolution="480p",
            reasoning="Default Hollywood cinematic style optimized for dramatic storytelling."
        )
        return StyleSuggestionResponse(suggested=fallback, alternatives=[
            SuggestedStyle(shot_style="tracking_shot", cinematic_style="neon_noir", mood="thriller", resolution="480p", reasoning="High-energy thriller aesthetic."),
            SuggestedStyle(shot_style="drone", cinematic_style="golden_hour", mood="drama", resolution="720p", reasoning="Sweeping cinematic drama feel."),
        ])
    
    prompt = f"""
    You are an expert cinematographer and visual storytelling director.
    Analyze this episode script and suggest the BEST cinematic style for a 3-second style preview video.

    Episode Title: {request.episode_title}
    Genre: {request.genre}
    Script excerpt:
    \"\"\"{request.script_text[:800]}\"\"\"

    Available shot_styles: {STYLE_OPTIONS['shot_styles']}
    Available cinematic_styles: {STYLE_OPTIONS['cinematic_styles']}
    Available moods: {STYLE_OPTIONS['moods']}
    Available resolutions: ["480p", "720p"]

    Return ONLY valid JSON with this exact structure:
    {{
        "suggested": {{
            "shot_style": "one from the list",
            "cinematic_style": "one from the list",
            "mood": "one from the list",
            "resolution": "480p or 720p",
            "reasoning": "1-2 sentence explanation of why this style fits the story"
        }},
        "alternatives": [
            {{"shot_style": "...", "cinematic_style": "...", "mood": "...", "resolution": "...", "reasoning": "..."}},
            {{"shot_style": "...", "cinematic_style": "...", "mood": "...", "resolution": "...", "reasoning": "..."}}
        ]
    }}
    """
    
    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return StyleSuggestionResponse(
            suggested=SuggestedStyle(**data["suggested"]),
            alternatives=[SuggestedStyle(**a) for a in data.get("alternatives", [])]
        )
    except Exception as e:
        print(f"Error in suggest_style: {e}")
        fallback = SuggestedStyle(
            shot_style="wide_shot", cinematic_style="teal_orange", mood="drama",
            resolution="480p", reasoning="Default cinematic style."
        )
        return StyleSuggestionResponse(suggested=fallback, alternatives=[])


# Track generation jobs in memory
_video_jobs: dict = {}

def _run_video_generation(job_id: str, request_data: dict):
    """Background task that runs the actual diffusion generation."""
    from ai_engine.video_generator import generate_episode_video
    _video_jobs[job_id] = {"status": "generating", "progress": 0, "clips_generated": 0}
    
    def on_progress(clips, total_clips):
        _video_jobs[job_id]["clips_generated"] = clips
        _video_jobs[job_id]["total_clips"] = total_clips
        # We can also compute a percentage here if wanted, but frontend relies on clips_generated mostly
        _video_jobs[job_id]["progress"] = int((clips / total_clips) * 100)

    try:
        result = generate_episode_video(
            script_segments=request_data["script_segments"],
            shot_style=request_data["shot_style"],
            cinematic_style=request_data["cinematic_style"],
            mood=request_data["mood"],
            resolution=request_data["resolution"],
            mode=request_data.get("mode", "preview"),
            job_id=job_id,
            progress_callback=on_progress,
        )
        _video_jobs[job_id] = {"status": "done", **result}
    except Exception as e:
        _video_jobs[job_id] = {"status": "error", "error": str(e)}


@app.post("/generate_video", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Start a 90-second video generation job in the background using Wan2.2."""
    import uuid
    job_id = str(uuid.uuid4())[:8]
    _video_jobs[job_id] = {"status": "queued"}
    background_tasks.add_task(_run_video_generation, job_id, request.model_dump())
    duration = 3.0 if request.mode == "preview" else 90.0
    return VideoGenerationResponse(
        job_id=job_id,
        video_filename=f"episode_{job_id}.mp4",
        clips_generated=0,
        duration_seconds=duration,
        status="queued",
        message=f"Video generation started. Job ID: {job_id}. Poll /video_status/{job_id} for updates."
    )


@app.get("/video_status/{job_id}")
async def get_video_status(job_id: str):
    """Poll for the status of a video generation job."""
    job = _video_jobs.get(job_id)
    if not job:
        return {"status": "not_found", "job_id": job_id}
    return {"job_id": job_id, **job}


@app.get("/video/{filename}")
async def serve_video(filename: str):
    """Serve a generated video file."""
    video_dir = os.path.join(os.path.dirname(__file__), "generated_videos")
    path = os.path.join(video_dir, filename)
    if not os.path.exists(path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path, media_type="video/mp4", filename=filename)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
