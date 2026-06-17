"""
Define risk categories and their numerical boundaries.

Risk Levels:
  0-25   = Low
  26-50  = Medium
  51-75  = High
  76-100 = Critical
"""
import logging

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants defining risk level thresholds
LOW_MAX = 25
MEDIUM_MAX = 50
HIGH_MAX = 75

def get_risk_level(score: float) -> str:
    """
    Return the corresponding risk level string for a given score between 0 and 100.
    """
    try:
        # Standardise and clamp input score to [0, 100] range
        clamped_score = max(0.0, min(100.0, float(score)))

        if clamped_score <= LOW_MAX:
            return "Low"
        elif clamped_score <= MEDIUM_MAX:
            return "Medium"
        elif clamped_score <= HIGH_MAX:
            return "High"
        else:
            return "Critical"

    except Exception as e:
        logger.error(f"Error mapping score {score} to risk level: {e}")
        return "Unknown"
