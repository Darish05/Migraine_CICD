"""
Model Drift Detection
Detects data drift and model performance degradation
Part of automated MLOps monitoring pipeline
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging
from scipy import stats
from sklearn.metrics import accuracy_score, f1_score
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DriftDetector:
    """Detect data drift and model performance drift"""
    
    def __init__(self, reference_data_path: str = "data/processed/classification_data.csv"):
        self.reference_data_path = reference_data_path
        self.reference_data = None
        self.drift_reports = []
        
    def load_reference_data(self):
        """Load reference (training) data"""
        logger.info(f"📂 Loading reference data from {self.reference_data_path}")
        self.reference_data = pd.read_csv(self.reference_data_path)
        logger.info(f"✅ Loaded {len(self.reference_data)} reference samples")
        
    def calculate_psi(self, reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
        """
        Calculate Population Stability Index (PSI)
        PSI < 0.1: No significant change
        0.1 <= PSI < 0.2: Moderate change
        PSI >= 0.2: Significant change
        """
        # Create bins based on reference data
        try:
            breakpoints = np.percentile(reference, np.linspace(0, 100, bins + 1))
            breakpoints = np.unique(breakpoints)  # Remove duplicates
            
            if len(breakpoints) < 3:
                logger.warning(f"Not enough unique values for PSI calculation")
                return 0.0
            
            # Calculate distributions
            ref_counts, _ = np.histogram(reference, bins=breakpoints)
            curr_counts, _ = np.histogram(current, bins=breakpoints)
            
            # Convert to proportions (add small epsilon to avoid log(0))
            epsilon = 0.0001
            ref_props = (ref_counts + epsilon) / (len(reference) + epsilon * bins)
            curr_props = (curr_counts + epsilon) / (len(current) + epsilon * bins)
            
            # Calculate PSI
            psi = np.sum((curr_props - ref_props) * np.log(curr_props / ref_props))
            
            return psi
        except Exception as e:
            logger.warning(f"Error calculating PSI: {e}")
            return 0.0
    
    def detect_feature_drift(self, current_data: pd.DataFrame, threshold: float = 0.2) -> dict:
        """Detect drift in individual features using PSI"""
        logger.info("🔍 Detecting feature drift...")
        
        if self.reference_data is None:
            self.load_reference_data()
        
        drift_results = {}
        drifted_features = []
        
        # Get common columns (exclude target)
        common_cols = [col for col in current_data.columns 
                      if col in self.reference_data.columns and col != 'migraine_occurrence']
        
        for col in common_cols:
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(current_data[col]):
                continue
            
            psi = self.calculate_psi(self.reference_data[col], current_data[col])
            
            # Determine drift status
            if psi >= threshold:
                status = "SIGNIFICANT_DRIFT"
                drifted_features.append(col)
            elif psi >= 0.1:
                status = "MODERATE_DRIFT"
            else:
                status = "NO_DRIFT"
            
            drift_results[col] = {
                'psi': float(psi),
                'status': status,
                'ref_mean': float(self.reference_data[col].mean()),
                'curr_mean': float(current_data[col].mean()),
                'ref_std': float(self.reference_data[col].std()),
                'curr_std': float(current_data[col].std())
            }
        
        summary = {
            'total_features': len(drift_results),
            'drifted_features': len(drifted_features),
            'drifted_feature_names': drifted_features,
            'drift_percentage': (len(drifted_features) / len(drift_results) * 100) if drift_results else 0,
            'overall_status': 'DRIFT_DETECTED' if drifted_features else 'NO_DRIFT'
        }
        
        logger.info(f"   Total features analyzed: {summary['total_features']}")
        logger.info(f"   Drifted features: {summary['drifted_features']}")
        logger.info(f"   Overall status: {summary['overall_status']}")
        
        return {
            'feature_drift': drift_results,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_statistical_drift(self, current_data: pd.DataFrame, alpha: float = 0.05) -> dict:
        """Detect drift using statistical tests (Kolmogorov-Smirnov test)"""
        logger.info("📊 Running statistical drift tests...")
        
        if self.reference_data is None:
            self.load_reference_data()
        
        drift_results = {}
        
        common_cols = [col for col in current_data.columns 
                      if col in self.reference_data.columns and col != 'migraine_occurrence']
        
        for col in common_cols:
            if not pd.api.types.is_numeric_dtype(current_data[col]):
                continue
            
            # Kolmogorov-Smirnov test
            statistic, p_value = stats.ks_2samp(
                self.reference_data[col].dropna(),
                current_data[col].dropna()
            )
            
            drift_detected = p_value < alpha
            
            drift_results[col] = {
                'statistic': float(statistic),
                'p_value': float(p_value),
                'drift_detected': drift_detected,
                'test': 'Kolmogorov-Smirnov'
            }
        
        drifted_count = sum(1 for r in drift_results.values() if r['drift_detected'])
        
        summary = {
            'total_features': len(drift_results),
            'drifted_features': drifted_count,
            'significance_level': alpha
        }
        
        logger.info(f"   Features with statistical drift: {drifted_count}/{len(drift_results)}")
        
        return {
            'statistical_drift': drift_results,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_target_drift(self, current_data: pd.DataFrame) -> dict:
        """Detect drift in target variable distribution"""
        logger.info("🎯 Detecting target distribution drift...")
        
        if self.reference_data is None:
            self.load_reference_data()
        
        target_col = 'migraine_occurrence'
        
        if target_col not in current_data.columns or target_col not in self.reference_data.columns:
            logger.warning(f"Target column '{target_col}' not found")
            return {}
        
        # Calculate distributions
        ref_dist = self.reference_data[target_col].value_counts(normalize=True).to_dict()
        curr_dist = current_data[target_col].value_counts(normalize=True).to_dict()
        
        # Calculate difference
        drift_magnitude = abs(ref_dist.get(1, 0) - curr_dist.get(1, 0))
        
        status = "SIGNIFICANT_DRIFT" if drift_magnitude > 0.1 else "NO_DRIFT"
        
        results = {
            'reference_distribution': ref_dist,
            'current_distribution': curr_dist,
            'drift_magnitude': float(drift_magnitude),
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"   Target drift magnitude: {drift_magnitude:.4f}")
        logger.info(f"   Status: {status}")
        
        return results
    
    def detect_model_performance_drift(self, model, current_data: pd.DataFrame, 
                                      current_labels: pd.Series, baseline_accuracy: float) -> dict:
        """Detect model performance degradation"""
        logger.info("📉 Detecting model performance drift...")
        
        # Get predictions
        predictions = model.predict(current_data)
        
        # Calculate metrics
        current_accuracy = accuracy_score(current_labels, predictions)
        current_f1 = f1_score(current_labels, predictions, average='weighted')
        
        # Calculate performance drop
        accuracy_drop = baseline_accuracy - current_accuracy
        performance_degradation = (accuracy_drop / baseline_accuracy) * 100
        
        # Determine status
        if performance_degradation > 10:
            status = "SIGNIFICANT_DEGRADATION"
        elif performance_degradation > 5:
            status = "MODERATE_DEGRADATION"
        else:
            status = "NO_DEGRADATION"
        
        results = {
            'baseline_accuracy': float(baseline_accuracy),
            'current_accuracy': float(current_accuracy),
            'current_f1': float(current_f1),
            'accuracy_drop': float(accuracy_drop),
            'performance_degradation_pct': float(performance_degradation),
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"   Baseline accuracy: {baseline_accuracy:.4f}")
        logger.info(f"   Current accuracy: {current_accuracy:.4f}")
        logger.info(f"   Performance degradation: {performance_degradation:.2f}%")
        logger.info(f"   Status: {status}")
        
        return results
    
    def comprehensive_drift_check(self, current_data: pd.DataFrame, 
                                 current_labels: pd.Series = None,
                                 model = None,
                                 baseline_accuracy: float = None) -> dict:
        """Run comprehensive drift detection"""
        logger.info("="*60)
        logger.info("🔍 Starting Comprehensive Drift Detection")
        logger.info("="*60)
        
        drift_report = {
            'timestamp': datetime.now().isoformat(),
            'data_size': len(current_data)
        }
        
        # Feature drift
        drift_report['feature_drift'] = self.detect_feature_drift(current_data)
        
        # Statistical drift
        drift_report['statistical_drift'] = self.detect_statistical_drift(current_data)
        
        # Target drift
        drift_report['target_drift'] = self.detect_target_drift(current_data)
        
        # Model performance drift (if model and labels provided)
        if model is not None and current_labels is not None and baseline_accuracy is not None:
            # Prepare data (remove target if present)
            X_current = current_data.drop(columns=['migraine_occurrence'], errors='ignore')
            drift_report['performance_drift'] = self.detect_model_performance_drift(
                model, X_current, current_labels, baseline_accuracy
            )
        
        # Overall assessment
        drift_detected = (
            drift_report['feature_drift']['summary']['overall_status'] == 'DRIFT_DETECTED' or
            drift_report['target_drift'].get('status') == 'SIGNIFICANT_DRIFT'
        )
        
        drift_report['overall_assessment'] = {
            'drift_detected': drift_detected,
            'action_required': drift_detected,
            'recommendation': self.get_drift_recommendation(drift_report)
        }
        
        # Save report
        self.save_drift_report(drift_report)
        
        logger.info("="*60)
        logger.info(f"✅ Drift Detection Completed")
        logger.info(f"   Drift Detected: {drift_detected}")
        logger.info(f"   Action Required: {drift_detected}")
        logger.info("="*60)
        
        return drift_report
    
    def get_drift_recommendation(self, drift_report: dict) -> str:
        """Generate recommendations based on drift detection"""
        recommendations = []
        
        # Check feature drift
        if drift_report['feature_drift']['summary']['overall_status'] == 'DRIFT_DETECTED':
            recommendations.append("RETRAIN MODEL: Significant feature drift detected")
        
        # Check target drift
        if drift_report['target_drift'].get('status') == 'SIGNIFICANT_DRIFT':
            recommendations.append("INVESTIGATE DATA: Target distribution has shifted significantly")
        
        # Check performance drift
        if 'performance_drift' in drift_report:
            status = drift_report['performance_drift']['status']
            if status in ['SIGNIFICANT_DEGRADATION', 'MODERATE_DEGRADATION']:
                recommendations.append(f"MODEL RETRAINING REQUIRED: {status}")
        
        if not recommendations:
            recommendations.append("NO ACTION REQUIRED: Model is performing well")
        
        return " | ".join(recommendations)
    
    def save_drift_report(self, report: dict, output_dir: str = "reports/drift"):
        """Save drift detection report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = output_path / f"drift_report_{timestamp}.json"
        
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"💾 Saved drift report: {json_file}")
        
        # Save latest report
        latest_file = output_path / "drift_report_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"💾 Saved latest drift report: {latest_file}")


if __name__ == "__main__":
    # Example usage
    detector = DriftDetector()
    
    # Simulate current data (in production, this would be recent production data)
    try:
        current_data = pd.read_csv("data/processed/classification_data.csv").sample(n=500, random_state=42)
        current_labels = current_data['migraine_occurrence']
        
        # Run drift detection
        drift_report = detector.comprehensive_drift_check(
            current_data=current_data,
            current_labels=current_labels
        )
        
        print(f"\n{'='*60}")
        print(f"📊 DRIFT DETECTION SUMMARY")
        print(f"{'='*60}")
        print(f"Drift Detected: {drift_report['overall_assessment']['drift_detected']}")
        print(f"Recommendation: {drift_report['overall_assessment']['recommendation']}")
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"❌ Drift detection failed: {e}")
        import traceback
        traceback.print_exc()
