"""
Clean LDAP.csv
Input : data/raw/ldap/2011-05.csv (snapshot)
Output: data/cleaned/ldap_clean.csv

Columns expected: user_id, department, title, manager
"""
import os
import logging
import pandas as pd

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_ldap(input_path: str, output_path: str) -> None:
    logger.info(f"Starting to clean LDAP data from {input_path}")
    try:
        # Resolve case sensitivity or paths for LDAP
        # In raw, directory could be 'LDAP' or 'ldap'. Let's try both to be safe.
        if not os.path.exists(input_path):
            alternative_path = input_path.replace("/ldap/", "/LDAP/")
            if os.path.exists(alternative_path):
                logger.info(f"Input path {input_path} not found, falling back to alternative: {alternative_path}")
                input_path = alternative_path
            else:
                raise FileNotFoundError(f"Input file not found at: {input_path}")

        # Load raw file
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} raw LDAP records")

        # Drop rows where user_id is missing
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

        # Merge department hierarchy
        # business_unit, functional_unit, department, team
        def merge_dept(row):
            parts = []
            for col in ['business_unit', 'functional_unit', 'department', 'team']:
                if col in row and pd.notna(row[col]):
                    val_str = str(row[col]).strip()
                    if val_str:
                        parts.append(val_str)
            return " / ".join(parts) if parts else "Unknown"

        df['merged_department'] = df.apply(merge_dept, axis=1)

        # Map and rename other columns
        # raw columns: employee_name, user_id, email, role, projects, business_unit, functional_unit, department, team, supervisor
        rename_map = {}
        if 'role' in df.columns:
            rename_map['role'] = 'title'
        if 'supervisor' in df.columns:
            rename_map['supervisor'] = 'manager'
        
        df = df.rename(columns=rename_map)

        # If manager or title columns are missing, fill them with "Unknown"
        for col in ['title', 'manager']:
            if col not in df.columns:
                logger.warning(f"Column '{col}' not found in raw data, filling with 'Unknown'")
                df[col] = "Unknown"
            else:
                df[col] = df[col].fillna("Unknown").astype(str).str.strip()

        # Place the merged department into 'department'
        df['department'] = df['merged_department']

        # Keep only expected columns
        expected_cols = ['user_id', 'department', 'title', 'manager']
        df = df[expected_cols]

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save output
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved {len(df)} cleaned LDAP records to {output_path}")

    except Exception as e:
        logger.error(f"Error cleaning LDAP: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    clean_ldap("data/raw/ldap/2011-05.csv", "data/cleaned/ldap_clean.csv")
