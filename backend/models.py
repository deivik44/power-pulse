from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from .database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    predicted_consumption = Column(
        Float,
        nullable=False
    )

    peak_probability = Column(
        Float,
        nullable=True
    )

    peak_risk = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class Anomaly(Base):

    __tablename__ = "anomalies"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    actual_consumption = Column(
        Float,
        nullable=False
    )

    predicted_consumption = Column(
        Float,
        nullable=False
    )

    residual = Column(
        Float,
        nullable=False
    )

    anomaly_score = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class ConsumptionReading(Base):
    __tablename__ = "consumption_readings"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(DateTime, nullable=False, index=True)

    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)

    general_diffuse_flows = Column(Float, nullable=False)
    diffuse_flows = Column(Float, nullable=False)

    consumption = Column(Float, nullable=False)

    # ML results
    predicted_consumption = Column(Float, nullable=True)

    peak_probability = Column(Float, nullable=True)
    peak_prediction = Column(Integer, nullable=True)
    peak_risk = Column(String, nullable=True)

    residual = Column(Float, nullable=True)
    residual_anomaly = Column(Integer, nullable=True)
    isolation_forest_anomaly = Column(Integer, nullable=True)
    anomaly_score = Column(Integer, nullable=True)
    anomaly_status = Column(String, nullable=True)