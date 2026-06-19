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
        self.current_dataset = "CERT"
        self.load_data()

    def switch_dataset(self, dataset_name: str) -> None:
        logger.info(f"Switching active dataset to: {dataset_name}")
        self.current_dataset = dataset_name
        self.load_data()

    def load_data(self) -> None:
        logger.info(f"Initializing Data Service data layers for dataset: {self.current_dataset}...")
        try:
            # Determine base path for the current dataset
            if self.current_dataset == "CERT":
                # Check if CERT is stored under datasets/CERT
                cert_path = "data/datasets/CERT"
                if os.path.exists(os.path.join(cert_path, "reports/final_security_profile.csv")):
                    base_dataset_dir = cert_path
                elif os.path.exists(os.path.join("..", cert_path, "reports/final_security_profile.csv")):
                    base_dataset_dir = os.path.join("..", cert_path)
                else:
                    # Fallback to legacy root paths for backward compatibility
                    base_dataset_dir = "data"
            else:
                base_dataset_dir = f"data/datasets/{self.current_dataset}"

            # Paths to master reports
            profile_path = os.path.join(base_dataset_dir, "reports/final_security_profile.csv")
            features_path = os.path.join(base_dataset_dir, "features/user_features.csv")
            
            # Since the backend directory runs from user-anomaly-detection/backend/,
            # relative paths to data are standard relative to the backend workspace root.
            # Let's adjust paths if they don't exist
            if not os.path.exists(profile_path) and os.path.exists(os.path.join("..", profile_path)):
                profile_path = os.path.join("..", profile_path)
                features_path = os.path.join("..", features_path)
                
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
                
                # Recalculate security status and anomaly reasons dynamically to ensure consistency
                from ml.prediction.generate_security_profile import determine_anomaly_reason, determine_security_status
                self.users_df['security_status'] = self.users_df.apply(determine_security_status, axis=1)
                self.users_df['anomaly_reason'] = self.users_df.apply(determine_anomaly_reason, axis=1)
                
                logger.info(f"Loaded {len(self.users_df)} consolidated user security profiles")
            else:
                logger.warning(f"Warning: profile or feature CSV files not found at {profile_path}. Initializing empty user profiles list.")
                self.users_df = pd.DataFrame(columns=[
                    'user_id', 'name', 'email', 'role', 'department', 'team', 'manager',
                    'risk_score', 'risk_level', 'anomaly_score', 'anomaly_label', 'security_status',
                    'anomaly_reason'
                ])

            # Pre-compute login trends
            logon_clean_path = os.path.join(base_dataset_dir, "cleaned/logon_clean.csv")
            if not os.path.exists(logon_clean_path) and os.path.exists(os.path.join("..", logon_clean_path)):
                logon_clean_path = os.path.join("..", logon_clean_path)

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
                self.login_trends_data = []

            # Pre-compute device trends
            device_clean_path = os.path.join(base_dataset_dir, "cleaned/device_clean.csv")
            if not os.path.exists(device_clean_path) and os.path.exists(os.path.join("..", device_clean_path)):
                device_clean_path = os.path.join("..", device_clean_path)

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
                self.device_trends_data = []

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

    def acknowledge_all_alerts(self) -> int:
        return self.alert_service.acknowledge_all_alerts()

    def get_top_risk_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        if self.users_df.empty:
            return []
        sorted_df = self.users_df.sort_values(by='risk_score', ascending=False)
        return sorted_df.head(limit).to_dict(orient='records')

    def get_department_risk_ranking(self) -> List[Dict[str, Any]]:
        if self.users_df.empty:
            return []
        
        dept_group = self.users_df.groupby('department')
        ranking = []
        for dept_name, group in dept_group:
            avg_risk = float(group['risk_score'].mean())
            suspicious_count = int((group['anomaly_label'] == 'Suspicious').sum())
            high_count = int((group['risk_level'] == 'High').sum())
            critical_count = int((group['risk_level'] == 'Critical').sum())
            ranking.append({
                'department': dept_name,
                'avg_risk_score': round(avg_risk, 2),
                'suspicious_users': suspicious_count,
                'high_risk_users': high_count,
                'critical_users': critical_count
            })
        
        ranking.sort(key=lambda x: x['avg_risk_score'], reverse=True)
        return ranking

    def get_anomaly_reason_breakdown(self) -> Dict[str, int]:
        breakdown = {
            "Elevated Off-Hours Logon Schedules": 0,
            "Suspicious USB Connection Ratios": 0,
            "Rare Endpoint Usage": 0,
            "Weekend Activity Anomaly": 0,
            "Multiple Behavioral Indicators": 0,
            "No Significant Anomalies": 0
        }
        if self.users_df.empty:
            return breakdown
            
        for reason in self.users_df['anomaly_reason'].fillna(''):
            if "No Significant" in reason:
                breakdown["No Significant Anomalies"] += 1
            elif "Multiple" in reason:
                breakdown["Multiple Behavioral Indicators"] += 1
                if "Off-Hours" in reason:
                    breakdown["Elevated Off-Hours Logon Schedules"] += 1
                if "USB" in reason:
                    breakdown["Suspicious USB Connection Ratios"] += 1
                if "Endpoint" in reason or "PC" in reason:
                    breakdown["Rare Endpoint Usage"] += 1
                if "Weekend" in reason:
                    breakdown["Weekend Activity Anomaly"] += 1
            else:
                if "Off-Hours" in reason:
                    breakdown["Elevated Off-Hours Logon Schedules"] += 1
                elif "USB" in reason:
                    breakdown["Suspicious USB Connection Ratios"] += 1
                elif "Endpoint" in reason or "PC" in reason:
                    breakdown["Rare Endpoint Usage"] += 1
                elif "Weekend" in reason:
                    breakdown["Weekend Activity Anomaly"] += 1
                else:
                    breakdown["No Significant Anomalies"] += 1
                    
        return breakdown

    def get_threat_heatmap(self) -> List[Dict[str, Any]]:
        if self.users_df.empty:
            return []
            
        departments = sorted(self.users_df['department'].dropna().unique())
        heatmap_data = []
        for dept in departments:
            dept_df = self.users_df[self.users_df['department'] == dept]
            heatmap_data.append({
                "department": dept,
                "Low": int((dept_df['risk_level'] == 'Low').sum()),
                "Medium": int((dept_df['risk_level'] == 'Medium').sum()),
                "High": int((dept_df['risk_level'] == 'High').sum()),
                "Critical": int((dept_df['risk_level'] == 'Critical').sum())
            })
        return heatmap_data

    def get_security_posture_score(self) -> Dict[str, Any]:
        if self.users_df.empty:
            return {"score": 100, "status": "Excellent"}
            
        total_users = len(self.users_df)
        critical_count = int((self.users_df['risk_level'] == 'Critical').sum())
        high_count = int((self.users_df['risk_level'] == 'High').sum())
        suspicious_count = int((self.users_df['anomaly_label'] == 'Suspicious').sum())
        avg_risk_score = float(self.users_df['risk_score'].mean())
        
        # Deductions based on threat prevalence (scaled proportionally)
        deductions = ((critical_count * 40.0 + high_count * 20.0 + suspicious_count * 20.0) / total_users) + (avg_risk_score * 0.20)
        score = max(0, min(100, round(100 - deductions)))
        
        if score >= 90:
            status = "Excellent"
        elif score >= 75:
            status = "Good"
        elif score >= 50:
            status = "Moderate"
        else:
            status = "Poor"
            
        return {
            "score": score,
            "status": status,
            "critical_users": critical_count,
            "high_risk_users": high_count,
            "suspicious_users": suspicious_count,
            "avg_risk_score": round(avg_risk_score, 2)
        }

    def get_user_activity_risk_matrix(self) -> List[Dict[str, Any]]:
        if self.users_df.empty:
            return []
            
        # Filter all suspicious or high/critical users, and sample low/normal users to keep plot performance smooth
        flagged_df = self.users_df[
            (self.users_df['anomaly_label'] == 'Suspicious') |
            (self.users_df['risk_level'].isin(['High', 'Critical']))
        ]
        
        normal_df = self.users_df[
            (self.users_df['anomaly_label'] == 'Normal') &
            (~self.users_df['risk_level'].isin(['High', 'Critical']))
        ]
        
        sample_size = min(len(normal_df), 1000 - len(flagged_df))
        if sample_size > 0:
            sampled_normal = normal_df.sample(n=sample_size, random_state=42)
            matrix_df = pd.concat([flagged_df, sampled_normal])
        else:
            matrix_df = flagged_df
            
        cols = ['user_id', 'name', 'department', 'risk_score', 'risk_level', 'anomaly_score', 'anomaly_reason']
        return matrix_df[cols].to_dict(orient='records')

    def get_behavioral_indicators_summary(self) -> Dict[str, float]:
        if self.users_df.empty:
            return {
                "avg_after_hours_ratio": 0.0,
                "avg_weekend_ratio": 0.0,
                "avg_usb_connections": 0.0,
                "avg_unique_endpoints": 0.0,
                "avg_risk_score": 0.0
            }
        
        return {
            "avg_after_hours_ratio": round(float(self.users_df['after_hours_ratio'].mean()), 4),
            "avg_weekend_ratio": round(float(self.users_df['weekend_ratio'].mean()), 4),
            "avg_usb_connections": round(float(self.users_df['usb_connects'].mean()), 2),
            "avg_unique_endpoints": round(float(self.users_df['unique_pcs_used'].mean()), 2),
            "avg_risk_score": round(float(self.users_df['risk_score'].mean()), 2)
        }

    def get_watchlist(self, limit: int = 20) -> List[Dict[str, Any]]:
        if self.users_df.empty:
            return []
            
        sorted_df = self.users_df.sort_values(by='risk_score', ascending=False)
        cols = ['user_id', 'name', 'department', 'risk_score', 'security_status', 'anomaly_reason']
        return sorted_df.head(limit)[cols].to_dict(orient='records')
