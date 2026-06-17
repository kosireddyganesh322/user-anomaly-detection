"""
Build per-user login behaviour features from cleaned logon data.

Features:
  - total_logins          : count of logon events
  - total_logoffs         : count of logoff events
  - active_days           : count of unique days active
  - avg_logins_per_day    : total_logins / active_days
  - unique_pcs_used       : distinct machines logged into
  - after_hours_logins    : logon events outside standard hours
  - weekend_logins        : logon events on weekends
"""
import os
import logging
import pandas as pd
import numpy as np

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_login_features(logon_path: str, output_path: str) -> None:
    logger.info(f"Starting to build login features from {logon_path}")
    try:
        if not os.path.exists(logon_path):
            raise FileNotFoundError(f"Input file not found at: {logon_path}")

        # Load cleaned logon logs
        df = pd.read_csv(logon_path)
        logger.info(f"Loaded {len(df)} logon records")

        if df.empty:
            logger.warning("Logon records dataframe is empty. Creating empty features file.")
            empty_df = pd.DataFrame(columns=[
                'user_id', 'total_logins', 'total_logoffs', 'active_days',
                'avg_logins_per_day', 'unique_pcs_used', 'after_hours_logins', 'weekend_logins'
            ])
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            empty_df.to_csv(output_path, index=False)
            return

        # Extract date-only part for active days calculation
        df['date_only'] = pd.to_datetime(df['date']).dt.date

        # Group operations
        logger.info("Computing user-level aggregations...")
        
        # 1. Total Logins and Logoffs
        logins = df[df['activity'] == 'Logon'].groupby('user').size()
        logoffs = df[df['activity'] == 'Logoff'].groupby('user').size()
        
        # 2. Active Days
        active_days = df.groupby('user')['date_only'].nunique()
        
        # 3. Unique PCs used
        unique_pcs = df.groupby('user')['pc'].nunique()
        
        # 4. After-hours logins
        after_hours_logins = df[(df['activity'] == 'Logon') & (df['is_after_hours'] == 1)].groupby('user').size()
        
        # 5. Weekend logins
        weekend_logins = df[(df['activity'] == 'Logon') & (df['is_weekend'] == 1)].groupby('user').size()

        # Combine all features
        all_users = df['user'].unique()
        features_df = pd.DataFrame(index=all_users)
        features_df.index.name = 'user_id'

        features_df['total_logins'] = features_df.index.map(logins).fillna(0).astype(int)
        features_df['total_logoffs'] = features_df.index.map(logoffs).fillna(0).astype(int)
        features_df['active_days'] = features_df.index.map(active_days).fillna(0).astype(int)
        
        # Calculate average logins per day, handling division by zero
        features_df['avg_logins_per_day'] = np.where(
            features_df['active_days'] > 0,
            features_df['total_logins'] / features_df['active_days'],
            0.0
        )
        
        features_df['unique_pcs_used'] = features_df.index.map(unique_pcs).fillna(0).astype(int)
        features_df['after_hours_logins'] = features_df.index.map(after_hours_logins).fillna(0).astype(int)
        features_df['weekend_logins'] = features_df.index.map(weekend_logins).fillna(0).astype(int)

        # Reset index to make user_id a column
        features_df = features_df.reset_index()

        # Save to features path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        features_df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved {len(features_df)} user login features to {output_path}")

    except Exception as e:
        logger.error(f"Error creating login features: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    create_login_features(
        "data/cleaned/logon_clean.csv",
        "data/features/login_features.csv"
    )
