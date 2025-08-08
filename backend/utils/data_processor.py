import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class DataProcessor:
    """
    Process and analyze datasets for AutoML pipeline
    """
    
    def __init__(self):
        pass
    
    def analyze_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive analysis of the dataset
        """
        try:
            analysis = {
                "shape": {
                    "rows": int(len(df)),
                    "columns": int(len(df.columns))
                },
                "columns": {
                    "names": [str(col) for col in df.columns],
                    "types": {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
                },
                "missing_values": {
                    "total": int(df.isnull().sum().sum()),
                    "by_column": {str(k): int(v) for k, v in df.isnull().sum().to_dict().items()},
                    "percentage": {str(k): float(v) for k, v in ((df.isnull().sum() / len(df)) * 100).to_dict().items()}
                },
                "data_types": {
                    "numeric": [str(col) for col in df.select_dtypes(include=[np.number]).columns],
                    "categorical": [str(col) for col in df.select_dtypes(include=['object', 'category']).columns],
                    "datetime": [str(col) for col in df.select_dtypes(include=['datetime64']).columns]
                },
                "summary_statistics": {},
                "categorical_analysis": {},
                "data_quality": {}
            }
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                stats_dict = df[numeric_cols].describe().to_dict()
                # Convert numpy types to Python types
                analysis["summary_statistics"] = {
                    str(col): {str(stat): float(val) if pd.notna(val) else None 
                              for stat, val in col_stats.items()}
                    for col, col_stats in stats_dict.items()
                }
            
            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            for col in categorical_cols:
                col_str = str(col)
                analysis["categorical_analysis"][col_str] = {
                    "unique_values": int(df[col].nunique()),
                    "most_frequent": str(df[col].mode().iloc[0]) if not df[col].mode().empty else None,
                    "value_counts": {str(k): int(v) for k, v in df[col].value_counts().head(10).to_dict().items()}
                }
            
            # Data quality assessment
            analysis["data_quality"] = self._assess_data_quality(df)
            
            # Potential target columns
            analysis["potential_targets"] = self._identify_potential_targets(df)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error analyzing dataset: {str(e)}"}
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess overall data quality
        """
        quality_score = 100.0
        issues = []
        
        # Missing values penalty
        missing_ratio = df.isnull().sum().sum() / df.size
        if missing_ratio > 0.1:
            quality_score -= 20
            issues.append(f"High missing values: {missing_ratio:.1%}")
        elif missing_ratio > 0.05:
            quality_score -= 10
            issues.append(f"Moderate missing values: {missing_ratio:.1%}")
        
        # Duplicate rows penalty
        duplicate_ratio = df.duplicated().sum() / len(df)
        if duplicate_ratio > 0.1:
            quality_score -= 15
            issues.append(f"High duplicate rows: {duplicate_ratio:.1%}")
        elif duplicate_ratio > 0.05:
            quality_score -= 8
            issues.append(f"Moderate duplicate rows: {duplicate_ratio:.1%}")
        
        # Very low variance columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        low_variance_cols = []
        for col in numeric_cols:
            if df[col].var() < 1e-6:
                low_variance_cols.append(col)
        
        if low_variance_cols:
            quality_score -= len(low_variance_cols) * 5
            issues.append(f"Low variance columns: {low_variance_cols}")
        
        # High cardinality categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        high_cardinality_cols = []
        for col in categorical_cols:
            cardinality_ratio = df[col].nunique() / len(df)
            if cardinality_ratio > 0.8:
                high_cardinality_cols.append(col)
        
        if high_cardinality_cols:
            quality_score -= len(high_cardinality_cols) * 10
            issues.append(f"High cardinality columns: {high_cardinality_cols}")
        
        return {
            "overall_score": max(0, quality_score),
            "issues": issues,
            "recommendations": self._get_data_quality_recommendations(issues)
        }
    
    def _get_data_quality_recommendations(self, issues: List[str]) -> List[str]:
        """
        Provide recommendations based on data quality issues
        """
        recommendations = []
        
        for issue in issues:
            if "missing values" in issue.lower():
                recommendations.append("Consider imputation strategies for missing values")
            elif "duplicate" in issue.lower():
                recommendations.append("Remove duplicate rows to improve data quality")
            elif "low variance" in issue.lower():
                recommendations.append("Consider removing low variance columns")
            elif "high cardinality" in issue.lower():
                recommendations.append("Consider encoding or grouping high cardinality categorical variables")
        
        return recommendations
    
    def _identify_potential_targets(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify columns that could potentially be target variables
        """
        potential_targets = []
        
        for col in df.columns:
            target_info = {
                "column": col,
                "type": str(df[col].dtype),
                "unique_values": int(df[col].nunique()),
                "missing_values": int(df[col].isnull().sum()),
                "suitability_score": 0,
                "reasons": []
            }
            
            # Scoring logic for target suitability
            unique_ratio = df[col].nunique() / len(df)
            
            # Good for classification (categorical with reasonable categories)
            if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                if 2 <= df[col].nunique() <= 20:
                    target_info["suitability_score"] += 30
                    target_info["reasons"].append("Good categorical target (2-20 categories)")
                elif df[col].nunique() > 20:
                    target_info["suitability_score"] += 10
                    target_info["reasons"].append("High cardinality categorical")
            
            # Good for regression (numeric with sufficient variance)
            elif pd.api.types.is_numeric_dtype(df[col]):
                if unique_ratio > 0.05:  # More than 5% unique values
                    target_info["suitability_score"] += 25
                    target_info["reasons"].append("Numeric with good variance")
                else:
                    target_info["suitability_score"] += 15
                    target_info["reasons"].append("Numeric but low variance")
            
            # Penalty for missing values
            missing_ratio = df[col].isnull().sum() / len(df)
            if missing_ratio > 0.1:
                target_info["suitability_score"] -= 20
                target_info["reasons"].append("High missing values")
            
            # Bonus for balanced classes (for classification)
            if df[col].nunique() <= 10:
                value_counts = df[col].value_counts()
                balance_score = (value_counts.min() / value_counts.max()) if value_counts.max() > 0 else 0
                if balance_score > 0.3:
                    target_info["suitability_score"] += 15
                    target_info["reasons"].append("Well-balanced classes")
                elif balance_score > 0.1:
                    target_info["suitability_score"] += 5
                    target_info["reasons"].append("Moderately balanced classes")
                else:
                    target_info["suitability_score"] -= 10
                    target_info["reasons"].append("Imbalanced classes")
            
            potential_targets.append(target_info)
        
        # Sort by suitability score
        potential_targets.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return potential_targets[:5]  # Return top 5 candidates
    
    def preprocess_data(self, df: pd.DataFrame, target_column: str, preprocessing_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Preprocess data for machine learning
        """
        try:
            config = preprocessing_config or {}
            
            # Separate features and target
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            preprocessing_steps = []
            
            # Handle missing values
            if config.get("handle_missing", True):
                # Numeric columns - fill with mean/median
                numeric_cols = X.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if X[col].isnull().any():
                        fill_value = X[col].median() if config.get("numeric_strategy") == "median" else X[col].mean()
                        X[col].fillna(fill_value, inplace=True)
                        preprocessing_steps.append(f"Filled missing values in {col} with {config.get('numeric_strategy', 'mean')}")
                
                # Categorical columns - fill with mode
                categorical_cols = X.select_dtypes(include=['object', 'category']).columns
                for col in categorical_cols:
                    if X[col].isnull().any():
                        mode_value = X[col].mode().iloc[0] if not X[col].mode().empty else "Unknown"
                        X[col].fillna(mode_value, inplace=True)
                        preprocessing_steps.append(f"Filled missing values in {col} with mode")
            
            # Encode categorical variables
            if config.get("encode_categorical", True):
                categorical_cols = X.select_dtypes(include=['object', 'category']).columns
                for col in categorical_cols:
                    X[col] = pd.Categorical(X[col]).codes
                    preprocessing_steps.append(f"Label encoded {col}")
            
            # Handle outliers (simple IQR method)
            if config.get("handle_outliers", False):
                numeric_cols = X.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    Q1 = X[col].quantile(0.25)
                    Q3 = X[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers_count = ((X[col] < lower_bound) | (X[col] > upper_bound)).sum()
                    if outliers_count > 0:
                        X[col] = X[col].clip(lower=lower_bound, upper=upper_bound)
                        preprocessing_steps.append(f"Clipped {outliers_count} outliers in {col}")
            
            return {
                "X": X,
                "y": y,
                "preprocessing_steps": preprocessing_steps,
                "shape_after_preprocessing": X.shape
            }
            
        except Exception as e:
            return {"error": f"Error preprocessing data: {str(e)}"}
