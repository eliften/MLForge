from pydantic import BaseModel

class Data(BaseModel):
    name: str
    type: str
    models: str
    dataset: str
    test_size: float
    random_state: int
    target: str
    features: list
