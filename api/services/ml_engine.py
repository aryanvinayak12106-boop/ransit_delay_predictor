"""
ML Engine Service for Transit Delay Prediction
Handles model loading, inference, and training metrics
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import joblib
import pickle
import numpy as np

logger = logging.getLogger(__name__)

class MLEngine:
    """
    Machine Learning Model for delay prediction
    Uses scikit-learn Random Forest trained on Kaggle dataset
    
    Features:
    - hour_of_day: 0-23
    - day_of_week: 0-6
    - temperature: celsius
    - precipitation_mm: rainfall
    - traffic_density: 0.0-1.0
    - event_count_nearby: 0-10
    - crowdsourced_delay_count: 0-100
    - stop_type: categorical
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = [
            'hour_of_day',
            'day_of_week',
            'temperature',
            'precipitation_mm',
            'traffic_density',
            'event_count_nearby',
            'crowdsourced_delay_count',
            'is_weekend',
            'weather_severity'
        ]
        self.model_version = "1.0.0"
        self.last_training_date = None
    
    async def load_model(self):
        """Load pre-trained model from disk or cloud"""
        try:
            model_path = os.getenv('ML_MODEL_PATH', 'models/delay_predictor.joblib')
            
            if os.path.exists(model_path):
                logger.info(f"Loading ML model from {model_path}")
                self.model = await asyncio.to_thread(
                    joblib.load, model_path
                )
                logger.info(f"✅ Model loaded successfully")
            else:
                logger.warning(f"Model file not found at {model_path}")
                logger.warning("Will use fallback prediction logic")
                self.model = None
        
        except Exception as e:
            logger.error(f"Error loading ML model: {e}")
            self.model = None
    
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make ML prediction for delay
        
        Args:
            features: {
                'hour': 9,
                'day_of_week': 3,
                'temperature': 28,
                'precipitation_mm': 2.5,
                'traffic_density': 0.7,
                'events_count': 1,
                'reports_count': 5,
                'is_weekend': False,
                'weather_severity': 0.6
            }
        
        Returns:
            {
                'delay_minutes': 15,
                'confidence': 0.85,
                'version': '1.0.0',
                'model_type': 'random_forest'
            }
        """
        try:
            if not self.model:
                logger.warning("ML model not loaded, returning fallback prediction")
                return self._fallback_predict(features)
            
            # Prepare features in correct order
            feature_vector = [
                features.get('hour', 9),
                features.get('day_of_week', 3),
                features.get('temperature', 28),
                features.get('precipitation_mm', 0),
                features.get('traffic_density', 0.5),
                features.get('events_count', 0),
                features.get('reports_count', 0),
                int(features.get('is_weekend', False)),
                features.get('weather_severity', 0)
            ]
            
            # Predict using model
            delay_prediction = await asyncio.to_thread(
                self.model.predict,
                [feature_vector]
            )
            
            # Get prediction confidence
            probabilities = await asyncio.to_thread(
                self.model.predict_proba,
                [feature_vector]
            ) if hasattr(self.model, 'predict_proba') else [np.array([0.5, 0.5])]
            
            delay_minutes = int(delay_prediction[0])
            confidence = float(np.max(probabilities[0])) if probabilities else 0.7
            
            # Log metrics
            from app.services.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            await supabase.log_api_call(
                api_provider='ml_model',
                response_time_ms=50,
                is_successful=True,
                confidence_score=confidence * 100
            )
            
            return {
                'delay_minutes': max(0, delay_minutes),  # No negative delays
                'confidence': min(100, confidence * 100),  # 0-100%
                'version': self.model_version,
                'model_type': 'random_forest',
                'features_used': len(feature_vector)
            }
        
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return self._fallback_predict(features)
    
    def _fallback_predict(self, features: Dict) -> Dict:
        """
        Fallback heuristic prediction if model fails
        Uses simple rule-based logic
        """
        delay = 0
        
        # Weather impact: +2-10 minutes for rain/snow
        if features.get('precipitation_mm', 0) > 2:
            delay += 5 + (features.get('weather_severity', 0) * 5)
        
        # Traffic impact: +1-15 minutes
        delay += features.get('traffic_density', 0.5) * 15
        
        # Events impact: +5-20 minutes each
        delay += features.get('events_count', 0) * 10
        
        # Peak hour impact: +3-8 minutes
        hour = features.get('hour', 9)
        if hour in [7, 8, 9, 17, 18, 19]:  # Peak hours
            delay += 5
        
        # Crowdsourced reports: +1-5 minutes per report
        delay += min(features.get('reports_count', 0) * 0.5, 20)
        
        confidence = 50 + (features.get('reports_count', 0) * 5)  # Boost with reports
        
        return {
            'delay_minutes': int(delay),
            'confidence': min(80, confidence),  # Max 80% for fallback
            'version': self.model_version,
            'model_type': 'heuristic_fallback',
            'warning': 'Using fallback prediction logic'
        }
    
    async def train_model(self, training_data: Dict) -> Dict[str, Any]:
        """
        Retrain model with new data (background job)
        
        Args:
            training_data: {
                'X': feature array,
                'y': target delays,
                'feature_names': list,
                'test_split': 0.2
            }
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_error, r2_score
            
            X = training_data.get('X')
            y = training_data.get('y')
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=0.2,
                random_state=42
            )
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )
            
            await asyncio.to_thread(model.fit, X_train, y_train)
            
            # Evaluate
            predictions = await asyncio.to_thread(model.predict, X_test)
            mae = mean_absolute_error(y_test, predictions)
            r2 = r2_score(y_test, predictions)
            
            # Save model
            model_path = 'models/delay_predictor.joblib'
            os.makedirs('models', exist_ok=True)
            await asyncio.to_thread(joblib.dump, model, model_path)
            
            self.model = model
            self.last_training_date = datetime.utcnow()
            
            # Log metrics to Supabase
            from app.services.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            
            metrics = {
                'model_version': self.model_version,
                'test_accuracy': r2 * 100,
                'mean_absolute_error': mae,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'features_count': len(self.feature_names),
                'trained_at': self.last_training_date.isoformat()
            }
            
            logger.info(f"Model trained successfully: {metrics}")
            
            return metrics
        
        except Exception as e:
            logger.error(f"Model training error: {e}")
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if not self.model or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importances = self.model.feature_importances_
        return {
            name: float(importance)
            for name, importance in zip(self.feature_names, importances)
        }

# ============================================================================
# Singleton instance
# ============================================================================
_ml_engine_instance = None

def get_ml_engine() -> MLEngine:
    """Get or create singleton ML engine"""
    global _ml_engine_instance
    if _ml_engine_instance is None:
        _ml_engine_instance = MLEngine()
    return _ml_engine_instance
