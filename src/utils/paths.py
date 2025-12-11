import joblib
import os

MODEL_PATH = "model/model.pkl"
ENCODER_PATH = "model/encoders.pkl"
DATA_PATH = "data/dataset.xlsx"

# Load model & encoder jika ada
model = None
encoders = None
if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODER_PATH)
