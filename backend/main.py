from fastapi import FastAPI
import joblib
import pandas as pd
from .auth import get_current_user,create_access_token


from backend.schemas import ForecastRequest,PeakRequest,AnomalyRequest,StreamingReading
from .database import Base, engine
from . import models
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from .database import get_db
from .models import User,ConsumptionReading,Prediction,Anomaly

Base.metadata.create_all(bind=engine)
password_hash = PasswordHash.recommended()

app = FastAPI(
    title="PowerPulse API",
    description="ML-powered electricity consumption intelligence API",
    version="1.0.0"
)


# Load forecasting model
forecast_model = joblib.load(
    "models/forecast_model.pkl"
)

peak_model = joblib.load("models/peak_model.pkl")
residual_threshold = joblib.load("models/residual_threshold.pkl")
isolation_model = joblib.load("models/isolation_forest.pkl")


FEATURES = [
    "Temperature",
    "Humidity",
    "WindSpeed",
    "GeneralDiffuseFlows",
    "DiffuseFlows",
    "hour",
    "day",
    "day_of_week",
    "month",
    "lag_1",
    "lag_6",
    "lag_24",
    "lag_144"
]

@app.post("/auth/register")
def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(
            (User.username == username) |
            (User.email == email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    hashed_password = password_hash.hash(password)

    user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "username": user.username
    }


@app.post("/auth/login")
def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not password_hash.verify(
        password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token({
        "sub": str(user.id),
        "username": user.username
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/")
def root():
    return {
        "message": "PowerPulse API is running",
        "status": "healthy"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/predict/forecast")
def predict_forecast(data: ForecastRequest,
                     current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)):

    input_data = pd.DataFrame(
        [[
            data.Temperature,
            data.Humidity,
            data.WindSpeed,
            data.GeneralDiffuseFlows,
            data.DiffuseFlows,
            data.hour,
            data.day,
            data.day_of_week,
            data.month,
            data.lag_1,
            data.lag_6,
            data.lag_24,
            data.lag_144
        ]],
        columns=FEATURES
    )

    prediction = forecast_model.predict(input_data)[0]
    prediction_record = Prediction(
    user_id=current_user.id,
    predicted_consumption=float(prediction)
)

    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)
    return {
        "predicted_consumption": float(prediction),
         "prediction_id": prediction_record.id
    }
@app.post("/predict/peak")
def predict_peak(
    data: PeakRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    input_data = [[
        data.Temperature,
        data.Humidity,
        data.WindSpeed,
        data.GeneralDiffuseFlows,
        data.DiffuseFlows,
        data.hour,
        data.day,
        data.day_of_week,
        data.month,
        data.lag_1,
        data.lag_6,
        data.lag_24,
        data.lag_144
    ]]

    PEAK_THRESHOLD = 0.5

    peak_probability = peak_model.predict_proba(input_data)[0][1]

    prediction = int(peak_probability >= PEAK_THRESHOLD)

    if prediction == 1:
        risk = "High"
    else:
        risk = "Normal"
    prediction_record = Prediction(
    user_id=current_user.id,
    predicted_consumption=0.0,
    peak_probability=float(peak_probability),
    peak_risk=risk
)

    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)
    return {
    "peak_probability": float(peak_probability),
    "peak_prediction": prediction,
    "peak_risk": risk,
    "threshold": PEAK_THRESHOLD,
    "prediction_id": prediction_record.id
}
@app.post("/predict/anomaly")
def predict_anomaly(
    data: AnomalyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    input_data = [[
        data.Temperature,
        data.Humidity,
        data.WindSpeed,
        data.GeneralDiffuseFlows,
        data.DiffuseFlows,
        data.hour,
        data.day,
        data.day_of_week,
        data.month,
        data.lag_1,
        data.lag_6,
        data.lag_24,
        data.lag_144
    ]]

    predicted = forecast_model.predict(input_data)[0]

    # We need the actual consumption to calculate the residual.
    actual = data.actual_consumption

    residual = actual - predicted

    # Residual anomaly
    residual_flag = int(abs(residual) > residual_threshold)

    # Isolation Forest
    iso_prediction = isolation_model.predict(input_data)[0]

    if iso_prediction == -1:
        isolation_flag = 1
    else:
        isolation_flag = 0

    # Combined anomaly score
    anomaly_score = residual_flag + isolation_flag

    if anomaly_score == 0:
        status = "Normal"
    elif anomaly_score == 1:
        status = "Anomaly"
    else:
        status = "High Confidence Anomaly"

    anomaly_record = Anomaly(
    user_id=current_user.id,
    actual_consumption=float(actual),
    predicted_consumption=float(predicted),
    residual=float(residual),
    anomaly_score=int(anomaly_score),
    status=status
)

    db.add(anomaly_record)
    db.commit()
    db.refresh(anomaly_record)
    return {
    "actual_consumption": float(actual),
    "predicted_consumption": float(predicted),
    "residual": float(residual),
    "residual_anomaly": residual_flag,
    "isolation_forest_anomaly": isolation_flag,
    "anomaly_score": anomaly_score,
    "status": status,
    "anomaly_id": anomaly_record.id
}


from datetime import timedelta


def build_lag_features(db: Session, current_reading):

    current_time = current_reading.timestamp

    lag_times = {
        "lag_1": current_time - timedelta(minutes=10),
        "lag_6": current_time - timedelta(minutes=60),
        "lag_24": current_time - timedelta(minutes=240),
        "lag_144": current_time - timedelta(minutes=1440)
    }

    lag_values = {}

    for lag_name, lag_time in lag_times.items():

        previous_reading = (
            db.query(ConsumptionReading)
            .filter(
                ConsumptionReading.timestamp == lag_time
            )
            .order_by(ConsumptionReading.id.desc())
            .first()
        )

        if previous_reading is None:
            return None

        lag_values[lag_name] = previous_reading.consumption

    features = {
        "Temperature": current_reading.temperature,
        "Humidity": current_reading.humidity,
        "WindSpeed": current_reading.wind_speed,
        "GeneralDiffuseFlows": current_reading.general_diffuse_flows,
        "DiffuseFlows": current_reading.diffuse_flows,

        "hour": current_time.hour,
        "day": current_time.day,
        "day_of_week": current_time.weekday(),
        "month": current_time.month,

        "lag_1": lag_values["lag_1"],
        "lag_6": lag_values["lag_6"],
        "lag_24": lag_values["lag_24"],
        "lag_144": lag_values["lag_144"]
    }

    return features
@app.post("/stream/reading")
def receive_reading(
    data: StreamingReading,
    db: Session = Depends(get_db)
):

    reading = ConsumptionReading(
        timestamp=data.timestamp,
        temperature=data.temperature,
        humidity=data.humidity,
        wind_speed=data.wind_speed,
        general_diffuse_flows=data.general_diffuse_flows,
        diffuse_flows=data.diffuse_flows,
        consumption=data.consumption
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    features = build_lag_features(
        db,
        reading
    )

    if features is None:
        return {
            "message": "Reading stored",
            "reading_id": reading.id,
            "status": "Waiting for sufficient history"
        }

    FEATURES = [
        "Temperature",
        "Humidity",
        "WindSpeed",
        "GeneralDiffuseFlows",
        "DiffuseFlows",
        "hour",
        "day",
        "day_of_week",
        "month",
        "lag_1",
        "lag_6",
        "lag_24",
        "lag_144"
    ]

    input_data = pd.DataFrame(
        [features],
        columns=FEATURES
    )

    prediction = forecast_model.predict(input_data)[0]
    peak_probability = peak_model.predict_proba(input_data)[0][1]

    peak_threshold = 0.5

    peak_prediction = int(
        peak_probability >= peak_threshold
    )

    peak_risk = (
        "Peak Risk"
    if peak_prediction == 1
    else "Normal"
)
    actual_consumption = data.consumption

    residual = actual_consumption - prediction

    residual_anomaly = int(
    abs(residual) > residual_threshold
)

    isolation_prediction = isolation_model.predict(
    input_data
)[0]

    isolation_anomaly = int(
    isolation_prediction == -1
)

    anomaly_score = (
    residual_anomaly +
    isolation_anomaly
)

    if anomaly_score == 0:
        anomaly_status = "Normal"

    elif anomaly_score == 1:
        anomaly_status = "Anomaly"

    else:
        anomaly_status = "High Confidence Anomaly"

    reading.predicted_consumption = float(prediction)

    reading.peak_probability = float(peak_probability)
    reading.peak_prediction = int(peak_prediction)
    reading.peak_risk = peak_risk

    reading.residual = float(residual)
    reading.residual_anomaly = int(residual_anomaly)
    reading.isolation_forest_anomaly = int(isolation_anomaly)
    reading.anomaly_score = int(anomaly_score)
    reading.anomaly_status = anomaly_status

    db.commit()
    db.refresh(reading)
    return {
    "message": "Prediction generated",
    "reading_id": reading.id,
    "timestamp": data.timestamp,

    "current_consumption": data.consumption,

    "predicted_consumption": float(prediction),

    "peak_probability": float(peak_probability),
    "peak_prediction": peak_prediction,
    "peak_risk": peak_risk,
    "peak_threshold": peak_threshold,

    "residual": float(residual),
    "residual_anomaly": residual_anomaly,
    "isolation_forest_anomaly": isolation_anomaly,
    "anomaly_score": anomaly_score,
    "anomaly_status": anomaly_status
}
@app.get("/stream/latest")
def get_latest_readings(
    db: Session = Depends(get_db)
):
    readings = (
        db.query(ConsumptionReading)
        .order_by(ConsumptionReading.timestamp.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "timestamp": reading.timestamp,

            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "wind_speed": reading.wind_speed,
            "consumption": reading.consumption,

            "predicted_consumption": reading.predicted_consumption,

            "peak_probability": reading.peak_probability,
            "peak_prediction": reading.peak_prediction,
            "peak_risk": reading.peak_risk,

            "residual": reading.residual,
            "residual_anomaly": reading.residual_anomaly,
            "isolation_forest_anomaly": reading.isolation_forest_anomaly,
            "anomaly_score": reading.anomaly_score,
            "anomaly_status": reading.anomaly_status
        }
        for reading in readings
    ]
@app.get("/auth/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
@app.get("/predictions/history")
def get_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    predictions = (
        db.query(Prediction)
        .filter(
            Prediction.user_id == current_user.id
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .limit(50)
        .all()
    )

    return [
        {
            "id": prediction.id,
            "predicted_consumption": prediction.predicted_consumption,
            "peak_probability": prediction.peak_probability,
            "peak_risk": prediction.peak_risk,
            "created_at": prediction.created_at
        }
        for prediction in predictions
    ]

@app.get("/anomalies/history")
def get_anomaly_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    anomalies = (
        db.query(Anomaly)
        .filter(
            Anomaly.user_id == current_user.id
        )
        .order_by(
            Anomaly.created_at.desc()
        )
        .limit(50)
        .all()
    )

    return [
        {
            "id": anomaly.id,
            "actual_consumption": anomaly.actual_consumption,
            "predicted_consumption": anomaly.predicted_consumption,
            "residual": anomaly.residual,
            "anomaly_score": anomaly.anomaly_score,
            "status": anomaly.status,
            "created_at": anomaly.created_at
        }
        for anomaly in anomalies
    ]