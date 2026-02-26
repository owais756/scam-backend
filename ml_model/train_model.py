import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

# Load dataset (NO HEADER)
data = pd.read_csv("../../datasets/raw/spam.csv", header=None)

# Column mapping
data.columns = ["label", "message", "extra1", "extra2", "extra3"]

# Use only label + message
X = data["message"]
y = data["label"]

# Convert text to numbers
vectorizer = TfidfVectorizer()
X_vector = vectorizer.fit_transform(X)

# Train model
model = LogisticRegression()
model.fit(X_vector, y)

# Save model
pickle.dump(model, open("scam_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model trained successfully!")