import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import joblib
import os

# -------- CONFIG --------
MODEL_NAME = "xlm-roberta-base"
NUM_CATEGORIES = 8
NUM_URGENCIES = 3
MAX_LENGTH = 128

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# -------- MODEL ARCHITECTURE --------
class MultiTaskModel(nn.Module):
    def __init__(self, model_name, num_categories, num_urgencies):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size
        
        self.category_classifier = nn.Linear(hidden_size, num_categories)
        self.urgency_classifier = nn.Linear(hidden_size, num_urgencies)

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        pooled_output = outputs.last_hidden_state[:, 0]
        
        category_logits = self.category_classifier(pooled_output)
        urgency_logits = self.urgency_classifier(pooled_output)
        
        return category_logits, urgency_logits


# -------- LOAD COMPONENTS --------
def load_model():
    base_dir = os.path.dirname(__file__)

    model = MultiTaskModel(MODEL_NAME, NUM_CATEGORIES, NUM_URGENCIES)
    model.load_state_dict(
        torch.load(os.path.join(base_dir, "../final_multilingual_model.pt"), map_location=device)
    )
    model.to(device)
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    category_encoder = joblib.load(os.path.join(base_dir, "../category_encoder.pkl"))
    urgency_encoder = joblib.load(os.path.join(base_dir, "../urgency_encoder.pkl"))

    return model, tokenizer, category_encoder, urgency_encoder


# -------- INITIALIZE ON START --------
model, tokenizer, category_encoder, urgency_encoder = load_model()


# -------- PREDICTION FUNCTION --------
def predict(text: str):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=MAX_LENGTH
    ).to(device)

    with torch.no_grad():
        category_logits, urgency_logits = model(
            inputs["input_ids"],
            inputs["attention_mask"]
        )

    cat_probs = F.softmax(category_logits, dim=1)
    urg_probs = F.softmax(urgency_logits, dim=1)

    cat_confidence, cat_pred = torch.max(cat_probs, dim=1)
    urg_confidence, urg_pred = torch.max(urg_probs, dim=1)

    predicted_category = category_encoder.inverse_transform([cat_pred.item()])[0]
    predicted_urgency = urgency_encoder.inverse_transform([urg_pred.item()])[0]

    return {
        "category": predicted_category,
        "category_confidence": round(cat_confidence.item(), 4),
        "urgency": predicted_urgency,
        "urgency_confidence": round(urg_confidence.item(), 4)
    }
