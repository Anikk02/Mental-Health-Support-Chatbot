# 🧠 Mental Health Support Chatbot

> AI-powered, safety-first conversational system for empathetic mental health support

---

## 🚀 Overview

The **Mental Health Support Chatbot** is an AI-driven conversational system designed to provide **empathetic, safe, and context-aware emotional support** to users experiencing stress, anxiety, or emotional distress.

With the increasing mental health challenges and limited access to professional care—especially in India—this project aims to bridge the gap using **responsible artificial intelligence**.

The system leverages:
- Transformer-based NLP models
- Emotion-aware response generation
- Real-time safety and crisis detection
- Secure and scalable full-stack architecture

> ⚠️ **Disclaimer:** This chatbot is not a replacement for professional therapists. It acts as a **non-clinical support tool** to encourage emotional expression and guide users toward professional help when necessary.

---

## 🌍 Problem Statement

Mental health issues such as stress, anxiety, and depression have significantly increased due to:
- Academic and professional pressure
- Rapid urbanization
- Social isolation and digital overload

Despite increased awareness:
- India faces a **70–90% treatment gap**
- Fewer than **3,500 clinical psychologists** are available nationwide
- Access to affordable and stigma-free support remains limited

### 🎯 Goal

To design and develop an **AI-powered chatbot** that:
- Understands emotional context
- Generates empathetic responses
- Detects crisis situations in real-time
- Ensures safety, privacy, and ethical compliance

---

## 🎯 Objectives

- Build an **emotion-aware conversational AI model**
- Integrate **sentiment and emotion analysis**
- Implement **safety, moderation, and crisis detection**
- Provide **secure authentication (JWT + 2FA)**
- Enable **conversation history and mood tracking**

---

## 🧠 Key Features

### 💬 Intelligent Conversation
- Fine-tuned **T5 Transformer model**
- Contextually relevant and empathetic responses
- Semantic understanding using embeddings

### ❤️ Emotion Awareness
- Real-time emotion detection
- Supports emotional states:
  - Stress
  - Anxiety
  - Sadness
  - Emotional distress

### 🛡️ Safety & Crisis Detection
- Detects:
  - Self-harm intent
  - Suicidal ideation
  - Harmful language
- Applies:
  - Toxicity filtering
  - Safe response generation
- Provides:
  - Guidance toward professional help

### 🔐 Secure User Management
- JWT-based authentication
- Email-based **2-Factor Authentication (2FA)**
- Secure session handling

### 📊 Personalization & Tracking
- Conversation history storage
- Mood tracking dashboard
- Emotional trend analysis

---

## 🏗️ System Architecture
```
User Input
↓
Authentication (JWT + 2FA)
↓
Text Preprocessing
↓
Embedding Generation (SentenceTransformers)
↓
Emotion & Sentiment Analysis
↓
T5 Transformer Response Generation
↓
Safety & Crisis Detection Layer
↓
Response Validation
↓
Output to User
↓
Conversation Storage + Mood Tracking
```

---

## ⚙️ Tech Stack

### 🧠 AI / ML
- Hugging Face Transformers (T5)
- SentenceTransformers (Embeddings)
- PyTorch

### 🖥️ Backend
- Python
- Flask / FastAPI
- JWT Authentication

### 🌐 Frontend
- React.js
- Tailwind CSS

### 🗄️ Database
- MongoDB (NoSQL)

### 📊 Tools
- Pandas
- NumPy
- Matplotlib

---

## 📂 Dataset

### 📌 Source
- **MentalChat16 Dataset (Hugging Face)**

### 📊 Size
- ~16,000 conversation pairs

### 🧾 Attributes
- `user_input`
- `chatbot_output`
- `emotion_labels`
- `user_sentiment`
- `response_empathy_score`
- `risky_term_count`
- `risk_intensity_score`
- `safety_flag`

---

## 🔍 System Modules

### 1. Authentication Module
- User registration & login
- Email verification
- 2FA security

### 2. Chat Interaction Module
- User message handling
- Session continuity

### 3. AI Processing Module
- Text preprocessing
- Embedding generation
- Emotion detection
- T5 response generation

### 4. Safety & Moderation Module
- Crisis detection
- Risk scoring
- Safe response filtering

### 5. Database Module
- User data
- Chat history
- Mood logs

---

## 🧪 Evaluation Metrics

| Metric | Value |
|--------|------|
| Context Similarity | 0.793 |
| Semantic Similarity | 0.765 |
| BERTScore (F1) | 0.905 |
| Emotional Alignment | 0.793 |
| Perplexity | 17.84 |
| Toxicity Score | 0.0024 |

### 📊 Analysis

- High **BERTScore** → strong semantic quality  
- High **emotional alignment** → effective empathy modeling  
- Low **perplexity** → fluent responses  
- Extremely low **toxicity** → safe system  

---

## 🖥️ Implementation Details

### 🔧 Backend
- Built with **FastAPI / Flask**
- Handles:
  - Authentication
  - AI processing
  - Safety checks

### 🎨 Frontend
- React-based UI
- Tailwind CSS styling
- Features:
  - Chat interface
  - History panel
  - Mood tracker

### 🗄️ Database
- MongoDB stores:
  - User data
  - Chat history
  - Mood tracking

---

## 📊 System Flow

1. User authentication (JWT + 2FA)
2. Message input
3. Preprocessing & embedding
4. Emotion detection
5. Response generation (T5)
6. Safety validation
7. Response delivery
8. Data storage & mood update

---

## 📸 Features Preview

- Secure login with 2FA  
- Real-time chatbot interaction  
- Crisis detection alerts  
- Conversation history view  
- Mood tracking dashboard  

---

## ⚠️ Limitations

- Single-turn context (no long-term memory)
- Dataset dependency (MentalChat16 only)
- English-only support
- Text-based interaction only
- Non-clinical system (no diagnosis)

---

## 🚀 Future Scope

- 🔁 Long-term memory integration
- 🌍 Multilingual & code-mixed support
- 🎤 Voice-based interaction (ASR + TTS)
- 🤝 Human-in-the-loop support
- 📱 Mobile app deployment
- 🧠 Advanced personalization

---

## 🧠 What Makes This Project Unique

- Combines **AI + Safety + Full-stack engineering**
- Focus on **ethical AI in mental healthcare**
- Includes **emotion modeling + crisis detection**
- Evaluated using **both NLP and psychological metrics**
- Designed as a **real-world scalable system**

---

## 📁 Project Structure
```
mental-health-chatbot/
│
├── backend/
│ ├── models/
│ ├── routes/
│ ├── services/
│ └── main.py
│
├── frontend/
│ ├── components/
│ ├── pages/
│ └── App.js
│
├── data/
├── notebooks/
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

```bash
# Clone repository
git clone https://github.com/your-username/mental-health-chatbot.git

cd mental-health-chatbot

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload

# Run frontend
cd frontend
npm install
npm start

📄 License
This project is for educational and research purposes only.

👨‍💻 Author
Aniket Paswan

Designed and developed complete system

Built AI pipeline, safety system, and architecture

Performed evaluation and optimization

Developed frontend and backend integration

🙏 Acknowledgments
Hugging Face for transformer models

MentalChat16 dataset contributors

Open-source community