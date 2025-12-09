# ✨ Adaptive Study Game — AI-Powered Learning Platform

### Built by: **Jada Henderson**
Mississippi State University | Senior Capstone  
📧 Contact: [MSU Email Required for Game Login]

---

## 🧠 Project Overview

The Adaptive Study Game is an **AI-driven personalized tutoring tool** designed to help students improve learning outcomes through:

✔ Reinforcement Learning  
✔ Naive Bayes performance prediction  
✔ K-Means clustering for learner classification  
✔ Game-based engagement

The more a student plays, the smarter the system becomes  
— adjusting question difficulty and selecting what they should learn next!

---

## 🎮 Features

| Feature | AI Technique | Benefit |
|--------|--------------|--------|
| Adaptive question selection | Reinforcement Learning (contextual bandit) | Personalized challenge level |
| Predict learner performance | Naive Bayes Classifier | Builds confidence with accurate risk control |
| Identify learning style clusters | K-Means + Silhouette Score | Tailored study strategies |
| Live learning analytics dashboard | Streamlit | Progress visualization |
| Custom question builder | User input | Upload personal study material |

---

## 🔬 AI + Data Science Components

📌 Reinforcement: Difficulty increases when student succeeds  
📌 Naive Bayes: Predicts success probability  
📌 KMeans: Clusters based on learning patterns  
📌 Real-time performance metrics stored per user  
📌 Data export (.csv) for academic evaluation

| Data Logged | Type |
|------------|------|
| Subject | Categorical |
| Question Type | Categorical |
| Difficulty | Easy → Hard |
| Correctness | Binary |
| Response Time | Float |
| Timestamp | Float |
| Email/Name | Identifier |

**No personal data collected beyond MSU email for study validation.**

---

## 📊 Demo Screenshots

> *Will automatically update once live deployment is completed*

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **scikit-learn**
- **pandas + numpy**
- **matplotlib**
- **Reinforcement Learning Theory**

---

## 🚀 Deployment

### Local

```bash
pip install -r requirements.txt
streamlit run app.py
