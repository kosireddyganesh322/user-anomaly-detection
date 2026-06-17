"""
Clean users.csv
Input : data/raw/users.csv
Output: data/cleaned/users_clean.csv

Columns expected: user_id, name, email, role, department, start_date
"""
import os
import logging
import pandas as pd

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_users(input_path: str, output_path: str) -> None:
    logger.info(f"Starting to clean users data from {input_path}")
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found at: {input_path}")

        # Load raw file
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} raw user records")

        # Rename columns if needed
        # raw columns: employee_name, user_id, email, role, projects, business_unit, functional_unit, department, team, supervisor, start_date, end_date
        if 'employee_name' in df.columns:
            df = df.rename(columns={'employee_name': 'name'})

        # Drop rows where critical identifier user_id is missing
        initial_len = len(df)
        df = df.dropna(subset=['user_id'])
        dropped_null_ids = initial_len - len(df)
        if dropped_null_ids > 0:
            logger.warning(f"Dropped {dropped_null_ids} rows due to null user_id")

        # Standardize user IDs (uppercase and stripped)
        df['user_id'] = df['user_id'].astype(str).str.strip().str.upper()

        # Remove duplicates based on user_id
        pre_dup_len = len(df)
        df = df.drop_duplicates(subset=['user_id'], keep='first')
        dropped_duplicates = pre_dup_len - len(df)
        if dropped_duplicates > 0:
            logger.info(f"Dropped {dropped_duplicates} duplicate user_id records")

        # Handle missing values in other fields
        for col in ['name', 'email', 'role', 'department']:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown").astype(str).str.strip()
            else:
                logger.warning(f"Column '{col}' not found in raw data, filling with 'Unknown'")
                df[col] = "Unknown"

        # Convert start_date to datetime and format as date (%Y-%m-%d)
        if 'start_date' in df.columns:
            df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
            # Handle any rows where start_date is invalid
            invalid_dates = df['start_date'].isnull().sum()
            if invalid_dates > 0:
                logger.warning(f"Found {invalid_dates} invalid/null start_date values, filling with default '1970-01-01'")
                df['start_date'] = df['start_date'].fillna(pd.Timestamp('1970-01-01'))
            df['start_date'] = df['start_date'].dt.strftime('%Y-%m-%d')
        else:
            logger.error("Column 'start_date' not found in users raw data")
            raise KeyError("start_date column is missing")

        # Keep only expected database columns
        expected_cols = ['user_id', 'name', 'email', 'role', 'department', 'start_date']
        df = df[expected_cols]

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save output
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved {len(df)} cleaned user records to {output_path}")

    except Exception as e:
        logger.error(f"Error cleaning users: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Get current working directory and adjust paths if needed
    clean_users("data/raw/users.csv", "data/cleaned/users_clean.csv")
