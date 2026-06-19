import pandas as pd
from ml.risk_scoring.risk_rules import (
    score_after_hours_logins,
    score_unique_pcs_used,
    score_login_device_ratio,
)
from ml.prediction.generate_security_profile import (
    determine_security_status,
    determine_anomaly_reason,
)

def test_score_after_hours_logins():
    # Linear up to threshold (50)
    assert score_after_hours_logins(0) == 0.0
    assert score_after_hours_logins(25) == 50.0
    assert score_after_hours_logins(50) == 100.0
    assert score_after_hours_logins(100) == 100.0
    assert score_after_hours_logins(-10) == 0.0

def test_score_unique_pcs_used():
    assert score_unique_pcs_used(1) == 0.0
    assert score_unique_pcs_used(2) == 50.0
    assert score_unique_pcs_used(3) == 100.0
    assert score_unique_pcs_used(5) == 100.0

def test_score_login_device_ratio():
    # No USB connections -> 0.0
    assert score_login_device_ratio(0.5, 0) == 0.0
    # ratio < 1.0 -> 100.0
    assert score_login_device_ratio(0.8, 10) == 100.0
    # 1.0 <= ratio < 5.0 -> 50.0
    assert score_login_device_ratio(3.0, 10) == 50.0
    # ratio >= 5.0 -> 0.0
    assert score_login_device_ratio(6.0, 10) == 0.0

def test_determine_security_status():
    # Critical Risk + Suspicious -> Critical Threat
    row_critical = pd.Series({'risk_level': 'Critical', 'anomaly_label': 'Suspicious'})
    assert determine_security_status(row_critical) == 'Critical Threat'

    # High Risk + Suspicious -> High Threat
    row_high = pd.Series({'risk_level': 'High', 'anomaly_label': 'Suspicious'})
    assert determine_security_status(row_high) == 'High Threat'

    # Medium Risk + Suspicious -> Medium Threat
    row_med = pd.Series({'risk_level': 'Medium', 'anomaly_label': 'Suspicious'})
    assert determine_security_status(row_med) == 'Medium Threat'

    # Normal -> Normal
    row_normal = pd.Series({'risk_level': 'Critical', 'anomaly_label': 'Normal'})
    assert determine_security_status(row_normal) == 'Normal'

def test_determine_anomaly_reason():
    # Normal label
    row_norm = pd.Series({'anomaly_label': 'Normal'})
    assert determine_anomaly_reason(row_norm) == 'No Significant Anomalies Detected'

    # Elevated Off-Hours Logon Schedules
    row_offhours = pd.Series({
        'anomaly_label': 'Suspicious',
        'after_hours_ratio': 0.45,
        'usb_connects': 2,
        'unique_pcs_used': 1,
        'weekend_ratio': 0.05
    })
    assert 'Elevated Off-Hours Logon Schedules' in determine_anomaly_reason(row_offhours)

    # Suspicious USB Connection Ratios
    row_usb = pd.Series({
        'anomaly_label': 'Suspicious',
        'after_hours_ratio': 0.10,
        'usb_connects': 20,
        'unique_pcs_used': 1,
        'weekend_ratio': 0.05
    })
    assert 'Suspicious USB Connection Ratios' in determine_anomaly_reason(row_usb)

    # Rare / Unauthorized Endpoint Usage
    row_pcs = pd.Series({
        'anomaly_label': 'Suspicious',
        'after_hours_ratio': 0.10,
        'usb_connects': 2,
        'unique_pcs_used': 4,
        'weekend_ratio': 0.05
    })
    assert 'Rare / Unauthorized Endpoint Usage' in determine_anomaly_reason(row_pcs)

    # Multiple Behavioral Indicators
    row_multiple = pd.Series({
        'anomaly_label': 'Suspicious',
        'after_hours_ratio': 0.50,
        'usb_connects': 25,
        'unique_pcs_used': 4,
        'weekend_ratio': 0.15
    })
    reason = determine_anomaly_reason(row_multiple)
    assert 'Multiple Behavioral Indicators Detected' in reason
    assert 'Elevated Off-Hours Logon Schedules' in reason
    assert 'Suspicious USB Connection Ratios' in reason

