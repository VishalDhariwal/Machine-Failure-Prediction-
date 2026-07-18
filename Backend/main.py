from fastapi import (
    FastAPI,
    UploadFile,
    File,
    WebSocket
)
import traceback
from fastapi import HTTPException

from fastapi.middleware.cors import CORSMiddleware

import asyncio

from Backend.schema import (
    MachineData,
    PredictionResponse,
    ChatRequest,
    ChatResponse
)

from Backend.models import (
    predict,
    predict_csv_file
)

from Backend.dataGenerator import generate_point

# AI Bot
from Backend.AI_Bot.src.graph import graph


LATEST_RESULT = None


app = FastAPI(
    title="Machine Failure Prediction API",
    version="1.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://your-app.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "API is running 🚀"
    }


# --------------------------------------------------
# Single Prediction
# --------------------------------------------------

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict_failure(data: MachineData):

    return predict(data.dict())


# --------------------------------------------------
# CSV Prediction
# --------------------------------------------------

@app.post("/predict_csv")
async def predict_csv(
    file: UploadFile = File(...)
):

    return await predict_csv_file(file)


# --------------------------------------------------
# WebSocket Streaming
# --------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    global LATEST_RESULT

    await ws.accept()

    try:

        while True:

            point = generate_point()

            result = predict(point)

            LATEST_RESULT = {
                "data": point,
                "prediction": result
            }

            await ws.send_json(
                LATEST_RESULT
            )

            await asyncio.sleep(1)

    except Exception as e:

        print(
            "WebSocket closed:",
            e
        )


# --------------------------------------------------
# Latest Prediction
# --------------------------------------------------

@app.get("/latest")
def get_latest():

    global LATEST_RESULT

    if LATEST_RESULT is None:

        return {
            "status": "no data yet"
        }

    return LATEST_RESULT


# --------------------------------------------------
# AI CHAT
# --------------------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest
):

    try:

        result = graph.invoke(
            {
                "user_question":
                    request.question,

                "machine_state":
                    request.machine_state
            }
        )

        return {
            "answer":
                result["answer"]
        }

    except Exception as e:
        print("\n========== CHAT ERROR ==========")
        traceback.print_exc()
        print("================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(e) or repr(e)
        )
