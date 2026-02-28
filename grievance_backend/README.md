# 🇮🇳 AI-Powered Multilingual Public Grievance Intelligence System

## 🚀 Overview

This project is a cloud-deployable AI system designed to automatically classify, prioritize, and route public grievances across departments in India.

The system leverages multilingual transformer models, multi-task learning, and cloud-native architecture to streamline grievance intake and resolution.

---

## 🧠 Core AI Capabilities

- Multilingual Text Classification (XLM-R)
- Multi-Task Learning:
  - Category Prediction
  - Urgency Prediction
- Confidence Scoring
- Automated Department Routing
- (Planned) Duplicate Detection via Sentence-BERT
- (Planned) Voice Input via Whisper

---

## 🏗 System Architecture

User Input (Text / Voice)
        ↓
Language Detection
        ↓
Transformer Encoder (XLM-R)
        ↓
Multi-Task Heads
   ├── Category Classification
   └── Urgency Prediction
        ↓
Routing Logic
        ↓
Database Storage
        ↓
Admin Dashboard

---

## 📂 Project Structure
