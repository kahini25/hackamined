from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class StoryRequest(BaseModel):
    idea: str
    genre: str

class AnalysisRequest(BaseModel):
    script_text: str

class ImprovementRequest(BaseModel):
    script_text: str

class ImprovementResponse(BaseModel):
    original_score: float
    analysis: str
    suggestions: List[str]
    rewritten_segment: str
    predicted_score: float

class Episode(BaseModel):
    title: str
    synopsis: str
    script_segment: str
    
class ArcResponse(BaseModel):
    episodes: List[Episode]
    
class AnalyticsResponse(BaseModel):
    pacing_curve: List[float]
    emotional_arc: List[Dict[str, Any]]
    emotion_analysis: Optional[List[Dict[str, Any]]] = None
    cliffhanger_score: float
    drop_off_risk: Dict[str, Any]
    retention_prediction: Optional[Dict[str, Any]] = None
    viral_moments: List[Dict[str, Any]]
    tension_graph: Dict[str, Any]
    scroll_stop_score: float
    narrative_dna: Optional[Dict[str, Any]] = None
