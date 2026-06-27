# 🤖 AI Interview Coach

> **Practice. Improve. Succeed.**

An AI-powered interview preparation platform that helps job seekers practice mock interviews, analyze resumes, and get personalized career guidance — built with Streamlit and powered by Groq's LLaMA 3.3 70B model.

🔗 **Live Demo:** [Click Here](https://ai-interview-coach-7f55svbstrzwgcbvbu497f.streamlit.app/)

---

## ✨ Features

### 🎤 Mock Interview
- Choose your domain, difficulty, and interview mode
- AI generates 10 real interview questions one by one
- Get instant feedback on every answer:
  - Technical Score
  - Communication Score
  - Confidence Score
  - Relevance Score
  - Grammar Score
- Works for **any domain** — Tech, Non-Tech, Medical, Finance, and more

### 📄 Resume Analyzer
- Upload your PDF resume
- AI extracts and analyzes:
  - Skills, Education, Experience, Projects
  - Strengths & Weaknesses
  - Missing Skills Suggestions
  - Resume Summary
- ATS Score with improvement tips

### 🔍 ATS Checker
- Check if your resume is ATS-friendly
- Keyword analysis
- Formatting issue detection
- Actionable improvement suggestions

### 🎯 Career Coach
- Personalized career recommendations
- Skill gap analysis
- Step-by-step learning roadmap
- Recommended courses & projects

### ✉️ Cover Letter Generator
- Job-specific cover letter in seconds
- Editable output
- Download as text file

### 📊 Analytics Dashboard
- Total interviews & average score
- Best performance & weakest area
- Score trend chart (last 10 interviews)
- Domain-wise performance breakdown
- Skill strength donut chart

### 📜 Interview History
- Complete history of all past interviews
- Domain, mode, difficulty, score, date

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Streamlit** | Frontend UI & Deployment |
| **Groq API** | AI Engine (Fast Inference) |
| **LLaMA 3.3 70B** | Language Model |
| **SQLite + SQLAlchemy** | Database |
| **pdfplumber** | PDF Text Extraction |
| **Plotly** | Charts & Visualizations |
| **Werkzeug** | Password Hashing |
| **Python** | Backend Logic |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ai-interview-coach.git
cd ai-interview-coach
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up API Key
Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free API key at: [console.groq.com](https://console.groq.com)

### 4. Run the app
```bash
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Push code to GitHub
2. Go to [streamlit.io](https://streamlit.io) → New App
3. Select your repo and `app.py`
4. Add secret in **Settings → Secrets**:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```
5. Deploy! 🎉

---

## 📁 Project Structure

```
ai-interview-coach/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
└── .env               # API keys (not committed)
```

---

## 🎯 Supported Domains (40+)

| Category | Domains |
|---|---|
| 🤖 AI/Data | AI/ML, Data Science, Machine Learning, Deep Learning |
| 💻 Programming | Python, Java, C++, JavaScript, TypeScript |
| 🌐 Web | Frontend, Backend, Full Stack, React, Node.js, Django |
| ⚙️ CS Core | DSA, System Design, Database/SQL, DevOps, Cloud, Cybersecurity |
| 📱 Mobile | Android Development, iOS Development |
| 💼 Non-Tech | HR, Business Analyst, Product Manager, Finance, Marketing |
| 🎨 Design | UI/UX Design, Graphic Design |
| 🌍 General | General/Mixed, Fresher/Entry Level |

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key (get free at console.groq.com) |

---

## 👩‍💻 Built By

**Amna Iqbal**
- GitHub: [@amnaiqbal0112](https://github.com/amnaiqbal0112)
- LinkedIn: (www.linkedin.com/in/amna-iqbal-119126389)



---

## ⭐ Show Your Support

If you found this project helpful, please give it a **star** ⭐ on GitHub!

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
