"""
Define configurable sub-scoring rules, weights, and normalization configurations.

Weighted scoring based on:
  - after_hours_logins  : Weight = 0.20
  - weekend_logins      : Weight = 0.15
  - unique_pcs_used     : Weight = 0.15
  - usb_connects        : Weight = 0.15
  - after_hours_usb     : Weight = 0.20
  - login_device_ratio  : Weight = 0.15
"""
import logging

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurable Weights (Must sum to 1.0 for normalized score mapping)
WEIGHTS = {
    'after_hours_logins': 0.20,
    'weekend_logins': 0.15,
    'unique_pcs_used': 0.15,
    'usb_connects': 0.15,
    'after_hours_usb': 0.20,
    'login_device_ratio': 0.15
}

# Configurable Thresholds for sub-scoring rules
THRESHOLDS = {
    'after_hours_logins_max': 50,    # Max count for 100 points
    'weekend_logins_max': 10,        # Max count for 100 points
    'usb_connects_max': 100,         # Max count for 100 points
    'after_hours_usb_max': 20,       # Max count for 100 points
}

def score_after_hours_logins(count: float) -> float:
    """
    Score after hours logins linearly up to a threshold.
    """
    max_val = THRESHOLDS['after_hours_logins_max']
    return min(max(0.0, float(count)) / max_val, 1.0) * 100.0

def score_weekend_logins(count: float) -> float:
    """
    Score weekend logins linearly up to a threshold.
    """
    max_val = THRESHOLDS['weekend_logins_max']
    return min(max(0.0, float(count)) / max_val, 1.0) * 100.0

def score_unique_pcs_used(count: float) -> float:
    """
    Score unique PCs used:
      - 1 PC      = 0 points (Standard behavior)
      - 2 PCs     = 50 points (Slightly elevated risk)
      - >=3 PCs   = 100 points (High risk / moving around PCs)
    """
    c = int(count)
    if c <= 1:
        return 0.0
    elif c == 2:
        return 50.0
    else:
        return 100.0

def score_usb_connects(count: float) -> float:
    """
    Score USB connects linearly up to a threshold.
    """
    max_val = THRESHOLDS['usb_connects_max']
    return min(max(0.0, float(count)) / max_val, 1.0) * 100.0

def score_after_hours_usb(count: float) -> float:
    """
    Score after hours USB connects linearly up to a threshold.
    """
    max_val = THRESHOLDS['after_hours_usb_max']
    return min(max(0.0, float(count)) / max_val, 1.0) * 100.0

def score_login_device_ratio(ratio: float, usb_connects: float) -> float:
    """
    Score login-to-device ratio.
    A low ratio (e.g. less than 1.0) indicates high device connect rate relative
    to logons, representing higher data copying risk.
      - If no USB connections were made: 0 points (No risk)
      - If ratio < 1.0 (Connects > Logins): 100 points (Elevated copying threat)
      - If 1.0 <= ratio < 5.0: 50 points (Moderate copying rate)
      - If ratio >= 5.0 (Standard/low copying rate): 0 points
    """
    if usb_connects <= 0:
        return 0.0
    
    r = float(ratio)
    if r < 1.0:
        return 100.0
    elif r < 5.0:
        return 50.0
    else:
        return 0.0

# Registry mapping features to scoring function handles
RULE_REGISTRY = {
    'after_hours_logins': score_after_hours_logins,
    'weekend_logins': score_weekend_logins,
    'unique_pcs_used': score_unique_pcs_used,
    'usb_connects': score_usb_connects,
    'after_hours_usb': score_after_hours_usb,
}
