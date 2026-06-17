# User Anomaly Detection — NFC / DAE

## Overview
Detects insider threats and anomalous user behaviour at the Nuclear Fuel Complex
by analysing login patterns, device usage, and LDAP attributes using Isolation Forest.

## Datasets Used
| File | Description |
|------|-------------|
| users.csv | Master user registry |
| LDAP.csv | Directory / department info |
| logon.csv | System logon/logoff events |
| device.csv | USB / removable device events |

> email.csv is intentionally excluded from this pipeline.

## Architecture
```
data/ → ml/preprocessing → ml/feature_engineering → ml/training → ml/prediction
                                                              ↓
                                                     backend (FastAPI)
                                                              ↓
                                                     frontend (React + Vite)
```

## ML Pipeline
1. **Clean** each raw CSV (4 scripts)
2. **Feature engineer** login & device features per user
3. **Merge** into master feature matrix
4. **Train** Isolation Forest (unsupervised)
5. **Score** users → risk levels LOW / MEDIUM / HIGH / CRITICAL
6. **Serve** scores & alerts via FastAPI REST API

## Run Instructions
See SETUP.md for step-by-step installation.
