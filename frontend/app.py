import streamlit as st
import requests
import pandas as pd
import requests

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }
# -----------------------------
# Configuration
# -----------------------------

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="PowerPulse",
    page_icon="",
    layout="wide"
)


# -----------------------------
# Styling
# -----------------------------

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1 {
    font-size: 2.2rem;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #777;
    font-size: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    padding: 1.2rem;
    border: 1px solid #ddd;
    border-radius: 10px;
    background-color: #ffffff;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# Header
# -----------------------------

if st.session_state.token is None:

    st.title("PowerPulse")

    st.caption(
        "Electricity Demand Intelligence Platform"
    )

    auth_mode = st.radio(
        "Account",
        ["Login", "Register"],
        horizontal=True
    )

    if auth_mode == "Login":

        st.subheader("Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            response = requests.post(
                "http://127.0.0.1:8000/auth/login",
                params={
                    "username": username,
                    "password": password
                }
            )

            if response.status_code == 200:

                result = response.json()

                st.session_state.token = (
                    result["access_token"]
                )

                st.session_state.username = username

                st.rerun()

            else:

                st.error(
                    response.json().get(
                        "detail",
                        "Login failed"
                    )
                )

    else:

        st.subheader("Create Account")

        username = st.text_input(
            "Username"
        )

        email = st.text_input(
            "Email"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Register"):

            response = requests.post(
                "http://127.0.0.1:8000/auth/register",
                params={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )

            if response.status_code == 200:

                st.success(
                    "Account created successfully. "
                    "You can now log in."
                )

            else:

                st.error(
                    response.json().get(
                        "detail",
                        "Registration failed"
                    )
                )

    st.stop()


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("PowerPulse")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Consumption Forecast",
        "Peak Risk",
        "Anomaly Detection",
        "Live Monitoring"
    ]
)


# -----------------------------
# Input helper
# -----------------------------

def get_inputs(include_actual=False):

    st.markdown("### Model Inputs")

    col1, col2, col3 = st.columns(3)

    with col1:
        temperature = st.number_input(
            "Temperature",
            value=28.0
        )

        humidity = st.number_input(
            "Humidity",
            value=70.0
        )

        wind_speed = st.number_input(
            "Wind Speed",
            value=2.0
        )

        general_diffuse = st.number_input(
            "General Diffuse Flows",
            value=30.0
        )

    with col2:
        diffuse_flows = st.number_input(
            "Diffuse Flows",
            value=25.0
        )

        hour = st.number_input(
            "Hour",
            min_value=0,
            max_value=23,
            value=12
        )

        day = st.number_input(
            "Day",
            min_value=1,
            max_value=31,
            value=19
        )

        day_of_week = st.number_input(
            "Day of Week",
            min_value=0,
            max_value=6,
            value=3
        )

    with col3:
        month = st.number_input(
            "Month",
            min_value=1,
            max_value=12,
            value=10
        )

        lag_1 = st.number_input(
            "Previous 10 min",
            value=28000.0
        )

        lag_6 = st.number_input(
            "Previous 1 hour",
            value=27500.0
        )

        lag_24 = st.number_input(
            "Previous 4 hours",
            value=25500.0
        )

    lag_144 = st.number_input(
        "Previous day (same time)",
        value=31500.0
    )

    data = {
        "Temperature": temperature,
        "Humidity": humidity,
        "WindSpeed": wind_speed,
        "GeneralDiffuseFlows": general_diffuse,
        "DiffuseFlows": diffuse_flows,
        "hour": hour,
        "day": day,
        "day_of_week": day_of_week,
        "month": month,
        "lag_1": lag_1,
        "lag_6": lag_6,
        "lag_24": lag_24,
        "lag_144": lag_144
    }

    if include_actual:

        actual = st.number_input(
            "Actual Consumption",
            value=30000.0
        )

        data["actual_consumption"] = actual

    return data


# =========================================================
# OVERVIEW
# =========================================================

if page == "Overview":

    st.header("PowerPulse")
    st.caption("Electricity demand intelligence and risk monitoring")

    st.divider()

    # -----------------------------
    # Top summary
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Forecast Model",
            "XGBoost"
        )

    with col2:
        st.metric(
            "Peak Detection",
            "XGBoost"
        )

    with col3:
        st.metric(
            "Anomaly Detection",
            "Hybrid"
        )

    st.divider()

    # -----------------------------
    # Project description
    # -----------------------------

    st.subheader("Demand Intelligence")

    st.write(
        "PowerPulse forecasts electricity consumption one hour ahead, "
        "identifies potential peak-demand conditions, and detects "
        "unusual consumption behaviour."
    )

    st.write(
        "The platform combines supervised machine learning with "
        "residual analysis and Isolation Forest anomaly detection."
    )

    st.divider()

    # -----------------------------
    # Capabilities
    # -----------------------------

    st.subheader("Capabilities")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("**Consumption Forecast**")

        st.write(
            "Predict electricity demand for the next hour "
            "using environmental, temporal, and historical "
            "consumption features."
        )

        st.markdown("**Peak Demand Risk**")

        st.write(
            "Estimate the probability of a future demand peak "
            "using a tuned classification threshold."
        )

    with col2:

        st.markdown("**Anomaly Detection**")

        st.write(
            "Compare actual consumption against the forecast "
            "and combine residual-based detection with "
            "Isolation Forest."
        )

        st.markdown("**Model Explainability**")

        st.write(
            "SHAP-based explanations are available for "
            "understanding which features influence forecasts."
        )

    st.divider()

    # -----------------------------
    # System architecture
    # -----------------------------

    st.subheader("System Architecture")

    st.code(
        """User
  |
  v
Streamlit Dashboard
  |
  | HTTP
  v
FastAPI
  |
  +-------------------+
  |                   |
  v                   v
Forecast Model    Peak Model
  |
  v
Anomaly Detection
  |
  +--> Residual Analysis
  |
  +--> Isolation Forest
  |
  v
Prediction Results
  |
  v
Streamlit Dashboard
""",
        language="text"
    )

    st.divider()

    # -----------------------------
    # Navigation hint
    # -----------------------------

    st.info(
        "Use the navigation panel to run a forecast, "
        "evaluate peak-demand risk, or analyze an anomaly."
    )

