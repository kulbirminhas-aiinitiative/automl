from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, classification_report, roc_auc_score
)
import pandas as pd

class ModelEvaluator:
    """
    Comprehensive model evaluation and comparison
    """
    
    def __init__(self):
        pass
    
    def evaluate_classification_model(self, y_true, y_pred, y_pred_proba=None) -> Dict[str, Any]:
        """
        Comprehensive evaluation for classification models
        """
        try:
            metrics = {
                "accuracy": float(accuracy_score(y_true, y_pred)),
                "precision": float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
                "recall": float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
                "f1_score": float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
            }
            
            # Add AUC score if probabilities are available
            if y_pred_proba is not None:
                try:
                    if len(np.unique(y_true)) == 2:  # Binary classification
                        metrics["auc_score"] = float(roc_auc_score(y_true, y_pred_proba[:, 1]))
                    else:  # Multi-class classification
                        metrics["auc_score"] = float(roc_auc_score(y_true, y_pred_proba, multi_class='ovr', average='weighted'))
                except:
                    metrics["auc_score"] = None
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            metrics["confusion_matrix"] = cm.tolist()
            
            # Classification report
            try:
                class_report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
                metrics["classification_report"] = class_report
            except:
                metrics["classification_report"] = None
            
            # Class distribution
            unique_classes, counts = np.unique(y_true, return_counts=True)
            metrics["class_distribution"] = dict(zip(unique_classes.tolist(), counts.tolist()))
            
            return metrics
            
        except Exception as e:
            return {"error": f"Error evaluating classification model: {str(e)}"}
    
    def evaluate_regression_model(self, y_true, y_pred) -> Dict[str, Any]:
        """
        Comprehensive evaluation for regression models
        """
        try:
            metrics = {
                "mse": float(mean_squared_error(y_true, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
                "mae": float(mean_absolute_error(y_true, y_pred)),
                "r2_score": float(r2_score(y_true, y_pred))
            }
            
            # Mean Absolute Percentage Error (MAPE)
            def mean_absolute_percentage_error(y_true, y_pred):
                y_true, y_pred = np.array(y_true), np.array(y_pred)
                non_zero_mask = y_true != 0
                if np.any(non_zero_mask):
                    return np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100
                else:
                    return np.inf
            
            metrics["mape"] = float(mean_absolute_percentage_error(y_true, y_pred))
            
            # Residual statistics
            residuals = np.array(y_true) - np.array(y_pred)
            metrics["residual_stats"] = {
                "mean": float(np.mean(residuals)),
                "std": float(np.std(residuals)),
                "min": float(np.min(residuals)),
                "max": float(np.max(residuals))
            }
            
            # Target variable statistics
            metrics["target_stats"] = {
                "mean": float(np.mean(y_true)),
                "std": float(np.std(y_true)),
                "min": float(np.min(y_true)),
                "max": float(np.max(y_true))
            }
            
            return metrics
            
        except Exception as e:
            return {"error": f"Error evaluating regression model: {str(e)}"}
    
    def compare_models(self, model_results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Compare multiple models and rank them
        """
        try:
            if not model_results:
                return {"error": "No model results provided"}
            
            # Determine problem type from first successful model
            problem_type = None
            for result in model_results.values():
                if result.get("status") == "success" and "metrics" in result:
                    metrics = result["metrics"]
                    if "accuracy" in metrics:
                        problem_type = "classification"
                    elif "mse" in metrics:
                        problem_type = "regression"
                    break
            
            if problem_type is None:
                return {"error": "Could not determine problem type from results"}
            
            # Extract successful models
            successful_models = {}
            for model_name, result in model_results.items():
                if result.get("status") == "success":
                    successful_models[model_name] = result
            
            if not successful_models:
                return {"error": "No successful model results found"}
            
            # Rank models based on primary metric
            if problem_type == "classification":
                primary_metric = "f1_score"
                ranking = sorted(
                    successful_models.items(),
                    key=lambda x: x[1]["metrics"].get(primary_metric, 0),
                    reverse=True
                )
            else:  # regression
                primary_metric = "r2_score"
                ranking = sorted(
                    successful_models.items(),
                    key=lambda x: x[1]["metrics"].get(primary_metric, -np.inf),
                    reverse=True
                )
            
            # Create comparison summary
            comparison = {
                "problem_type": problem_type,
                "primary_metric": primary_metric,
                "model_count": len(successful_models),
                "ranking": [
                    {
                        "rank": idx + 1,
                        "model": model_name,
                        "primary_score": result["metrics"].get(primary_metric, None),
                        "training_time": result.get("training_time", None)
                    }
                    for idx, (model_name, result) in enumerate(ranking)
                ],
                "best_model": ranking[0][0] if ranking else None,
                "detailed_comparison": {}
            }
            
            # Detailed metric comparison
            all_metrics = set()
            for result in successful_models.values():
                all_metrics.update(result["metrics"].keys())
            
            for metric in all_metrics:
                comparison["detailed_comparison"][metric] = {}
                for model_name, result in successful_models.items():
                    comparison["detailed_comparison"][metric][model_name] = result["metrics"].get(metric, None)
            
            # Performance insights
            insights = self._generate_performance_insights(successful_models, problem_type)
            comparison["insights"] = insights
            
            return comparison
            
        except Exception as e:
            return {"error": f"Error comparing models: {str(e)}"}
    
    def _generate_performance_insights(self, model_results: Dict, problem_type: str) -> List[str]:
        """
        Generate insights about model performance
        """
        insights = []
        
        try:
            # Training time analysis
            training_times = {name: result.get("training_time", 0) for name, result in model_results.items()}
            fastest_model = min(training_times.items(), key=lambda x: x[1])
            slowest_model = max(training_times.items(), key=lambda x: x[1])
            
            if slowest_model[1] > 0:
                time_diff = slowest_model[1] / fastest_model[1] if fastest_model[1] > 0 else 1
                if time_diff > 5:
                    insights.append(f"{fastest_model[0]} is significantly faster ({time_diff:.1f}x) than {slowest_model[0]}")
            
            # Performance analysis
            if problem_type == "classification":
                accuracies = {name: result["metrics"].get("accuracy", 0) for name, result in model_results.items()}
                best_accuracy = max(accuracies.items(), key=lambda x: x[1])
                worst_accuracy = min(accuracies.items(), key=lambda x: x[1])
                
                if best_accuracy[1] - worst_accuracy[1] > 0.1:
                    insights.append(f"Significant accuracy difference: {best_accuracy[0]} ({best_accuracy[1]:.3f}) vs {worst_accuracy[0]} ({worst_accuracy[1]:.3f})")
                
                # Check for overfitting
                for name, result in model_results.items():
                    metrics = result["metrics"]
                    train_acc = metrics.get("train_accuracy", 0)
                    test_acc = metrics.get("test_accuracy", 0)
                    if train_acc - test_acc > 0.1:
                        insights.append(f"{name} shows signs of overfitting (train: {train_acc:.3f}, test: {test_acc:.3f})")
            
            else:  # regression
                r2_scores = {name: result["metrics"].get("r2_score", 0) for name, result in model_results.items()}
                best_r2 = max(r2_scores.items(), key=lambda x: x[1])
                
                if best_r2[1] > 0.9:
                    insights.append(f"{best_r2[0]} shows excellent fit (R² = {best_r2[1]:.3f})")
                elif best_r2[1] < 0.5:
                    insights.append("All models show poor fit (R² < 0.5). Consider feature engineering or different algorithms.")
            
            # Model-specific insights
            ensemble_models = ["random_forest", "xgboost", "lightgbm"]
            linear_models = ["logistic_regression", "linear_regression"]
            
            ensemble_present = any(model in model_results for model in ensemble_models)
            linear_present = any(model in model_results for model in linear_models)
            
            if ensemble_present and linear_present:
                insights.append("Dataset benefits from both ensemble methods and linear models - consider feature importance analysis")
            
        except Exception as e:
            insights.append(f"Could not generate insights: {str(e)}")
        
        return insights
    
    def generate_model_report(self, model_name: str, model_result: Dict, comparison_data: Dict = None) -> Dict[str, Any]:
        """
        Generate a comprehensive report for a single model
        """
        try:
            if model_result.get("status") != "success":
                return {"error": f"Model {model_name} did not train successfully"}
            
            metrics = model_result.get("metrics", {})
            
            report = {
                "model_name": model_name,
                "training_time": model_result.get("training_time", 0),
                "metrics": metrics,
                "feature_importance": model_result.get("feature_importance", {}),
                "strengths": [],
                "weaknesses": [],
                "recommendations": []
            }
            
            # Determine problem type
            problem_type = "classification" if "accuracy" in metrics else "regression"
            
            # Analyze performance
            if problem_type == "classification":
                accuracy = metrics.get("accuracy", 0)
                f1_score = metrics.get("f1_score", 0)
                
                if accuracy > 0.9:
                    report["strengths"].append("Excellent accuracy")
                elif accuracy > 0.8:
                    report["strengths"].append("Good accuracy")
                else:
                    report["weaknesses"].append("Low accuracy")
                
                if f1_score > 0.85:
                    report["strengths"].append("Well-balanced precision and recall")
                elif f1_score < 0.7:
                    report["weaknesses"].append("Poor balance between precision and recall")
            
            else:  # regression
                r2_score = metrics.get("r2_score", 0)
                mape = metrics.get("mape", float('inf'))
                
                if r2_score > 0.9:
                    report["strengths"].append("Excellent explanatory power")
                elif r2_score > 0.7:
                    report["strengths"].append("Good explanatory power")
                else:
                    report["weaknesses"].append("Low explanatory power")
                
                if mape < 5:
                    report["strengths"].append("Very low prediction error")
                elif mape < 15:
                    report["strengths"].append("Acceptable prediction error")
                else:
                    report["weaknesses"].append("High prediction error")
            
            # Training time analysis
            training_time = model_result.get("training_time", 0)
            if training_time < 1:
                report["strengths"].append("Very fast training")
            elif training_time > 30:
                report["weaknesses"].append("Slow training time")
            
            # Feature importance analysis
            feature_importance = model_result.get("feature_importance", {})
            if feature_importance:
                top_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
                report["top_features"] = [{"feature": feat, "importance": float(imp)} for feat, imp in top_features]
            
            # Generate recommendations
            report["recommendations"] = self._generate_model_recommendations(model_name, metrics, problem_type)
            
            return report
            
        except Exception as e:
            return {"error": f"Error generating model report: {str(e)}"}
    
    def _generate_model_recommendations(self, model_name: str, metrics: Dict, problem_type: str) -> List[str]:
        """
        Generate model-specific recommendations
        """
        recommendations = []
        
        if problem_type == "classification":
            accuracy = metrics.get("accuracy", 0)
            precision = metrics.get("precision", 0)
            recall = metrics.get("recall", 0)
            
            if accuracy < 0.8:
                recommendations.append("Consider hyperparameter tuning to improve accuracy")
            
            if precision > recall + 0.1:
                recommendations.append("Model has high precision but low recall - consider adjusting decision threshold")
            elif recall > precision + 0.1:
                recommendations.append("Model has high recall but low precision - consider feature selection")
        
        else:  # regression
            r2_score = metrics.get("r2_score", 0)
            mape = metrics.get("mape", float('inf'))
            
            if r2_score < 0.7:
                recommendations.append("Consider adding polynomial features or interaction terms")
            
            if mape > 15:
                recommendations.append("High prediction error - consider outlier removal or feature scaling")
        
        # Model-specific recommendations
        if model_name == "linear_regression" or model_name == "logistic_regression":
            recommendations.append("Consider feature scaling for better performance")
        elif model_name == "random_forest":
            recommendations.append("Try tuning n_estimators and max_depth parameters")
        elif model_name in ["xgboost", "lightgbm"]:
            recommendations.append("Consider early stopping and learning rate tuning")
        
        return recommendations
