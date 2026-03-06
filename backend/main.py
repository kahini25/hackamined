import os
import sys
sys.path.append(os.path.dirname(__file__))
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from dotenv import load_dotenv
load_dotenv()
import json

# Import our AI modules
from ai_engine import emotion, cliffhanger
from ai_engine.aggregator import NarrativeDNAAggregator
from models.schemas import StoryRequest, ArcResponse, AnalysisRequest, AnalyticsResponse, Episode, ImprovementRequest, ImprovementResponse

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
    # Fallback data for demo/quota limits
    fallback_episodes = [
        Episode(
            title="The Silent Echo (Demo Arc)",
            synopsis="In a world where sound is currency, a mute girl discovers a frequency that can rewrite reality.",
            script_segment="INT. ABANDONED SUBWAY - NIGHT\n\nKIRA (20s) touches the rusted rail. It vibrates.\n\nKIRA\n(signing)\nIt's alive.\n\nMARCUS watches her, terrified.\n\nMARCUS\nDon't let it hear you.\n\nThe tunnel SHAKES. Dust falls from the ceiling."
        ),
        Episode(
            title="Frequency Shift",
            synopsis="Kira is hunted by the Sound Guardians who want to harvest her discovery.",
            script_segment="EXT. ROOFTOP - RAIN\n\nRain lashes down. A dark figure lands behind Kira.\n\nGUARDIAN\nGive us the frequency.\n\nKira steps to the edge. She taps her foot. The thunder syncs with her rhythm."
        ),
        Episode(
            title="Resonance",
            synopsis="Marcus betrays Kira to save his family, leading to a confrontation at the harmonic plant.",
            script_segment="INT. CONTROL ROOM - DAY\n\nMARCUS\nI had no choice, Kira.\n\nKira looks at the screens. They show her heartbeat.\n\nKIRA\n(signing)\nWe always have a choice.\n\nShe pulls the lever. The sirens turn into a melody."
        ),
        Episode(
            title="Dissonance",
            synopsis="The city begins to crumble as the frequency destabilizes the foundations of society.",
            script_segment="EXT. CITY SQUARE - DAY\n\nBuildings vibrate. Glass shatters in slow motion.\n\nCITIZEN\nMake it stop!\n\nKira stands in the center, eyes closed, conducting the destruction."
        ),
        Episode(
            title="The Final Note",
            synopsis="Kira must decide whether to silence the world to save it, or let the song play out.",
            script_segment="INT. THE VOID - TIMELESS\n\nKira floats in white space.\n\nVOICE\nEnd the song, Kira.\n\nKira opens her mouth. For the first time, she speaks.\n\nKIRA\nNo.\n\nThe world fades to white."
        )
    ]

    if not client:
        print("WARNING: Gemini client not configured. Returning Demo Data.")
        return ArcResponse(episodes=fallback_episodes)

    prompt = f"""
    Act as a master screenwriter. Create a 5-episode arc for a {request.genre} show based on this idea: "{request.idea}".
    For each episode, provide a Title, a 1-sentence Synopsis, and a 'Script Segment' (approx 150 words of dialogue/action from the climax).
    Return ONLY valid JSON in this format:
    [
        {{"title": "Ep 1 Title", "synopsis": "...", "script_segment": "..."}},
        ...
    ]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text.replace("```json", "").replace("```", "")
        data = json.loads(text)
        episodes = [Episode(**ep) for ep in data]
        return ArcResponse(episodes=episodes)
    except Exception as e:
        print(f"Error calling Gemini API (likely quota): {e}")
        print("Returning Demo Data due to error.")
        return ArcResponse(episodes=fallback_episodes)

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
            model='gemini-2.5-flash',
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
