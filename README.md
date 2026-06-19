# 🚀 AI Resume Analyzer

An AI-powered Resume Analyzer that helps job seekers evaluate resumes, improve ATS compatibility, identify missing skills, and receive intelligent recommendations for career growth.

## 🌟 Features

### 🔐 User Authentication

* User Registration & Login
* OTP Verification using Gmail SMTP
* Secure User Authentication

### 📄 Resume Analysis

* Upload Resume (PDF/DOCX)
* Automatic Resume Text Extraction
* Resume Score Calculation
* ATS Compatibility Score
* Resume Quality Assessment

### 🤖 AI-Powered Insights

* Skill Extraction
* Missing Skills Detection
* Job Role Matching
* Resume Improvement Suggestions
* Keyword Analysis

### 📊 Interactive Dashboard

* Resume Score Visualization
* ATS Score Display
* Skill Analysis Dashboard
* Performance Metrics

### ☁️ Cloud Integration

* Railway MySQL Database
* Streamlit Cloud Deployment
* Environment Variable Security

---

## 🛠️ Tech Stack

### Frontend

* Streamlit

### Backend

* Python

### Database

* MySQL
* Railway

### AI / Machine Learning

* Scikit-learn
* CountVectorizer
* Natural Language Processing (NLP)

### File Processing

* pdfplumber
* python-docx

### Authentication

* Gmail SMTP
* OTP Verification

### Version Control

* Git
* GitHub

---

## 📂 Project Structure

```text
AI_Resume_Analyzer/
│
├── app.py
├── auth.py
├── db.py
├── requirements.txt
├── README.md
├── .env
│
├── uploads/
├── resumes/
└── assets/
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI_Resume_Analyzer.git
cd AI_Resume_Analyzer
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

---

## ▶️ Run Application

```bash
streamlit run app.py
```

---

## 🌐 Deployment

### Streamlit Cloud

1. Push project to GitHub
2. Connect repository to Streamlit Cloud
3. Add Secrets in Streamlit Settings
4. Deploy Application

### Railway

1. Create Railway MySQL Database
2. Copy Database Credentials
3. Configure Environment Variables

---

## 🎯 Key Functionalities

* Resume Upload & Parsing
* ATS Score Analysis
* Resume Quality Assessment
* Skill Gap Analysis
* Job Role Recommendation
* OTP Email Verification
* Cloud Database Integration

---

## 📚 Libraries Used

```text
streamlit
mysql-connector-python
scikit-learn
pdfplumber
python-docx
python-dotenv
smtplib
```

---

## 🚀 Future Enhancements

* AI Interview Question Generator
* Resume Comparison System
* Resume Builder
* LinkedIn Profile Analyzer
* Multi-language Resume Analysis
* Advanced ATS Optimization
* AI Career Guidance Assistant

---

## 👨‍💻 Author

**Jayendra Pilla**

B.Tech – Computer Science & Artificial Intelligence

Passionate about AI, Machine Learning, Full Stack Development, and Cloud Technologies.

---

## 📄 License

This project is developed for educational and learning purposes.
## 🌐 Live Demo

🔗 Streamlit App:[ https://ai26resume.streamlit.app/ ]
Try the live application here:
- Upload Resume (PDF/DOCX)
- Get ATS Score
- Analyze Skills
- Match Job Roles
- Receive AI Suggestions
- Compare Resumes
