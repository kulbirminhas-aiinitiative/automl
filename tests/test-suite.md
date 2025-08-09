# AutoML System Test Suite

## Overview
Comprehensive testing framework for AutoML solution with Next.js frontend and FastAPI backend.

## Test Categories

### 1. Backend API Tests
- Health check endpoint
- Data upload functionality 
- Model suggestion endpoint
- Model training endpoint
- CORS configuration

### 2. Frontend Component Tests
- Data upload component
- Dashboard component
- Error handling
- Loading states

### 3. Integration Tests
- End-to-end file upload workflow
- Frontend-backend communication
- Error propagation

### 4. Performance Tests
- Response times
- Memory usage
- Concurrent requests

## Test Execution

### Backend Tests
```bash
# Start backend server
source venv/bin/activate
python -m backend.main

# Test endpoints
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/upload -F "file=@sample_data.csv"
```

### Frontend Tests
```bash
# Start frontend server
npm run dev -- --port 3004

# Access in browser
http://localhost:3004
```

### Integration Tests
```bash
# Run end-to-end test script
python test_frontend_e2e.py
```

## Expected Outcomes
- All API endpoints respond correctly
- Frontend loads without errors
- File upload works end-to-end
- No compilation or runtime errors
