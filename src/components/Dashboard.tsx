'use client';

import { useState, useEffect } from 'react';
import { Brain, BarChart3, TrendingUp, Download, RefreshCw, AlertTriangle } from 'lucide-react';

/**
 * Props interface for the Dashboard component
 * @interface DashboardProps
 */
interface DashboardProps {
  /** Session ID for the current AutoML session */
  sessionId: string;
  /** Callback function to return to the data upload screen */
  onBack: () => void;
}

/**
 * Interface for AI-generated model suggestions
 * @interface ModelSuggestion
 */
interface ModelSuggestion {
  /** Name of the suggested model */
  model_name?: string;
  /** Confidence score for the suggestion (0-1) */
  confidence?: number;
  /** AI reasoning for why this model was suggested */
  reasoning?: string;
  /** Recommended hyperparameters for the model */
  hyperparameters?: Record<string, unknown>;
}

/**
 * Interface for enhanced suggestions with performance comparison
 * @interface EnhancedSuggestions
 */
interface EnhancedSuggestions {
  /** Problem type (classification/regression) */
  problem_type?: string;
  /** Model comparison results */
  model_comparison?: Record<string, {
    model_name: string;
    training_time: number;
    primary_score: number;
    primary_metric: string;
    status: string;
  }>;
  /** Performance ranking of models */
  performance_ranking?: string[];
  /** Recommended models (top performers) */
  recommended_models?: string[];
  /** Rule-based suggestions with reasoning */
  rule_based_suggestions?: {
    recommended_models: string[];
    reasoning: string[];
    method?: string;
  };
}

/**
 * Interface for model training results
 * @interface TrainingResult
 */
interface TrainingResult {
  /** Name of the trained model */
  model_name?: string;
  /** Alternative field name for model */
  model?: string;
  /** Performance metrics for the trained model */
  performance?: Record<string, number>;
  /** Alternative field name for metrics */
  metrics?: Record<string, number>;
  /** Time taken to train the model (in seconds) */
  training_time?: number;
  /** Generated visualization charts */
  charts?: {
    confusion_matrix?: string;
    feature_importance?: string;
    learning_curve?: string;
    residuals?: string;
  };
}

/**
 * Interface for session data containing dataset information
 * @interface SessionData
 */
interface SessionData {
  /** Original filename of the uploaded dataset */
  filename: string;
  /** Shape of the dataset as [rows, columns] */
  shape: [number, number];
  /** List of column names in the dataset */
  columns: string[];
  /** Data analysis results from the backend */
  analysis: {
    data_quality?: {
      overall_score?: number;
      missing_percentage?: number;
      duplicate_rows?: number;
    };
    column_types?: {
      numerical?: string[];
      categorical?: string[];
      datetime?: string[];
    };
  };
  /** Selected target column for prediction */
  target_column?: string;
  /** Type of ML problem (classification/regression) */
  problem_type?: string;
}

/**
 * Main Dashboard component for the AutoML application
 * 
 * Features:
 * - Data overview and quality metrics
 * - Target column selection
 * - AI-powered model suggestions
 * - Model training and results visualization
 * - Interactive charts and performance metrics
 * 
 * @param props - Component props
 * @returns JSX.Element
 */
