# 🪪 VeriKTP AI

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)
![Gemini](https://img.shields.io/badge/Gemini-Vision-orange)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![Render](https://img.shields.io/badge/Deploy-Render-purple)

An AI-powered web application for **Indonesian KTP verification** using **Google Gemini Vision**, OCR, and Business Rules Validation.

🌐 **Live Demo**

https://ai-ktp-project-app.onrender.com

---

## ✨ Features

- 📄 AI-based KTP document classification
- 🔍 OCR extraction using Google Gemini Vision
- ✅ Business Rules Validation
- 🗂 Verification History
- 📊 Export verification results to CSV
- 💾 SQLite database integration
- 🌐 Web interface powered by FastAPI

---

## 🛠 Tech Stack

| Category   | Technology            |
| ---------- | --------------------- |
| Backend    | FastAPI               |
| AI Model   | Google Gemini Flash   |
| OCR        | Gemini Vision         |
| Database   | SQLite + SQLAlchemy   |
| Frontend   | HTML, CSS, JavaScript |
| Language   | Python                |
| Deployment | Render                |

---

## 📂 Project Structure

```text
ai-ktp-project/
│
├── backend/
│   ├── ai_service.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── validation.py
│   └── main.py
│
├── static/
├── templates/
├── tests/
├── data/
│   └── .gitkeep
│
├── main.py
├── requirements.txt
├── README.md
└── .env.example
```

---

## 🚀 Installation

Clone this repository

```bash
git clone https://github.com/nadiraaini77/ai-ktp-project-app.git
cd ai-ktp-project-app
```

Create virtual environment

```bash
python -m venv .venv
```

Activate environment

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create `.env`

```env
OPENROUTER_API_KEY=your_api_key
MODEL_CLASSIFICATION=google/gemini-flash-latest
MODEL_OCR=google/gemini-flash-latest
APP_NAME=VeriKTP AI
DB_PATH=data/database.db
```

Run application

```bash
python -m uvicorn main:app --reload
```

Open

```
http://127.0.0.1:8000
```

---

## 📸 Application Preview

### Home

_(Add screenshot)_

### Verification Result

_(Add screenshot)_

### Database History

_(Add screenshot)_

---

## 🔍 Verification Workflow

```text
Upload Image
      │
      ▼
AI Classification
      │
      ▼
OCR Extraction
      │
      ▼
Business Rules Validation
      │
      ▼
Save to SQLite Database
      │
      ▼
History & CSV Export
```

---

## 🧪 Testing

The application has been tested using various document images including:

- Indonesian KTP
- Non-KTP documents

The evaluation covers:

- Document classification
- OCR extraction
- Business Rules Validation
- Database storage
- CSV export functionality

---

## 📄 License

MIT License

---

## 👩‍💻 Author

**Nadira Aini**

GitHub

https://github.com/nadiraaini77
