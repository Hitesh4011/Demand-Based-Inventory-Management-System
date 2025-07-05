from fastapi import FastAPI
from pydantic import BaseModel

# Create FastAPI instance
app = FastAPI()

# Sample input model using Pydantic
class DemandInput(BaseModel):
    product_id: int
    week: int

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}

# Test POST endpoint
@app.post("/predict-demand")
def predict_demand(data: DemandInput):
    # Dummy logic for testing
    predicted_values = [100, 110, 120, 130, 140]
    return {
        "product_id": data.product_id,
        "current_week": data.week,
        "predicted_demand": predicted_values
    }
