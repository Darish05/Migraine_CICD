"""
Deployment Monitoring with Prometheus Metrics
Real-time monitoring and alerting for ML deployment
Part of MLOps monitoring and MLSecOps pipeline
"""

import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import numpy as np

# Prometheus client
from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server, generate_latest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentMonitor:
    """Monitor ML model deployment with Prometheus metrics"""
    
    def __init__(self, port: int = 9090):
        self.port = port
        
        # Define Prometheus metrics
        
        # Counters
        self.prediction_counter = Counter(
            'migraine_predictions_total',
            'Total number of predictions made',
            ['model_type', 'prediction_result']
        )
        
        self.errors_counter = Counter(
            'migraine_prediction_errors_total',
            'Total number of prediction errors',
            ['error_type']
        )
        
        self.api_requests_counter = Counter(
            'migraine_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status']
        )
        
        # Histograms
        self.prediction_latency = Histogram(
            'migraine_prediction_latency_seconds',
            'Prediction latency in seconds',
            ['model_type'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
        
        self.api_latency = Histogram(
            'migraine_api_latency_seconds',
            'API request latency in seconds',
            ['endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Gauges
        self.model_accuracy = Gauge(
            'migraine_model_accuracy',
            'Current model accuracy',
            ['model_type']
        )
        
        self.model_confidence = Gauge(
            'migraine_prediction_confidence',
            'Average prediction confidence',
            ['model_type']
        )
        
        self.active_requests = Gauge(
            'migraine_active_requests',
            'Number of active requests'
        )
        
        self.drift_score = Gauge(
            'migraine_data_drift_score',
            'Data drift score (PSI)',
            ['feature']
        )
        
        self.performance_degradation = Gauge(
            'migraine_performance_degradation',
            'Model performance degradation percentage'
        )
        
        # Info
        self.model_info = Info(
            'migraine_model',
            'Information about the deployed model'
        )
        
        # Internal monitoring
        self.predictions_window = deque(maxlen=1000)  # Last 1000 predictions
        self.latencies_window = deque(maxlen=1000)
        self.start_time = time.time()
        
        logger.info(f"✅ Monitoring metrics initialized")
    
    def start_server(self):
        """Start Prometheus metrics server"""
        try:
            start_http_server(self.port)
            logger.info(f"🚀 Prometheus metrics server started on port {self.port}")
            logger.info(f"   Metrics available at: http://localhost:{self.port}/metrics")
        except Exception as e:
            logger.error(f"❌ Failed to start metrics server: {e}")
    
    def record_prediction(self, model_type: str, prediction: int, 
                         confidence: float, latency: float):
        """Record a prediction event"""
        # Update counters
        result = 'positive' if prediction == 1 else 'negative'
        self.prediction_counter.labels(
            model_type=model_type,
            prediction_result=result
        ).inc()
        
        # Update histograms
        self.prediction_latency.labels(model_type=model_type).observe(latency)
        
        # Update gauges
        self.model_confidence.labels(model_type=model_type).set(confidence)
        
        # Store in window
        self.predictions_window.append({
            'timestamp': datetime.now(),
            'prediction': prediction,
            'confidence': confidence,
            'latency': latency
        })
        
        logger.debug(f"📊 Recorded prediction: {model_type}, result={result}, latency={latency:.4f}s")
    
    def record_api_request(self, endpoint: str, method: str, 
                          status: int, latency: float):
        """Record an API request"""
        self.api_requests_counter.labels(
            endpoint=endpoint,
            method=method,
            status=str(status)
        ).inc()
        
        self.api_latency.labels(endpoint=endpoint).observe(latency)
        
        logger.debug(f"📊 API request: {method} {endpoint}, status={status}, latency={latency:.4f}s")
    
    def record_error(self, error_type: str):
        """Record an error"""
        self.errors_counter.labels(error_type=error_type).inc()
        logger.warning(f"⚠️ Error recorded: {error_type}")
    
    def update_model_accuracy(self, model_type: str, accuracy: float):
        """Update model accuracy metric"""
        self.model_accuracy.labels(model_type=model_type).set(accuracy)
        logger.info(f"📊 Model accuracy updated: {model_type} = {accuracy:.4f}")
    
    def update_drift_score(self, feature: str, psi_score: float):
        """Update drift score for a feature"""
        self.drift_score.labels(feature=feature).set(psi_score)
        
        # Alert if drift detected
        if psi_score > 0.2:
            logger.warning(f"🚨 ALERT: Significant drift detected in '{feature}': PSI={psi_score:.4f}")
    
    def update_performance_degradation(self, degradation_pct: float):
        """Update performance degradation metric"""
        self.performance_degradation.set(degradation_pct)
        
        # Alert if significant degradation
        if degradation_pct > 10:
            logger.warning(f"🚨 ALERT: Significant performance degradation: {degradation_pct:.2f}%")
    
    def set_model_info(self, model_name: str, version: str, 
                       training_date: str, accuracy: str):
        """Set model information"""
        self.model_info.info({
            'model_name': model_name,
            'version': version,
            'training_date': training_date,
            'baseline_accuracy': accuracy
        })
        logger.info(f"ℹ️ Model info updated: {model_name} v{version}")
    
    def get_current_stats(self) -> dict:
        """Get current monitoring statistics"""
        if not self.predictions_window:
            return {}
        
        recent_predictions = list(self.predictions_window)
        
        stats = {
            'total_predictions': len(recent_predictions),
            'avg_latency': np.mean([p['latency'] for p in recent_predictions]),
            'avg_confidence': np.mean([p['confidence'] for p in recent_predictions]),
            'positive_rate': sum(1 for p in recent_predictions if p['prediction'] == 1) / len(recent_predictions),
            'uptime_hours': (time.time() - self.start_time) / 3600
        }
        
        return stats
    
    def check_health(self) -> dict:
        """Perform health check"""
        stats = self.get_current_stats()
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_hours': stats.get('uptime_hours', 0),
            'checks': {}
        }
        
        # Check average latency
        avg_latency = stats.get('avg_latency', 0)
        if avg_latency > 1.0:
            health_status['checks']['latency'] = {
                'status': 'warning',
                'value': avg_latency,
                'message': f'High latency detected: {avg_latency:.2f}s'
            }
            health_status['status'] = 'warning'
        else:
            health_status['checks']['latency'] = {
                'status': 'ok',
                'value': avg_latency
            }
        
        # Check prediction rate
        if stats.get('total_predictions', 0) > 0:
            health_status['checks']['predictions'] = {
                'status': 'ok',
                'value': stats['total_predictions']
            }
        else:
            health_status['checks']['predictions'] = {
                'status': 'warning',
                'message': 'No predictions made recently'
            }
        
        return health_status
    
    def generate_alert(self, alert_type: str, severity: str, message: str):
        """Generate monitoring alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'severity': severity,
            'message': message
        }
        
        # Log alert
        if severity == 'critical':
            logger.critical(f"🚨 CRITICAL ALERT: {message}")
        elif severity == 'warning':
            logger.warning(f"⚠️ WARNING: {message}")
        else:
            logger.info(f"ℹ️ INFO: {message}")
        
        # Save alert
        self.save_alert(alert)
        
        return alert
    
    def save_alert(self, alert: dict):
        """Save alert to file"""
        alerts_dir = Path("reports/alerts")
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        # Append to alerts log
        alerts_file = alerts_dir / f"alerts_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(alerts_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
    
    def continuous_monitoring(self, check_interval: int = 60):
        """Run continuous monitoring loop"""
        logger.info(f"🔄 Starting continuous monitoring (interval: {check_interval}s)")
        
        try:
            while True:
                # Perform health check
                health = self.check_health()
                
                # Log health status
                logger.info(f"💚 Health Status: {health['status']}")
                logger.info(f"   Uptime: {health['uptime_hours']:.2f} hours")
                
                # Check for warnings
                for check_name, check_result in health['checks'].items():
                    if check_result['status'] == 'warning':
                        self.generate_alert(
                            alert_type=check_name,
                            severity='warning',
                            message=check_result.get('message', f'{check_name} check failed')
                        )
                
                # Sleep until next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("⏸️ Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")


class MLSecOpsMonitor:
    """Security monitoring for ML deployment (MLSecOps)"""
    
    def __init__(self):
        self.security_events = []
        
    def check_input_validation(self, input_data: dict) -> dict:
        """Validate input data for security issues"""
        validation_result = {
            'valid': True,
            'issues': []
        }
        
        # Check for null/missing values
        for key, value in input_data.items():
            if value is None:
                validation_result['issues'].append(f"Null value in field: {key}")
                validation_result['valid'] = False
        
        # Check for out-of-range values
        numeric_ranges = {
            'age': (18, 100),
            'sleep_hours': (0, 24),
            'stress_level': (0, 10)
        }
        
        for field, (min_val, max_val) in numeric_ranges.items():
            if field in input_data:
                if not (min_val <= input_data[field] <= max_val):
                    validation_result['issues'].append(
                        f"{field} out of range: {input_data[field]} not in [{min_val}, {max_val}]"
                    )
                    validation_result['valid'] = False
        
        return validation_result
    
    def log_security_event(self, event_type: str, severity: str, details: dict):
        """Log security event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        
        self.security_events.append(event)
        
        # Log to file
        security_dir = Path("reports/security")
        security_dir.mkdir(parents=True, exist_ok=True)
        
        security_file = security_dir / f"security_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(security_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        logger.warning(f"🔒 Security Event: {event_type} ({severity})")


if __name__ == "__main__":
    logger.info("="*60)
    logger.info("🚀 Starting Deployment Monitoring")
    logger.info("="*60)
    
    # Initialize monitor
    monitor = DeploymentMonitor(port=9090)
    
    # Set model info
    monitor.set_model_info(
        model_name="MigrainePredictor",
        version="1.0.0",
        training_date=datetime.now().strftime('%Y-%m-%d'),
        accuracy="0.89"
    )
    
    # Start metrics server
    monitor.start_server()
    
    logger.info("\n" + "="*60)
    logger.info("📊 Monitoring Dashboard")
    logger.info("="*60)
    logger.info(f"Prometheus Metrics: http://localhost:9090/metrics")
    logger.info(f"Health Endpoint: Available via API")
    logger.info("="*60 + "\n")
    
    # Run continuous monitoring
    monitor.continuous_monitoring(check_interval=30)
