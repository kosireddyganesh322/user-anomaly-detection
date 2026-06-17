"""
Build per-user device activity features from cleaned device data.

Features:
  - usb_connects        : count of connect events
  - usb_disconnects     : count of disconnect events
  - after_hours_usb     : count of USB events outside standard hours
  - weekend_usb         : count of USB events on weekends
"""
import os
import logging
import pandas as pd
import numpy as np

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_device_features(device_path: str, output_path: str) -> None:
    logger.info(f"Starting to build device features from {device_path}")
    try:
        if not os.path.exists(device_path):
            raise FileNotFoundError(f"Input file not found at: {device_path}")

        # Load cleaned device logs
        df = pd.read_csv(device_path)
        logger.info(f"Loaded {len(df)} device records")

        if df.empty:
            logger.warning("Device records dataframe is empty. Creating empty features file.")
            empty_df = pd.DataFrame(columns=[
                'user_id', 'usb_connects', 'usb_disconnects',
                'after_hours_usb', 'weekend_usb'
            ])
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            empty_df.to_csv(output_path, index=False)
            return

        # Group operations
        logger.info("Computing user-level device aggregations...")
        
        # 1. Connects and Disconnects
        connects = df[df['activity'] == 'Connect'].groupby('user').size()
        disconnects = df[df['activity'] == 'Disconnect'].groupby('user').size()
        
        # 2. After-hours events
        after_hours_usb = df[df['is_after_hours'] == 1].groupby('user').size()
        
        # 3. Weekend events
        weekend_usb = df[df['is_weekend'] == 1].groupby('user').size()

        # Combine all features
        all_users = df['user'].unique()
        features_df = pd.DataFrame(index=all_users)
        features_df.index.name = 'user_id'

        features_df['usb_connects'] = features_df.index.map(connects).fillna(0).astype(int)
        features_df['usb_disconnects'] = features_df.index.map(disconnects).fillna(0).astype(int)
        features_df['after_hours_usb'] = features_df.index.map(after_hours_usb).fillna(0).astype(int)
        features_df['weekend_usb'] = features_df.index.map(weekend_usb).fillna(0).astype(int)

        # Reset index to make user_id a column
        features_df = features_df.reset_index()

        # Save to features path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        features_df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved {len(features_df)} user device features to {output_path}")

    except Exception as e:
        logger.error(f"Error creating device features: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    create_device_features(
        "data/cleaned/device_clean.csv",
        "data/features/device_features.csv"
    )
