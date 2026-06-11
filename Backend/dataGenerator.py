import random
import math

MACHINE_TYPES = ["H", "L", "M"]

LIMITS = {
    "Air_temperature__K_": (295.3, 304.5, 300.0, 2.0),
    "Process_temperature__K_": (305.7, 313.8, 310.0, 1.48),
    "Rotational_speed__rpm_": (1168, 2886, 1538, 179),
    "Torque__Nm_": (3.8, 76.6, 39.9, 9.96),
    "Tool_wear__min_": (0, 253, 108, 63),
}

state = {
    "Air_temperature__K_": 300.0,
    "Process_temperature__K_": 310.0,
    "Rotational_speed__rpm_": 1538.0,
    "Torque__Nm_": 39.9,
    "Tool_wear__min_": 0,
    "machineType": random.choice(MACHINE_TYPES),

    # NEW: lifecycle state
    "health_state": "HEALTHY",
    "cycle_counter": 0,
}


def clamp(v, min_v, max_v):
    return max(min_v, min(max_v, v))


def noise(std):
    u = random.random()
    v = random.random()
    z = math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * v)
    return z * std


def update_health_state():
    """
    Simulates machine degradation lifecycle
    """
    global state

    wear = state["Tool_wear__min_"]

    if wear < 80:
        state["health_state"] = "HEALTHY"

    elif wear < 160:
        state["health_state"] = "DEGRADING"

    elif wear < 240:
        state["health_state"] = "CRITICAL"

    else:
        state["health_state"] = "MAINTENANCE"


def generate_point():
    global state
    state["cycle_counter"] += 1

    drift = 0.15

    # ─────────────────────────────
    # NORMAL SENSOR DRIFT
    # ─────────────────────────────
    state["Air_temperature__K_"] = clamp(
        state["Air_temperature__K_"] + noise(LIMITS["Air_temperature__K_"][3] * drift),
        *LIMITS["Air_temperature__K_"][:2]
    )

    state["Process_temperature__K_"] = clamp(
        state["Process_temperature__K_"] + noise(LIMITS["Process_temperature__K_"][3] * drift),
        *LIMITS["Process_temperature__K_"][:2]
    )

    state["Rotational_speed__rpm_"] = clamp(
        state["Rotational_speed__rpm_"] + noise(LIMITS["Rotational_speed__rpm_"][3] * drift),
        *LIMITS["Rotational_speed__rpm_"][:2]
    )

    state["Torque__Nm_"] = clamp(
        state["Torque__Nm_"] + noise(LIMITS["Torque__Nm_"][3] * drift),
        *LIMITS["Torque__Nm_"][:2]
    )

    # ─────────────────────────────
    # TOOL WEAR BEHAVIOR (KEY CHANGE)
    # ─────────────────────────────
    state["Tool_wear__min_"] += 1

    update_health_state()

    # ─────────────────────────────
    # REALISTIC FAILURE + RESET
    # ─────────────────────────────
    if state["health_state"] == "MAINTENANCE":
        # simulate downtime / repair
        state["Tool_wear__min_"] = 0
        state["machineType"] = random.choice(MACHINE_TYPES)

        # reset slightly noisy baseline (not perfect reset like before)
        state["Air_temperature__K_"] = 300 + random.uniform(-2, 2)
        state["Process_temperature__K_"] = 310 + random.uniform(-2, 2)
        state["Rotational_speed__rpm_"] = 1538 + random.uniform(-50, 50)
        state["Torque__Nm_"] = 39 + random.uniform(-5, 5)

        state["health_state"] = "HEALTHY"

    t = state["machineType"]

    return {
        "Air_temperature__K_": round(state["Air_temperature__K_"], 2),
        "Process_temperature__K_": round(state["Process_temperature__K_"], 2),
        "Rotational_speed__rpm_": int(state["Rotational_speed__rpm_"]),
        "Torque__Nm_": round(state["Torque__Nm_"], 2),
        "Tool_wear__min_": state["Tool_wear__min_"],

        "Type_H": 1 if t == "H" else 0,
        "Type_L": 1 if t == "L" else 0,
        "Type_M": 1 if t == "M" else 0,

        # NEW FEATURE (VERY USEFUL FOR DEBUG/ML)
        "health_state": state["health_state"],

        "_tick": state["cycle_counter"],
    }


def reset_generator():
    global state
    state = {
        "Air_temperature__K_": 300.0,
        "Process_temperature__K_": 310.0,
        "Rotational_speed__rpm_": 1538.0,
        "Torque__Nm_": 39.9,
        "Tool_wear__min_": 0,
        "machineType": random.choice(MACHINE_TYPES),
        "health_state": "HEALTHY",
        "cycle_counter": 0,
    }