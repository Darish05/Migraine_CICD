"""
Feature Engineering Pipeline
Advanced feature creation and selection for migraine prediction
Part of automated MLOps pipeline
"""

import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
import pickle
from pathlib import Path
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Advanced feature engineering for migraine prediction"""
    
    def __init__(self):
        self.feature_selector = None
        self.pca = None
        self.feature_importance = None
        self.selected_features = None
        
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between important variables"""
        logger.info("🔬 Creating interaction features...")
        
        # Stress x Sleep interaction
        if 'stress_level' in df.columns and 'sleep_quality' in df.columns:
            df['stress_sleep_interaction'] = df['stress_level'] * (10 - df['sleep_quality'])
        
        # Weather x Dehydration
        if 'weather_changes' in df.columns and 'dehydration' in df.columns:
            df['weather_dehydration'] = df['weather_changes'] * df['dehydration']
        
        # Screen time x Sleep quality
        if 'screen_time' in df.columns and 'sleep_quality' in df.columns:
            df['screen_sleep_impact'] = df['screen_time'] * (10 - df['sleep_quality'])
        
        # Caffeine x Alcohol
        if 'caffeine_intake' in df.columns and 'alcohol_intake' in df.columns:
            df['substance_interaction'] = df['caffeine_intake'] * df['alcohol_intake']
        
        # Multiple triggers active
        trigger_cols = [col for col in df.columns if col in [
            'bright_light', 'loud_noises', 'strong_smells', 'missed_meals'
        ]]
        if len(trigger_cols) >= 2:
            df['multi_trigger_exposure'] = (df[trigger_cols].sum(axis=1) >= 2).astype(int)
        
        logger.info(f"✅ Created interaction features")
        return df
    
    def create_polynomial_features(self, df: pd.DataFrame, columns: list = None, degree: int = 2) -> pd.DataFrame:
        """Create polynomial features for non-linear relationships"""
        logger.info(f"🔢 Creating polynomial features (degree={degree})...")
        
        if columns is None:
            columns = ['stress_level', 'sleep_hours', 'screen_time']
        
        # Only use columns that exist
        columns = [col for col in columns if col in df.columns]
        
        for col in columns:
            for d in range(2, degree + 1):
                df[f'{col}_pow{d}'] = df[col] ** d
        
        logger.info(f"✅ Created polynomial features for {len(columns)} columns")
        return df
    
    def create_binning_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create binned versions of continuous features"""
        logger.info("📊 Creating binned features...")
        
        # Age bins
        if 'age' in df.columns:
            df['age_bin'] = pd.cut(df['age'], bins=[0, 25, 35, 45, 55, 100], labels=[1, 2, 3, 4, 5])
            df['age_bin'] = df['age_bin'].astype(int)
        
        # Stress level bins
        if 'stress_level' in df.columns:
            df['stress_category'] = pd.cut(df['stress_level'], bins=[0, 3, 6, 10], labels=[0, 1, 2])
            df['stress_category'] = df['stress_category'].astype(int)
        
        # Sleep hours bins
        if 'sleep_hours' in df.columns:
            df['sleep_category'] = pd.cut(df['sleep_hours'], bins=[0, 5, 7, 9, 24], labels=[0, 1, 2, 3])
            df['sleep_category'] = df['sleep_category'].astype(int)
        
        # Hydration level
        if 'hydration' in df.columns:
            df['hydration_adequate'] = (df['hydration'] >= 6).astype(int)
        
        logger.info("✅ Created binned features")
        return df
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features based on patterns (if timestamp available)"""
        logger.info("🕐 Creating temporal pattern features...")
        
        # For now, create synthetic temporal patterns based on existing data
        # In production, you'd have actual timestamps
        
        # Rolling averages simulation (assuming rows are time-ordered)
        window = 7  # 7-day window
        
        if 'stress_level' in df.columns:
            df['stress_7day_avg'] = df['stress_level'].rolling(window=window, min_periods=1).mean()
        
        if 'sleep_quality' in df.columns:
            df['sleep_7day_avg'] = df['sleep_quality'].rolling(window=window, min_periods=1).mean()
        
        logger.info("✅ Created temporal features")
        return df
    
    def create_health_indices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create composite health indices"""
        logger.info("🏥 Creating health indices...")
        
        # Sleep health index
        if 'sleep_hours' in df.columns and 'sleep_quality' in df.columns:
            df['sleep_health_index'] = (
                (df['sleep_hours'] / 8) * 0.5 +  # Normalized sleep hours
                (df['sleep_quality'] / 10) * 0.5   # Normalized sleep quality
            )
        
        # Lifestyle health index
        wellness_factors = []
        if 'exercise' in df.columns:
            wellness_factors.append(df['exercise'] / 10)
        if 'hydration' in df.columns:
            wellness_factors.append(df['hydration'] / 10)
        if 'stress_level' in df.columns:
            wellness_factors.append(1 - (df['stress_level'] / 10))  # Inverted
        
        if wellness_factors:
            df['lifestyle_health_index'] = sum(wellness_factors) / len(wellness_factors)
        
        # Trigger burden index
        trigger_columns = [col for col in df.columns if col in [
            'weather_changes', 'dehydration', 'bright_light', 'loud_noises',
            'strong_smells', 'missed_meals', 'specific_foods', 'neck_pain'
        ]]
        if trigger_columns:
            df['trigger_burden'] = df[trigger_columns].sum(axis=1) / len(trigger_columns)
        
        logger.info("✅ Created health indices")
        return df
    
    def select_features_statistical(self, X: pd.DataFrame, y: pd.Series, k: int = 20) -> tuple:
        """Select top k features using statistical tests"""
        logger.info(f"🎯 Selecting top {k} features using statistical tests...")
        
        selector = SelectKBest(score_func=f_classif, k=min(k, X.shape[1]))
        X_selected = selector.fit_transform(X, y)
        
        # Get selected feature names
        selected_mask = selector.get_support()
        selected_features = X.columns[selected_mask].tolist()
        
        # Get scores
        scores = pd.DataFrame({
            'feature': X.columns,
            'score': selector.scores_
        }).sort_values('score', ascending=False)
        
        logger.info(f"✅ Selected {len(selected_features)} features")
        logger.info(f"   Top 5 features: {selected_features[:5]}")
        
        return X_selected, selected_features, scores
    
    def select_features_importance(self, X: pd.DataFrame, y: pd.Series, k: int = 20) -> tuple:
        """Select features using Random Forest importance"""
        logger.info(f"🌲 Selecting top {k} features using Random Forest...")
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        
        # Get feature importance
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Select top k features
        selected_features = importance_df.head(k)['feature'].tolist()
        X_selected = X[selected_features]
        
        self.feature_importance = importance_df
        
        logger.info(f"✅ Selected {len(selected_features)} features")
        logger.info(f"   Top 5 features: {selected_features[:5]}")
        
        return X_selected, selected_features, importance_df
    
    def create_pca_features(self, X: pd.DataFrame, n_components: int = 10) -> pd.DataFrame:
        """Create PCA features for dimensionality reduction"""
        logger.info(f"🔄 Creating {n_components} PCA components...")
        
        if self.pca is None:
            self.pca = PCA(n_components=n_components, random_state=42)
            pca_features = self.pca.fit_transform(X)
        else:
            pca_features = self.pca.transform(X)
        
        # Create DataFrame with PCA features
        pca_cols = [f'pca_{i+1}' for i in range(n_components)]
        pca_df = pd.DataFrame(pca_features, columns=pca_cols, index=X.index)
        
        # Log explained variance
        explained_var = self.pca.explained_variance_ratio_.sum()
        logger.info(f"✅ Created {n_components} PCA components")
        logger.info(f"   Explained variance: {explained_var:.2%}")
        
        return pca_df
    
    def feature_engineering_pipeline(
        self,
        input_file: str = "data/processed/classification_data.csv",
        output_dir: str = "data/features",
        use_feature_selection: bool = True,
        n_features: int = 20
    ):
        """Complete feature engineering pipeline"""
        logger.info("="*60)
        logger.info("🚀 Starting Feature Engineering Pipeline")
        logger.info("="*60)
        
        # Load processed data
        logger.info(f"📂 Loading data from {input_file}")
        df = pd.read_csv(input_file)
        
        # Separate features and target
        target_col = 'migraine_occurrence'
        y = df[target_col]
        X = df.drop(columns=[target_col])
        
        logger.info(f"📊 Initial features: {X.shape[1]}")
        
        # Create engineered features
        X = self.create_interaction_features(X)
        X = self.create_polynomial_features(X)
        X = self.create_binning_features(X)
        X = self.create_temporal_features(X)
        X = self.create_health_indices(X)
        
        logger.info(f"📊 After engineering: {X.shape[1]} features")
        
        # Feature selection
        if use_feature_selection:
            X_selected, selected_features, importance_scores = self.select_features_importance(
                X, y, k=n_features
            )
            self.selected_features = selected_features
        else:
            X_selected = X
            selected_features = X.columns.tolist()
        
        # Save engineered features
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Combine with target
        engineered_data = pd.concat([X_selected, y], axis=1)
        output_file = output_path / "engineered_features.csv"
        engineered_data.to_csv(output_file, index=False)
        logger.info(f"💾 Saved engineered features to {output_file}")
        
        # Save feature importance
        if self.feature_importance is not None:
            importance_file = output_path / "feature_importance.csv"
            self.feature_importance.to_csv(importance_file, index=False)
            logger.info(f"💾 Saved feature importance to {importance_file}")
        
        # Save selected feature names
        metadata = {
            "selected_features": selected_features,
            "n_original_features": len(df.columns) - 1,
            "n_engineered_features": X.shape[1],
            "n_final_features": len(selected_features),
            "timestamp": datetime.now().isoformat()
        }
        
        metadata_file = output_path / "feature_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"💾 Saved metadata to {metadata_file}")
        
        # Save artifacts
        self.save_artifacts(output_dir="models/feature_engineering")
        
        logger.info("="*60)
        logger.info("✅ Feature Engineering Pipeline Completed!")
        logger.info(f"   Final features: {len(selected_features)}")
        logger.info("="*60)
        
        return X_selected, y, selected_features
    
    def save_artifacts(self, output_dir: str = "models/feature_engineering"):
        """Save feature engineering artifacts"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if self.pca is not None:
            with open(output_path / "pca.pkl", "wb") as f:
                pickle.dump(self.pca, f)
            logger.info(f"💾 Saved PCA to {output_path / 'pca.pkl'}")
        
        if self.selected_features is not None:
            with open(output_path / "selected_features.json", "w") as f:
                json.dump({"features": self.selected_features}, f, indent=2)
            logger.info(f"💾 Saved selected features to {output_path / 'selected_features.json'}")


if __name__ == "__main__":
    engineer = FeatureEngineer()
    X, y, features = engineer.feature_engineering_pipeline(
        input_file="data/processed/classification_data.csv",
        output_dir="data/features",
        use_feature_selection=True,
        n_features=20
    )
    
    print(f"\n📊 Final Feature Set: {len(features)} features")
    print(f"   Shape: X={X.shape}, y={y.shape}")
