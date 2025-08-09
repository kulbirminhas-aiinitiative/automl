#!/bin/bash
# AutoML System Test Runner
# Comprehensive test execution script

echo "=== AutoML System Test Runner ==="
echo "Starting comprehensive system tests..."

# Clear previous logs
> logs/web-output.log
> logs/runtime-errors.log

# Function to check if process is running on port
check_port() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s $url >/dev/null 2>&1; then
            echo "Service at $url is ready"
            return 0
        fi
        echo "Waiting for service at $url (attempt $attempt/$max_attempts)..."
        sleep 2
        ((attempt++))
    done
    
    echo "Service at $url failed to start after $max_attempts attempts"
    return 1
}

# Test 1: Backend Health Check
echo "=== Test 1: Backend API Health Check ==="
source venv/bin/activate
python -m backend.main &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

if wait_for_service "http://localhost:8000/"; then
    echo "✓ Backend health check passed"
else
    echo "✗ Backend health check failed"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Test 2: Frontend Build and Start
echo "=== Test 2: Frontend Build and Health Check ==="
npm run build >> logs/web-output.log 2>> logs/runtime-errors.log
if [ $? -eq 0 ]; then
    echo "✓ Frontend build successful"
else
    echo "✗ Frontend build failed"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

npm run dev -- --port 3004 >> logs/web-output.log 2>> logs/runtime-errors.log &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

if wait_for_service "http://localhost:3004"; then
    echo "✓ Frontend health check passed"
else
    echo "✗ Frontend health check failed"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

# Test 3: API Endpoint Tests
echo "=== Test 3: API Endpoint Tests ==="

# Test upload endpoint
if [ -f "sample_data.csv" ]; then
    UPLOAD_RESULT=$(curl -s -X POST http://localhost:8000/api/upload-data -F "file=@sample_data.csv")
    if echo "$UPLOAD_RESULT" | grep -q "success\|uploaded\|filename\|session_id"; then
        echo "✓ File upload endpoint test passed"
    else
        echo "✗ File upload endpoint test failed"
        echo "Upload response: $UPLOAD_RESULT"
    fi
else
    echo "⚠ sample_data.csv not found, skipping upload test"
fi

# Test 4: Integration Test
echo "=== Test 4: End-to-End Integration Test ==="
if [ -f "test_frontend_e2e.py" ]; then
    python test_frontend_e2e.py >> logs/web-output.log 2>> logs/runtime-errors.log
    if [ $? -eq 0 ]; then
        echo "✓ End-to-end integration test passed"
    else
        echo "✗ End-to-end integration test failed"
    fi
else
    echo "⚠ End-to-end test script not found, skipping"
fi

# Test 5: Error Log Check
echo "=== Test 5: Error Log Analysis ==="
node scripts/read-logs.js
if [ $? -eq 0 ]; then
    echo "✓ No errors found in logs"
else
    echo "✗ Errors detected in logs"
fi

# Cleanup
echo "=== Cleanup ==="
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "Services stopped"

echo "=== Test Summary ==="
echo "All tests completed. Check logs/web-output.log and logs/runtime-errors.log for details."
