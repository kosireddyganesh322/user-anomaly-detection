# Machine Learning Model Artifacts — User Anomaly Detection

This directory contains the serialized machine learning model components used by the User Anomaly Detection System (UADS) to classify and predict suspicious employee behaviors.

---

## 1. Serialized Model Files

This directory contains two primary model artifacts:

* **`isolation_forest.pkl`**: The serialized Scikit-learn `IsolationForest` model.
* **`scaler.pkl`**: The serialized Scikit-learn `StandardScaler` used to normalize feature inputs before inference.

These files are loaded into memory by the FastAPI backend on startup to support real-time endpoint prediction queries.

---

## 2. Input Features Definition

The machine learning models operate on a user-level feature matrix containing $11$ numeric features. These features are extracted from the raw logon and device csv datasets:

| Feature Name | Description | Target Behavior Analyzed |
| :--- | :--- | :--- |
| `total_logins` | Total count of logon events | General workstation activity baseline. |
| `active_days` | Number of unique days the user logged in | User presence consistency. |
| `avg_logins_per_day` | `total_logins` / `active_days` | System session frequency. |
| `unique_pcs_used` | Number of distinct computer terminals logged into | Workstation hopping / roaming activity. |
| `after_hours_logins` | Total logins between 18:00 and 06:00 | Off-shift and night activity. |
| `weekend_logins` | Total logins on Saturdays or Sundays | Weekend maintenance or off-hours intrusion. |
| `usb_connects` | Total count of USB storage drive mounts | Removable media usage frequency. |
| `after_hours_usb` | USB storage mounts outside business hours | Out-of-hours data staging. |
| `login_device_ratio` | Total logins / USB connects | Connection intensity (Low ratio = High USB connects). |
| `after_hours_ratio` | After-hours logins / Total logins | Proportion of night-time operations. |
| `weekend_ratio` | Weekend logins / Total logins | Proportion of weekend operations. |

---

## 3. Preprocessing & Feature Scaling

Because features like `total_logins` can range in the thousands, while ratio features like `login_device_ratio` range between 0 and 1, we apply a **`StandardScaler`** to normalize all inputs.

$$\mathbf{z} = \frac{\mathbf{x} - \mu}{\sigma}$$

* **$\mu$**: Feature mean.
* **$\sigma$**: Feature standard deviation.

This scaling ensures that features with large numerical magnitudes do not dominate the distance calculations during Isolation Tree splits. The fitted means ($\mu$) and variances ($\sigma^2$) are saved inside `scaler.pkl`.

---

## 4. Isolation Forest Model Architecture

The core ML model is based on the **Isolation Forest** algorithm. It is an unsupervised ensemble method particularly suited for anomaly detection in high-dimensional feature spaces.

### Hyperparameter Settings
* **`n_estimators = 100`**: The ensemble builds $100$ isolation trees.
* **`contamination = 0.05`**: The expected proportion of anomalies in the dataset. This parameter sets the decision boundary, designating the top $5\%$ of users with the most isolated feature values as anomalies.
* **`random_state = 42`**: Ensures that the randomized features and splits are reproducible across training runs.
* **`n_jobs = -1`**: Leverages all available CPU cores to speed up tree isolation splits.

### Anomaly Scoring Process
1. For each user, the algorithm constructs path lengths across the $100$ random isolation trees.
2. Because anomalies have extreme or unusual feature values, they require fewer splits to isolate, resulting in shorter path lengths in the trees.
3. The average path length is mapped to an **Anomaly Score**:
   * **Score near 0.5 or lower**: Represents anomalous behavior (the user is easily isolated).
   * **Score near 1.0**: Represents normal behavior (the user requires many splits to isolate).
4. In Scikit-learn, the raw anomaly score is retrieved using `decision_function()`:
   * **Negative Scores** $\rightarrow$ Flagged as anomalies (`Suspicious`).
   * **Positive Scores** $\rightarrow$ Flagged as normal (`Normal`).

### Inference Pipeline Code Snippet
During the execution of `predict.py`, predictions are generated using:

```python
# Load fitted scaler and model
with open("ml/models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("ml/models/isolation_forest.pkl", "rb") as f:
    model = pickle.load(f)

# Scale features
X_scaled = scaler.transform(X)

# Predict outlier labels: 1 for normal, -1 for outlier/anomaly
predictions = model.predict(X_scaled)
raw_scores = model.decision_function(X_scaled)

# Map output labels
df['anomaly_score'] = raw_scores
df['anomaly_label'] = pd.Series(predictions).map({1: 'Normal', -1: 'Suspicious'})
```

---

## 5. Model Retraining Guidelines

To maintain accuracy and prevent baseline drift (e.g., when new departments are onboarded or working hours shift), retrain the model quarterly:

1. Place new raw logging CSVs in `data/raw/`.
2. Run the preprocessing scripts to compile new feature files.
3. Execute `python ml/training/train_model.py`.
4. Run prediction pipelines to compile new final security profiles:
   ```bash
   python ml/risk_scoring/risk_engine.py
   python ml/prediction/predict.py
   python ml/prediction/generate_security_profile.py
   ```
5. Restart the FastAPI backend to load the updated `final_security_profile.csv`.
