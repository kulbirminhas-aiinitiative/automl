from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
import xgboost as xgb
import lightgbm as lgb
import openai
import os
from datetime import datetime
import json

class AutoMLOrchestrator:
    """
    Main orchestrator that uses LLM to guide the AutoML process
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Define available models
        self.classification_models = {
            "random_forest": RandomForestClassifier,
            "logistic_regression": LogisticRegression,
            "svm": SVC,
            "naive_bayes": GaussianNB,
            "decision_tree": DecisionTreeClassifier,
            "xgboost": xgb.XGBClassifier,
            "lightgbm": lgb.LGBMClassifier
        }
        
        self.regression_models = {
            "random_forest": RandomForestRegressor,
            "linear_regression": LinearRegression,
            "svm": SVR,
            "decision_tree": DecisionTreeRegressor,
            "xgboost": xgb.XGBRegressor,
            "lightgbm": lgb.LGBMRegressor
        }
    
    async def suggest_models(self, df: pd.DataFrame, target_column: str, problem_type: Optional[str] = None, data_analysis: Dict = None) -> Dict[str, Any]:
        """
        Use LLM to suggest best models based on data characteristics
        Enhanced to actually run all models and compare performance
        """
        try:
            # Determine problem type if not provided
            if problem_type is None:
                problem_type = self._determine_problem_type(df, target_column)
            
            # Prepare data summary for LLM
            data_summary = {
                "shape": [int(df.shape[0]), int(df.shape[1])],
                "target_column": str(target_column),
                "target_type": str(df[target_column].dtype),
                "target_unique_values": int(df[target_column].nunique()),
                "missing_values": int(df.isnull().sum().sum()),
                "numeric_columns": int(len(df.select_dtypes(include=[np.number]).columns)),
                "categorical_columns": int(len(df.select_dtypes(include=['object', 'category']).columns)),
                "problem_type": str(problem_type)
            }
            
            # Get all available models for the problem type
            model_dict = self.classification_models if problem_type == "classification" else self.regression_models
            all_models = list(model_dict.keys())
            
            print(f"🔍 Running model comparison for {problem_type} problem...")
            print(f"   Testing models: {all_models}")
            
            # Run quick comparison of all models
            model_comparison = await self._quick_model_comparison(df, target_column, all_models)
            
            # Get LLM recommendations if API key is available
            llm_suggestions = None
            if self.openai_api_key:
                llm_suggestions = await self._get_llm_suggestions(data_summary, model_comparison)
            
            # Fallback to rule-based suggestions with performance data
            rule_based_suggestions = self._get_performance_based_suggestions(data_summary, model_comparison)
            
            # Rank models by performance
            ranked_models = self._rank_models_by_performance(model_comparison, problem_type)
            
            return {
                "problem_type": problem_type,
                "data_summary": data_summary,
                "model_comparison": model_comparison,
                "performance_ranking": ranked_models,
                "llm_suggestions": llm_suggestions,
                "rule_based_suggestions": rule_based_suggestions,
                "recommended_models": ranked_models[:3]  # Top 3 models
            }
            
        except Exception as e:
            print(f"❌ Error in model suggestion: {str(e)}")
            return {
                "error": f"Error in model suggestion: {str(e)}",
                "fallback_suggestions": self._get_rule_based_suggestions({"problem_type": problem_type or "classification"})
            }
    
    def _prepare_data(self, df: pd.DataFrame, target_column: str) -> tuple:
        """
        Prepare data for training by handling preprocessing
        """
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Handle categorical variables
        from sklearn.preprocessing import LabelEncoder
        
        categorical_columns = X.select_dtypes(include=['object', 'category']).columns
        
        # Create a copy to avoid modifying original data
        X_processed = X.copy()
        
        # Encode categorical variables
        for col in categorical_columns:
            le = LabelEncoder()
            X_processed[col] = le.fit_transform(X_processed[col].astype(str))
        
        # Handle missing values
        X_processed = X_processed.fillna(X_processed.mean() if len(X_processed.select_dtypes(include=[np.number]).columns) > 0 else 0)
        
        return X_processed, y

    async def train_models(self, df: pd.DataFrame, target_column: str, selected_models: List[str], config: Dict) -> Dict[str, Any]:
        """
        Train selected models and evaluate their performance
        """
        # Prepare data
        X_processed, y = self._prepare_data(df, target_column)
        
        # Split data - handle small datasets
        test_size = config.get("test_size", 0.2)
        random_state = config.get("random_state", 42)
        
        # For very small datasets, use smaller test size or cross-validation
        if len(X_processed) < 10:
            test_size = min(0.1, 1/len(X_processed))  # At least 1 sample for test
            print(f"⚠️  Small dataset detected ({len(X_processed)} samples). Using test_size={test_size:.2f}")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y, test_size=test_size, random_state=random_state
        )
        
        # Determine problem type
        problem_type = self._determine_problem_type(df, target_column)
        model_dict = self.classification_models if problem_type == "classification" else self.regression_models
        
        # Validate selected models
        invalid_models = [m for m in selected_models if m not in model_dict]
        if invalid_models:
            raise ValueError(f"Invalid model(s) selected: {', '.join(invalid_models)}. Available models for {problem_type}: {', '.join(model_dict.keys())}")

        results = {}
        
        for model_name in selected_models:
            if model_name in model_dict:
                try:
                    # Initialize model with appropriate parameters
                    model_class = model_dict[model_name]
                    
                    # Some models don't accept random_state
                    if model_name in ["linear_regression", "naive_bayes"]:
                        model = model_class()
                    else:
                        model = model_class(random_state=random_state)
                    
                    # Train model
                    start_time = datetime.now()
                    model.fit(X_train, y_train)
                    training_time = (datetime.now() - start_time).total_seconds()
                    
                    # Make predictions
                    train_pred = model.predict(X_train)
                    test_pred = model.predict(X_test)
                    
                    # Calculate metrics
                    metrics = self._calculate_metrics(y_train, train_pred, y_test, test_pred, problem_type)
                    
                    results[model_name] = {
                        "model": str(model_name),
                        "training_time": float(training_time),
                        "metrics": metrics,
                        "feature_importance": self._get_feature_importance(model, X_processed.columns),
                        "status": "success"
                    }
                    
                except Exception as e:
                    results[model_name] = {
                        "model": str(model_name),
                        "status": "error",
                        "error": str(e)
                    }
        
        return {
            "results": results,
            "problem_type": str(problem_type),
            "data_shape": {
                "train": [int(X_train.shape[0]), int(X_train.shape[1])], 
                "test": [int(X_test.shape[0]), int(X_test.shape[1])]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _determine_problem_type(self, df: pd.DataFrame, target_column: str) -> str:
        """Determine if it's a classification or regression problem"""
        target = df[target_column]
        
        # Check if target is numeric and has many unique values
        if pd.api.types.is_numeric_dtype(target):
            unique_ratio = target.nunique() / len(target)
            if unique_ratio > 0.05:  # More than 5% unique values suggests regression
                return "regression"
        
        return "classification"
    
    def _preprocess_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Simple preprocessing for features"""
        X_processed = X.copy()
        
        # Handle categorical variables with simple label encoding
        for col in X_processed.select_dtypes(include=['object', 'category']).columns:
            X_processed[col] = pd.Categorical(X_processed[col]).codes
        
        # Fill missing values
        X_processed = X_processed.fillna(X_processed.mean())
        
        return X_processed
    
    def _calculate_metrics(self, y_train, train_pred, y_test, test_pred, problem_type: str) -> Dict[str, float]:
        """Calculate appropriate metrics based on problem type"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error, r2_score
        import math
        
        def clean_nan_values(value):
            """Convert NaN/inf values to None for JSON serialization"""
            if isinstance(value, (int, float)) and (math.isnan(value) or math.isinf(value)):
                return None
            return value
        
        metrics = {}
        
        if problem_type == "classification":
            metrics = {
                "train_accuracy": clean_nan_values(float(accuracy_score(y_train, train_pred))),
                "test_accuracy": clean_nan_values(float(accuracy_score(y_test, test_pred))),
                "precision": clean_nan_values(float(precision_score(y_test, test_pred, average='weighted', zero_division=0))),
                "recall": clean_nan_values(float(recall_score(y_test, test_pred, average='weighted', zero_division=0))),
                "f1_score": clean_nan_values(float(f1_score(y_test, test_pred, average='weighted', zero_division=0)))
            }
        else:  # regression
            # Handle small sample size issues
            try:
                r2_value = r2_score(y_test, test_pred)
            except:
                r2_value = float('nan')
                
            metrics = {
                "train_mse": clean_nan_values(float(mean_squared_error(y_train, train_pred))),
                "test_mse": clean_nan_values(float(mean_squared_error(y_test, test_pred))),
                "train_mae": clean_nan_values(float(mean_absolute_error(y_train, train_pred))),
                "test_mae": clean_nan_values(float(mean_absolute_error(y_test, test_pred))),
                "r2_score": clean_nan_values(float(r2_value))
            }
        
        return metrics
    
    def _get_feature_importance(self, model, feature_names) -> Dict[str, float]:
        """Extract feature importance if available"""
        import math
        
        def clean_nan_values(value):
            """Convert NaN/inf values to None for JSON serialization"""
            if isinstance(value, (int, float)) and (math.isnan(value) or math.isinf(value)):
                return None
            return value
        
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                return {str(name): clean_nan_values(float(imp)) for name, imp in zip(feature_names, importance)}
            elif hasattr(model, 'coef_'):
                coef = model.coef_
                if len(coef.shape) > 1:
                    coef = np.abs(coef).mean(axis=0)
                return {str(name): clean_nan_values(float(imp)) for name, imp in zip(feature_names, np.abs(coef))}
        except:
            pass
        
        return {}
    
    async def _get_llm_suggestions(self, data_summary: Dict) -> Dict[str, Any]:
        """Get model suggestions from LLM"""
        try:
            prompt = f"""
            Given the following dataset characteristics, suggest the best machine learning models:
            
            Dataset Info:
            - Shape: {data_summary['shape']}
            - Problem Type: {data_summary['problem_type']}
            - Target Column Type: {data_summary['target_type']}
            - Unique Target Values: {data_summary['target_unique_values']}
            - Missing Values: {data_summary['missing_values']}
            - Numeric Columns: {data_summary['numeric_columns']}
            - Categorical Columns: {data_summary['categorical_columns']}
            
            Please suggest the top 3-5 most suitable machine learning models and explain why.
            Respond in JSON format with 'recommended_models' (list of model names) and 'reasoning' (explanation).
            
            Available models for classification: random_forest, logistic_regression, svm, naive_bayes, decision_tree, xgboost, lightgbm
            Available models for regression: random_forest, linear_regression, svm, decision_tree, xgboost, lightgbm
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM suggestion error: {e}")
            return None
    
    async def _quick_model_comparison(self, df: pd.DataFrame, target_column: str, models_to_test: List[str]) -> Dict[str, Any]:
        """
        Run a quick comparison of all models to determine best performers
        """
        print(f"🏃‍♂️ Running quick model comparison...")
        
        try:
            # Prepare data
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Handle categorical variables
            X_processed = self._preprocess_features(X)
            
            # Use smaller split for quick comparison
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=0.3, random_state=42
            )
            
            # Determine problem type
            problem_type = self._determine_problem_type(df, target_column)
            model_dict = self.classification_models if problem_type == "classification" else self.regression_models
            
            comparison_results = {}
            
            for model_name in models_to_test:
                if model_name in model_dict:
                    try:
                        print(f"   Testing {model_name}...")
                        
                        # Initialize model
                        model_class = model_dict[model_name]
                        if model_name in ["linear_regression", "naive_bayes"]:
                            model = model_class()
                        else:
                            model = model_class(random_state=42)
                        
                        # Quick training
                        start_time = datetime.now()
                        model.fit(X_train, y_train)
                        training_time = (datetime.now() - start_time).total_seconds()
                        
                        # Quick predictions
                        train_pred = model.predict(X_train)
                        test_pred = model.predict(X_test)
                        
                        # Calculate metrics
                        metrics = self._calculate_metrics(y_train, train_pred, y_test, test_pred, problem_type)
                        
                        # Get primary performance metric
                        if problem_type == "classification":
                            primary_score = metrics.get("test_accuracy", 0)
                            primary_metric = "accuracy"
                        else:
                            primary_score = metrics.get("r2_score", 0)
                            primary_metric = "r2_score"
                        
                        comparison_results[model_name] = {
                            "model_name": model_name,
                            "training_time": training_time,
                            "primary_score": primary_score,
                            "primary_metric": primary_metric,
                            "all_metrics": metrics,
                            "status": "success"
                        }
                        
                        print(f"     ✅ {model_name}: {primary_metric}={primary_score:.3f}, time={training_time:.3f}s")
                        
                    except Exception as e:
                        print(f"     ❌ {model_name}: Failed - {str(e)}")
                        comparison_results[model_name] = {
                            "model_name": model_name,
                            "status": "failed",
                            "error": str(e),
                            "primary_score": 0
                        }
            
            print(f"✅ Model comparison completed: {len(comparison_results)} models tested")
            return comparison_results
            
        except Exception as e:
            print(f"❌ Error in model comparison: {str(e)}")
            return {}
    
    def _rank_models_by_performance(self, model_comparison: Dict[str, Any], problem_type: str) -> List[str]:
        """
        Rank models by their performance scores
        """
        try:
            # Filter successful models and sort by primary score
            successful_models = [
                (name, result) for name, result in model_comparison.items() 
                if result.get("status") == "success"
            ]
            
            # Sort by primary score (higher is better)
            ranked = sorted(successful_models, key=lambda x: x[1]["primary_score"], reverse=True)
            
            # Return just the model names
            ranked_names = [name for name, _ in ranked]
            
            print(f"🏆 Model ranking by performance:")
            for i, (name, result) in enumerate(ranked[:5], 1):
                score = result["primary_score"]
                metric = result["primary_metric"]
                print(f"   {i}. {name}: {metric}={score:.3f}")
            
            return ranked_names
            
        except Exception as e:
            print(f"❌ Error ranking models: {str(e)}")
            return []
    
    def _get_performance_based_suggestions(self, data_summary: Dict, model_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate suggestions based on actual performance results
        """
        try:
            # Get top performers
            ranked_models = self._rank_models_by_performance(model_comparison, data_summary["problem_type"])
            
            if not ranked_models:
                return self._get_rule_based_suggestions(data_summary)
            
            # Generate reasoning based on performance
            reasoning = []
            reasoning.append(f"Based on actual model testing with your data:")
            
            for i, model_name in enumerate(ranked_models[:3], 1):
                if model_name in model_comparison:
                    result = model_comparison[model_name]
                    score = result.get("primary_score", 0)
                    metric = result.get("primary_metric", "score")
                    time = result.get("training_time", 0)
                    
                    reasoning.append(f"{i}. {model_name}: {metric}={score:.3f} (trained in {time:.3f}s)")
            
            # Add insights about performance vs speed trade-offs
            if len(ranked_models) >= 2:
                top_model = model_comparison.get(ranked_models[0], {})
                second_model = model_comparison.get(ranked_models[1], {})
                
                if top_model.get("training_time", 0) > second_model.get("training_time", 0) * 2:
                    reasoning.append(f"Note: {ranked_models[1]} trains much faster with similar performance")
            
            return {
                "recommended_models": ranked_models[:3],
                "reasoning": reasoning,
                "performance_data": model_comparison,
                "method": "performance_based"
            }
            
        except Exception as e:
            print(f"❌ Error in performance-based suggestions: {str(e)}")
            return self._get_rule_based_suggestions(data_summary)
    
    def _get_rule_based_suggestions(self, data_summary: Dict) -> Dict[str, Any]:
        """Fallback rule-based model suggestions"""
        problem_type = data_summary.get("problem_type", "classification")
        
        if problem_type == "classification":
            return {
                "recommended_models": ["random_forest", "xgboost", "logistic_regression"],
                "reasoning": "Random Forest and XGBoost are robust ensemble methods, Logistic Regression provides interpretability"
            }
        else:
            return {
                "recommended_models": ["random_forest", "xgboost", "linear_regression"],
                "reasoning": "Random Forest and XGBoost handle non-linear relationships, Linear Regression provides baseline"
            }
