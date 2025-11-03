"""
Model Evaluation Pipeline
Comprehensive model evaluation with overfitting detection
Part of automated MLOps pipeline
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
import logging
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.model_selection import learning_curve, validation_curve
import mlflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Comprehensive model evaluation and validation"""
    
    def __init__(self, models_dir: str = ".", reports_dir: str = "reports/evaluation"):
        self.models_dir = Path(models_dir)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.evaluation_results = {}
        
    def load_models(self):
        """Load trained models"""
        logger.info("📂 Loading trained models...")
        
        models = {}
        
        # Load classification models
        for i in [1, 2]:
            model_path = self.models_dir / f"classification_model_top{i}.pkl"
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    models[f'classification_top{i}'] = pickle.load(f)
                logger.info(f"✅ Loaded classification model {i}")
        
        # Load regression models
        for i in [1, 2]:
            model_path = self.models_dir / f"regression_model_top{i}.pkl"
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    models[f'regression_top{i}'] = pickle.load(f)
                logger.info(f"✅ Loaded regression model {i}")
        
        return models
    
    def evaluate_classification(self, model, X_train, X_test, y_train, y_test, model_name: str):
        """Comprehensive classification evaluation"""
        logger.info(f"📊 Evaluating classification model: {model_name}")
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Probabilities (if available)
        try:
            y_train_prob = model.predict_proba(X_train)[:, 1]
            y_test_prob = model.predict_proba(X_test)[:, 1]
            has_prob = True
        except:
            has_prob = False
            y_train_prob = None
            y_test_prob = None
        
        # Calculate metrics
        train_metrics = {
            'accuracy': accuracy_score(y_train, y_train_pred),
            'precision': precision_score(y_train, y_train_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_train, y_train_pred, average='weighted', zero_division=0),
            'f1': f1_score(y_train, y_train_pred, average='weighted', zero_division=0)
        }
        
        test_metrics = {
            'accuracy': accuracy_score(y_test, y_test_pred),
            'precision': precision_score(y_test, y_test_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_test_pred, average='weighted', zero_division=0),
            'f1': f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
        }
        
        # ROC-AUC if probabilities available
        if has_prob:
            train_metrics['roc_auc'] = roc_auc_score(y_train, y_train_prob)
            test_metrics['roc_auc'] = roc_auc_score(y_test, y_test_prob)
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_test_pred)
        
        # Classification Report
        class_report = classification_report(y_test, y_test_pred, output_dict=True)
        
        # Detect overfitting/underfitting
        overfit_status = self.detect_overfitting(train_metrics, test_metrics)
        
        results = {
            'model_name': model_name,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'confusion_matrix': cm.tolist(),
            'classification_report': class_report,
            'overfitting_status': overfit_status,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log metrics
        logger.info(f"   Train Accuracy: {train_metrics['accuracy']:.4f}")
        logger.info(f"   Test Accuracy: {test_metrics['accuracy']:.4f}")
        logger.info(f"   Test F1: {test_metrics['f1']:.4f}")
        logger.info(f"   Overfitting Status: {overfit_status['status']}")
        
        # Generate plots
        if has_prob:
            self.plot_roc_curve(y_test, y_test_prob, model_name)
        self.plot_confusion_matrix(cm, model_name)
        
        return results
    
    def evaluate_regression(self, model, X_train, X_test, y_train, y_test, model_name: str):
        """Comprehensive regression evaluation"""
        logger.info(f"📊 Evaluating regression model: {model_name}")
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Calculate metrics
        train_metrics = {
            'mse': mean_squared_error(y_train, y_train_pred),
            'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'mae': mean_absolute_error(y_train, y_train_pred),
            'r2': r2_score(y_train, y_train_pred)
        }
        
        test_metrics = {
            'mse': mean_squared_error(y_test, y_test_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'mae': mean_absolute_error(y_test, y_test_pred),
            'r2': r2_score(y_test, y_test_pred)
        }
        
        # Detect overfitting/underfitting
        overfit_status = self.detect_overfitting_regression(train_metrics, test_metrics)
        
        results = {
            'model_name': model_name,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'overfitting_status': overfit_status,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log metrics
        logger.info(f"   Train R²: {train_metrics['r2']:.4f}")
        logger.info(f"   Test R²: {test_metrics['r2']:.4f}")
        logger.info(f"   Test RMSE: {test_metrics['rmse']:.4f}")
        logger.info(f"   Overfitting Status: {overfit_status['status']}")
        
        # Generate plots
        self.plot_predictions(y_test, y_test_pred, model_name)
        self.plot_residuals(y_test, y_test_pred, model_name)
        
        return results
    
    def detect_overfitting(self, train_metrics: dict, test_metrics: dict, threshold: float = 0.10):
        """Detect overfitting in classification models"""
        
        # Calculate performance gap
        accuracy_gap = train_metrics['accuracy'] - test_metrics['accuracy']
        f1_gap = train_metrics['f1'] - test_metrics['f1']
        
        # Determine status
        if accuracy_gap > threshold or f1_gap > threshold:
            status = "OVERFITTING"
            severity = "HIGH" if accuracy_gap > 0.15 else "MEDIUM"
        elif test_metrics['accuracy'] < 0.60:
            status = "UNDERFITTING"
            severity = "HIGH" if test_metrics['accuracy'] < 0.50 else "MEDIUM"
        else:
            status = "GOOD_FIT"
            severity = "NONE"
        
        return {
            'status': status,
            'severity': severity,
            'accuracy_gap': accuracy_gap,
            'f1_gap': f1_gap,
            'recommendation': self.get_recommendation(status)
        }
    
    def detect_overfitting_regression(self, train_metrics: dict, test_metrics: dict, threshold: float = 0.10):
        """Detect overfitting in regression models"""
        
        # Calculate performance gap
        r2_gap = train_metrics['r2'] - test_metrics['r2']
        
        # Determine status
        if r2_gap > threshold:
            status = "OVERFITTING"
            severity = "HIGH" if r2_gap > 0.15 else "MEDIUM"
        elif test_metrics['r2'] < 0.50:
            status = "UNDERFITTING"
            severity = "HIGH" if test_metrics['r2'] < 0.30 else "MEDIUM"
        else:
            status = "GOOD_FIT"
            severity = "NONE"
        
        return {
            'status': status,
            'severity': severity,
            'r2_gap': r2_gap,
            'recommendation': self.get_recommendation(status)
        }
    
    def get_recommendation(self, status: str) -> str:
        """Get recommendations based on fitting status"""
        recommendations = {
            'OVERFITTING': "Consider: 1) Regularization, 2) More training data, 3) Reduce model complexity, 4) Cross-validation",
            'UNDERFITTING': "Consider: 1) More complex model, 2) More features, 3) Feature engineering, 4) Remove regularization",
            'GOOD_FIT': "Model is performing well! Continue monitoring."
        }
        return recommendations.get(status, "No specific recommendation")
    
    def plot_confusion_matrix(self, cm: np.ndarray, model_name: str):
        """Plot confusion matrix"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title(f'Confusion Matrix - {model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        output_file = self.reports_dir / f'confusion_matrix_{model_name}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"💾 Saved confusion matrix: {output_file}")
    
    def plot_roc_curve(self, y_true, y_prob, model_name: str):
        """Plot ROC curve"""
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        auc = roc_auc_score(y_true, y_prob)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {model_name}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        output_file = self.reports_dir / f'roc_curve_{model_name}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"💾 Saved ROC curve: {output_file}")
    
    def plot_predictions(self, y_true, y_pred, model_name: str):
        """Plot actual vs predicted values"""
        plt.figure(figsize=(8, 6))
        plt.scatter(y_true, y_pred, alpha=0.5)
        plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title(f'Actual vs Predicted - {model_name}')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        output_file = self.reports_dir / f'predictions_{model_name}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"💾 Saved predictions plot: {output_file}")
    
    def plot_residuals(self, y_true, y_pred, model_name: str):
        """Plot residuals"""
        residuals = y_true - y_pred
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Residual plot
        ax1.scatter(y_pred, residuals, alpha=0.5)
        ax1.axhline(y=0, color='r', linestyle='--')
        ax1.set_xlabel('Predicted Values')
        ax1.set_ylabel('Residuals')
        ax1.set_title('Residual Plot')
        ax1.grid(True, alpha=0.3)
        
        # Residual distribution
        ax2.hist(residuals, bins=30, edgecolor='black')
        ax2.set_xlabel('Residuals')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Residual Distribution')
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(f'{model_name}', fontsize=14)
        plt.tight_layout()
        
        output_file = self.reports_dir / f'residuals_{model_name}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"💾 Saved residuals plot: {output_file}")
    
    def generate_evaluation_report(self):
        """Generate comprehensive evaluation report"""
        logger.info("📝 Generating evaluation report...")
        
        # Save JSON report
        json_file = self.reports_dir / "model_evaluation_report.json"
        with open(json_file, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2)
        logger.info(f"💾 Saved JSON report: {json_file}")
        
        # Generate HTML report
        self.generate_html_report()
    
    def generate_html_report(self):
        """Generate HTML evaluation report"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Model Evaluation Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .header { background: #2196F3; color: white; padding: 20px; border-radius: 5px; }
                .model-section { background: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric { display: inline-block; margin: 10px 20px 10px 0; }
                .metric-label { font-weight: bold; color: #666; }
                .metric-value { font-size: 1.2em; color: #2196F3; }
                .good-fit { border-left: 4px solid #4CAF50; }
                .overfitting { border-left: 4px solid #f44336; }
                .underfitting { border-left: 4px solid #ff9800; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #f5f5f5; }
                img { max-width: 100%; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Model Evaluation Report</h1>
                <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
        """
        
        for model_type, results in self.evaluation_results.items():
            status_class = results['overfitting_status']['status'].lower().replace('_', '')
            
            html += f"""
            <div class="model-section {status_class}">
                <h2>{results['model_name']}</h2>
                <h3>Performance Metrics</h3>
                <div style="margin: 20px 0;">
            """
            
            # Display metrics
            for metric, value in results['test_metrics'].items():
                html += f"""
                <div class="metric">
                    <div class="metric-label">{metric.upper()}</div>
                    <div class="metric-value">{value:.4f}</div>
                </div>
                """
            
            html += f"""
                </div>
                <h3>Overfitting Analysis</h3>
                <p><strong>Status:</strong> {results['overfitting_status']['status']}</p>
                <p><strong>Severity:</strong> {results['overfitting_status']['severity']}</p>
                <p><strong>Recommendation:</strong> {results['overfitting_status']['recommendation']}</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        html_file = self.reports_dir / "model_evaluation_report.html"
        with open(html_file, 'w') as f:
            f.write(html)
        logger.info(f"💾 Saved HTML report: {html_file}")


if __name__ == "__main__":
    from sklearn.model_selection import train_test_split
    
    logger.info("="*60)
    logger.info("🚀 Starting Model Evaluation Pipeline")
    logger.info("="*60)
    
    # Load data (assuming models were trained with processed data)
    try:
        df = pd.read_csv("data/processed/classification_data.csv")
        
        # Prepare data
        y = df['migraine_occurrence']
        X = df.drop(columns=['migraine_occurrence'])
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Initialize evaluator
        evaluator = ModelEvaluator()
        
        # Load models
        models = evaluator.load_models()
        
        # Evaluate each model
        for model_name, model in models.items():
            if 'classification' in model_name:
                results = evaluator.evaluate_classification(
                    model, X_train, X_test, y_train, y_test, model_name
                )
            evaluator.evaluation_results[model_name] = results
        
        # Generate report
        evaluator.generate_evaluation_report()
        
        logger.info("="*60)
        logger.info("✅ Model Evaluation Completed!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