# =========================================================
# FORECAST
# =========================================================

elif page == "Consumption Forecast":

    st.header("Consumption Forecast")

    st.caption(
        "One-hour-ahead electricity demand prediction"
    )

    st.divider()

    # -----------------------------
    # Model information
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Forecast Horizon",
            "1 hour"
        )

    with col2:
        st.metric(
            "Model",
            "XGBoost"
        )

    with col3:
        st.metric(
            "Prediction Target",
            "Zone 1"
        )

    st.divider()

    # -----------------------------
    # Advanced inputs
    # -----------------------------

    with st.expander("Advanced Inputs"):

        inputs = get_inputs()

    # -----------------------------
    # Prediction
    # -----------------------------

    if st.button(
        "Generate Forecast",
        type="primary"
    ):

        try:

            response = requests.post(
                f"{API_URL}/predict/forecast",
                json=inputs
            )

            if response.status_code == 200:

                result = response.json()

                prediction = result["predicted_consumption"]

                st.divider()

                st.subheader("Forecast Result")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Predicted Consumption",
                        f"{prediction:,.0f}"
                    )

                with col2:

                    st.metric(
                        "Forecast Horizon",
                        "Next 1 hour"
                    )

                st.divider()

                # -----------------------------
                # Recent demand context
                # -----------------------------

                st.subheader("Recent Demand Context")

                chart_data = {
                    "Previous 24 hours": inputs["lag_144"],
                    "Previous 4 hours": inputs["lag_24"],
                    "Previous 1 hour": inputs["lag_6"],
                    "Previous 10 min": inputs["lag_1"],
                    "Next hour forecast": prediction
                }

                st.bar_chart(chart_data)

                st.caption(
                    "Historical values are provided as model lag features. "
                    "The final value represents the model's one-hour-ahead forecast."
                )

            else:

                st.error(
                    f"API error: {response.status_code}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the PowerPulse API. "
                "Make sure FastAPI is running."
            )

# =========================================================
# PEAK RISK
# =========================================================

