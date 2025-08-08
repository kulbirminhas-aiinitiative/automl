from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from io import StringIO
import json
from typing import Dict, List, Any, Optional
import uvicorn
from datetime import datetime
import os
import hashlib
from pydantic import BaseModel

from models.automl_orchestrator import AutoMLOrchestrator
from utils.data_processor import DataProcessor
from utils.model_evaluator import ModelEvaluator
from utils.chart_generator import ChartGenerator

# Request models
class ModelSuggestionRequest(BaseModel):
    target_column: str
    problem_type: Optional[str] = None

class TrainModelRequest(BaseModel):
    target_column: str
    selected_models: List[str]
    train_config: Optional[Dict[str, Any]] = None

app = FastAPI(
    title="AutoML Orchestration API",
    description="Automated Machine Learning pipeline with LLM orchestration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3004", 
        "http://127.0.0.1:3004"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
orchestrator = AutoMLOrchestrator()
data_processor = DataProcessor()
model_evaluator = ModelEvaluator()
chart_generator = ChartGenerator()

# Store for active sessions
active_sessions: Dict[str, Dict[str, Any]] = {}
# Store for file hashes to prevent duplicate uploads
file_hash_to_session: Dict[str, str] = {}

def calculate_file_hash(content: bytes) -> str:
    """Calculate MD5 hash of file content"""
    return hashlib.md5(content).hexdigest()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AutoML Orchestration API is running", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """Upload and process dataset"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.json')):
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload CSV, XLSX, or JSON files.")
        
        # Read file content
        content = await file.read()
        
        # Calculate file hash to check for duplicates
        file_hash = calculate_file_hash(content)
        
        # Check if this file was already uploaded
        if file_hash in file_hash_to_session:
            existing_session_id = file_hash_to_session[file_hash]
            if existing_session_id in active_sessions:
                session_data = active_sessions[existing_session_id]
                return {
                    "session_id": existing_session_id,
                    "filename": session_data["filename"],
                    "shape": [len(session_data["data"]), len(session_data["data"].keys())],
                    "columns": [str(col) for col in session_data["data"].keys()],
                    "analysis": session_data["analysis"],
                    "message": f"File already uploaded. Using existing analysis from session {existing_session_id}.",
                    "is_duplicate": True
                }
        
        # Process based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(content.decode('utf-8')))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(content)
        elif file.filename.endswith('.json'):
            df = pd.read_json(StringIO(content.decode('utf-8')))
        
        # Generate session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Process data
        processed_data = data_processor.analyze_dataset(df)
        
        # Store session data
        active_sessions[session_id] = {
            "data": df.to_dict(),
            "analysis": processed_data,
            "uploaded_at": datetime.now().isoformat(),
            "filename": file.filename,
            "file_hash": file_hash
        }
        
        # Store file hash mapping
        file_hash_to_session[file_hash] = session_id
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "shape": [int(df.shape[0]), int(df.shape[1])],
            "columns": [str(col) for col in df.columns],
            "analysis": processed_data,
            "message": "Data uploaded and analyzed successfully",
            "is_duplicate": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/suggest-models/{session_id}")
async def suggest_models(session_id: str, request: ModelSuggestionRequest):
    """Get AI-powered model recommendations"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        df = pd.DataFrame(session_data["data"])
        
        # Get model suggestions from orchestrator
        suggestions = await orchestrator.suggest_models(
            df=df,
            target_column=request.target_column,
            problem_type=request.problem_type,
            data_analysis=session_data["analysis"]
        )
        
        return {
            "session_id": session_id,
            "target_column": request.target_column,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@app.post("/api/train-model/{session_id}")
async def train_model(session_id: str, request: TrainModelRequest):
    """Train selected models"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        df = pd.DataFrame(session_data["data"])
        
        # Train models
        training_results = await orchestrator.train_models(
            df=df,
            target_column=request.target_column,
            selected_models=request.selected_models,
            config=request.train_config or {}
        )
        
        # Store results in session
        session_data["training_results"] = training_results
        
        return {
            "session_id": session_id,
            "target_column": request.target_column,
            "results": training_results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.post("/api/train-model/{session_id}")
async def train_model(
    session_id: str,
    target_column: str,
    selected_models: List[str],
    train_config: Optional[Dict[str, Any]] = None
):
    """Train selected models"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        df = pd.DataFrame(session_data["data"])
        
        # Train models
        training_results = await orchestrator.train_models(
            df=df,
            target_column=target_column,
            selected_models=selected_models,
            config=train_config or {}
        )
        
        # Update session with results
        active_sessions[session_id]["training_results"] = training_results
        
        return {
            "session_id": session_id,
            "results": training_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training models: {str(e)}")

@app.get("/api/generate-charts/{session_id}")
async def generate_charts(session_id: str, chart_types: Optional[List[str]] = None):
    """Generate visualization charts for the dataset and results"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        df = pd.DataFrame(session_data["data"])
        
        # Generate charts
        charts = chart_generator.generate_charts(
            df=df,
            training_results=session_data.get("training_results"),
            chart_types=chart_types
        )
        
        return {
            "session_id": session_id,
            "charts": charts,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {str(e)}")

@app.get("/api/sessions")
async def get_sessions():
    """Get all active sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "filename": data["filename"],
                "uploaded_at": data["uploaded_at"],
                "has_results": "training_results" in data
            }
            for sid, data in active_sessions.items()
        ]
    }

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get specific session details"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = active_sessions[session_id]
    return {
        "session_id": session_id,
        "filename": session_data["filename"],
        "uploaded_at": session_data["uploaded_at"],
        "analysis": session_data["analysis"],
        "has_results": "training_results" in session_data,
        "shape": [len(session_data["data"]), len(session_data["data"].keys())] if session_data["data"] else [0, 0]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
