from fastapi import FastAPI, UploadFile, File
from Backend.schema import MachineData, PredictionResponse
from Backend.models import predict, predict_csv_file
from fastapi.middleware.cors import CORSMiddleware
from Backend.dataGenerator import generate_point
from fastapi import WebSocket
import asyncio


app = FastAPI(
    title="Machine Failure Prediction API",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API is running 🚀"}


@app.post("/predict", response_model=PredictionResponse)
def predict_failure(data: MachineData):
    return predict(data.dict())


@app.post("/predict_csv")
async def predict_csv(file: UploadFile = File(...)):
    return await predict_csv_file(file)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            point = generate_point()

            result = predict(point)

            await ws.send_json({
                "data": point,
                "prediction": result
            })

            await asyncio.sleep(1)

    except Exception as e:
        print("WebSocket closed:", e)
    finally:
        await ws.close()