elif page == "Peak Risk":

    st.header("Peak Demand Risk")

    st.caption(
        "Estimate the probability of a peak-demand event in the next hour"
    )

    st.divider()

    # -----------------------------
    # Model information
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Forecast Horizon",
            "1 hour"
        )

    with col2:
        st.metric(
            "Model",
            "XGBoost"
        )

    with col3:
        st.metric(
            "Operating Threshold",
            "90%"
        )

    st.divider()

    # -----------------------------
    # Advanced inputs
    # -----------------------------

    with st.expander("Advanced Inputs"):

        inputs = get_inputs()

    # -----------------------------
    # Prediction
    # -----------------------------

    if st.button(
        "Check Peak Risk",
        type="primary"
    ):

        try:

            response = requests.post(
                f"{API_URL}/predict/peak",
                json=inputs
            )

            if response.status_code == 200:

                result = response.json()

                probability = result["peak_probability"]
                risk = result["peak_risk"]
                threshold = result["threshold"]

                st.divider()

                st.subheader("Peak Risk Assessment")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Peak Probability",
                        f"{probability * 100:.2f}%"
                    )

                with col2:

                    st.metric(
                        "Risk Classification",
                        risk
                    )

                st.divider()

                # -----------------------------
                # Probability visualization
                # -----------------------------

                st.subheader("Probability")

                probability_data = {
                    "Peak probability": probability,
                    "Remaining probability": 1 - probability
                }

                st.bar_chart(
                    probability_data
                )

                st.caption(
                    f"The model classifies a prediction as peak "
                    f"when the probability reaches the {threshold:.0%} "
                    f"operating threshold."
                )

                # -----------------------------
                # Interpretation
                # -----------------------------

                if probability >= threshold:

                    st.warning(
                        "The predicted probability is above the "
                        "configured peak-demand threshold."
                    )

                else:

                    st.success(
                        "The predicted probability is below the "
                        "configured peak-demand threshold."
                    )

            else:

                st.error(
                    f"API error: {response.status_code}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the PowerPulse API. "
                "Make sure FastAPI is running."
            )


# =========================================================
# ANOMALY
# =========================================================
elif page == "Anomaly Detection":

    st.header("Anomaly Detection")

    st.caption(
        "Identify unusual electricity consumption using forecast residuals "
        "and Isolation Forest"
    )

    st.divider()

    # -----------------------------
    # Detection methods
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Detection Method 1",
            "Forecast Residual"
        )

    with col2:
        st.metric(
            "Detection Method 2",
            "Isolation Forest"
        )

    st.divider()

    # -----------------------------
    # Advanced inputs
    # -----------------------------

    with st.expander("Advanced Inputs"):

        inputs = get_inputs(
            include_actual=True
        )

    # -----------------------------
    # Prediction
    # -----------------------------

    if st.button(
        "Analyze Consumption",
        type="primary"
    ):

        try:

            response = requests.post(
                f"{API_URL}/predict/anomaly",
                json=inputs
            )

            if response.status_code == 200:

                result = response.json()

                actual = result["actual_consumption"]
                predicted = result["predicted_consumption"]
                residual = result["residual"]

                residual_flag = result["residual_anomaly"]
                isolation_flag = result["isolation_forest_anomaly"]
                anomaly_score = result["anomaly_score"]
                status = result["status"]

                st.divider()

                # -----------------------------
                # Main result
                # -----------------------------

                st.subheader("Detection Result")

                if anomaly_score == 0:

                    st.success(
                        f"Status: {status}"
                    )

                elif anomaly_score == 1:

                    st.warning(
                        f"Status: {status}"
                    )

                else:

                    st.error(
                        f"Status: {status}"
                    )

                st.divider()

                # -----------------------------
                # Consumption comparison
                # -----------------------------

                st.subheader("Actual vs Predicted")

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Actual Consumption",
                        f"{actual:,.0f}"
                    )

                with col2:

                    st.metric(
                        "Predicted Consumption",
                        f"{predicted:,.0f}"
                    )

                with col3:

                    st.metric(
                        "Residual",
                        f"{residual:,.0f}"
                    )

                comparison_data = {
                    "Actual": actual,
                    "Predicted": predicted
                }

                st.bar_chart(
                    comparison_data
                )

                st.divider()

                # -----------------------------
                # Detection methods
                # -----------------------------

                st.subheader("Detection Signals")

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown("**Forecast Residual**")

                    if residual_flag == 1:

                        st.warning(
                            "Unusual deviation from the forecast detected."
                        )

                    else:

                        st.success(
                            "Consumption is within the residual threshold."
                        )

                with col2:

                    st.markdown("**Isolation Forest**")

                    if isolation_flag == 1:

                        st.warning(
                            "The input was identified as an unusual "
                            "feature pattern."
                        )

                    else:

                        st.success(
                            "No unusual feature pattern detected."
                        )

                st.divider()

                st.metric(
                    "Combined Anomaly Score",
                    anomaly_score
                )

                st.caption(
                    "Score 0: neither method flagged the observation. "
                    "Score 1: one method flagged it. "
                    "Score 2: both methods flagged it."
                )

            else:

                st.error(
                    f"API error: {response.status_code}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the PowerPulse API. "
                "Make sure FastAPI is running."
            )
