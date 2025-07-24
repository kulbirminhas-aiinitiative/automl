import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import json

class ChartGenerator:
    """
    Generate various charts and visualizations for data analysis and model results
    """
    
    def __init__(self):
        # Set style for matplotlib
        plt.style.use('default')
        sns.set_palette("husl")
    
    def generate_charts(self, df: pd.DataFrame, training_results: Optional[Dict] = None, chart_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive charts for the dataset and model results
        """
        charts = {}
        
        try:
            # Default chart types if not specified
            if chart_types is None:
                chart_types = ["data_overview", "correlation", "distribution", "missing_values"]
                if training_results:
                    chart_types.extend(["model_performance", "feature_importance"])
            
            # Generate data overview charts
            if "data_overview" in chart_types:
                charts["data_overview"] = self._generate_data_overview(df)
            
            # Generate correlation heatmap
            if "correlation" in chart_types:
                charts["correlation"] = self._generate_correlation_heatmap(df)
            
            # Generate distribution plots
            if "distribution" in chart_types:
                charts["distribution"] = self._generate_distribution_plots(df)
            
            # Generate missing values chart
            if "missing_values" in chart_types:
                charts["missing_values"] = self._generate_missing_values_chart(df)
            
            # Generate model performance charts
            if "model_performance" in chart_types and training_results:
                charts["model_performance"] = self._generate_model_performance_chart(training_results)
            
            # Generate feature importance charts
            if "feature_importance" in chart_types and training_results:
                charts["feature_importance"] = self._generate_feature_importance_chart(training_results)
            
            return {
                "charts": charts,
                "chart_count": len(charts),
                "generated_types": list(charts.keys())
            }
            
        except Exception as e:
            return {"error": f"Error generating charts: {str(e)}"}
    
    def _generate_data_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate basic data overview charts"""
        try:
            # Data types distribution
            dtype_counts = df.dtypes.value_counts()
            
            fig = go.Figure(data=[
                go.Bar(
                    x=dtype_counts.index.astype(str),
                    y=dtype_counts.values,
                    marker_color='skyblue'
                )
            ])
            
            fig.update_layout(
                title="Data Types Distribution",
                xaxis_title="Data Type",
                yaxis_title="Count",
                template="plotly_white"
            )
            
            # Basic statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            stats_data = []
            
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                stats_data.append({
                    'column': col,
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max()
                })
            
            return {
                "data_types_chart": json.loads(fig.to_json()),
                "basic_statistics": stats_data,
                "shape": df.shape,
                "memory_usage": df.memory_usage(deep=True).sum()
            }
            
        except Exception as e:
            return {"error": f"Error generating data overview: {str(e)}"}
    
    def _generate_correlation_heatmap(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate correlation heatmap for numeric columns"""
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                return {"message": "No numeric columns found for correlation analysis"}
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Create heatmap using plotly
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Feature Correlation Heatmap",
                template="plotly_white",
                width=600,
                height=600
            )
            
            # Find highly correlated pairs
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        corr_pairs.append({
                            'feature1': corr_matrix.columns[i],
                            'feature2': corr_matrix.columns[j],
                            'correlation': corr_val
                        })
            
            return {
                "heatmap": json.loads(fig.to_json()),
                "high_correlations": corr_pairs
            }
            
        except Exception as e:
            return {"error": f"Error generating correlation heatmap: {str(e)}"}
    
    def _generate_distribution_plots(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate distribution plots for numeric columns"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns[:6]  # Limit to 6 columns
            
            if len(numeric_cols) == 0:
                return {"message": "No numeric columns found for distribution analysis"}
            
            # Create subplots
            n_cols = min(3, len(numeric_cols))
            n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
            
            fig = make_subplots(
                rows=n_rows,
                cols=n_cols,
                subplot_titles=list(numeric_cols),
                vertical_spacing=0.08
            )
            
            for idx, col in enumerate(numeric_cols):
                row = idx // n_cols + 1
                col_pos = idx % n_cols + 1
                
                # Create histogram
                fig.add_trace(
                    go.Histogram(
                        x=df[col].dropna(),
                        name=col,
                        showlegend=False,
                        marker_color='lightblue'
                    ),
                    row=row,
                    col=col_pos
                )
            
            fig.update_layout(
                title="Distribution of Numeric Features",
                template="plotly_white",
                height=300 * n_rows
            )
            
            return {
                "distribution_plots": json.loads(fig.to_json()),
                "analyzed_columns": list(numeric_cols)
            }
            
        except Exception as e:
            return {"error": f"Error generating distribution plots: {str(e)}"}
    
    def _generate_missing_values_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate missing values visualization"""
        try:
            missing_data = df.isnull().sum()
            missing_percentage = (missing_data / len(df)) * 100
            
            # Filter columns with missing values
            missing_cols = missing_data[missing_data > 0]
            
            if len(missing_cols) == 0:
                return {"message": "No missing values found in the dataset"}
            
            fig = go.Figure()
            
            # Add bars for missing counts
            fig.add_trace(go.Bar(
                x=missing_cols.index,
                y=missing_cols.values,
                name='Missing Count',
                marker_color='coral',
                yaxis='y'
            ))
            
            # Add line for missing percentage
            fig.add_trace(go.Scatter(
                x=missing_cols.index,
                y=missing_percentage[missing_cols.index].values,
                mode='lines+markers',
                name='Missing %',
                yaxis='y2',
                line=dict(color='darkblue', width=2),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Missing Values Analysis",
                xaxis_title="Columns",
                yaxis=dict(title="Missing Count", side="left"),
                yaxis2=dict(title="Missing Percentage (%)", side="right", overlaying="y"),
                template="plotly_white",
                legend=dict(x=0.02, y=0.98)
            )
            
            return {
                "missing_values_chart": json.loads(fig.to_json()),
                "missing_summary": {
                    "total_missing": int(missing_data.sum()),
                    "columns_with_missing": len(missing_cols),
                    "missing_percentage_total": float((missing_data.sum() / df.size) * 100)
                }
            }
            
        except Exception as e:
            return {"error": f"Error generating missing values chart: {str(e)}"}
    
    def _generate_model_performance_chart(self, training_results: Dict) -> Dict[str, Any]:
        """Generate model performance comparison charts"""
        try:
            results = training_results.get("results", {})
            problem_type = training_results.get("problem_type", "classification")
            
            if not results:
                return {"message": "No training results available"}
            
            # Extract metrics for comparison
            model_names = []
            metrics_data = {}
            
            for model_name, result in results.items():
                if result.get("status") == "success":
                    model_names.append(model_name)
                    metrics = result.get("metrics", {})
                    
                    for metric_name, value in metrics.items():
                        if metric_name not in metrics_data:
                            metrics_data[metric_name] = []
                        metrics_data[metric_name].append(value)
            
            if not model_names:
                return {"message": "No successful model results found"}
            
            # Create performance comparison chart
            fig = go.Figure()
            
            # Add bars for each metric
            colors = ['skyblue', 'lightcoral', 'lightgreen', 'plum', 'khaki']
            
            for idx, (metric_name, values) in enumerate(metrics_data.items()):
                if len(values) == len(model_names):
                    fig.add_trace(go.Bar(
                        name=metric_name.replace('_', ' ').title(),
                        x=model_names,
                        y=values,
                        marker_color=colors[idx % len(colors)]
                    ))
            
            fig.update_layout(
                title=f"Model Performance Comparison ({problem_type.title()})",
                xaxis_title="Models",
                yaxis_title="Score",
                barmode='group',
                template="plotly_white"
            )
            
            # Training time comparison
            training_times = []
            for model_name in model_names:
                training_times.append(results[model_name].get("training_time", 0))
            
            time_fig = go.Figure(data=[
                go.Bar(
                    x=model_names,
                    y=training_times,
                    marker_color='lightsteelblue',
                    text=[f"{t:.2f}s" for t in training_times],
                    textposition='auto'
                )
            ])
            
            time_fig.update_layout(
                title="Model Training Time Comparison",
                xaxis_title="Models",
                yaxis_title="Training Time (seconds)",
                template="plotly_white"
            )
            
            return {
                "performance_chart": json.loads(fig.to_json()),
                "training_time_chart": json.loads(time_fig.to_json()),
                "best_model": model_names[0] if model_names else None
            }
            
        except Exception as e:
            return {"error": f"Error generating model performance chart: {str(e)}"}
    
    def _generate_feature_importance_chart(self, training_results: Dict) -> Dict[str, Any]:
        """Generate feature importance charts for models that support it"""
        try:
            results = training_results.get("results", {})
            
            importance_charts = {}
            
            for model_name, result in results.items():
                if result.get("status") == "success":
                    feature_importance = result.get("feature_importance", {})
                    
                    if feature_importance:
                        # Sort features by importance
                        sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
                        
                        # Take top 10 features
                        top_features = sorted_features[:10]
                        
                        if top_features:
                            features, importances = zip(*top_features)
                            
                            fig = go.Figure(data=[
                                go.Bar(
                                    x=list(importances),
                                    y=list(features),
                                    orientation='h',
                                    marker_color='lightblue',
                                    text=[f"{imp:.3f}" for imp in importances],
                                    textposition='auto'
                                )
                            ])
                            
                            fig.update_layout(
                                title=f"Feature Importance - {model_name.replace('_', ' ').title()}",
                                xaxis_title="Importance Score",
                                yaxis_title="Features",
                                template="plotly_white",
                                height=400
                            )
                            
                            importance_charts[model_name] = json.loads(fig.to_json())
            
            return {
                "feature_importance_charts": importance_charts,
                "models_with_importance": list(importance_charts.keys())
            }
            
        except Exception as e:
            return {"error": f"Error generating feature importance chart: {str(e)}"}
