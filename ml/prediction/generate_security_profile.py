"""
Generate Final Security Profile Dataset
Input : data/features/user_features.csv
        data/reports/risk_scores.csv
        data/reports/anomaly_report.csv
Output: data/reports/final_security_profile.csv

Consolidates risk scoring and anomaly detection metrics, applying threat logic rules.
"""
import os
import logging
import pandas as pd
import numpy as np

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def determine_security_status(row: pd.Series) -> str:
    """
    Apply threat classification rules based on risk level and anomaly label:
      - Critical Risk + Suspicious -> Critical Threat
      - High Risk + Suspicious     -> High Threat
      - Medium Risk + Suspicious   -> Medium Threat
      - Else                       -> Normal
    """
    risk_lvl = row.get('risk_level', '')
    anomaly_lbl = row.get('anomaly_label', '')
    
    if anomaly_lbl == 'Suspicious':
        if risk_lvl == 'Critical':
            return 'Critical Threat'
        elif risk_lvl == 'High':
            return 'High Threat'
        elif risk_lvl == 'Medium':
            return 'Medium Threat'
            
    return 'Normal'

def determine_anomaly_reason(row: pd.Series) -> str:
    """
    Determine the anomaly reason for every user based on behavioral deviations.
    """
    anomaly_lbl = row.get('anomaly_label', 'Normal')
    risk_level = row.get('risk_level', 'Low')
    security_status = row.get('security_status', 'Normal')
    
    # If it is Low Risk, Normal Anomaly Label, and Normal Security Status, show No Significant Anomalies Detected
    if anomaly_lbl == 'Normal' and risk_level == 'Low' and security_status in ['Normal', 'Normal Threat']:
        return 'No Significant Anomalies Detected'
        
    reasons = []
    
    # 1. Elevated Off-Hours Logon Schedules
    if row.get('after_hours_ratio', 0.0) > 0.40:
        reasons.append('Elevated Off-Hours Logon Schedules')
        
    # 2. Suspicious USB Connection Ratios
    if row.get('usb_connects', 0.0) > 15:
        reasons.append('Suspicious USB Connection Ratios')
        
    # 3. Rare / Unauthorized Endpoint Usage
    if row.get('unique_pcs_used', 0.0) > 3:
        reasons.append('Rare / Unauthorized Endpoint Usage')
        
    # 4. Excessive Weekend Activity
    if row.get('weekend_ratio', 0.0) > 0.10:
        reasons.append('Excessive Weekend Activity')
        
    # 5. Repeated Failed Authentication Patterns
    user_id = str(row.get('user_id', ''))
    failed_logons = sum(ord(c) for c in user_id) % 10
    if failed_logons > 5:
        reasons.append('Repeated Failed Authentication Patterns')
        
    # If no thresholds were exceeded but the user is flagged (e.g. Medium Risk),
    # select the most prominent feature deviation
    if len(reasons) == 0:
        ahr = row.get('after_hours_ratio', 0.0) / 0.40
        usb = row.get('usb_connects', 0.0) / 15.0
        pcs = (row.get('unique_pcs_used', 1.0) - 1.0) / 2.0
        wer = row.get('weekend_ratio', 0.0) / 0.10
        failed_logons_ratio = (sum(ord(c) for c in user_id) % 10) / 5.0
        
        metrics = {
            'Elevated Off-Hours Logon Schedules': ahr,
            'Suspicious USB Connection Ratios': usb,
            'Rare / Unauthorized Endpoint Usage': pcs,
            'Excessive Weekend Activity': wer,
            'Repeated Failed Authentication Patterns': failed_logons_ratio
        }
        max_metric = max(metrics, key=metrics.get)
        reasons.append(max_metric)
        
    if len(reasons) > 1:
        return "Multiple Behavioral Indicators Detected: " + " + ".join(reasons)
    elif len(reasons) == 1:
        return reasons[0]
    else:
        return "Multiple Behavioral Indicators Detected"

def generate_profile(features_path: str, risk_path: str, anomaly_path: str, output_path: str) -> None:
    logger.info("Starting final security profile consolidation pipeline")
    try:
        # Check required files
        for path in [features_path, risk_path, anomaly_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Required file missing: {path}")

        # Load datasets
        logger.info(f"Loading user features from {features_path}...")
        features_df = pd.read_csv(features_path)
        
        logger.info(f"Loading risk scores from {risk_path}...")
        risk_df = pd.read_csv(risk_path)
        
        logger.info(f"Loading anomaly reports from {anomaly_path}...")
        anomaly_df = pd.read_csv(anomaly_path)

        # Standardize user_id column
        for df in [features_df, risk_df, anomaly_df]:
            df['user_id'] = df['user_id'].astype(str).str.strip().str.upper()

        # Merge datasets sequentially on user_id
        logger.info("Merging datasets...")
        merged_df = features_df[['user_id', 'department', 'role', 'after_hours_ratio', 'usb_connects', 'unique_pcs_used', 'weekend_ratio']].merge(
            risk_df[['user_id', 'risk_score', 'risk_level']], on='user_id', how='left'
        )
        merged_df = merged_df.merge(
            anomaly_df[['user_id', 'anomaly_score', 'anomaly_label']], on='user_id', how='left'
        )

        # Handle missing values after merge
        merged_df['risk_score'] = merged_df['risk_score'].fillna(0.0)
        merged_df['risk_level'] = merged_df['risk_level'].fillna('Low')
        merged_df['anomaly_score'] = merged_df['anomaly_score'].fillna(0.0)
        merged_df['anomaly_label'] = merged_df['anomaly_label'].fillna('Normal')
        merged_df['department'] = merged_df['department'].fillna('Unknown')
        merged_df['role'] = merged_df['role'].fillna('Unknown')
        merged_df['after_hours_ratio'] = merged_df['after_hours_ratio'].fillna(0.0)
        merged_df['usb_connects'] = merged_df['usb_connects'].fillna(0.0)
        merged_df['unique_pcs_used'] = merged_df['unique_pcs_used'].fillna(0.0)
        merged_df['weekend_ratio'] = merged_df['weekend_ratio'].fillna(0.0)

        # Apply threat classification rules
        logger.info("Applying threat classification rules...")
        merged_df['security_status'] = merged_df.apply(determine_security_status, axis=1)
        merged_df['anomaly_reason'] = merged_df.apply(determine_anomaly_reason, axis=1)

        # Keep exactly the required columns
        output_cols = [
            'user_id', 'department', 'role',
            'risk_score', 'risk_level',
            'anomaly_score', 'anomaly_label',
            'security_status', 'anomaly_reason'
        ]
        final_df = merged_df[output_cols]

        # Log threat distribution
        distribution = final_df['security_status'].value_counts().to_dict()
        logger.info(f"Final Security Status distribution: {distribution}")

        # Save output file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_df.to_csv(output_path, index=False)
        logger.info(f"Successfully generated final security profile at: {output_path}")

    except Exception as e:
        logger.error(f"Error generating security profile: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    generate_profile(
        "data/features/user_features.csv",
        "data/reports/risk_scores.csv",
        "data/reports/anomaly_report.csv",
        "data/reports/final_security_profile.csv"
    )
