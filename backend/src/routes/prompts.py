

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from services.prompt_service import PromptService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_prompt_service() -> PromptService:
    """Dependency injection for prompt service"""
    from main import app  # Import locally to avoid circular import
    return app.state.prompt_service

class PromptRequest(BaseModel):
    prompt: str
    sector: Optional[str] = None
    detailed: bool = False
    include_visualizations: bool = True

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_prompt(
    request: PromptRequest,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """Analyze user prompt and generate insights"""
    try:
        from datetime import datetime  # Import locally
        
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(request.prompt) > 1000:
            raise HTTPException(status_code=400, detail="Prompt too long. Maximum 1000 characters.")
        
        # Analyze the prompt
        analysis = await prompt_service.analyze_prompt(request.prompt, request.sector)

        print('analysing prompt')
        
        processing_time = 0.0  # You would calculate this based on start time
        
        response_data = {
            "status": "success",
            "prompt": request.prompt,
            "sector": analysis.get('sector', request.sector),
            "insights": analysis.get('insights', ''),
            "data_summary": analysis.get('data_summary', {}),
            "recommendations": analysis.get('recommendations', []),
            "related_questions": analysis.get('related_questions', []),
            "confidence_score": analysis.get('confidence_score', 0.5),
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Include visualizations if requested
        if request.include_visualizations:
            response_data["visualizations"] = analysis.get('visualizations', [])
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze prompt")

@router.get("/suggestions", response_model=Dict[str, Any])
async def get_prompt_suggestions(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """Get suggested prompts for different sectors"""
    suggestions = {
        "energy": [
            "What are the current energy prices in the UK?",
            "How have energy prices changed over the past month?",
            "What time of day has the cheapest electricity?",
            "How do renewable energy sources affect pricing?",
            "Predict energy prices for next week based on current trends"
        ],
        "transportation": [
            "Which tube lines have the most delays right now?",
            "What are the peak hours for transport delays?",
            "How does weather affect transport reliability?",
            "Compare delay patterns between weekdays and weekends",
            "Which stations have the best on-time performance?"
        ],
        "finance": [
            "What's the current FTSE 100 performance?",
            "Which UK stocks are performing best this week?",
            "How do interest rates affect stock prices?",
            "What's the market volatility trend?",
            "Predict market movement based on economic indicators"
        ],
        "weather": [
            "How does weather impact energy consumption?",
            "What's the correlation between weather and transport delays?",
            "How does temperature affect retail sales?",
            "Predict energy demand based on weather forecasts",
            "Compare weather patterns across different UK regions"
        ]
    }
    
    if sector:
        if sector not in suggestions:
            raise HTTPException(status_code=400, detail=f"Invalid sector. Available: {list(suggestions.keys())}")
        filtered_suggestions = {sector: suggestions[sector]}
    else:
        filtered_suggestions = suggestions
    
    return {
        "status": "success",
        "sector": sector,
        "suggestions": filtered_suggestions
    }

@router.get("/history", response_model=Dict[str, Any])
async def get_prompt_history(
    limit: int = Query(10, ge=1, le=100),
    sector: Optional[str] = Query(None)
):
    """Get recent prompt analysis history"""
    # This would typically query a database
    # For now, return mock data
    history = [
        {
            "id": "1",
            "prompt": "Show me current energy prices",
            "sector": "energy",
            "timestamp": "2024-01-15T10:30:00Z",
            "confidence_score": 0.85
        },
        {
            "id": "2",
            "prompt": "Which tube lines are delayed?",
            "sector": "transportation",
            "timestamp": "2024-01-15T09:15:00Z",
            "confidence_score": 0.92
        }
    ]
    
    if sector:
        history = [h for h in history if h['sector'] == sector]
    
    return {
        "status": "success",
        "count": len(history),
        "history": history[:limit]
    }

@router.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(
    analysis_id: str = Body(..., embed=True),
    rating: int = Body(..., ge=1, le=5),
    comments: Optional[str] = Body(None),
    helpful: bool = Body(..., description="Whether the analysis was helpful")
):
    """Submit feedback on prompt analysis results"""
    return {
        "status": "success",
        "message": "Feedback received",
        "analysis_id": analysis_id,
        "rating": rating,
        "helpful": helpful
    }