export function Dashboard({ sessionId, onBack }: DashboardProps) {
  // State management for dashboard data
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [suggestions, setSuggestions] = useState<EnhancedSuggestions | null>(null);
  const [trainingResults, setTrainingResults] = useState<TrainingResult[]>([]);
  const [selectedTarget, setSelectedTarget] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'models' | 'results'>('overview');

  useEffect(() => {
    void fetchSessionData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  /**
   * Fetches session data from the backend API
   * @async
   */
  const fetchSessionData = async (): Promise<void> => {
    console.log('🔄 Dashboard: Fetching session data for session:', sessionId);
    try {
      const response = await fetch(`http://localhost:8000/api/session/${sessionId}`);
      console.log('📡 Dashboard: Session API response status:', response.status);
      
      if (!response.ok) throw new Error('Failed to fetch session data');
      
      const data = await response.json();
      console.log('📊 Dashboard: Session data received:', data);
      
      // Transform API response to match expected interface
      const transformedData: SessionData = {
        filename: data.filename,
        shape: [data.analysis.shape.rows, data.analysis.shape.columns],
        columns: data.analysis.columns.names,
        analysis: {
          data_quality: {
            overall_score: data.analysis.data_quality?.overall_score,
            missing_percentage: data.analysis.missing_values?.total || 0,
            duplicate_rows: 0 // API doesn't provide this yet
          },
          column_types: {
            numerical: data.analysis.data_types?.numeric || [],
            categorical: data.analysis.data_types?.categorical || [],
            datetime: data.analysis.data_types?.datetime || []
          }
        }
      };
      
      setSessionData(transformedData);
      console.log('✅ Dashboard: Session data loaded successfully');
    } catch (err) {
      console.error('❌ Dashboard: Error fetching session data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load session data');
    }
  };

  /**
   * Handles getting AI-powered model suggestions
   * @async
   */
  const handleGetSuggestions = async (): Promise<void> => {
    if (!selectedTarget) {
      setError('Please select a target column');
      return;
    }

    console.log('🤖 Dashboard: Getting suggestions for target:', selectedTarget);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/suggest-models/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_column: selectedTarget
        })
      });

      console.log('📡 Dashboard: Suggestions API response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get suggestions');
      }

      const result = await response.json();
      console.log('🎯 Dashboard: Suggestions received:', result);
      
      // Handle the enhanced suggestions structure
      const enhancedSuggestions: EnhancedSuggestions = {
        problem_type: result.suggestions?.problem_type,
        model_comparison: result.suggestions?.model_comparison,
        performance_ranking: result.suggestions?.performance_ranking,
        recommended_models: result.suggestions?.recommended_models,
        rule_based_suggestions: result.suggestions?.rule_based_suggestions
      };
      
      setSuggestions(enhancedSuggestions);
      setActiveTab('models');
      console.log('✅ Dashboard: Suggestions loaded successfully');
    } catch (err) {
      console.error('❌ Dashboard: Error getting suggestions:', err);
      setError(err instanceof Error ? err.message : 'Failed to get model suggestions');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handles training a specific model
   * @param modelName - Name of the model to train
   * @async
   */
  const handleTrainModel = async (modelName: string): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/train-model/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_column: selectedTarget,
          selected_models: [modelName]
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Training failed');
      }

      const result = await response.json();
      console.log('🎯 Dashboard: Training result received:', result);
      
      // Transform the API response to match our interface
      let trainingResult: TrainingResult;
      
      if (result.results && result.results.results && result.results.results[modelName]) {
        // Handle the nested results.results.modelName structure
        const modelData = result.results.results[modelName];
        trainingResult = {
          model_name: modelData.model || modelName,
          model: modelData.model || modelName,
          training_time: modelData.training_time,
          metrics: modelData.metrics,
          performance: modelData.metrics, // Use metrics as performance
          charts: modelData.charts || {}
        };
      } else if (result.results && result.results[modelName]) {
        // Handle results.modelName structure
        const modelData = result.results[modelName];
        trainingResult = {
          model_name: modelData.model || modelName,
          model: modelData.model || modelName,
          training_time: modelData.training_time,
          metrics: modelData.metrics,
          performance: modelData.metrics,
          charts: modelData.charts || {}
        };
      } else {
        // Handle direct result structure
        trainingResult = {
          model_name: result.model || modelName,
          model: result.model || modelName,
          training_time: result.training_time,
          metrics: result.metrics,
          performance: result.metrics,
          charts: result.charts || {}
        };
      }
      
      console.log('✅ Dashboard: Transformed training result:', trainingResult);
      setTrainingResults(prev => [...prev, trainingResult]);
      setActiveTab('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Training failed');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Generates visualization charts for the dataset
   * @async
   */
  const generateCharts = async (): Promise<void> => {
    if (!selectedTarget) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/generate-charts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          target_column: selectedTarget
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate charts');
      }

      const result = await response.json();
      // Defensive: check for charts structure
      if (!result.charts || !result.charts.charts) {
        setError('No chart data returned from backend');
        return;
      }

      // Store chart data in trainingResults for display in results tab
      setTrainingResults(prev => [
        ...prev,
        {
          model_name: 'Data Charts',
          charts: result.charts.charts,
          training_time: 0,
          metrics: {},
          performance: {}
        }
      ]);
      setActiveTab('results');
      console.log('✅ Charts loaded:', result.charts.charts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate charts');
    } finally {
      setLoading(false);
    }
  };

  // Loading state
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
                onClick={() => setActiveTab(tab as 'overview' | 'models' | 'results')}
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
          <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Model Suggestions & Performance Comparison</h2>
          {!suggestions || !suggestions.recommended_models ? (
            <div className="text-center py-8">
              <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No suggestions yet. Select a target column and click &quot;Get AI Suggestions&quot;.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Performance Comparison Table */}
              {suggestions.model_comparison && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">🏆 Model Performance Comparison</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full border border-gray-200 rounded-lg">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Rank</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Model</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Performance</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Training Time</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {suggestions.performance_ranking?.slice(0, 7).map((modelName, index) => {
                          const comparison = suggestions.model_comparison?.[modelName];
                          if (!comparison) return null;
                          
                          const isRecommended = suggestions.recommended_models?.includes(modelName);
                          const rankColors = ['text-yellow-600', 'text-gray-600', 'text-orange-600'];
                          const rankColor = rankColors[index] || 'text-gray-500';
                          
                          return (
                            <tr key={modelName} className={isRecommended ? 'bg-blue-50' : ''}>
                              <td className={`px-4 py-3 text-sm font-bold ${rankColor}`}>
                                #{index + 1}
                                {index === 0 && ' 🥇'}
                                {index === 1 && ' 🥈'}
                                {index === 2 && ' 🥉'}
                              </td>
                              <td className="px-4 py-3 text-sm font-medium text-gray-900">
                                {modelName}
                                {isRecommended && <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Recommended</span>}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-700">
                                {comparison.primary_metric}: {comparison.primary_score.toFixed(3)}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-700">
                                {comparison.training_time.toFixed(3)}s
                              </td>
                              <td className="px-4 py-3 text-sm">
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  comparison.status === 'success' 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {comparison.status}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-sm">
                                <button
                                  onClick={() => handleTrainModel(modelName)}
                                  disabled={loading || comparison.status !== 'success'}
                                  className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition-colors disabled:opacity-50"
                                >
                                  Train Full Model
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* AI Recommendations */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 AI Recommendations</h3>
                {suggestions.rule_based_suggestions?.reasoning && (
                  <div className="bg-blue-50 rounded-lg p-4 mb-4">
                    <h4 className="font-medium text-blue-900 mb-2">Analysis Summary:</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      {suggestions.rule_based_suggestions.reasoning.map((reason, index) => (
                        <li key={index}>• {reason}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="grid gap-4">
                  {suggestions.recommended_models?.slice(0, 3).map((modelName, index) => {
                    const comparison = suggestions.model_comparison?.[modelName];
                    
                    return (
                      <div key={modelName} className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">
                              {index === 0 && '🥇 '}{index === 1 && '🥈 '}{index === 2 && '🥉 '}
                              {modelName}
                            </h4>
                            {comparison && (
                              <p className="text-sm text-blue-600">
                                {comparison.primary_metric}: {comparison.primary_score.toFixed(3)} 
                                | Training time: {comparison.training_time.toFixed(3)}s
                              </p>
                            )}
                          </div>
                          <button
                            onClick={() => handleTrainModel(modelName)}
                            disabled={loading}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
                          >
                            {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
                            <span>Train Full Model</span>
                          </button>
                        </div>
                        {index === 0 && (
                          <p className="text-sm text-gray-600">
                            🏆 Best performing model based on actual testing with your data
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
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
                    <h3 className="text-lg font-semibold text-gray-900">{result.model_name || result.model || 'Unknown Model'}</h3>
                    <span className="text-sm text-gray-500">
                      Training time: {result.training_time ? result.training_time.toFixed(2) : 'N/A'}s
                    </span>
                  </div>
                  <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    {Object.entries(result.performance || result.metrics || {}).map(([metric, value]) => (
                      <div key={metric} className="bg-gray-50 rounded p-3">
                        <p className="text-sm text-gray-600 capitalize">{metric.replace('_', ' ')}</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {typeof value === 'number' ? value.toFixed(4) : value}
                        </p>
                      </div>
                    ))}
                  </div>
                  {result.charts && Object.keys(result.charts).length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Generated Charts:</h4>
                      <div className="flex flex-wrap gap-2 mb-2">
                        {Object.entries(result.charts).map(([chartType, chartData]) => (
                          <button
                            key={chartType}
                            className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200 transition-colors"
                          >
                            {chartType.replace('_', ' ')}
                          </button>
                        ))}
                      </div>
                      {/* Chart error display and JSON preview */}
                      {Object.entries(result.charts).map(([chartType, chartData]) => (
                        chartData && typeof chartData === 'object' && 'error' in chartData ? (
                          <div key={chartType} className="bg-red-50 border border-red-200 rounded-lg p-3 mb-2">
                            <strong className="text-red-700">{chartType.replace('_', ' ')} Error:</strong>
                            <span className="text-red-600 ml-2">{chartData.error}</span>
                          </div>
                        ) : null
                      ))}
                      <div className="bg-gray-50 rounded p-3 text-xs overflow-auto max-h-64">
                        <pre>{JSON.stringify(result.charts, null, 2)}</pre>
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
