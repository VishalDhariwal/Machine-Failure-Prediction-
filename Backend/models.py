import joblib
import io
import csv
import numpy as np

# ==============================
# LOAD MODELS
# ==============================
stage1_bundle = joblib.load("Backend/ml-models/stage1_bundle7.pkl")
stage2_bundle = joblib.load("Backend/ml-models/stage2_bundle7.pkl")
iso_bundle = joblib.load("Backend/ml-models/iso_bundle.pkl")

stage1_model = stage1_bundle["model"]
stage1_features = stage1_bundle["feature_columns"]

stage2_model = stage2_bundle["model"]
stage2_features = stage2_bundle["feature_columns"]
failure_encoder = stage2_bundle["failure_encoder"]

iso_model = iso_bundle["model"]
iso_features = iso_bundle["feature_columns"]
iso_scaler = iso_bundle["scaler"]

# ==============================
# STATISTICAL LIMITS (mean, std)
# ==============================
LIMITS = {
    "Air_temperature__K_": (300.004930, 2.000259),
    "Process_temperature__K_": (310.005560, 1.483734),
    "Rotational_speed__rpm_": (1538.776100, 179.284096),
    "Torque__Nm_": (39.986910, 9.968934),
    "Tool_wear__min_": (107.951000, 63.654147),
}

# ==============================
# PREPROCESSING
# ==============================
def preprocess_data(data_list, feature_columns):
    result = []
    for d in data_list:
        row = []
        for col in feature_columns:
            val = d.get(col, 0)
            try:
                row.append(float(val))
            except (ValueError, TypeError):
                row.append(0.0)
        result.append(row)
    return np.array(result)

def encode_type_column(data_list):
    for d in data_list:
        if "Type" in d:
            t = str(d["Type"]).upper()
            d["Type_H"] = 1 if t == "H" else 0
            d["Type_L"] = 1 if t == "L" else 0
            d["Type_M"] = 1 if t == "M" else 0
            del d["Type"]
    return data_list

# ==============================
# STATISTICAL ANOMALY CHECK
# ==============================
def statistical_anomaly(data_dict, threshold=5):
    for col, (mean, std) in LIMITS.items():
        if col in data_dict:
            try:
                val = float(data_dict[col])
                z = abs(val - mean) / std
                if z > threshold:
                    return True
            except:
                continue
    return False

# ==============================
# SINGLE PREDICTION
# ==============================
def predict(data: dict):
    results = predict_batch([data.copy()])
    return results[0]

# ==============================
# BATCH PREDICTION
# ==============================
def predict_batch(data_list):
    if not data_list:
        return []

    encoded_data = [d.copy() for d in data_list]
    encoded_data = encode_type_column(encoded_data)

    # ----------------------
    # Stage 1
    # ----------------------
    X1 = preprocess_data(encoded_data, stage1_features)
    probs = stage1_model.predict_proba(X1)[:, 1]

    # ----------------------
    # Anomaly
    # ----------------------
    X_iso = preprocess_data(encoded_data, iso_features)
    X_scaled = iso_scaler.transform(X_iso)

    anomaly_scores = iso_model.decision_function(X_scaled)
    iso_flags = iso_model.predict(X_scaled)

    iso_anomalies = (iso_flags == -1)
    stat_anomalies = [statistical_anomaly(d) for d in encoded_data]

    # ----------------------
    # Risk and Decision
    # ----------------------
    results = []
    failed_indices = []
    failed_rows = []

    for i in range(len(encoded_data)):
        d = encoded_data[i]
        prob = float(probs[i])
        is_anomaly = bool(iso_anomalies[i] or stat_anomalies[i])
        anomaly_score = float(anomaly_scores[i])
        
        try:
            wear = float(d.get("Tool_wear__min_", 0))
        except:
            wear = 0.0
            
        wear_score = min(max(wear / 250, 0.0), 1.0)

        risk = (
            0.6 * prob +
            0.25 * int(is_anomaly) +
            0.15 * wear_score
        )

        level = "NORMAL"
        if prob >= 0.8:
            level = "CRITICAL"
            is_anomaly = True
            risk = max(risk, 0.85)
        elif is_anomaly:
            level = "CRITICAL"
            risk = max(risk, 0.8)
        elif risk >= 0.7:
            level = "CRITICAL"
        elif risk >= 0.4:
            level = "WARNING"

        failure_detected = (level == "CRITICAL")
        
        res_dict = {
            "failure_probability": prob,
            "failure_detected": failure_detected,
            "failure_type": None,
            "anomaly_score": anomaly_score,
            "is_anomaly": is_anomaly,
            "risk_score": float(risk),
            "risk_level": level
        }
        
        results.append(res_dict)
        
        if failure_detected:
            failed_indices.append(i)
            failed_rows.append(d)

    # ----------------------
    # Stage 2
    # ----------------------
    if failed_rows:
        X2 = preprocess_data(failed_rows, stage2_features)
        preds = stage2_model.predict(X2)
        failure_types = failure_encoder.inverse_transform(preds)
        for idx, ftype in zip(failed_indices, failure_types):
            results[idx]["failure_type"] = str(ftype)

    return results

# ==============================
# CSV PREDICTION
# ==============================
async def predict_csv_file(file):
    contents = await file.read()
    text = contents.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    data_list = list(reader)
    
    if not data_list:
        return []

    results = predict_batch(data_list)
    
    for d, res in zip(data_list, results):
        d.update(res)
        
    return data_list