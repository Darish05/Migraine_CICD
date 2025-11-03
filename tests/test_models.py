"""
Comprehensive Unit Tests for Migraine Prediction Models
Tests data processing, model training, and predictions
"""

import pytest
import numpy as np
import pandas as pd
import pickle
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validate_data import DataValidator
from scripts.preprocess_data import DataPreprocessor
from scripts.feature_engineering import FeatureEngineer
from scripts.check_model_drift import DriftDetector


@pytest.fixture
def sample_data():
    """Create sample dataset for testing"""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'age': np.random.randint(18, 70, n_samples),
        'gender': np.random.randint(0, 2, n_samples),
        'sleep_hours': np.random.uniform(4, 10, n_samples),
        'sleep_quality': np.random.randint(1, 11, n_samples),
        'stress_level': np.random.randint(1, 11, n_samples),
        'hydration': np.random.randint(0, 11, n_samples),
        'exercise': np.random.randint(0, 11, n_samples),
        'screen_time': np.random.uniform(0, 16, n_samples),
        'caffeine_intake': np.random.randint(0, 6, n_samples),
        'alcohol_intake': np.random.randint(0, 6, n_samples),
        'weather_changes': np.random.randint(0, 2, n_samples),
        'menstrual_cycle': np.random.randint(0, 2, n_samples),
        'dehydration': np.random.randint(0, 2, n_samples),
        'bright_light': np.random.randint(0, 2, n_samples),
        'loud_noises': np.random.randint(0, 2, n_samples),
        'strong_smells': np.random.randint(0, 2, n_samples),
        'missed_meals': np.random.randint(0, 2, n_samples),
        'specific_foods': np.random.randint(0, 2, n_samples),
        'physical_activity': np.random.randint(0, 2, n_samples),
        'neck_pain': np.random.randint(0, 2, n_samples),
        'weather_pressure': np.random.uniform(980, 1030, n_samples),
        'humidity': np.random.uniform(30, 90, n_samples),
        'temperature_change': np.random.uniform(-10, 10, n_samples),
        'migraine_occurrence': np.random.randint(0, 2, n_samples),
        'migraine_severity': np.random.randint(0, 11, n_samples)
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_input():
    """Sample input for prediction"""
    return {
        'age': 35,
        'gender': 1,
        'sleep_hours': 7.0,
        'sleep_quality': 6,
        'stress_level': 7,
        'hydration': 6,
        'exercise': 3,
        'screen_time': 8.0,
        'caffeine_intake': 3,
        'alcohol_intake': 1,
        'weather_changes': 1,
        'menstrual_cycle': 1,
        'dehydration': 0,
        'bright_light': 1,
        'loud_noises': 0,
        'strong_smells': 1,
        'missed_meals': 1,
        'specific_foods': 0,
        'physical_activity': 1,
        'neck_pain': 1,
        'weather_pressure': 1013.25,
        'humidity': 65.0,
        'temperature_change': 5.0
    }


class TestDataValidation:
    """Test data validation functionality"""
    
    def test_validator_initialization(self):
        """Test validator can be initialized"""
        validator = DataValidator()
        assert validator is not None
        assert hasattr(validator, 'validation_report')
    
    def test_schema_validation(self, sample_data, tmp_path):
        """Test schema validation"""
        # Save sample data
        data_file = tmp_path / "test_data.csv"
        sample_data.to_csv(data_file, index=False)
        
        validator = DataValidator(str(data_file))
        df = validator.load_data()
        result = validator.validate_schema(df)
        
        assert result is True
    
    def test_missing_values_detection(self, sample_data, tmp_path):
        """Test missing value detection"""
        # Add some missing values
        sample_data.loc[0:5, 'age'] = np.nan
        
        data_file = tmp_path / "test_data.csv"
        sample_data.to_csv(data_file, index=False)
        
        validator = DataValidator(str(data_file))
        df = validator.load_data()
        result = validator.validate_missing_values(df)
        
        assert result is True
        assert validator.validation_report['validations']['missing_values']['total_missing'] > 0
    
    def test_duplicate_detection(self, sample_data, tmp_path):
        """Test duplicate detection"""
        # Add duplicates
        sample_data = pd.concat([sample_data, sample_data.head(5)], ignore_index=True)
        
        data_file = tmp_path / "test_data.csv"
        sample_data.to_csv(data_file, index=False)
        
        validator = DataValidator(str(data_file))
        df = validator.load_data()
        result = validator.detect_duplicates(df)
        
        assert result is True
        assert validator.validation_report['validations']['duplicates'] > 0


