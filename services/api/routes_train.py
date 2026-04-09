from fastapi import FastAPI
from services.api.schemas import Data
from core.preprocessing import loader, transform
import numpy as np
from fastapi.encoders import jsonable_encoder

app = FastAPI()

@app.get("/")
def root():
    return {"message": "ok"}

@app.post("/data")
def post_data(data: Data):
    module  = loader.DataLoader
    raw_data = module.read_file(data.model_dump()["dataset"])
    data_val = module.validate_data(raw_data)
    result = (
        transform.DataTransformer(data_val)
        .coerce_types()
        .fill_nulls()
    )

    safe_data = result.to_json_safe()

    return jsonable_encoder({
        "status": "success",
        "status_code": 200,
        "message": "Data received and processed successfully",
        "received": safe_data
    })
