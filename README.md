# PowerPulse

## Electricity Demand Intelligence Platform

PowerPulse is an ML-powered electricity demand intelligence platform that forecasts future electricity consumption, predicts peak demand, and detects potential anomalies in consumption patterns.

The project combines machine learning with a FastAPI backend, Streamlit dashboard, SQLAlchemy/SQLite database, JWT authentication, and a simulated real-time streaming pipeline.

## Features

- 1-hour-ahead electricity consumption forecasting
- Peak demand prediction
- Hybrid anomaly detection using:
  - Forecast residual analysis
  - Isolation Forest
- SHAP-based model explainability
- Simulated real-time electricity data streaming
- Automatic lag-feature generation
- FastAPI REST API
- Streamlit dashboard
- JWT-based authentication
- Password hashing using Argon2
- User-specific prediction and anomaly history
- SQLite database using SQLAlchemy

## System Architecture

```text
                    Streamlit Dashboard
                           |
                           | HTTP Requests
                           v
                     FastAPI Backend
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
       Forecast Model  Peak Model   Anomaly Models
         XGBoost        XGBoost      Residual +
                                      Isolation Forest
             |             |             |
             +-------------+-------------+
                           |
                           v
                    SQLite Database
                           |
                           v
                  Prediction / Anomaly
                       History
```

## Machine Learning Models

### 1. Electricity Demand Forecasting

An XGBoost Regressor is used to predict electricity consumption one hour into the future.

The model uses:

- Temperature
- Humidity
- Wind Speed
- General Diffuse Flows
- Diffuse Flows
- Hour
- Day
- Day of Week
- Month
- Historical consumption lags

Historical lag features include:

- `lag_1` — previous 10-minute consumption
- `lag_6` — previous 1-hour consumption
- `lag_24` — previous 4-hour consumption
- `lag_144` — previous-day consumption at the same time

The dataset is split chronologically to avoid future information leakage.

### 2. Peak Demand Prediction

The system predicts whether electricity consumption one hour ahead is likely to reach a peak-demand level.

Peak demand is defined using the 90th percentile of future consumption calculated from the training data.

An XGBoost Classifier produces a peak probability.

A probability threshold of `0.9` is currently used for high-confidence peak alerts after evaluating different operating thresholds.

### 3. Anomaly Detection

PowerPulse uses two complementary approaches.

#### Forecast Residual Detection

The difference between actual and predicted consumption is calculated:

```text
Residual = Actual Consumption - Predicted Consumption
```

Large residuals are treated as potential anomalies based on a threshold learned from training residuals.

#### Isolation Forest

Isolation Forest analyzes the input feature patterns and identifies observations that differ significantly from normal patterns.

The two approaches are combined:

```text
Anomaly Score =
    Residual Anomaly +
    Isolation Forest Anomaly
```

A score of `2` represents a high-confidence anomaly candidate.

Because the dataset does not contain ground-truth anomaly labels, these are treated as anomaly candidates rather than confirmed real-world faults.

## Dataset

The project uses the Tetouan City power consumption dataset.

The dataset contains 10-minute electricity consumption measurements along with environmental variables such as:

- Temperature
- Humidity
- Wind Speed
- General Diffuse Flows
- Diffuse Flows
- Power consumption for three zones

PowerPulse currently focuses on Zone 1 consumption.

## Real-Time Streaming Simulation

The project includes a streaming simulator that reads historical electricity measurements chronologically and sends them to the FastAPI backend.

```text
Historical Dataset
       |
       v
Streaming Simulator
       |
       | HTTP POST
       v
FastAPI /stream/reading
       |
       v
Store Reading
       |
       v
Generate Historical Lag Features
       |
       v
Run ML Models
       |
       v
Store Predictions + Anomaly Results
```

This simulates how the system could process continuously arriving readings from a smart meter or energy monitoring system.

The simulator automatically generates historical lag features from previously stored readings rather than requiring them to be entered manually.

## Backend

The backend is built using FastAPI.

Main API capabilities:

- User registration
- User login
- JWT authentication
- Current-user verification
- Electricity demand prediction
- Peak demand prediction
- Anomaly detection
- Prediction history
- Anomaly history
- Streaming electricity readings
- Latest monitoring data

Interactive API documentation is available through FastAPI Swagger UI.

```text
http://127.0.0.1:8000/docs
```

## Authentication

PowerPulse implements JWT-based authentication.

Authentication flow:

```text
Register
   |
   v
Password Hashing
   |
   v
Login
   |
   v
JWT Access Token
   |
   v
Protected API Endpoints
   |
   v
Current User
```

Passwords are hashed using Argon2 rather than being stored directly.

Prediction and anomaly history are associated with the authenticated user.

## Database

PowerPulse uses:

- SQLite
- SQLAlchemy ORM

The database stores information such as:

- Users
- Predictions
- Anomalies
- Consumption readings
- Model outputs from the streaming pipeline

## Explainability

SHAP is used to explain the XGBoost forecasting model.

The project uses:

- SHAP summary plots
- Feature importance plots
- Individual prediction explanations using waterfall plots

This helps identify which features have the strongest influence on predictions and overall model behavior.

## Project Structure

```text
PowerPulse/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── auth.py
│
├── frontend/
│   └── app.py
│
├── streaming/
│   └── simulator.py
│
├── models/
│   ├── forecast_model.pkl
│   ├── peak_model.pkl
│   ├── isolation_forest.pkl
│   └── residual_threshold.pkl
│
├── data/
│   └── Tetuan City power consumption.csv
│
├── model.ipynb
├── .gitignore
├── README.md
└── requirements.txt
```

## Technologies Used

### Machine Learning

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- SHAP
- Joblib

### Backend

- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic
- Python-Jose
- pwdlib
- Argon2

### Frontend

- Streamlit

### Development

- Jupyter Notebook
- VS Code
- Git
- GitHub

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/PowerPulse.git
cd PowerPulse
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
POWERPULSE_SECRET_KEY=your-secret-key
```

Do not commit `.env` to GitHub.

## Running the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Running the Streamlit Dashboard

Open another terminal:

```bash
streamlit run frontend/app.py
```

The dashboard will open in your browser.

## Running the Streaming Simulator

With the FastAPI server running:

```bash
python streaming/simulator.py
```

The simulator sends historical readings to the streaming endpoint and displays the resulting forecast, peak-risk, and anomaly information.

## Model Performance

### Demand Forecasting

Current test performance:

| Metric | Value |
|---|---:|
| MAE | ~1743 |
| RMSE | ~2146 |
| R² | ~0.879 |

The model was evaluated using a chronological train/test split.

A previous-hour baseline produced an MAE of approximately 3406, showing that the XGBoost model improves substantially over this simple baseline.

### Peak Demand Classification

The peak classifier achieved:

- PR-AUC: ~0.882
- F1 score at the selected 0.9 probability threshold: ~0.813

The threshold was selected by evaluating multiple probability thresholds and considering the precision/recall trade-off.

## Future Improvements

Potential future improvements include:

- Stronger seasonal-naive forecasting baselines
- Weather API integration
- More advanced time-series models
- Prediction and anomaly history visualization
- SHAP explanations directly inside the dashboard
- Improved database migrations using Alembic
- Site/building-specific streaming data
- More robust production deployment
- Decision and recommendation layer using an AI agent

## Disclaimer

This project is an educational and portfolio implementation using a public electricity consumption dataset and a simulated streaming pipeline.

The anomaly detection system identifies statistical anomaly candidates and does not represent confirmed electrical faults or safety-critical alerts.
