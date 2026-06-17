"""
Run Isolation Forest predictions on user feature data.

Output: data/reports/anomaly_report.csv
  Columns: user_id, anomaly_score, anomaly_label
"""
import os
import logging
import pickle
import pandas as pd
from ml.training.train_model import FEATURE_COLS

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def predict(features_path: str, model_path: str, scaler_path: str, output_path: str) -> None:
    logger.info(f"Starting Isolation Forest prediction pipeline on {features_path}")
    try:
        # Check files
        for path in [features_path, model_path, scaler_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Required file missing: {path}")

        # Load latest features data
        df = pd.read_csv(features_path)
        logger.info(f"Loaded {len(df)} user feature rows")

        # Load model and scaler objects
        logger.info(f"Loading scaler from {scaler_path}...")
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)

        logger.info(f"Loading Isolation Forest model from {model_path}...")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        # Verify columns exist
        missing_cols = [col for col in FEATURE_COLS if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Missing columns in feature matrix: {missing_cols}")

        X = df[FEATURE_COLS]

        # 1. Normalise features using fitted scaler
        logger.info("Scaling features...")
        X_scaled = scaler.transform(X)

        # 2. Run prediction scoring
        logger.info("Scoring records using Isolation Forest...")
        raw_scores = model.decision_function(X_scaled)
        predictions = model.predict(X_scaled) # 1 = Normal, -1 = Outlier / Anomaly

        # 3. Build predictions report dataframe
        report_df = pd.DataFrame()
        report_df['user_id'] = df['user_id'].astype(str).str.strip().str.upper()
        report_df['anomaly_score'] = raw_scores
        
        # Map labels: -1 to 'Suspicious', 1 to 'Normal'
        report_df['anomaly_label'] = pd.Series(predictions).map({1: 'Normal', -1: 'Suspicious'})

        # 4. Print evaluation metrics
        suspicious_df = report_df[report_df['anomaly_label'] == 'Suspicious']
        normal_df = report_df[report_df['anomaly_label'] == 'Normal']
        
        logger.info("=== Anomaly Detection Evaluation Metrics ===")
        logger.info(f"Total Users Checked: {len(report_df)}")
        logger.info(f"Normal Users (Inliers): {len(normal_df)} ({len(normal_df)/len(report_df)*100:.2f}%)")
        logger.info(f"Suspicious Users (Outliers): {len(suspicious_df)} ({len(suspicious_df)/len(report_df)*100:.2f}%)")
        logger.info(f"Suspicious Users Anomaly Score range: [{suspicious_df['anomaly_score'].min():.4f}, {suspicious_df['anomaly_score'].max():.4f}]")
        logger.info(f"Normal Users Anomaly Score range: [{normal_df['anomaly_score'].min():.4f}, {normal_df['anomaly_score'].max():.4f}]")

        # 5. Save report to reports directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        report_df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved anomaly reports to {output_path}")

    except Exception as e:
        logger.error(f"Error running Isolation Forest prediction: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    predict(
        "data/features/user_features.csv",
        "ml/models/isolation_forest.pkl",
        "ml/models/scaler.pkl",
        "data/reports/anomaly_report.csv"
    )
