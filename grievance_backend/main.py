from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import torch.nn.functional as F

app = FastAPI()

# Load model and tokenizer
model_path = "./grievance_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Label mapping (IMPORTANT: match your training order)
labels = [
    "Education",
    "Electricity",
    "Health Services",
    "Pension & Social Welfare",
    "Roads & Infrastructure",
    "Sanitation",
    "Telecommunications",
    "Water Supply"
]
department_mapping = {
    "Water Supply": "Water Authority",
    "Electricity": "Electricity Board",
    "Roads & Infrastructure": "Municipal Corporation",
    "Health Services": "Health Department",
    "Education": "Education Department",
    "Sanitation": "Sanitation Department",
    "Telecommunications": "Telecom Authority",
    "Pension & Social Welfare": "Social Welfare Department"
}


class TextInput(BaseModel):
    text: str

@app.post("/predict")
def predict(input: TextInput):
    inputs = tokenizer(
        input.text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probs = F.softmax(logits, dim=1)

    confidence, prediction = torch.max(probs, dim=1)

    predicted_label = labels[prediction.item()]
    confidence_score = round(confidence.item(), 4)

    assigned_department = department_mapping[predicted_label]

    return {
        "text": input.text,
        "predicted_category": predicted_label,
        "confidence": confidence_score,
        "assigned_department": assigned_department
    }


