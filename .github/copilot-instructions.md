# Copilot Instructions for AutoML Solution

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is an AutoML (Automated Machine Learning) solution with a Next.js frontend and Python FastAPI backend. The system provides:

### Frontend Features
- Data upload and preprocessing interface
- Model selection and configuration
- Real-time training progress monitoring
- Interactive charts and visualizations using Chart.js/Recharts
- Results dashboard with model performance metrics
- AutoML pipeline recommendations

### Backend Features
- FastAPI orchestration server
- Integration with scikit-learn, XGBoost, LightGBM, and other ML libraries
- LLM-powered model selection and hyperparameter optimization
- Automated data preprocessing and feature engineering
- Model training and evaluation pipelines
- Chart generation and insights extraction

## Code Guidelines
- Use TypeScript for all frontend components
- Implement responsive design with Tailwind CSS
- Use React hooks and modern patterns
- Follow RESTful API design for backend endpoints
- Implement proper error handling and loading states
- Use environment variables for configuration
- Add comprehensive JSDoc comments for complex functions
- Follow the established file structure and naming conventions

## Key Technologies
- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS, Chart.js/Recharts
- **Backend**: FastAPI, Python, scikit-learn, XGBoost, pandas, numpy
- **Database**: SQLite/PostgreSQL for metadata storage
- **ML Libraries**: scikit-learn, XGBoost, LightGBM, TensorFlow/PyTorch (optional)
- **Visualization**: Chart.js, Recharts, Plotly (for backend-generated charts)

## File Structure
- `/src/app` - Next.js app router pages and API routes
- `/src/components` - Reusable React components
- `/src/lib` - Utility functions and configurations
- `/backend` - Python FastAPI backend
- `/backend/models` - ML model implementations
- `/backend/utils` - Backend utility functions
- `/backend/api` - API route handlers

## Coding Conventions
- Use descriptive variable and function names
- Implement proper TypeScript types and interfaces
- Add loading states and error boundaries
- Use consistent formatting and linting
- Write unit tests for critical functions
- Document API endpoints with proper OpenAPI specs
