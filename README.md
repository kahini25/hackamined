# Narrative DNA Engine
### AI-Powered Episodic Intelligence for Vertical Storytelling

The **Narrative DNA Engine** is an AI-driven platform designed to analyze, deconstruct, and optimize narrative scripts for episodic storytelling. It computationally extracts the structural “DNA” of a story — including pacing, emotional volatility, character archetypes, cliffhanger tension, and retention risk.

Built for the **Quantloop Technologies Hackathon – Adaptive Episodic Intelligence for Vertical Storytelling**, the system provides creators with an intelligent toolkit to design compelling **multi-part vertical series** optimized for audience retention.

---

# Overview

The system allows creators to:

1. Input a story idea or script
2. Automatically generate a structured episodic arc
3. Analyze emotional progression and pacing
4. Score cliffhanger strength
5. Predict audience retention risks
6. Improve scene endings with AI
7. Generate cinematic previews of scenes

The result is a **Narrative DNA fingerprint** that helps creators optimize storytelling.

---

# Features

## Story Decomposer Engine
Transforms a raw story idea or script into a structured episodic narrative arc.

- Episode segmentation
- Narrative stage detection (Todorov model)
- Character extraction
- Archetype classification (Propp archetypes)

---

## Emotional Arc Analyzer
Tracks emotional volatility across the script.

- Sentence-level sentiment scoring
- Emotional intensity classification
- Detection of flat engagement zones
- Emotional arc visualization

---

## Cliffhanger Strength Scoring
Evaluates the effectiveness of episode endings.

- DistilBERT classification model
- Scene ending analysis
- Tension probability scoring
- AI-assisted cliffhanger improvement

---

## Retention Risk Predictor
Predicts viewer drop-off zones within episodes.

- Sequence classification models
- Structural tension tracking
- Engagement curve modeling

---

## Narrative Pacing Engine
Measures narrative pacing using semantic embedding drift.

- Sentence embeddings using SentenceTransformers
- Cosine similarity analysis
- Detection of pacing slowdowns

---

## AI Scene Improvement
Automatically improves weak narrative segments.

- AI rewriting of cliffhangers
- Tension optimization
- Context-aware improvements

---

## Cinematic Scene Generator
Converts text scenes into AI-generated cinematic previews.

- Diffusion-based video generation
- Style and camera selection
- Asynchronous background generation pipeline

---

# Tech Stack

## Frontend
- React 18
- Vite
- Tailwind CSS
- Axios
- D3.js (data visualization)

Key Components:
- `StoryInput.jsx`
- `EpisodeDashboard.jsx`
- `VideoGenerator.jsx`

---

## Backend
- Python
- FastAPI
- Uvicorn
- Pydantic
- BackgroundTasks

### API Endpoints

| Endpoint | Function |
|--------|--------|
| `/generate_arc` | Generate episodic arc |
| `/split_episodes` | Segment script |
| `/analyze_story` | Narrative DNA analysis |
| `/improve_cliffhanger` | Rewrite scene endings |
| `/generate_video` | Generate scene preview |
| `/video_status/{job_id}` | Check video generation status |

---

## AI / ML Stack

### Transformers
- DistilBERT (cliffhanger classification)
- DistilBERT (emotion intensity)
- DistilBERT (retention prediction)

### Embedding Models
- SentenceTransformers
- `all-MiniLM-L6-v2`

### NLP Pipelines
- spaCy (`en_core_web_sm`)
- Named Entity Recognition
- Interaction graphs

### Sentiment Analysis
- VADER sentiment

### External Generative Models
- Google Gemini 2.0 Flash (story generation)
- Fal.ai diffusion video generation

---

# AI Engine Pipeline

The **NarrativeDNAAggregator** orchestrates multiple analysis modules.


The platform follows a **decoupled client-server architecture**.