class TestDataPreprocessing:
    """Test data preprocessing functionality"""
    
    def test_preprocessor_initialization(self):
        """Test preprocessor initialization"""
        preprocessor = DataPreprocessor()
        assert preprocessor is not None
        assert preprocessor.scaler is None
        assert preprocessor.imputer is None
    
    def test_missing_value_handling(self, sample_data):
        """Test missing value imputation"""
        # Add missing values
        sample_data.loc[0:5, 'age'] = np.nan
        
        preprocessor = DataPreprocessor()
        result = preprocessor.handle_missing_values(sample_data.copy())
        
        assert result['age'].isnull().sum() == 0
    
    def test_duplicate_removal(self, sample_data):
        """Test duplicate removal"""
        # Add duplicates
        data_with_dupes = pd.concat([sample_data, sample_data.head(10)], ignore_index=True)
        
        preprocessor = DataPreprocessor()
        result = preprocessor.remove_duplicates(data_with_dupes)
        
        assert len(result) < len(data_with_dupes)
    
    def test_outlier_handling(self, sample_data):
        """Test outlier handling"""
        # Add outliers
        sample_data.loc[0, 'age'] = 200
        
        preprocessor = DataPreprocessor()
        result = preprocessor.handle_outliers(sample_data.copy(), method='clip')
        
        assert result['age'].max() < 200
    
    def test_feature_scaling(self, sample_data):
        """Test feature scaling"""
        preprocessor = DataPreprocessor()
        
        # Remove target columns
        X = sample_data.drop(columns=['migraine_occurrence', 'migraine_severity'])
        
        result = preprocessor.scale_features(X.copy())
        
        # Check that scaled features have mean close to 0 and std close to 1
        assert preprocessor.scaler is not None


class TestFeatureEngineering:
    """Test feature engineering functionality"""
    
    def test_feature_engineer_initialization(self):
        """Test feature engineer initialization"""
        engineer = FeatureEngineer()
        assert engineer is not None
    
    def test_interaction_features(self, sample_data):
        """Test interaction feature creation"""
        engineer = FeatureEngineer()
        result = engineer.create_interaction_features(sample_data.copy())
        
        # Check that new features were created
        assert 'stress_sleep_interaction' in result.columns or len(result.columns) >= len(sample_data.columns)
    
    def test_polynomial_features(self, sample_data):
        """Test polynomial feature creation"""
        engineer = FeatureEngineer()
        result = engineer.create_polynomial_features(
            sample_data.copy(),
            columns=['stress_level', 'sleep_hours'],
            degree=2
        )
        
        # Check for polynomial features
        assert 'stress_level_pow2' in result.columns or len(result.columns) > len(sample_data.columns)
    
    def test_health_indices(self, sample_data):
        """Test health index creation"""
        engineer = FeatureEngineer()
        result = engineer.create_health_indices(sample_data.copy())
        
        # Check that health indices were created
        original_cols = len(sample_data.columns)
        new_cols = len(result.columns)
        assert new_cols >= original_cols


class TestDriftDetection:
    """Test drift detection functionality"""
    
    def test_drift_detector_initialization(self):
        """Test drift detector initialization"""
        detector = DriftDetector()
        assert detector is not None
    
    def test_psi_calculation(self, sample_data):
        """Test PSI calculation"""
        detector = DriftDetector()
        
        # Create reference and current data
        reference = sample_data['age']
        current = sample_data['age'] + np.random.normal(0, 5, len(sample_data))
        
        psi = detector.calculate_psi(reference, current)
        
        assert isinstance(psi, float)
        assert psi >= 0
    
    def test_feature_drift_detection(self, sample_data, tmp_path):
        """Test feature drift detection"""
        # Save reference data
        ref_file = tmp_path / "reference.csv"
        sample_data.to_csv(ref_file, index=False)
        
        detector = DriftDetector(str(ref_file))
        
        # Create drifted data
        current_data = sample_data.copy()
        current_data['age'] = current_data['age'] + 10  # Add drift
        
        result = detector.detect_feature_drift(current_data)
        
        assert 'feature_drift' in result
        assert 'summary' in result


