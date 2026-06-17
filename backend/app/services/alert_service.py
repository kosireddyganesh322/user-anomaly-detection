import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, users_df):
        self.alerts: List[Dict[str, Any]] = []
        self.generate_alerts(users_df)

    def generate_alerts(self, users_df) -> None:
        """
        Dynamically scans the consolidated users and features dataset,
        generating alert structures based on rules and levels.
        """
        if users_df.empty:
            self.alerts = []
            logger.warning("No users available to evaluate alert conditions.")
            return

        logger.info(f"Scanning {len(users_df)} user profiles for security events...")
        generated = []
        alert_id = 1

        # We evaluate rules sequentially per user
        for _, row in users_df.iterrows():
            user_id = row['user_id']
            name = row.get('name', 'Unknown')
            role = row.get('role', 'Unknown')
            risk_score = row.get('risk_score', 0.0)
            risk_level = row.get('risk_level', 'Low')
            anomaly_score = row.get('anomaly_score', 0.0)
            anomaly_label = row.get('anomaly_label', 'Normal')
            
            # Features (safe fetch using get to avoid KeyError)
            after_hours_logins = int(row.get('after_hours_logins', 0))
            after_hours_ratio = float(row.get('after_hours_ratio', 0.0))
            usb_connects = int(row.get('usb_connects', 0))
            after_hours_usb = int(row.get('after_hours_usb', 0))
            unique_pcs_used = int(row.get('unique_pcs_used', 0))

            # 1. CRITICAL RISK RULE
            if risk_level == 'Critical':
                generated.append({
                    'id': alert_id,
                    'user_id': user_id,
                    'name': name,
                    'alert_type': 'Critical Risk',
                    'severity': 'Critical',
                    'description': f"User {user_id} ({role}) evaluated with Critical risk level (Behavioral Score: {risk_score:.1f}).",
                    'created_at': "2026-06-17 08:30:00",
                    'acknowledged': False
                })
                alert_id += 1

            # 2. HIGH RISK RULE
            elif risk_level == 'High':
                generated.append({
                    'id': alert_id,
                    'user_id': user_id,
                    'name': name,
                    'alert_type': 'High Risk',
                    'severity': 'High',
                    'description': f"User {user_id} ({role}) evaluated with High risk level (Behavioral Score: {risk_score:.1f}).",
                    'created_at': "2026-06-17 08:45:00",
                    'acknowledged': False
                })
                alert_id += 1

            # 3. SUSPICIOUS ANOMALY RULE
            if anomaly_label == 'Suspicious':
                # Map severity based on risk level
                severity = 'High' if risk_level in ['Critical', 'High'] else 'Warning'
                generated.append({
                    'id': alert_id,
                    'user_id': user_id,
                    'name': name,
                    'alert_type': 'Suspicious Anomaly',
                    'severity': severity,
                    'description': f"Isolation Forest flagged user {user_id} ({role}) as Outlier (Anomaly Score: {anomaly_score:.4f}).",
                    'created_at': "2026-06-17 09:00:00",
                    'acknowledged': False
                })
                alert_id += 1

            # 4. EXCESSIVE AFTER-HOURS ACTIVITY RULE
            if after_hours_logins > 10 or after_hours_ratio > 0.25:
                generated.append({
                    'id': alert_id,
                    'user_id': user_id,
                    'name': name,
                    'alert_type': 'Excessive After-Hours Activity',
                    'severity': 'Warning',
                    'description': f"User {user_id} displays excessive off-hours logons ({after_hours_logins} logins, representing {after_hours_ratio:.1%} of events).",
                    'created_at': "2026-06-17 09:15:00",
                    'acknowledged': False
                })
                alert_id += 1

            # 5. EXCESSIVE USB ACTIVITY RULE
            if usb_connects > 15 or after_hours_usb > 4:
                generated.append({
                    'id': alert_id,
                    'user_id': user_id,
                    'name': name,
                    'alert_type': 'Excessive USB Activity',
                    'severity': 'Warning',
                    'description': f"User {user_id} displays excessive USB connect events ({usb_connects} connects, {after_hours_usb} off-hours connects).",
                    'created_at': "2026-06-17 09:20:00",
                    'acknowledged': False
                })
                alert_id += 1

            # 6. INFO LEVEL: MULTIPLE SYSTEMS ACCESS
            if unique_pcs_used > 3:
                generated.append({
                    'id': alert_id,
                    'user_id': user_id,
                    'name': name,
                    'alert_type': 'Multiple Endpoint Access',
                    'severity': 'Info',
                    'description': f"User {user_id} accessed system from {unique_pcs_used} unique terminal workstations.",
                    'created_at': "2026-06-17 09:25:00",
                    'acknowledged': False
                })
                alert_id += 1

        self.alerts = generated
        logger.info(f"Alert Engine initialization complete. Registered {len(self.alerts)} active alerts.")

    def get_alerts(
        self,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves in-memory alerts applying search, severity, and acknowledgment filters.
        """
        filtered = self.alerts

        if severity:
            filtered = [a for a in filtered if a['severity'].lower() == severity.lower()]

        if acknowledged is not None:
            filtered = [a for a in filtered if a['acknowledged'] == acknowledged]

        if search:
            search_term = search.lower().strip()
            filtered = [
                a for a in filtered
                if search_term in a['user_id'].lower()
                or search_term in a['name'].lower()
                or search_term in a['alert_type'].lower()
                or search_term in a['description'].lower()
            ]

        return filtered

    def acknowledge_alert(self, alert_id: int) -> bool:
        """
        Marks an alert as acknowledged in backend memory.
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                logger.info(f"Alert ID {alert_id} acknowledged for user {alert['user_id']}.")
                return True
        return False
