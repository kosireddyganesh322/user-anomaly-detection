"""
Train an Isolation Forest model on the user features matrix.

Outputs:
  - ml/models/isolation_forest.pkl
  - ml/models/scaler.pkl
"""
import os
import logging
import pickle
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurable feature list
FEATURE_COLS = [
    'total_logins',
    'active_days',
    'avg_logins_per_day',
    'unique_pcs_used',
    'after_hours_logins',
    'weekend_logins',
    'usb_connects',
    'after_hours_usb',
    'login_device_ratio',
    'after_hours_ratio',
    'weekend_ratio'
]

def train(
    features_path: str,
    model_path: str = "ml/models/isolation_forest.pkl",
    scaler_path: str = "ml/models/scaler.pkl"
) -> None:
    logger.info(f"Starting Isolation Forest training pipeline on {features_path}")
    try:
        # Resolve path fallback if needed
        if not os.path.exists(features_path):
            fallback_path = features_path.replace("user_features.csv", "master_features.csv")
            if os.path.exists(fallback_path):
                logger.info(f"Input path {features_path} not found, falling back to: {fallback_path}")
                features_path = fallback_path
            else:
                raise FileNotFoundError(f"Input file not found at: {features_path}")

        # Load features
        df = pd.read_csv(features_path)
        logger.info(f"Loaded {len(df)} user feature rows")

        # Verify columns exist
        missing_cols = [col for col in FEATURE_COLS if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Missing columns in feature matrix: {missing_cols}")

        X = df[FEATURE_COLS]

        # 1. StandardScaler feature normalization
        logger.info("Normalizing features using StandardScaler...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 2. Fit IsolationForest Model
        # We configure:
        #   - contamination=0.05 (expected anomaly rate of 5%)
        #   - random_state=42 (ensure reproducibility)
        #   - n_estimators=100 (standard number of isolation trees)
        contamination = 0.05
        logger.info(f"Fitting IsolationForest model (contamination={contamination}, random_state=42)...")
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            n_jobs=-1
        )
        model.fit(X_scaled)

        # 3. Save serialized pickles
        models_dir = os.path.dirname(model_path)
        if models_dir:
            os.makedirs(models_dir, exist_ok=True)

        logger.info(f"Saving scaler to {scaler_path}...")
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)

        logger.info(f"Saving model to {model_path}...")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        logger.info("Model training pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Error training Isolation Forest model: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    train("data/features/user_features.csv")