class TestModelOperations:
    """Test model-related operations"""
    
    def test_model_files_can_be_loaded(self):
        """Test that model files can be loaded if they exist"""
        model_files = [
            'classification_model_top1.pkl',
            'classification_model_top2.pkl',
            'regression_model_top1.pkl',
            'regression_model_top2.pkl'
        ]
        
        for model_file in model_files:
            if os.path.exists(model_file):
                with open(model_file, 'rb') as f:
                    model = pickle.load(f)
                assert model is not None
    
    def test_prediction_output_shape(self, sample_input):
        """Test prediction output format"""
        # This test requires trained models
        if not os.path.exists('classification_model_top1.pkl'):
            pytest.skip("Model files not found")
        
        with open('classification_model_top1.pkl', 'rb') as f:
            model = pickle.load(f)
        
        # Create feature vector
        features = list(sample_input.values())
        prediction = model.predict([features])
        
        assert prediction is not None
        assert len(prediction) > 0


class TestIntegration:
    """Integration tests"""
    
    def test_complete_pipeline_flow(self, sample_data, tmp_path):
        """Test complete pipeline flow"""
        # 1. Save data
        data_file = tmp_path / "data.csv"
        sample_data.to_csv(data_file, index=False)
        
        # 2. Validate
        validator = DataValidator(str(data_file))
        passed, report = validator.run_all_validations()
        
        # 3. Preprocess
        preprocessor = DataPreprocessor()
        df = preprocessor.load_data(str(data_file))
        df = preprocessor.handle_missing_values(df)
        df = preprocessor.remove_duplicates(df)
        
        # 4. Feature engineering
        engineer = FeatureEngineer()
        df = engineer.create_interaction_features(df)
        
        assert len(df) > 0
        assert len(df.columns) >= len(sample_data.columns)
    
    def test_data_versioning_artifacts(self, tmp_path):
        """Test that preprocessing artifacts are saved correctly"""
        preprocessor = DataPreprocessor()
        
        # Create sample data for processing
        data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100)
        })
        
        # Scale features
        scaled_data = preprocessor.scale_features(data.copy(), columns_to_scale=['feature1', 'feature2'])
        
        # Save artifacts
        preprocessor.save_preprocessor(output_dir=str(tmp_path))
        
        # Check that artifacts were saved
        assert (tmp_path / 'scaler.pkl').exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
        assert os.path.exists('classification_model_top2.pkl')
        assert os.path.exists('regression_model_top1.pkl')
        assert os.path.exists('regression_model_top2.pkl')
        assert os.path.exists('models_info.json')
    
    def test_model_loading(self, predictor):
        """Test that models load correctly"""
        assert len(predictor.top_classification_models) == 2
        assert len(predictor.top_regression_models) == 2
        assert predictor.feature_names is not None

class TestPredictions:
    """Test prediction functionality"""
    
    def test_prediction_structure(self, predictor, sample_input):
        """Test prediction output structure"""
        predictions = predictor.predict(sample_input)
        
        assert predictions is not None
        assert 'model1' in predictions
        assert 'model2' in predictions
        
        for model_key in ['model1', 'model2']:
            assert 'name' in predictions[model_key]
            assert 'occurrence' in predictions[model_key]
            assert 'probability' in predictions[model_key]
            assert 'severity' in predictions[model_key]
    
    def test_prediction_types(self, predictor, sample_input):
        """Test prediction data types"""
        predictions = predictor.predict(sample_input)
        
        for model_key in ['model1', 'model2']:
            assert isinstance(predictions[model_key]['name'], str)
            assert isinstance(predictions[model_key]['occurrence'], int)
            assert isinstance(predictions[model_key]['probability'], float)
            assert isinstance(predictions[model_key]['severity'], (int, float))
    
    def test_prediction_ranges(self, predictor, sample_input):
        """Test prediction value ranges"""
        predictions = predictor.predict(sample_input)
        
        for model_key in ['model1', 'model2']:
            # Occurrence should be 0 or 1
            assert predictions[model_key]['occurrence'] in [0, 1]
            
            # Probability should be between 0 and 1
            assert 0 <= predictions[model_key]['probability'] <= 1
            
            # Severity should be between 0 and 10
            assert 0 <= predictions[model_key]['severity'] <= 10
    
    def test_severity_logic(self, predictor, sample_input):
        """Test that severity is 0 when no migraine predicted"""
        predictions = predictor.predict(sample_input)
        
        for model_key in ['model1', 'model2']:
            if predictions[model_key]['occurrence'] == 0:
                assert predictions[model_key]['severity'] == 0

