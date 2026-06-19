"""
Merge all per-user feature tables and registries into one master feature matrix.

Inputs:
  - data/cleaned/users_clean.csv
  - data/cleaned/ldap_clean.csv
  - data/features/login_features.csv
  - data/features/device_features.csv
  - data/raw/users.csv (to extract raw 'team' attribute)

Output: data/features/user_features.csv
"""
import os
import logging
import pandas as pd
import numpy as np

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def merge_features(
    output_path: str,
    users_clean_path: str = "data/cleaned/users_clean.csv",
    ldap_clean_path: str = "data/cleaned/ldap_clean.csv",
    login_features_path: str = "data/features/login_features.csv",
    device_features_path: str = "data/features/device_features.csv",
    raw_users_path: str = "data/raw/users.csv"
) -> None:
    logger.info("Starting master feature merging pipeline")
    try:

        # Check required files
        for path in [users_clean_path, login_features_path, device_features_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Required features file missing: {path}")

        # 1. Load users_clean.csv as master registry
        logger.info(f"Loading master users registry from {users_clean_path}")
        users_df = pd.read_csv(users_clean_path)
        # Standardize user_id
        users_df['user_id'] = users_df['user_id'].astype(str).str.strip().str.upper()

        # 2. Extract 'team' column from raw users.csv
        logger.info(f"Extracting 'team' from raw user data: {raw_users_path}")
        if os.path.exists(raw_users_path):
            raw_df = pd.read_csv(raw_users_path)
            raw_df['user_id'] = raw_df['user_id'].astype(str).str.strip().str.upper()
            if 'team' not in raw_df.columns:
                raw_df['team'] = "Unknown"
            team_mapping = raw_df[['user_id', 'team']].drop_duplicates(subset=['user_id'])
            # Merge team mapping to users registry
            users_df = users_df.merge(team_mapping, on='user_id', how='left')
        else:
            logger.warning(f"Raw users file {raw_users_path} not found. Filling team with 'Unknown'")
            users_df['team'] = "Unknown"

        # 3. Load and merge LDAP clean info (useful if we want to fallback or cross-reference)
        # Since role, department are already in users_clean.csv, we can join LDAP department or supervisor.
        # Let's check if ldap_clean.csv exists
        if os.path.exists(ldap_clean_path):
            logger.info(f"Loading LDAP info from {ldap_clean_path}")
            ldap_df = pd.read_csv(ldap_clean_path)
            ldap_df['user_id'] = ldap_df['user_id'].astype(str).str.strip().str.upper()
            # If we want to capture supervisor/manager or title from LDAP:
            ldap_subset = ldap_df[['user_id', 'manager']].drop_duplicates(subset=['user_id'])
            users_df = users_df.merge(ldap_subset, on='user_id', how='left')
        else:
            logger.warning(f"Cleaned LDAP info {ldap_clean_path} not found. Filling manager with 'Unknown'")
            users_df['manager'] = "Unknown"

        # 4. Merge login features
        logger.info(f"Loading and merging login features from {login_features_path}")
        login_df = pd.read_csv(login_features_path)
        login_df['user_id'] = login_df['user_id'].astype(str).str.strip().str.upper()
        users_df = users_df.merge(login_df, on='user_id', how='left')

        # 5. Merge device features
        logger.info(f"Loading and merging device features from {device_features_path}")
        device_df = pd.read_csv(device_features_path)
        device_df['user_id'] = device_df['user_id'].astype(str).str.strip().str.upper()
        users_df = users_df.merge(device_df, on='user_id', how='left')

        # 6. Fill missing values
        logger.info("Handling missing values for non-active users...")
        
        # Categoricals fill with 'Unknown'
        categorical_cols = ['name', 'email', 'role', 'department', 'team', 'manager']
        for col in categorical_cols:
            if col in users_df.columns:
                users_df[col] = users_df[col].fillna("Unknown").astype(str).str.strip()

        # Numericals fill with 0
        numerical_cols = [
            'total_logins', 'total_logoffs', 'active_days', 'avg_logins_per_day',
            'unique_pcs_used', 'after_hours_logins', 'weekend_logins',
            'usb_connects', 'usb_disconnects', 'after_hours_usb', 'weekend_usb'
        ]
        for col in numerical_cols:
            if col in users_df.columns:
                users_df[col] = users_df[col].fillna(0)
                # Cast counts to integers
                if col not in ['avg_logins_per_day']:
                    users_df[col] = users_df[col].astype(int)

        # 7. Compute Behavior Features
        logger.info("Computing behavioral ratio features...")
        # login_device_ratio = total_logins / usb_connects (default to 0.0 if connect count is 0)
        users_df['login_device_ratio'] = np.where(
            users_df['usb_connects'] > 0,
            users_df['total_logins'] / users_df['usb_connects'],
            0.0
        )

        # total_events = total_logins + usb_connects
        total_events = users_df['total_logins'] + users_df['usb_connects']

        # after_hours_ratio = (after_hours_logins + after_hours_usb) / total_events
        users_df['after_hours_ratio'] = np.where(
            total_events > 0,
            (users_df['after_hours_logins'] + users_df['after_hours_usb']) / total_events,
            0.0
        )

        # weekend_ratio = (weekend_logins + weekend_usb) / total_events
        users_df['weekend_ratio'] = np.where(
            total_events > 0,
            (users_df['weekend_logins'] + users_df['weekend_usb']) / total_events,
            0.0
        )

        # 8. Reorder and select the output columns to match specifications
        # User Features: department, role, team
        # Login Features: total_logins, total_logoffs, active_days, avg_logins_per_day, unique_pcs_used, after_hours_logins, weekend_logins
        # Device Features: usb_connects, usb_disconnects, after_hours_usb, weekend_usb
        # Behavior Features: login_device_ratio, after_hours_ratio, weekend_ratio
        # Identifiers: user_id, name, email, manager
        output_cols = [
            'user_id', 'name', 'email', 'role', 'department', 'team', 'manager',
            'total_logins', 'total_logoffs', 'active_days', 'avg_logins_per_day', 'unique_pcs_used', 'after_hours_logins', 'weekend_logins',
            'usb_connects', 'usb_disconnects', 'after_hours_usb', 'weekend_usb',
            'login_device_ratio', 'after_hours_ratio', 'weekend_ratio'
        ]
        
        # Ensure only columns present in users_df are exported, keeping ordering
        output_cols = [col for col in output_cols if col in users_df.columns]
        users_df = users_df[output_cols]

        # Save merged dataframe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        users_df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved {len(users_df)} user feature rows to {output_path}")

        # Also save to master_features.csv for backward compatibility
        compat_path = output_path.replace("user_features.csv", "master_features.csv")
        users_df.to_csv(compat_path, index=False)
        logger.info(f"Saved duplicate compatibility master features copy to {compat_path}")

    except Exception as e:
        logger.error(f"Error merging features: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    merge_features("data/features/user_features.csv")
