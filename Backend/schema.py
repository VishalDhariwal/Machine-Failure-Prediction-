from pydantic import BaseModel, model_validator
from typing import Dict, Any

class MachineData(BaseModel):
    Air_temperature__K_: float
    Process_temperature__K_: float
    Rotational_speed__rpm_: float
    Torque__Nm_: float
    Tool_wear__min_: float
    
    Type_H: int
    Type_L: int
    Type_M: int

    @model_validator(mode="after")
    def check_one_hot(self):
        if (self.Type_H + self.Type_L + self.Type_M) != 1:
            raise ValueError("Exactly one Type must be 1")
        return self


class PredictionResponse(BaseModel):
    failure_probability: float
    failure_detected: bool
    failure_type: str | None

    # ✅ ADD THESE
    anomaly_score: float
    is_anomaly: bool




class ChatRequest(BaseModel):
    question: str
    machine_state: Dict[str, Any]


class ChatResponse(BaseModel):
    answer: str