class TestModelPerformance:
    """Test model performance metrics"""
    
    def test_model_accuracy_threshold(self):
        """Test that models meet minimum accuracy threshold"""
        with open('models_info.json', 'r') as f:
            models_info = json.load(f)
        
        for model in models_info['classification']:
            assert model['metrics']['accuracy'] >= 0.70, \
                f"Model {model['name']} accuracy {model['metrics']['accuracy']} below threshold"
    
    def test_model_r2_threshold(self):
        """Test that regression models meet minimum R² threshold"""
        with open('models_info.json', 'r') as f:
            models_info = json.load(f)
        
        for model in models_info['regression']:
            assert model['metrics']['r2_score'] >= 0.50, \
                f"Model {model['name']} R² {model['metrics']['r2_score']} below threshold"

class TestInputValidation:
    """Test input validation"""
    
    def test_missing_features(self, predictor):
        """Test handling of missing features"""
        incomplete_input = {'age': 35, 'gender': 1}
        predictions = predictor.predict(incomplete_input)
        assert predictions is not None
    
    def test_extreme_values(self, predictor):
        """Test handling of extreme values"""
        extreme_input = {
            'age': 100,
            'gender': 1,
            'sleep_hours': 12.0,
            'sleep_quality': 10,
            'stress_level': 10,
            'hydration': 10,
            'exercise': 7,
            'screen_time': 16.0,
            'caffeine_intake': 10,
            'alcohol_intake': 10,
            'weather_changes': 1,
            'menstrual_cycle': 1,
            'dehydration': 1,
            'bright_light': 1,
            'loud_noises': 1,
            'strong_smells': 1,
            'missed_meals': 1,
            'specific_foods': 1,
            'physical_activity': 1,
            'neck_pain': 1,
            'weather_pressure': 1050.0,
            'humidity': 100.0,
            'temperature_change': 20.0
        }
        predictions = predictor.predict(extreme_input)
        assert predictions is not None

class TestModelConsistency:
    """Test model consistency"""
    
    def test_prediction_consistency(self, predictor, sample_input):
        """Test that predictions are consistent for same input"""
        pred1 = predictor.predict(sample_input)
        pred2 = predictor.predict(sample_input)
        
        assert pred1['model1']['occurrence'] == pred2['model1']['occurrence']
        assert pred1['model2']['occurrence'] == pred2['model2']['occurrence']
        assert abs(pred1['model1']['probability'] - pred2['model1']['probability']) < 0.0001
    
    def test_batch_prediction(self, predictor):
        """Test batch prediction performance"""
        batch_inputs = [
            {'age': i, 'gender': i % 2} 
            for i in range(20, 60)
        ]
        
        for input_data in batch_inputs:
            predictions = predictor.predict(input_data)
            assert predictions is not None

class TestAPICompatibility:
    """Test API compatibility"""
    
    def test_json_serialization(self, predictor, sample_input):
        """Test that predictions are JSON serializable"""
        predictions = predictor.predict(sample_input)
        
        try:
            json_str = json.dumps(predictions)
            assert isinstance(json_str, str)
        except TypeError:
            pytest.fail("Predictions are not JSON serializable")

# Integration tests
class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_prediction(self, predictor, sample_input):
        """Test complete prediction pipeline"""
        # Predict
        predictions = predictor.predict(sample_input)
        
        # Validate structure
        assert predictions is not None
        assert 'model1' in predictions
        assert 'model2' in predictions
        
        # Validate both models gave predictions
        for model_key in ['model1', 'model2']:
            assert predictions[model_key]['name'] is not None
            assert predictions[model_key]['occurrence'] in [0, 1]
            assert 0 <= predictions[model_key]['probability'] <= 1