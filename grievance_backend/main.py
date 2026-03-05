from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

from ai.duplicate import check_duplicate


# CREATE APP FIRST
app = FastAPI()


# THEN ADD MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load model
model_path = "./grievance_model"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)


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

    duplicate_info = check_duplicate(input.text)

    return {
        "text": input.text,
        "predicted_category": predicted_label,
        "category_confidence": confidence_score,
        "urgency": "Low",
        "urgency_confidence": 1,
        "assigned_department": assigned_department,
        "duplicate_info": duplicate_info
    }
