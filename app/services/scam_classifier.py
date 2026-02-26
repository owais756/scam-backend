import os
import pickle

# Get base directory (backend/)
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

model_path = os.path.join(BASE_DIR, "ml_model", "scam_model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "ml_model", "vectorizer.pkl")

# Load model safely
with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)


def predict_message(message: str):
    vec = vectorizer.transform([message])
    prediction = model.predict(vec)
    probability = model.predict_proba(vec)

    return {
        "prediction": prediction[0],
        "confidence": float(max(probability[0]))
    }