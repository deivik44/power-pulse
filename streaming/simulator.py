import pandas as pd
import requests
import time

DATA_PATH = "data/powerconsumption.csv"
API_URL = "http://127.0.0.1:8000/stream/reading"

# Load dataset
df = pd.read_csv(DATA_PATH)

# Convert timestamp
df["Datetime"] = pd.to_datetime(df["Datetime"])

# Ensure chronological order
df = df.sort_values("Datetime").reset_index(drop=True)

print("PowerPulse Streaming Simulator")
print(f"Total readings: {len(df)}")

# Send readings one by one
for _, row in df.iterrows():

    reading = {
        "timestamp": row["Datetime"].isoformat(),
        "temperature": float(row["Temperature"]),
        "humidity": float(row["Humidity"]),
        "wind_speed": float(row["WindSpeed"]),
        "general_diffuse_flows": float(row["GeneralDiffuseFlows"]),
        "diffuse_flows": float(row["DiffuseFlows"]),
        "consumption": float(row["PowerConsumption_Zone1"])
    }

    try:
        response = requests.post(
            API_URL,
            json=reading
        )

        if response.status_code == 200:

            result = response.json()

            if result.get("message") == "Prediction generated":
                if "predicted_consumption" in result:

                    print(
        f"Sent: {reading['timestamp']} | "
        f"Consumption: {reading['consumption']:.2f} | "
        f"Forecast: {result['predicted_consumption']:.2f} | "
        f"Peak Probability: "
        f"{result['peak_probability']:.2%} | "
        f"Risk: {result['peak_risk']} |"
        f"Anomaly: {result['anomaly_status']} | "
        f"Score: {result['anomaly_score']}"

    )
                else:
                    print(
                    f"Sent: {reading['timestamp']} | "
                    f"Consumption: {reading['consumption']:.2f} | "
                    f"Prediction: "
                    f"{result['predicted_consumption']:.2f}"
                )

            else:

                print(
                    f"Sent: {reading['timestamp']} | "
                    f"Consumption: {reading['consumption']:.2f} | "
                    f"{result.get('status')}"
                )

        else:

            print(
                f"API Error {response.status_code}: "
                f"{response.text}"
            )

    except requests.exceptions.ConnectionError:

        print("Could not connect to FastAPI.")
        break

    # Accelerated streaming
    time.sleep(2)