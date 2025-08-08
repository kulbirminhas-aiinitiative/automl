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
            
            # Get LLM recommendations if API key is available
            llm_suggestions = None
            if self.openai_api_key:
                llm_suggestions = await self._get_llm_suggestions(data_summary)
            
            # Fallback to rule-based suggestions
            rule_based_suggestions = self._get_rule_based_suggestions(data_summary)
            
            return {
                "problem_type": problem_type,
                "data_summary": data_summary,
                "llm_suggestions": llm_suggestions,
                "rule_based_suggestions": rule_based_suggestions,
                "recommended_models": llm_suggestions.get("recommended_models", rule_based_suggestions["recommended_models"]) if llm_suggestions else rule_based_suggestions["recommended_models"]
            }
            
        except Exception as e:
            return {
                "error": f"Error in model suggestion: {str(e)}",
                "fallback_suggestions": self._get_rule_based_suggestions({"problem_type": problem_type or "classification"})
            }
    
    async def train_models(self, df: pd.DataFrame, target_column: str, selected_models: List[str], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Train selected models and return results
        """
        try:
            # Prepare data
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Handle categorical variables (simple encoding)
            X_processed = self._preprocess_features(X)
            
            # Split data
            test_size = config.get("test_size", 0.2)
            random_state = config.get("random_state", 42)
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=test_size, random_state=random_state
            )
            
            # Determine problem type
            problem_type = self._determine_problem_type(df, target_column)
            model_dict = self.classification_models if problem_type == "classification" else self.regression_models
            
            results = {}
            
            for model_name in selected_models:
                if model_name in model_dict:
                    try:
                        # Initialize model
                        model_class = model_dict[model_name]
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
            
        except Exception as e:
            return {"error": f"Error in model training: {str(e)}"}
    
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
        
        metrics = {}
        
        if problem_type == "classification":
            metrics = {
                "train_accuracy": float(accuracy_score(y_train, train_pred)),
                "test_accuracy": float(accuracy_score(y_test, test_pred)),
                "precision": float(precision_score(y_test, test_pred, average='weighted', zero_division=0)),
                "recall": float(recall_score(y_test, test_pred, average='weighted', zero_division=0)),
                "f1_score": float(f1_score(y_test, test_pred, average='weighted', zero_division=0))
            }
        else:  # regression
            metrics = {
                "train_mse": float(mean_squared_error(y_train, train_pred)),
                "test_mse": float(mean_squared_error(y_test, test_pred)),
                "train_mae": float(mean_absolute_error(y_train, train_pred)),
                "test_mae": float(mean_absolute_error(y_test, test_pred)),
                "r2_score": float(r2_score(y_test, test_pred))
            }
        
        return metrics
    
    def _get_feature_importance(self, model, feature_names) -> Dict[str, float]:
        """Extract feature importance if available"""
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                return {str(name): float(imp) for name, imp in zip(feature_names, importance)}
            elif hasattr(model, 'coef_'):
                coef = model.coef_
                if len(coef.shape) > 1:
                    coef = np.abs(coef).mean(axis=0)
                return {str(name): float(imp) for name, imp in zip(feature_names, np.abs(coef))}
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
            return None
    
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
