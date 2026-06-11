import joblib
import pandas as pd
import io

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
def preprocess_df(df, feature_columns):
    df = df.reindex(columns=feature_columns, fill_value=0)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    return df


def encode_type_column(df):
    if "Type" not in df.columns:
        return df

    df["Type"] = df["Type"].astype(str).str.upper()

    df["Type_H"] = (df["Type"] == "H").astype(int)
    df["Type_L"] = (df["Type"] == "L").astype(int)
    df["Type_M"] = (df["Type"] == "M").astype(int)

    return df.drop(columns=["Type"])


# ==============================
# STATISTICAL ANOMALY CHECK
# ==============================
def statistical_anomaly(df, threshold=5):
    for col, (mean, std) in LIMITS.items():
        if col in df.columns:
            try:
                value = float(df.iloc[0][col])
                z = abs(value - mean) / std
                if z > threshold:
                    return True
            except:
                continue
    return False


# ==============================
# ANOMALY DETECTION
# ==============================
def get_anomaly(df):
    X = preprocess_df(df.copy(), iso_features)
    X_scaled = iso_scaler.transform(X)

    scores = iso_model.decision_function(X_scaled)
    flags = iso_model.predict(X_scaled)

    iso_anomaly = (flags[0] == -1)
    stat_anomaly = statistical_anomaly(df)

    return scores, (iso_anomaly or stat_anomaly)


# ==============================
# SINGLE PREDICTION
# ==============================
def predict(data: dict):

    df = pd.DataFrame([data])
    df = encode_type_column(df)

    # ----------------------
    # Stage 1 Prediction
    # ----------------------
    X1 = preprocess_df(df.copy(), stage1_features)
    prob = stage1_model.predict_proba(X1)[0][1]

    # ----------------------
    # Anomaly Detection
    # ----------------------
    anomaly_score, is_anomaly = get_anomaly(df)

    # ----------------------
    # Risk Score
    # ----------------------
    wear = data.get("Tool_wear__min_", 0)
    wear_score = min(wear / 250, 1.0)

    risk = (
        0.6 * prob +
        0.25 * int(is_anomaly) +
        0.15 * wear_score
    )

    # ----------------------
    # FINAL DECISION ENGINE
    # ----------------------
    if prob >= 0.80:
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

    else:
        level = "NORMAL"

    result = {
        "failure_probability": float(prob),
        "failure_detected": level == "CRITICAL",
        "failure_type": None,
        "anomaly_score": float(anomaly_score[0]),
        "is_anomaly": bool(is_anomaly),
        "risk_score": float(risk),
        "risk_level": level
    }

    # ----------------------
    # Stage 2
    # ----------------------
    if result["failure_detected"]:
        X2 = preprocess_df(df.copy(), stage2_features)
        pred = stage2_model.predict(X2)[0]
        result["failure_type"] = failure_encoder.inverse_transform([pred])[0]

    return result


# ==============================
# BATCH PREDICTION
# ==============================
def predict_batch(df):

    df = encode_type_column(df.copy())

    # ----------------------
    # Stage 1
    # ----------------------
    X1 = preprocess_df(df.copy(), stage1_features)
    probs = stage1_model.predict_proba(X1)[:, 1]

    # ----------------------
    # Anomaly
    # ----------------------
    X_iso = preprocess_df(df.copy(), iso_features)
    X_scaled = iso_scaler.transform(X_iso)

    anomaly_scores = iso_model.decision_function(X_scaled)
    iso_flags = iso_model.predict(X_scaled)

    iso_anomaly = (iso_flags == -1)

    stat_anomaly = df.apply(
        lambda row: statistical_anomaly(pd.DataFrame([row])),
        axis=1
    )

    is_anomaly = iso_anomaly | stat_anomaly

    # ----------------------
    # Risk
    # ----------------------
    wear = df.get("Tool_wear__min_", pd.Series([0] * len(df)))
    wear_score = (wear / 250).clip(0, 1)

    risk = (
        0.6 * probs +
        0.25 * is_anomaly.astype(int) +
        0.15 * wear_score
    )

    # ----------------------
    # FINAL DECISION
    # ----------------------
    levels = []

    for i in range(len(df)):

        if probs[i] >= 0.8:
            levels.append("CRITICAL")

        elif is_anomaly.iloc[i]:
            levels.append("CRITICAL")

        elif risk.iloc[i] >= 0.7:
            levels.append("CRITICAL")

        elif risk.iloc[i] >= 0.4:
            levels.append("WARNING")

        else:
            levels.append("NORMAL")

    levels = pd.Series(levels)

    results = pd.DataFrame({
        "failure_probability": probs,
        "failure_detected": levels == "CRITICAL",
        "failure_type": None,
        "anomaly_score": anomaly_scores,
        "is_anomaly": is_anomaly,
        "risk_score": risk,
        "risk_level": levels
    })

    # ----------------------
    # Stage 2
    # ----------------------
    mask = results["failure_detected"]

    if mask.any():
        X2 = preprocess_df(df.loc[mask].copy(), stage2_features)
        preds = stage2_model.predict(X2)
        results.loc[mask, "failure_type"] = failure_encoder.inverse_transform(preds)

    return results


# ==============================
# CSV PREDICTION
# ==============================
async def predict_csv_file(file):

    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    result_df = predict_batch(df)

    final_df = pd.concat(
        [df.reset_index(drop=True), result_df],
        axis=1
    )

    return final_df.to_dict(orient="records")