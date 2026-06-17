"""
Data Service Layer
Loads consolidated security reports and clean logon/device event files,
providing memory-efficient querying and caching of analytics trends.
"""
import os
import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from backend.app.services.alert_service import AlertService

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.users_df = pd.DataFrame()
        self.login_trends_data: List[Dict[str, Any]] = []
        self.device_trends_data: List[Dict[str, Any]] = []
        self.alerts_list: List[Dict[str, Any]] = []
        self.load_data()

    def load_data(self) -> None:
        logger.info("Initializing Data Service data layers...")
        try:
            # Paths to master reports
            profile_path = "../data/reports/final_security_profile.csv"
            features_path = "../data/features/user_features.csv"
            
            # Since the backend directory runs from user-anomaly-detection/backend/,
            # relative paths to data are standard relative to the backend workspace root.
            # Let's adjust paths if they don't exist
            if not os.path.exists(profile_path):
                profile_path = "data/reports/final_security_profile.csv"
                features_path = "data/features/user_features.csv"
                
            if os.path.exists(profile_path) and os.path.exists(features_path):
                logger.info(f"Loading user profile metadata from {profile_path}")
                profile_df = pd.read_csv(profile_path)
                features_df = pd.read_csv(features_path)
                
                # Standardize keys
                profile_df['user_id'] = profile_df['user_id'].astype(str).str.strip().str.upper()
                features_df['user_id'] = features_df['user_id'].astype(str).str.strip().str.upper()
                
                # Merge profile and user details (including all features)
                logger.info("Merging user profiles and features...")
                dup_cols = [c for c in features_df.columns if c in profile_df.columns and c != 'user_id']
                features_subset = features_df.drop(columns=dup_cols)
                
                self.users_df = features_subset.merge(profile_df, on='user_id', how='right')
                logger.info(f"Loaded {len(self.users_df)} consolidated user security profiles")
            else:
                logger.warning("Warning: profile or feature CSV files not found. Initializing empty user profiles list.")
                self.users_df = pd.DataFrame(columns=[
                    'user_id', 'name', 'email', 'role', 'department', 'team', 'manager',
                    'risk_score', 'risk_level', 'anomaly_score', 'anomaly_label', 'security_status'
                ])

            # Pre-compute login trends
            logon_clean_path = "../data/cleaned/logon_clean.csv"
            if not os.path.exists(logon_clean_path):
                logon_clean_path = "data/cleaned/logon_clean.csv"

            if os.path.exists(logon_clean_path):
                logger.info(f"Pre-computing login trends from {logon_clean_path}...")
                logon_df = pd.read_csv(logon_clean_path)
                logon_df['day'] = logon_df['date'].str[:10]
                trends = logon_df[logon_df['activity'] == 'Logon'].groupby('day').size().reset_index(name='count')
                trends = trends.sort_values('day')
                self.login_trends_data = trends.to_dict(orient='records')
                logger.info(f"Cached {len(self.login_trends_data)} days of login trends")
                del logon_df # Free memory
            else:
                logger.warning(f"Cleaned logon file {logon_clean_path} not found. Login trends are unavailable.")

            # Pre-compute device trends
            device_clean_path = "../data/cleaned/device_clean.csv"
            if not os.path.exists(device_clean_path):
                device_clean_path = "data/cleaned/device_clean.csv"

            if os.path.exists(device_clean_path):
                logger.info(f"Pre-computing device trends from {device_clean_path}...")
                device_df = pd.read_csv(device_clean_path)
                device_df['day'] = device_df['date'].str[:10]
                trends = device_df[device_df['activity'] == 'Connect'].groupby('day').size().reset_index(name='count')
                trends = trends.sort_values('day')
                self.device_trends_data = trends.to_dict(orient='records')
                logger.info(f"Cached {len(self.device_trends_data)} days of device trends")
                del device_df # Free memory
            else:
                logger.warning(f"Cleaned device file {device_clean_path} not found. Device trends are unavailable.")

            # Initialize the dedicated alert service engine
            self.alert_service = AlertService(self.users_df)

        except Exception as e:
            logger.error(f"Error loading backend service data: {e}", exc_info=True)

    def generate_alerts(self) -> None:
        """
        Generate mock active alerts from suspicious users list.
        """
        if self.users_df.empty:
            self.alerts_list = []
            return
            
        suspicious_df = self.users_df[self.users_df['anomaly_label'] == 'Suspicious']
        logger.info(f"Generating active alerts for {len(suspicious_df)} suspicious users")
        
        alerts = []
        for i, (_, row) in enumerate(suspicious_df.iterrows()):
            alert = {
                'id': i + 1,
                'user_id': row['user_id'],
                'name': row['name'],
                'alert_type': 'Suspicious Behavior',
                'severity': 'Critical' if row['risk_level'] in ['Critical', 'High'] else 'Medium',
                'description': f"Isolation Forest flagged user {row['user_id']} ({row['role']}) as Suspicious with risk score {row['risk_score']} ({row['risk_level']} risk level).",
                'created_at': "2026-06-17 00:00:00",
                'acknowledged': False
            }
            alerts.append(alert)
        self.alerts_list = alerts

    def get_dashboard_overview(self) -> Dict[str, Any]:
        if self.users_df.empty:
            return {
                "total_users": 0,
                "anomalies_detected": 0,
                "high_risk_users": 0,
                "critical_users": 0,
                "total_alerts": 0,
                "pending_alerts": 0,
                "critical_alerts": 0,
                "high_alerts": 0,
                "warning_alerts": 0,
                "info_alerts": 0
            }
            
        all_alerts = self.alert_service.alerts
        return {
            "total_users": int(len(self.users_df)),
            "anomalies_detected": int(sum(self.users_df['anomaly_label'] == 'Suspicious')),
            "high_risk_users": int(sum(self.users_df['risk_level'] == 'High')),
            "critical_users": int(sum(self.users_df['risk_level'] == 'Critical')),
            "total_alerts": int(len(all_alerts)),
            "pending_alerts": int(sum(not a['acknowledged'] for a in all_alerts)),
            "critical_alerts": int(sum(a['severity'] == 'Critical' for a in all_alerts)),
            "high_alerts": int(sum(a['severity'] == 'High' for a in all_alerts)),
            "warning_alerts": int(sum(a['severity'] == 'Warning' for a in all_alerts)),
            "info_alerts": int(sum(a['severity'] == 'Info' for a in all_alerts))
        }

    def get_users(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        department: Optional[str] = None,
        risk_level: Optional[str] = None,
        anomaly_label: Optional[str] = None,
        security_status: Optional[str] = None
    ) -> Dict[str, Any]:
        if self.users_df.empty:
            return {"users": [], "total": 0, "page": page, "limit": limit}

        df = self.users_df.copy()

        # Apply search
        if search:
            search_str = search.lower()
            df = df[
                df['user_id'].str.lower().str.contains(search_str) |
                df['name'].str.lower().str.contains(search_str) |
                df['role'].str.lower().str.contains(search_str)
            ]

        # Apply filters
        if department:
            df = df[df['department'] == department]
        if risk_level:
            df = df[df['risk_level'] == risk_level]
        if anomaly_label:
            df = df[df['anomaly_label'] == anomaly_label]
        if security_status:
            df = df[df['security_status'] == security_status]

        total = len(df)

        # Apply paging
        start = (page - 1) * limit
        end = start + limit
        paginated_df = df.iloc[start:end]

        return {
            "users": paginated_df.to_dict(orient='records'),
            "total": total,
            "page": page,
            "limit": limit
        }

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if self.users_df.empty:
            return None
            
        uid = user_id.strip().upper()
        user_rows = self.users_df[self.users_df['user_id'] == uid]
        if user_rows.empty:
            return None
        return user_rows.iloc[0].to_dict()

    def get_anomalies(self) -> List[Dict[str, Any]]:
        if self.users_df.empty:
            return []
        return self.users_df[self.users_df['anomaly_label'] == 'Suspicious'].to_dict(orient='records')

    def get_high_risk_anomalies(self) -> List[Dict[str, Any]]:
        if self.users_df.empty:
            return []
        subset = self.users_df[
            (self.users_df['anomaly_label'] == 'Suspicious') &
            (self.users_df['risk_level'].isin(['High', 'Critical']))
        ]
        return subset.to_dict(orient='records')

    def get_risk_distribution(self) -> Dict[str, int]:
        if self.users_df.empty:
            return {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
            
        counts = self.users_df['risk_level'].value_counts().to_dict()
        return {level: counts.get(level, 0) for level in ['Low', 'Medium', 'High', 'Critical']}

    def get_login_trends(self) -> List[Dict[str, Any]]:
        return self.login_trends_data

    def get_device_trends(self) -> List[Dict[str, Any]]:
        return self.device_trends_data

    def get_department_summary(self) -> List[Dict[str, Any]]:
        if self.users_df.empty:
            return []
            
        summary = self.users_df.groupby('department').agg(
            total_users=('user_id', 'count'),
            anomalies=('anomaly_label', lambda x: int(sum(x == 'Suspicious')))
        ).reset_index()
        return summary.to_dict(orient='records')

    def get_alerts(
        self,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return self.alert_service.get_alerts(severity=severity, acknowledged=acknowledged, search=search)

    def acknowledge_alert(self, alert_id: int) -> bool:
        return self.alert_service.acknowledge_alert(alert_id)
