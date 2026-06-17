"""
Risk Engine
Input : data/features/user_features.csv
Output: data/reports/risk_scores.csv

Appends columns 'risk_score' and 'risk_level' based on weighted behavioral metrics.
"""
import os
import logging
import pandas as pd
from ml.risk_scoring.risk_rules import WEIGHTS, RULE_REGISTRY, score_login_device_ratio
from ml.risk_scoring.risk_levels import get_risk_level

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_user_risk(row: pd.Series) -> float:
    """
    Calculate the weighted risk score for a single user row.
    Returns a float score between 0.0 and 100.0.
    """
    weighted_score = 0.0
    
    # 1. Run rule-based scoring from registry
    for feature, score_func in RULE_REGISTRY.items():
        val = row.get(feature, 0.0)
        sub_score = score_func(val)
        weight = WEIGHTS[feature]
        weighted_score += sub_score * weight

    # 2. Run login-to-device ratio scoring
    ratio_val = row.get('login_device_ratio', 0.0)
    usb_val = row.get('usb_connects', 0.0)
    ratio_sub_score = score_login_device_ratio(ratio_val, usb_val)
    weighted_score += ratio_sub_score * WEIGHTS['login_device_ratio']
    
    # Return rounded score
    return round(weighted_score, 2)

def run_risk_scoring(input_path: str, output_path: str) -> None:
    logger.info(f"Starting risk scoring engine using features from {input_path}")
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found at: {input_path}")

        # Load user features
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} user feature records")

        if df.empty:
            logger.warning("User features dataframe is empty. Creating empty risk scores file.")
            df['risk_score'] = []
            df['risk_level'] = []
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            return

        # Calculate scores
        logger.info("Calculating risk scores and mapping levels...")
        df['risk_score'] = df.apply(calculate_user_risk, axis=1)
        df['risk_level'] = df['risk_score'].apply(get_risk_level)

        # Log risk level distribution
        distribution = df['risk_level'].value_counts().to_dict()
        logger.info(f"Risk level distribution: {distribution}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved risk scores to {output_path}")

    except Exception as e:
        logger.error(f"Error running risk scoring engine: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    run_risk_scoring(
        "data/features/user_features.csv",
        "data/reports/risk_scores.csv"
    )
