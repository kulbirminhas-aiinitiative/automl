# Changelog

All notable changes to the AutoML project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-08-08

### Added
- **Duplicate File Detection**: MD5 hashing to detect and reuse existing analysis
- **Enhanced User Feedback**: Different visual states for new vs duplicate uploads
- **Comprehensive Documentation**: CORS troubleshooting and upload functionality guides
- **End-to-End Testing**: Complete automated testing suite for frontend-backend integration
- **Manual Dashboard Navigation**: "Go to Dashboard Now" button for immediate access
- **Smart Session Management**: Intelligent reuse of existing sessions for duplicate files

### Fixed
- **CORS Configuration**: Added support for frontend running on port 3004
- **LinearRegression Model**: Removed invalid random_state parameter
- **Dashboard API Integration**: Fixed data transformation between API and component interfaces
- **Upload Button States**: Proper state management and visual feedback
- **JSON Serialization**: Complete resolution of numpy type conversion issues
- **Frontend Error Handling**: Better error messages and network failure handling

### Changed
- **Upload Experience**: Faster processing for duplicate files (1s vs 2s redirect)
- **Visual Design**: Yellow warning for duplicates, green success for new uploads
- **API Responses**: Enhanced structure with duplicate detection flags
- **Button Behavior**: Dynamic text based on upload state and file status
- **Error Messages**: More specific and actionable error descriptions

### Technical
- **Backend CORS**: Now supports localhost:3000, 3004, and 127.0.0.1 variants
- **File Processing**: Hash-based duplicate detection with session mapping
- **Request Handling**: Pydantic models for proper API request validation
- **Response Format**: Standardized JSON responses with comprehensive metadata
- **TypeScript**: Enhanced interfaces for better type safety

## [1.1.0] - 2025-08-08log

All notable changes to the AutoML project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.1.0] - 2025-08-08

### 🎯 Major Features
- **Comprehensive Testing Infrastructure**: Added automated testing suite with 8+ datasets
- **Dataset Management**: Implemented Kaggle API integration and dataset download utilities
- **Error Handling**: Enhanced API error responses and logging

### 🔧 Bug Fixes
- **JSON Serialization**: Fixed critical numpy type serialization errors in FastAPI
  - Resolved `TypeError: 'numpy.int64' object is not iterable`
  - Fixed pandas dtypes serialization in data processor
  - Ensured all API responses are JSON-serializable
- **OpenMP Integration**: Fixed XGBoost compatibility on macOS with OpenMP installation
- **API Endpoints**: Resolved 500 errors in model suggestion and training endpoints

### 📦 Dependencies
- **scikit-learn**: Verified compatibility with v1.7.1
- **XGBoost**: Updated to v3.0.3 with proper OpenMP support
- **LightGBM**: Updated to v4.6.0
- **Pandas**: Updated to v2.3.1
- **NumPy**: Updated to v2.3.2

### 🧪 Testing
- **API Testing**: Added comprehensive API endpoint testing (`test_automl_api.py`)
- **Frontend Testing**: Added Selenium-based UI testing framework (`test_frontend.py`)
- **Dataset Testing**: Added synthetic and real-world dataset generators
- **Fix Verification**: Added specific scikit-learn compatibility tests

### 📊 Datasets Added
- Synthetic regression and classification datasets
- Boston Housing (regression)
- Iris classification
- Wine classification
- Customer churn prediction
- Diabetes progression
- Titanic survival
- Tips regression

### 🔧 Infrastructure
- **Git Workflow**: Enhanced .gitignore for ML project structure
- **Documentation**: Added comprehensive fix documentation (`SKLEARN_FIXES.md`)
- **Utilities**: Added master test runner (`run_tests.py`)
- **Demo Scripts**: Added complete workflow demonstration (`final_test_demo.py`)

### 🌐 API Improvements
- `POST /api/upload-data`: Fixed numpy serialization in data analysis
- `POST /api/suggest-models/{id}`: Resolved model suggestion JSON errors
- `GET /api/session/{id}`: Improved session data serialization
- `GET /docs`: Updated API documentation with proper schemas

## [v1.0.0] - 2025-08-07

### 🎯 Initial Release
- **AutoML Core**: Basic automated machine learning pipeline
- **Frontend**: Next.js React application with data upload interface
- **Backend**: FastAPI server with ML model orchestration
- **AI Integration**: OpenAI-powered model suggestions and analysis

### 🔧 Core Features
- **Data Upload**: CSV, Excel, JSON file support
- **Model Training**: Random Forest, XGBoost, LightGBM, Linear models
- **Visualization**: Chart generation and results dashboard
- **Session Management**: Multi-user session handling

### 📦 Initial Dependencies
- Next.js 15 for frontend
- FastAPI for backend API
- scikit-learn for ML algorithms
- pandas for data processing
- Chart.js for visualizations

---

## Version Comparison

| Version | Release Date | Major Changes | Breaking Changes |
|---------|-------------|---------------|------------------|
| v1.1.0  | 2025-08-08  | Testing infrastructure, serialization fixes | None |
| v1.0.0  | 2025-08-07  | Initial AutoML application | N/A |

## Migration Guide

### From v1.0.0 to v1.1.0
No breaking changes. This is a backward-compatible update with bug fixes and new testing features.

**Recommended actions:**
1. Pull latest changes: `git pull origin main`
2. Install new dependencies: `pip install -r backend/requirements.txt`
3. Run tests to verify setup: `python run_tests.py`
4. Optional: Use new testing utilities for development

## Development Status

- ✅ **v1.1.0**: Released - Stable with comprehensive testing
- 🚧 **v1.2.0**: In development - Advanced ML features
- 📋 **v1.3.0**: Planned - Model deployment and serving

## Contributing

Please see [VERSION_CONTROL.md](VERSION_CONTROL.md) for development workflow and contribution guidelines.
