"""
Data Preprocessing Pipeline
Handles data cleaning, transformation, and preparation
Part of automated MLOps pipeline
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.impute import SimpleImputer
import pickle
from pathlib import Path
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Automated data preprocessing for migraine prediction"""
    
    def __init__(self):
        self.scaler = None
        self.imputer = None
        self.feature_names = None
        
    def load_data(self, file_path: str = "data/raw/migraine_dataset.csv") -> pd.DataFrame:
        """Load raw data"""
        logger.info(f"📂 Loading data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with appropriate strategies"""
        logger.info("🔧 Handling missing values...")
        
        # Separate numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove target columns from imputation
        if 'migraine_occurrence' in numeric_cols:
            numeric_cols.remove('migraine_occurrence')
        if 'migraine_severity' in numeric_cols:
            numeric_cols.remove('migraine_severity')
        
        # Impute numeric columns with median
        if self.imputer is None:
            self.imputer = SimpleImputer(strategy='median')
            df[numeric_cols] = self.imputer.fit_transform(df[numeric_cols])
        else:
            df[numeric_cols] = self.imputer.transform(df[numeric_cols])
        
        missing_after = df.isnull().sum().sum()
        logger.info(f"✅ Missing values after imputation: {missing_after}")
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        removed = before - after
        
        if removed > 0:
            logger.info(f"🗑️ Removed {removed} duplicate rows")
        
        return df
    
    def handle_outliers(self, df: pd.DataFrame, method='clip') -> pd.DataFrame:
        """Handle outliers using IQR method"""
        logger.info(f"🔧 Handling outliers using {method} method...")
        
        numeric_cols = [
            'age', 'sleep_hours', 'stress_level', 'hydration',
            'exercise', 'screen_time', 'caffeine_intake', 'alcohol_intake',
            'weather_pressure', 'humidity', 'temperature_change'
        ]
        
        outliers_count = 0
        
        for col in numeric_cols:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                if method == 'clip':
                    # Clip outliers to bounds
                    before_outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                    df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                    outliers_count += before_outliers
                elif method == 'remove':
                    # Remove outliers
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        logger.info(f"✅ Handled {outliers_count} outliers")
        return df
    
    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features from existing ones"""
        logger.info("🔬 Creating derived features...")
        
        # Sleep quality score (combination of hours and quality)
        if 'sleep_hours' in df.columns and 'sleep_quality' in df.columns:
            df['sleep_score'] = df['sleep_hours'] * df['sleep_quality'] / 10
        
        # Lifestyle risk score
        if all(col in df.columns for col in ['stress_level', 'exercise', 'hydration']):
            df['lifestyle_risk'] = (df['stress_level'] * 0.4) - (df['exercise'] * 0.3) - (df['hydration'] * 0.3)
        
        # Total trigger count
        trigger_cols = [
            'weather_changes', 'bright_light', 'loud_noises', 'strong_smells',
            'missed_meals', 'specific_foods', 'neck_pain'
        ]
        existing_triggers = [col for col in trigger_cols if col in df.columns]
        if existing_triggers:
            df['total_triggers'] = df[existing_triggers].sum(axis=1)
        
        # Screen time category
        if 'screen_time' in df.columns:
            df['high_screen_time'] = (df['screen_time'] > 8).astype(int)
        
        # Age group
        if 'age' in df.columns:
            df['age_group'] = pd.cut(df['age'], bins=[0, 30, 45, 60, 100], labels=[0, 1, 2, 3])
            df['age_group'] = df['age_group'].astype(int)
        
        logger.info(f"✅ Created derived features, total columns: {len(df.columns)}")
        return df
    
    def scale_features(self, df: pd.DataFrame, columns_to_scale: list = None) -> pd.DataFrame:
        """Scale numeric features"""
        logger.info("📏 Scaling features...")
        
        if columns_to_scale is None:
            columns_to_scale = [
                'age', 'sleep_hours', 'sleep_quality', 'stress_level',
                'hydration', 'exercise', 'screen_time', 'caffeine_intake',
                'alcohol_intake', 'weather_pressure', 'humidity',
                'temperature_change', 'sleep_score', 'lifestyle_risk'
            ]
        
        # Only scale columns that exist
        columns_to_scale = [col for col in columns_to_scale if col in df.columns]
        
        if self.scaler is None:
            self.scaler = StandardScaler()
            df[columns_to_scale] = self.scaler.fit_transform(df[columns_to_scale])
        else:
            df[columns_to_scale] = self.scaler.transform(df[columns_to_scale])
        
        logger.info(f"✅ Scaled {len(columns_to_scale)} features")
        return df
    
    def split_features_targets(self, df: pd.DataFrame):
        """Split into features and targets"""
        logger.info("🎯 Splitting features and targets...")
        
        # Target columns
        target_class = 'migraine_occurrence'
        target_reg = 'migraine_severity'
        
        # Feature columns (everything except targets)
        feature_cols = [col for col in df.columns if col not in [target_class, target_reg]]
        self.feature_names = feature_cols
        
        X = df[feature_cols]
        y_class = df[target_class]
        
        # For regression, only use samples where migraine occurred
        migraine_mask = df[target_class] == 1
        X_reg = df[migraine_mask][feature_cols]
        y_reg = df[migraine_mask][target_reg]
        
        logger.info(f"✅ Features: {len(feature_cols)}, Classification samples: {len(X)}, Regression samples: {len(X_reg)}")
        
        return X, y_class, X_reg, y_reg
    
    def save_preprocessor(self, output_dir: str = "models/preprocessors"):
        """Save preprocessing artifacts"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save scaler
        if self.scaler is not None:
            with open(output_path / "scaler.pkl", "wb") as f:
                pickle.dump(self.scaler, f)
            logger.info(f"💾 Saved scaler to {output_path / 'scaler.pkl'}")
        
        # Save imputer
        if self.imputer is not None:
            with open(output_path / "imputer.pkl", "wb") as f:
                pickle.dump(self.imputer, f)
            logger.info(f"💾 Saved imputer to {output_path / 'imputer.pkl'}")
        
        # Save feature names
        if self.feature_names is not None:
            with open(output_path / "feature_names.json", "w") as f:
                json.dump({"features": self.feature_names}, f, indent=2)
            logger.info(f"💾 Saved feature names to {output_path / 'feature_names.json'}")
    
    def load_preprocessor(self, input_dir: str = "models/preprocessors"):
        """Load preprocessing artifacts"""
        input_path = Path(input_dir)
        
        # Load scaler
        scaler_path = input_path / "scaler.pkl"
        if scaler_path.exists():
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            logger.info(f"📂 Loaded scaler from {scaler_path}")
        
        # Load imputer
        imputer_path = input_path / "imputer.pkl"
        if imputer_path.exists():
            with open(imputer_path, "rb") as f:
                self.imputer = pickle.load(f)
            logger.info(f"📂 Loaded imputer from {imputer_path}")
        
        # Load feature names
        features_path = input_path / "feature_names.json"
        if features_path.exists():
            with open(features_path, "r") as f:
                self.feature_names = json.load(f)["features"]
            logger.info(f"📂 Loaded feature names from {features_path}")
    
    def preprocess_pipeline(self, input_file: str, output_dir: str = "data/processed", save_artifacts: bool = True):
        """Complete preprocessing pipeline"""
        logger.info("="*60)
        logger.info("🚀 Starting Data Preprocessing Pipeline")
        logger.info("="*60)
        
        # Load data
        df = self.load_data(input_file)
        
        # Preprocessing steps
        df = self.handle_missing_values(df)
        df = self.remove_duplicates(df)
        df = self.handle_outliers(df, method='clip')
        df = self.create_derived_features(df)
        
        # Split before scaling
        X, y_class, X_reg, y_reg = self.split_features_targets(df)
        
        # Initialize and fit scaler if not already done
        if self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = pd.DataFrame(
                self.scaler.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
        else:
            X_scaled = pd.DataFrame(
                self.scaler.transform(X),
                columns=X.columns,
                index=X.index
            )
        
        X_reg_scaled = pd.DataFrame(
            self.scaler.transform(X_reg),
            columns=X_reg.columns,
            index=X_reg.index
        )
        
        # Save processed data
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save classification data
        class_data = pd.concat([X_scaled, y_class], axis=1)
        class_output = output_path / "classification_data.csv"
        class_data.to_csv(class_output, index=False)
        logger.info(f"💾 Saved classification data to {class_output}")
        
        # Save regression data
        reg_data = pd.concat([X_reg_scaled, y_reg], axis=1)
        reg_output = output_path / "regression_data.csv"
        reg_data.to_csv(reg_output, index=False)
        logger.info(f"💾 Saved regression data to {reg_output}")
        
        # Save artifacts
        if save_artifacts:
            self.save_preprocessor()
        
        logger.info("="*60)
        logger.info("✅ Preprocessing Pipeline Completed Successfully!")
        logger.info("="*60)
        
        return X_scaled, y_class, X_reg_scaled, y_reg


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    X, y_class, X_reg, y_reg = preprocessor.preprocess_pipeline(
        input_file="data/raw/migraine_dataset.csv",
        output_dir="data/processed"
    )
    
    print(f"\n📊 Final Data Shape:")
    print(f"   Classification: X={X.shape}, y={y_class.shape}")
    print(f"   Regression: X={X_reg.shape}, y={y_reg.shape}")
