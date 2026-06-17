"""
Clean device.csv
Input : data/raw/device.csv
Output: data/cleaned/device_clean.csv

Columns expected: id, date, user, pc, file_tree, activity
Plus features: hour, day_of_week, month, is_weekend, is_after_hours
"""
import os
import logging
import pandas as pd

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_device(input_path: str, output_path: str) -> None:
    logger.info(f"Starting to clean device data from {input_path}")
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found at: {input_path}")

        # Load raw file
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} raw device records")

        # Drop rows with null values in critical fields (id, user, date)
        initial_len = len(df)
        df = df.dropna(subset=['id', 'user', 'date'])
        dropped_nulls = initial_len - len(df)
        if dropped_nulls > 0:
            logger.warning(f"Dropped {dropped_nulls} rows due to null id, user, or date")

        # Remove duplicates based on event id
        pre_dup_len = len(df)
        df = df.drop_duplicates(subset=['id'], keep='first')
        dropped_duplicates = pre_dup_len - len(df)
        if dropped_duplicates > 0:
            logger.info(f"Dropped {dropped_duplicates} duplicate event records")

        # Standardize user IDs (uppercase and stripped)
        df['user'] = df['user'].astype(str).str.strip().str.upper()
        df['id'] = df['id'].astype(str).str.strip()

        # Handle other columns missing values
        df['pc'] = df['pc'].fillna("Unknown").astype(str).str.strip()
        df['activity'] = df['activity'].fillna("Unknown").astype(str).str.strip().str.title()
        
        # Disconnect activity typically has null/NaN file_tree; fill with empty string
        df['file_tree'] = df['file_tree'].fillna("").astype(str).str.strip()

        # Parse date and convert timestamps
        logger.info("Parsing datetime field...")
        df['parsed_date'] = pd.to_datetime(df['date'], format='%m/%d/%Y %H:%M:%S', errors='coerce')
        
        # Handle rows with invalid timestamps
        invalid_dates = df['parsed_date'].isnull().sum()
        if invalid_dates > 0:
            logger.warning(f"Dropped {invalid_dates} rows with invalid dates")
            df = df.dropna(subset=['parsed_date'])

        # Create datetime features
        logger.info("Generating datetime features (hour, day_of_week, month, is_weekend, is_after_hours)...")
        df['hour'] = df['parsed_date'].dt.hour.astype(int)
        df['day_of_week'] = df['parsed_date'].dt.dayofweek.astype(int) # 0=Monday, 6=Sunday
        df['month'] = df['parsed_date'].dt.month.astype(int)
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Working hours defined as 08:00 - 18:00, Mon-Fri
        # After-hours is defined as weekend OR hour < 8 OR hour >= 18
        df['is_after_hours'] = ((df['day_of_week'] >= 5) | (df['hour'] < 8) | (df['hour'] >= 18)).astype(int)

        # Standardize date format to ISO string YYYY-MM-DD HH:MM:SS
        df['date'] = df['parsed_date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Select columns to output: standard event fields + created features
        output_cols = [
            'id', 'date', 'user', 'pc', 'file_tree', 'activity',
            'hour', 'day_of_week', 'month', 'is_weekend', 'is_after_hours'
        ]
        df = df[output_cols]

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save output
        logger.info("Saving cleaned device records...")
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved {len(df)} cleaned device records to {output_path}")

    except Exception as e:
        logger.error(f"Error cleaning device data: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    clean_device("data/raw/device.csv", "data/cleaned/device_clean.csv")
