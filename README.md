# AutoML Solution

A comprehensive automated machine learning platform that combines AI-powered model selection with a modern web interface. This application provides end-to-end machine learning workflows, from data upload to model training and visualization.

## 🌟 Features

### 🤖 AI-Powered Model Selection
- **LLM Integration**: Uses OpenAI GPT models for intelligent model recommendations
- **Smart Analysis**: Automatic dataset analysis and preprocessing suggestions
- **Confidence Scoring**: AI provides confidence scores for each model recommendation
- **Reasoning Explanations**: Clear explanations for why specific models are recommended

### 📊 Comprehensive ML Pipeline
- **Multiple Algorithms**: Support for Random Forest, XGBoost, LightGBM, SVM, Linear/Logistic Regression
- **Auto-Preprocessing**: Automatic handling of missing values, categorical encoding, and feature scaling
- **Model Evaluation**: Comprehensive performance metrics for both classification and regression
- **Hyperparameter Optimization**: AI-suggested hyperparameters for optimal performance

### 📈 Advanced Visualization
- **Interactive Charts**: Data distribution, correlation matrices, feature importance plots
- **Model Performance**: Confusion matrices, ROC curves, learning curves, residual plots
- **Real-time Updates**: Dynamic chart generation during model training
- **Export Capabilities**: Download charts and analysis results

### 🌐 Modern Web Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Intuitive Workflow**: Upload → Analyze → Train → Results
- **Real-time Feedback**: Progress indicators and live updates
- **Professional UI**: Clean, modern interface built with React and Tailwind CSS

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
backend/
├── main.py                 # FastAPI application entry point
├── models/
│   └── automl_orchestrator.py  # AI model selection engine
├── utils/
│   ├── chart_generator.py      # Visualization system
│   ├── data_processor.py       # Data analysis and preprocessing
│   └── model_evaluator.py      # Model training and evaluation
└── requirements.txt        # Python dependencies
```

### Frontend (Next.js + React)
```
src/
├── app/
│   └── page.tsx           # Main application page
└── components/
    ├── DataUpload.tsx     # File upload and data analysis
    ├── Dashboard.tsx      # Model selection and results
    ├── Header.tsx         # Navigation and branding
    └── index.ts          # Component exports
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **npm or yarn**

### 1. Clone the Repository
```bash
git clone <repository-url>
cd automl
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv v_automl

# Activate virtual environment
# Windows:
v_automl\Scripts\activate
# macOS/Linux:
source v_automl/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
# Install dependencies
npm install
```

### 4. Environment Configuration
Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### 6. Access the Application
- **Frontend**: http://localhost:3000 (or the port shown in terminal)
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs

## 📝 Usage Guide

### 1. Data Upload
- Click "Upload Dataset" or drag and drop your file
- Supported formats: CSV, XLSX, JSON
- Get instant data quality analysis and insights

### 2. Target Selection
- Choose the column you want to predict
- The system automatically detects classification vs regression tasks

### 3. AI Model Suggestions
- Click "Get AI Suggestions" for intelligent model recommendations
- Review confidence scores and reasoning for each suggestion
- See recommended hyperparameters for optimal performance

### 4. Model Training
- Train models with one click
- Monitor real-time training progress
- View comprehensive performance metrics

### 5. Results Analysis
- Compare model performances side-by-side
- Generate interactive visualizations
- Export results and charts for reporting

## 🛠️ API Endpoints

### Data Management
- `POST /api/upload-data` - Upload and analyze dataset
- `GET /api/session/{session_id}` - Retrieve session data

### ML Operations
- `POST /api/get-model-suggestions` - Get AI-powered model recommendations
- `POST /api/train-model` - Train a specific model
- `POST /api/generate-charts` - Create visualization charts

### Utilities
- `GET /docs` - Interactive API documentation
- `GET /health` - Health check endpoint

## 🧪 Sample Data

The repository includes `sample_data.csv` with employee performance data for testing:
- **Features**: name, age, salary, experience, department
- **Target**: performance_score
- **Use Case**: Predict employee performance based on demographics and experience

## 🔧 Configuration

### Supported File Formats
- **CSV**: Comma-separated values
- **XLSX**: Excel spreadsheets
- **JSON**: JavaScript Object Notation

### Supported ML Algorithms
- **Classification**: Random Forest, XGBoost, LightGBM, SVM, Logistic Regression
- **Regression**: Random Forest, XGBoost, LightGBM, SVR, Linear Regression

### Performance Metrics
- **Classification**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Regression**: RMSE, MAE, R²-Score, Mean Absolute Percentage Error

## 🚀 Deployment

### Docker Deployment (Coming Soon)
```dockerfile
# Dockerfile example
FROM python:3.11-slim
# ... deployment configuration
```

### Cloud Deployment
- **Vercel**: Frontend deployment
- **Railway/Heroku**: Backend deployment
- **AWS/GCP**: Full-stack deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT model integration
- **Scikit-learn** for machine learning algorithms
- **FastAPI** for high-performance backend
- **Next.js** for modern frontend framework
- **Plotly** for interactive visualizations

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@automl-solution.com
- Documentation: [Link to docs]

---

**Built with ❤️ using Python, FastAPI, React, and Next.js**
