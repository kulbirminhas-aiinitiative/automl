'use client';

import { useState, useEffect } from 'react';
import { Brain, BarChart3, TrendingUp, Download, RefreshCw, AlertTriangle } from 'lucide-react';

interface DashboardProps {
  sessionId: string;
  onBack: () => void;
}

interface ModelSuggestion {
  model_name: string;
  confidence: number;
  reasoning: string;
  hyperparameters: Record<string, any>;
}

interface TrainingResult {
  model_name: string;
  performance: Record<string, number>;
  training_time: number;
  charts: {
    confusion_matrix?: string;
    feature_importance?: string;
    learning_curve?: string;
    residuals?: string;
  };
}

interface SessionData {
  filename: string;
  shape: [number, number];
  columns: string[];
  analysis: any;
  target_column?: string;
  problem_type?: string;
}

export function Dashboard({ sessionId, onBack }: DashboardProps) {
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [suggestions, setSuggestions] = useState<ModelSuggestion[]>([]);
  const [trainingResults, setTrainingResults] = useState<TrainingResult[]>([]);
  const [selectedTarget, setSelectedTarget] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'models' | 'results'>('overview');

  useEffect(() => {
    fetchSessionData();
  }, [sessionId]);

  const fetchSessionData = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/session/${sessionId}`);
      if (!response.ok) throw new Error('Failed to fetch session data');
      
      const data = await response.json();
      setSessionData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session data');
    }
  };

  const handleGetSuggestions = async () => {
    if (!selectedTarget) {
      setError('Please select a target column');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8080/api/get-model-suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          target_column: selectedTarget
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get suggestions');
      }

      const result = await response.json();
      setSuggestions(result.suggestions);
      setActiveTab('models');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get model suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModel = async (modelName: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8080/api/train-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          model_name: modelName,
          target_column: selectedTarget
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Training failed');
      }

      const result = await response.json();
      setTrainingResults(prev => [...prev, result]);
      setActiveTab('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Training failed');
    } finally {
      setLoading(false);
    }
  };

  const generateCharts = async () => {
    if (!selectedTarget) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/generate-charts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          target_column: selectedTarget
        })
      });

      if (!response.ok) throw new Error('Failed to generate charts');
      
      // Charts are generated and can be accessed via the API
      console.log('Charts generated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate charts');
    } finally {
      setLoading(false);
    }
  };

  if (!sessionData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AutoML Dashboard</h1>
            <p className="text-gray-600">
              Dataset: {sessionData.filename} ({sessionData.shape[0]} rows × {sessionData.shape[1]} columns)
            </p>
          </div>
          <button
            onClick={onBack}
            className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
          >
            Upload New Dataset
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-xl shadow-lg mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {['overview', 'models', 'results'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`py-4 px-2 border-b-2 font-medium text-sm capitalize transition-colors ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Error</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Target Column Selection */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Target Column</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Column (what you want to predict)
                </label>
                <select
                  value={selectedTarget}
                  onChange={(e) => setSelectedTarget(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select a column...</option>
                  {sessionData.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleGetSuggestions}
                  disabled={!selectedTarget || loading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                >
                  {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
                  <Brain className="w-4 h-4" />
                  <span>Get AI Suggestions</span>
                </button>
              </div>
            </div>
          </div>

          {/* Data Overview */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Data Quality</h3>
                <BarChart3 className="w-5 h-5 text-blue-500" />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Overall Score</span>
                  <span className="font-semibold text-green-600">
                    {sessionData.analysis?.data_quality?.overall_score?.toFixed(1) || 'N/A'}/100
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Missing Values</span>
                  <span className="font-semibold">
                    {sessionData.analysis?.data_quality?.missing_percentage?.toFixed(1) || 'N/A'}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Duplicates</span>
                  <span className="font-semibold">
                    {sessionData.analysis?.data_quality?.duplicate_rows || 0}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Column Types</h3>
                <TrendingUp className="w-5 h-5 text-green-500" />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Numerical</span>
                  <span className="font-semibold text-blue-600">
                    {sessionData.analysis?.column_types?.numerical?.length || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Categorical</span>
                  <span className="font-semibold text-purple-600">
                    {sessionData.analysis?.column_types?.categorical?.length || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">DateTime</span>
                  <span className="font-semibold text-orange-600">
                    {sessionData.analysis?.column_types?.datetime?.length || 0}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Actions</h3>
              </div>
              <div className="space-y-3">
                <button
                  onClick={generateCharts}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  Generate Data Charts
                </button>
                <button className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                  <Download className="w-4 h-4 inline mr-2" />
                  Export Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'models' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Model Suggestions</h2>
          {suggestions.length === 0 ? (
            <div className="text-center py-8">
              <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No suggestions yet. Select a target column and click "Get AI Suggestions".</p>
            </div>
          ) : (
            <div className="grid gap-6">
              {suggestions.map((suggestion, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{suggestion.model_name}</h3>
                      <p className="text-sm text-blue-600">Confidence: {(suggestion.confidence * 100).toFixed(1)}%</p>
                    </div>
                    <button
                      onClick={() => handleTrainModel(suggestion.model_name)}
                      disabled={loading}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
                    >
                      {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
                      <span>Train Model</span>
                    </button>
                  </div>
                  <p className="text-gray-600 mb-4">{suggestion.reasoning}</p>
                  {Object.keys(suggestion.hyperparameters).length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Recommended Hyperparameters:</h4>
                      <div className="bg-gray-50 rounded p-3">
                        <code className="text-sm">
                          {JSON.stringify(suggestion.hyperparameters, null, 2)}
                        </code>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'results' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Training Results</h2>
          {trainingResults.length === 0 ? (
            <div className="text-center py-8">
              <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No training results yet. Train some models to see results here.</p>
            </div>
          ) : (
            <div className="grid gap-6">
              {trainingResults.map((result, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{result.model_name}</h3>
                    <span className="text-sm text-gray-500">
                      Training time: {result.training_time.toFixed(2)}s
                    </span>
                  </div>
                  <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    {Object.entries(result.performance).map(([metric, value]) => (
                      <div key={metric} className="bg-gray-50 rounded p-3">
                        <p className="text-sm text-gray-600 capitalize">{metric.replace('_', ' ')}</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {typeof value === 'number' ? value.toFixed(4) : value}
                        </p>
                      </div>
                    ))}
                  </div>
                  {Object.keys(result.charts).length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Generated Charts:</h4>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(result.charts).map(([chartType, chartPath]) => (
                          <button
                            key={chartType}
                            className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200 transition-colors"
                          >
                            {chartType.replace('_', ' ')}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