elif page == "Live Monitoring":

    st.header("Live Monitoring")
    st.caption(
        "Real-time electricity consumption intelligence from the streaming pipeline."
    )

    try:

        response = requests.get(
            "http://127.0.0.1:8000/stream/latest"
        )

        if response.status_code == 200:

            readings = response.json()

            if readings:

                latest = readings[0]

                # -------------------------
                # Latest Reading
                # -------------------------

                st.subheader("Latest Reading")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Current Consumption",
                        f"{latest['consumption']:.2f}"
                    )

                with col2:
                    st.metric(
                        "Temperature",
                        f"{latest['temperature']:.2f}"
                    )

                with col3:
                    st.metric(
                        "Humidity",
                        f"{latest['humidity']:.2f}"
                    )

                st.divider()

                # -------------------------
                # ML Results
                # -------------------------

                st.subheader("Live Intelligence")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if latest["predicted_consumption"] is not None:
                        st.metric(
                            "1-Hour Forecast",
                            f"{latest['predicted_consumption']:.2f}"
                        )
                    else:
                        st.metric(
                            "1-Hour Forecast",
                            "Waiting"
                        )

                with col2:
                    if latest["peak_probability"] is not None:
                        st.metric(
                            "Peak Probability",
                            f"{latest['peak_probability'] * 100:.1f}%"
                        )
                    else:
                        st.metric(
                            "Peak Probability",
                            "Waiting"
                        )

                with col3:
                    st.metric(
                        "Peak Risk",
                        latest["peak_risk"]
                        if latest["peak_risk"]
                        else "Waiting"
                    )

                with col4:
                    st.metric(
                        "Anomaly Status",
                        latest["anomaly_status"]
                        if latest["anomaly_status"]
                        else "Waiting"
                    )

                st.divider()

                # -------------------------
                # Anomaly Details
                # -------------------------

                if latest["anomaly_score"] is not None:

                    st.subheader("Anomaly Detection")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Residual",
                            f"{latest['residual']:.2f}"
                        )

                    with col2:
                        st.metric(
                            "Anomaly Score",
                            latest["anomaly_score"]
                        )

                    with col3:
                        st.metric(
                            "Isolation Forest",
                            "Anomaly"
                            if latest["isolation_forest_anomaly"] == 1
                            else "Normal"
                        )

                st.divider()

                # -------------------------
                # Consumption Chart
                # -------------------------

                st.subheader("Recent Consumption")

                chart_data = pd.DataFrame(readings)

                chart_data = chart_data.sort_values(
                    "timestamp"
                )

                chart_data["timestamp"] = pd.to_datetime(
                    chart_data["timestamp"]
                )

                chart_data = chart_data.set_index(
                    "timestamp"
                )

                st.line_chart(
                    chart_data[
                        [
                            "consumption",
                            "predicted_consumption"
                        ]
                    ]
                )

                st.divider()

                # -------------------------
                # Recent Readings
                # -------------------------

                st.subheader("Recent Stream")

                display_data = chart_data.reset_index()

                st.dataframe(
                    display_data[
                        [
                            "timestamp",
                            "consumption",
                            "predicted_consumption",
                            "peak_probability",
                            "peak_risk",
                            "anomaly_status"
                        ]
                    ],
                    use_container_width=True
                )

            else:

                st.info(
                    "No streaming readings available yet."
                )

        else:

            st.error(
                "Could not retrieve streaming data."
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to the PowerPulse API."
        )