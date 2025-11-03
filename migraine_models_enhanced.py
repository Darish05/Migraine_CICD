# migraine_models_enhanced.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor,
                              GradientBoostingClassifier, GradientBoostingRegressor,
                              AdaBoostClassifier, AdaBoostRegressor)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_squared_error, r2_score, mean_absolute_error
import mlflow
import mlflow.sklearn
import pickle
import json
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

class EnhancedMigrainePredictor:
    def __init__(self, mlflow_tracking_uri="mlruns"):
        self.top_classification_models = []
        self.top_regression_models = []
        self.feature_names = None
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment("migraine_prediction")
        
    def load_and_prepare_data(self, file_path='data/raw/migraine_dataset.csv'):
        """Load and prepare the dataset"""
        df = pd.read_csv(file_path)
        
        feature_columns = [
            'age', 'gender', 'sleep_hours', 'sleep_quality', 'stress_level',
            'hydration', 'exercise', 'screen_time', 'caffeine_intake',
            'alcohol_intake', 'weather_changes', 'menstrual_cycle',
            'dehydration', 'bright_light', 'loud_noises', 'strong_smells',
            'missed_meals', 'specific_foods', 'physical_activity',
            'neck_pain', 'weather_pressure', 'humidity', 'temperature_change'
        ]
        
        X = df[feature_columns]
        y_class = df['migraine_occurrence']
        y_reg = df[df['migraine_occurrence'] == 1]['migraine_severity']
        X_reg = X[df['migraine_occurrence'] == 1]
        
        self.feature_names = feature_columns
        
        return X, y_class, X_reg, y_reg
    
    def get_classification_models(self):
        """Define 8 classification models with hyperparameters"""
        return {
            'RandomForest': {
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15],
                    'min_samples_split': [2, 5]
                }
            },
            'XGBoost': {
                'model': XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1, 0.3]
                }
            },
            'LightGBM': {
                'model': LGBMClassifier(random_state=42, verbose=-1),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1, 0.3]
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingClassifier(random_state=42),
                'params': {
                    'n_estimators': [50, 100],
                    'max_depth': [3, 5],
                    'learning_rate': [0.01, 0.1]
                }
            },
            'LogisticRegression': {
                'model': LogisticRegression(random_state=42, max_iter=1000),
                'params': {
                    'C': [0.1, 1, 10],
                    'penalty': ['l2']
                }
            },
            'SVM': {
                'model': SVC(random_state=42, probability=True),
                'params': {
                    'C': [0.1, 1, 10],
                    'kernel': ['rbf', 'linear']
                }
            },
            'KNeighbors': {
                'model': KNeighborsClassifier(),
                'params': {
                    'n_neighbors': [3, 5, 7, 9],
                    'weights': ['uniform', 'distance']
                }
            },
            'AdaBoost': {
                'model': AdaBoostClassifier(random_state=42),
                'params': {
                    'n_estimators': [50, 100],
                    'learning_rate': [0.1, 0.5, 1.0]
                }
            }
        }
    
    def get_regression_models(self):
        """Define 8 regression models with hyperparameters"""
        return {
            'RandomForest': {
                'model': RandomForestRegressor(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15],
                    'min_samples_split': [2, 5]
                }
            },
            'XGBoost': {
                'model': XGBRegressor(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1, 0.3]
                }
            },
            'LightGBM': {
                'model': LGBMRegressor(random_state=42, verbose=-1),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1, 0.3]
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingRegressor(random_state=42),
                'params': {
                    'n_estimators': [50, 100],
                    'max_depth': [3, 5],
                    'learning_rate': [0.01, 0.1]
                }
            },
            'Ridge': {
                'model': Ridge(random_state=42),
                'params': {
                    'alpha': [0.1, 1, 10, 100]
                }
            },
            'SVR': {
                'model': SVR(),
                'params': {
                    'C': [0.1, 1, 10],
                    'kernel': ['rbf', 'linear']
                }
            },
            'KNeighbors': {
                'model': KNeighborsRegressor(),
                'params': {
                    'n_neighbors': [3, 5, 7, 9],
                    'weights': ['uniform', 'distance']
                }
            },
            'AdaBoost': {
                'model': AdaBoostRegressor(random_state=42),
                'params': {
                    'n_estimators': [50, 100],
                    'learning_rate': [0.1, 0.5, 1.0]
                }
            }
        }
    
    def train_models(self):
        """Train all models with hyperparameter tuning and MLflow tracking"""
        print("🔄 Loading and preparing data...")
        X, y_class, X_reg, y_reg = self.load_and_prepare_data()
        
        # Split data
        X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
            X, y_class, test_size=0.2, random_state=42, stratify=y_class
        )
        
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
            X_reg, y_reg, test_size=0.2, random_state=42
        )
        
        # Train Classification Models
        print("\n" + "="*80)
        print("🔍 TRAINING CLASSIFICATION MODELS (8 ALGORITHMS)")
        print("="*80)
        
        classification_results = []
        classification_models = self.get_classification_models()
        
        for name, config in classification_models.items():
            with mlflow.start_run(run_name=f"Classification_{name}"):
                print(f"\n🤖 Training {name}...")
                
                # Hyperparameter tuning
                grid_search = GridSearchCV(
                    config['model'], 
                    config['params'], 
                    cv=3, 
                    scoring='accuracy',
                    n_jobs=-1
                )
                grid_search.fit(X_train_class, y_train_class)
                
                best_model = grid_search.best_estimator_
                y_pred = best_model.predict(X_test_class)
                
                # Calculate metrics
                accuracy = accuracy_score(y_test_class, y_pred)
                f1 = f1_score(y_test_class, y_pred, average='weighted')
                precision = precision_score(y_test_class, y_pred, average='weighted')
                recall = recall_score(y_test_class, y_pred, average='weighted')
                
                # Log to MLflow
                mlflow.log_params(grid_search.best_params_)
                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("f1_score", f1)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                mlflow.sklearn.log_model(best_model, f"model_{name}")
                
                classification_results.append({
                    'name': name,
                    'model': best_model,
                    'accuracy': accuracy,
                    'f1_score': f1,
                    'precision': precision,
                    'recall': recall,
                    'best_params': grid_search.best_params_
                })
                
                print(f"   ✅ Accuracy: {accuracy:.4f} | F1: {f1:.4f}")
        
        # Sort and get top 2
        classification_results.sort(key=lambda x: x['accuracy'], reverse=True)
        self.top_classification_models = classification_results[:2]
        
        print("\n" + "="*80)
        print("🏆 TOP 2 CLASSIFICATION MODELS:")
        print("="*80)
        for i, result in enumerate(self.top_classification_models, 1):
            print(f"{i}. {result['name']}: Accuracy={result['accuracy']:.4f}, F1={result['f1_score']:.4f}")
        
        # Train Regression Models
        print("\n" + "="*80)
        print("🔍 TRAINING REGRESSION MODELS (8 ALGORITHMS)")
        print("="*80)
        
        regression_results = []
        regression_models = self.get_regression_models()
        
        for name, config in regression_models.items():
            with mlflow.start_run(run_name=f"Regression_{name}"):
                print(f"\n🤖 Training {name}...")
                
                # Hyperparameter tuning
                grid_search = GridSearchCV(
                    config['model'], 
                    config['params'], 
                    cv=3, 
                    scoring='r2',
                    n_jobs=-1
                )
                grid_search.fit(X_train_reg, y_train_reg)
                
                best_model = grid_search.best_estimator_
                y_pred = best_model.predict(X_test_reg)
                
                # Calculate metrics
                r2 = r2_score(y_test_reg, y_pred)
                mse = mean_squared_error(y_test_reg, y_pred)
                mae = mean_absolute_error(y_test_reg, y_pred)
                rmse = np.sqrt(mse)
                
                # Log to MLflow
                mlflow.log_params(grid_search.best_params_)
                mlflow.log_metric("r2_score", r2)
                mlflow.log_metric("mse", mse)
                mlflow.log_metric("mae", mae)
                mlflow.log_metric("rmse", rmse)
                mlflow.sklearn.log_model(best_model, f"model_{name}")
                
                regression_results.append({
                    'name': name,
                    'model': best_model,
                    'r2_score': r2,
                    'mse': mse,
                    'mae': mae,
                    'rmse': rmse,
                    'best_params': grid_search.best_params_
                })
                
                print(f"   ✅ R²: {r2:.4f} | RMSE: {rmse:.4f}")
        
        # Sort and get top 2
        regression_results.sort(key=lambda x: x['r2_score'], reverse=True)
        self.top_regression_models = regression_results[:2]
        
        print("\n" + "="*80)
        print("🏆 TOP 2 REGRESSION MODELS:")
        print("="*80)
        for i, result in enumerate(self.top_regression_models, 1):
            print(f"{i}. {result['name']}: R²={result['r2_score']:.4f}, RMSE={result['rmse']:.4f}")
        
        # Save models
        self.save_models()
        
        return classification_results, regression_results
    
    def save_models(self):
        """Save top 2 models for each task"""
        models_info = {
            'classification': [
                {
                    'name': model['name'],
                    'metrics': {
                        'accuracy': model['accuracy'],
                        'f1_score': model['f1_score'],
                        'precision': model['precision'],
                        'recall': model['recall']
                    },
                    'params': model['best_params']
                }
                for model in self.top_classification_models
            ],
            'regression': [
                {
                    'name': model['name'],
                    'metrics': {
                        'r2_score': model['r2_score'],
                        'mse': model['mse'],
                        'mae': model['mae'],
                        'rmse': model['rmse']
                    },
                    'params': model['best_params']
                }
                for model in self.top_regression_models
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        # Save models
        for i, model in enumerate(self.top_classification_models):
            with open(f'classification_model_top{i+1}.pkl', 'wb') as f:
                pickle.dump(model['model'], f)
        
        for i, model in enumerate(self.top_regression_models):
            with open(f'regression_model_top{i+1}.pkl', 'wb') as f:
                pickle.dump(model['model'], f)
        
        with open('feature_names.pkl', 'wb') as f:
            pickle.dump(self.feature_names, f)
        
        with open('models_info.json', 'w') as f:
            json.dump(models_info, f, indent=2)
        
        print("\n💾 All models saved successfully!")
    
    def load_models(self):
        """Load top 2 models"""
        try:
            self.top_classification_models = []
            self.top_regression_models = []
            
            with open('models_info.json', 'r') as f:
                models_info = json.load(f)
            
            for i in range(2):
                with open(f'classification_model_top{i+1}.pkl', 'rb') as f:
                    model = pickle.load(f)
                    self.top_classification_models.append({
                        'model': model,
                        'name': models_info['classification'][i]['name'],
                        **models_info['classification'][i]['metrics']
                    })
                
                with open(f'regression_model_top{i+1}.pkl', 'rb') as f:
                    model = pickle.load(f)
                    self.top_regression_models.append({
                        'model': model,
                        'name': models_info['regression'][i]['name'],
                        **models_info['regression'][i]['metrics']
                    })
            
            with open('feature_names.pkl', 'rb') as f:
                self.feature_names = pickle.load(f)
            
            print("✅ Top 2 models loaded successfully!")
            return True
        except FileNotFoundError:
            print("❌ Models not found. Please train models first.")
            return False
    
    def predict(self, input_data):
        """Make predictions using both top models"""
        if not self.top_classification_models:
            if not self.load_models():
                return None
        
        input_df = pd.DataFrame([input_data])
        
        for feature in self.feature_names:
            if feature not in input_df.columns:
                input_df[feature] = 0
        
        input_df = input_df[self.feature_names]
        
        predictions = {
            'model1': {},
            'model2': {}
        }
        
        # Model 1 predictions
        class_model1 = self.top_classification_models[0]['model']
        predictions['model1']['name'] = self.top_classification_models[0]['name']
        predictions['model1']['occurrence'] = int(class_model1.predict(input_df)[0])
        predictions['model1']['probability'] = float(class_model1.predict_proba(input_df)[0][1])
        
        if predictions['model1']['occurrence'] == 1:
            reg_model1 = self.top_regression_models[0]['model']
            severity = reg_model1.predict(input_df)[0]
            predictions['model1']['severity'] = float(max(1, min(10, round(severity, 1))))
        else:
            predictions['model1']['severity'] = 0
        
        # Model 2 predictions
        class_model2 = self.top_classification_models[1]['model']
        predictions['model2']['name'] = self.top_classification_models[1]['name']
        predictions['model2']['occurrence'] = int(class_model2.predict(input_df)[0])
        predictions['model2']['probability'] = float(class_model2.predict_proba(input_df)[0][1])
        
        if predictions['model2']['occurrence'] == 1:
            reg_model2 = self.top_regression_models[1]['model']
            severity = reg_model2.predict(input_df)[0]
            predictions['model2']['severity'] = float(max(1, min(10, round(severity, 1))))
        else:
            predictions['model2']['severity'] = 0
        
        return predictions

if __name__ == "__main__":
    predictor = EnhancedMigrainePredictor()
    predictor.train_models()