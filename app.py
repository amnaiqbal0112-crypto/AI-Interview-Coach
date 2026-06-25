# ============================================
# AI Interview Coach - Streamlit App
# app.py
# ============================================

import streamlit as st
import json
import os
import uuid
import bcrypt
import pdfplumber
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
from fpdf import FPDF
import io

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark Theme CSS (matches UI mockup) ───────────────────────────────────────
st.markdown("""
<style>
  /* ---- Global ---- */
  html, body, [class*="css"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: 'Segoe UI', sans-serif;
  }
  .stApp { background-color: #0d1117; }

  /* ---- Sidebar ---- */
  [data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d;
  }
  [data-testid="stSidebar"] .stRadio label {
    color: #e6edf3 !important;
    font-size: 15px;
    padding: 6px 0;
  }

  /* ---- Metric Cards ---- */
  [data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px !important;
  }
  [data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 13px; }
  [data-testid="stMetricValue"] { color: #e6edf3 !important; font-size: 28px; font-weight: 700; }
  [data-testid="stMetricDelta"] { font-size: 13px; }

  /* ---- Cards / Containers ---- */
  .card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
  }
  .card h4 { color: #7c3aed; margin-bottom: 8px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
  .card p  { color: #e6edf3; margin: 4px 0; }

  /* ---- Buttons ---- */
  .stButton > button {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: opacity 0.2s;
  }
  .stButton > button:hover { opacity: 0.85; }

  /* ---- Inputs ---- */
  .stTextInput > div > div > input,
  .stTextArea textarea,
  .stSelectbox > div > div {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
  }

  /* ---- Score Badge ---- */
  .score-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
  }
  .score-high   { background: #1a3a2a; color: #3fb950; }
  .score-mid    { background: #3a2a00; color: #d29922; }
  .score-low    { background: #3a1a1a; color: #f85149; }

  /* ---- Section titles ---- */
  h1, h2, h3 { color: #e6edf3 !important; }
  .purple-accent { color: #7c3aed; }

  /* ---- Divider ---- */
  hr { border-color: #30363d !important; }

  /* ---- Upgrade Banner ---- */
  .upgrade-box {
    background: linear-gradient(135deg, #3b1f6e, #1e1b4b);
    border: 1px solid #7c3aed;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    margin-top: 24px;
  }
  .upgrade-box p { color: #c4b5fd; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ── Database Setup ────────────────────────────────────────────────────────────
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    resumes       = relationship("Resume", back_populates="user")
    sessions      = relationship("InterviewSession", back_populates="user")

class Resume(Base):
    __tablename__  = "resumes"
    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id        = Column(String, ForeignKey("users.id"))
    filename       = Column(String)
    raw_text       = Column(Text)
    skills         = Column(Text)
    education      = Column(Text)
    experience     = Column(Text)
    projects       = Column(Text)
    summary        = Column(Text)
    strengths      = Column(Text)
    weaknesses     = Column(Text)
    missing_skills = Column(Text)
    ats_score      = Column(Float)
    uploaded_at    = Column(DateTime, default=datetime.utcnow)
    user           = relationship("User", back_populates="resumes")

class InterviewSession(Base):
    __tablename__       = "interview_sessions"
    id                  = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id             = Column(String, ForeignKey("users.id"))
    domain              = Column(String)
    difficulty          = Column(String)
    mode                = Column(String)
    total_questions     = Column(Integer, default=0)
    overall_score       = Column(Float)
    technical_score     = Column(Float)
    communication_score = Column(Float)
    confidence_score    = Column(Float)
    started_at          = Column(DateTime, default=datetime.utcnow)
    ended_at            = Column(DateTime)
    user                = relationship("User", back_populates="sessions")
    questions           = relationship("InterviewQuestion", back_populates="session")

class InterviewQuestion(Base):
    __tablename__    = "interview_questions"
    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id       = Column(String, ForeignKey("interview_sessions.id"))
    question_no      = Column(Integer)
    question         = Column(Text)
    user_answer      = Column(Text)
    tech_score       = Column(Float)
    comm_score       = Column(Float)
    conf_score       = Column(Float)
    relevance_score  = Column(Float)
    grammar_score    = Column(Float)
    strengths        = Column(Text)
    improvements     = Column(Text)
    overall_rating   = Column(Float)
    feedback         = Column(Text)
    asked_at         = Column(DateTime, default=datetime.utcnow)
    session          = relationship("InterviewSession", back_populates="questions")

@st.cache_resource
def get_db():
    engine = create_engine("sqlite:///interview_coach.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

db = get_db()

# ── Claude Helper ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    api_key = ""
    # Try Streamlit secrets first
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    # Fallback to env variable
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found! Please add it in Streamlit Secrets.")
        st.stop()
    from groq import Groq
    return Groq(api_key=api_key)

def ask_claude(system: str, user_msg: str, max_tokens: int = 1500) -> str:
    """Uses Groq (llama-3.3-70b) — same interface as before."""
    try:
        client = get_groq_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_msg},
            ],
        )
        return resp.choices[0].message.content
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return "{}"  

# ── Session State Init ────────────────────────────────────────────────────────
for key, val in {
    "logged_in": False, "user_id": None, "user_name": "",
    "page": "Dashboard",
    "interview_session_id": None, "current_question": None,
    "current_question_id": None, "question_no": 0,
    "interview_active": False, "interview_ended": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Auth Helpers ──────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def score_badge(score: float) -> str:
    pct = score * 10 if score <= 10 else score
    cls = "score-high" if pct >= 75 else ("score-mid" if pct >= 50 else "score-low")
    return f'<span class="score-badge {cls}">{pct:.0f}%</span>'

# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## 🤖 AI Interview Coach")
        st.markdown("*Practice. Improve. Succeed.*")
        st.markdown("---")
        tab_login, tab_reg = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            email = st.text_input("Email", key="li_email")
            pw    = st.text_input("Password", type="password", key="li_pw")
            if st.button("Login", use_container_width=True):
                user = db.query(User).filter_by(email=email.lower()).first()
                if user and verify_password(pw, user.password_hash):
                    st.session_state.logged_in = True
                    st.session_state.user_id   = user.id
                    st.session_state.user_name = user.name
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

        with tab_reg:
            name  = st.text_input("Full Name", key="r_name")
            email = st.text_input("Email", key="r_email")
            pw    = st.text_input("Password", type="password", key="r_pw")
            if st.button("Create Account", use_container_width=True):
                if db.query(User).filter_by(email=email.lower()).first():
                    st.error("Email already registered.")
                elif not all([name, email, pw]):
                    st.warning("All fields required.")
                else:
                    u = User(name=name, email=email.lower(), password_hash=hash_password(pw))
                    db.add(u); db.commit()
                    st.success("Account created! Please login.")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def show_sidebar():
    with st.sidebar:
        st.markdown("### 🤖 AI Interview Coach")
        st.markdown(f"*Welcome, **{st.session_state.user_name}**!*")
        st.markdown("---")

        pages = [
            "📊 Dashboard", "📄 Resume Analyzer", "🎤 Mock Interview",
            "📜 Interview History", "📈 Analytics",
            "🎯 Career Coach", "🔍 ATS Checker", "✉️ Cover Letter",
            "👤 Profile", "⚙️ Settings",
        ]
        choice = st.radio("Navigation", pages, label_visibility="collapsed")
        st.session_state.page = choice.split(" ", 1)[1]

        st.markdown("---")
        st.markdown("""
        <div class="upgrade-box">
          <p>⭐ <strong>Upgrade to Pro</strong></p>
          <p>Voice interview, custom questions & more</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in","user_id","user_name","interview_active","interview_ended"]:
                st.session_state[k] = False if isinstance(st.session_state[k], bool) else None
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown(f"## Welcome back, {st.session_state.user_name}! 👋")
    st.markdown("*Ready to ace your next interview?*")
    st.markdown("---")

    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == st.session_state.user_id,
        InterviewSession.overall_score != None
    ).all()

    scores     = [s.overall_score * 10 for s in sessions]
    avg_score  = round(sum(scores) / len(scores), 1) if scores else 0
    best_score = round(max(scores), 1) if scores else 0
    this_week  = [s for s in sessions if s.started_at >= datetime.utcnow() - timedelta(days=7)]

    domain_scores = {}
    for s in sessions:
        domain_scores.setdefault(s.domain, []).append(s.overall_score * 10)
    domain_avg = {d: sum(v)/len(v) for d, v in domain_scores.items()}
    weakest    = min(domain_avg, key=domain_avg.get) if domain_avg else "System Design"

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Interviews", len(sessions), f"+{len(this_week)} this week")
    c2.metric("Average Score",    f"{avg_score}%", "Good progress 📈" if avg_score >= 70 else "Keep going 💪")
    c3.metric("Best Score",       f"{best_score}%", "Great job! 🎉" if best_score >= 85 else "")
    c4.metric("Weakest Area",     weakest, "Practice more")

    st.markdown("---")
    col_left, col_right = st.columns([1, 1])

    # Recent Interviews
    with col_left:
        st.markdown("#### 📋 Recent Interviews")
        recent = sorted(sessions, key=lambda x: x.started_at, reverse=True)[:5]
        if recent:
            for s in recent:
                pct = s.overall_score * 10
                delta = datetime.utcnow() - s.started_at
                time_label = f"{delta.days}d ago" if delta.days > 0 else "Today"
                st.markdown(f"""
                <div class="card">
                  <b>{s.domain}</b> &nbsp;
                  {score_badge(pct)}
                  <span style="color:#8b949e;float:right;font-size:12px">{time_label}</span>
                  <br><small style="color:#8b949e">{s.mode} · {s.difficulty}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No interviews yet. Start one from Mock Interview!")

    # Performance Chart
    with col_right:
        st.markdown("#### 📈 Performance Overview")
        if len(sessions) >= 2:
            sorted_s = sorted(sessions, key=lambda x: x.started_at)[-10:]
            df = pd.DataFrame({
                "Date":  [s.started_at.strftime("%d %b") for s in sorted_s],
                "Score": [round(s.overall_score * 10, 1) for s in sorted_s],
            })
            fig = px.line(df, x="Date", y="Score", markers=True,
                          color_discrete_sequence=["#7c3aed"])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e6edf3",
                yaxis=dict(range=[0, 100], gridcolor="#30363d"),
                xaxis=dict(gridcolor="#30363d"),
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complete 2+ interviews to see your trend!")

    # Bottom row
    st.markdown("---")
    b1, b2, b3 = st.columns(3)

    with b1:
        st.markdown("#### ⚡ Quick Actions")
        if st.button("📄 Analyze Resume",  use_container_width=True): st.session_state.page = "Resume Analyzer"; st.rerun()
        if st.button("🎤 Start Interview", use_container_width=True): st.session_state.page = "Mock Interview";  st.rerun()
        if st.button("🔍 ATS Checker",     use_container_width=True): st.session_state.page = "ATS Checker";     st.rerun()
        if st.button("🎯 Career Coach",    use_container_width=True): st.session_state.page = "Career Coach";    st.rerun()

    with b2:
        st.markdown("#### 🧠 Skill Strength")
        if domain_avg:
            fig2 = go.Figure(go.Pie(
                labels=list(domain_avg.keys()),
                values=list(domain_avg.values()),
                hole=0.55,
                marker_colors=["#7c3aed","#3b82f6","#10b981","#f59e0b","#06b6d4"],
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e6edf3",
                showlegend=True,
                margin=dict(l=0,r=0,t=0,b=0),
                height=230,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Complete interviews to see skill breakdown.")

    with b3:
        st.markdown("#### 🚀 Next Recommended")
        recs = [
            ("Practice " + weakest, "Your weakest area", "🎯"),
            ("HR Interview Practice", "Improve communication", "🗣️"),
            ("Advanced ML Questions", "Based on your profile", "🤖"),
        ]
        for title, sub, icon in recs:
            col_a, col_b = st.columns([3, 1])
            col_a.markdown(f"**{icon} {title}**\n\n*{sub}*")
            if col_b.button("Start", key=f"rec_{title}"):
                st.session_state.page = "Mock Interview"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# RESUME ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
def page_resume():
    st.markdown("## 📄 Resume Analyzer")
    st.markdown("Upload your PDF resume for AI-powered analysis.")
    st.markdown("---")

    uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if uploaded and st.button("🔍 Analyze Resume", use_container_width=True):
        with st.spinner("Extracting and analyzing your resume..."):
            raw_text = ""
            with pdfplumber.open(io.BytesIO(uploaded.read())) as pdf:
                for page in pdf.pages:
                    raw_text += (page.extract_text() or "") + "\n"

            system = (
                "You are an expert HR analyst. Analyze the resume and return a JSON object with keys: "
                "skills (list), education (list), experience (list), projects (list), "
                "summary (string), strengths (list), weaknesses (list), missing_skills (list). "
                "Return ONLY valid JSON, no extra text."
            )
            resp = ask_claude(system, raw_text, max_tokens=2000)
            try:    analysis = json.loads(resp)
            except: analysis = {}

            ats_sys = (
                "You are an ATS expert. Analyze resume for ATS compatibility and return JSON with: "
                "ats_score (float 0-100), formatting_issues (list), keywords_found (list), "
                "missing_keywords (list), improvement_suggestions (list). Return ONLY valid JSON."
            )
            ats_resp = ask_claude(ats_sys, raw_text, max_tokens=1500)
            try:    ats = json.loads(ats_resp)
            except: ats = {"ats_score": 0}

            resume = Resume(
                user_id=st.session_state.user_id,
                filename=uploaded.name,
                raw_text=raw_text,
                skills=json.dumps(analysis.get("skills", [])),
                education=json.dumps(analysis.get("education", [])),
                experience=json.dumps(analysis.get("experience", [])),
                projects=json.dumps(analysis.get("projects", [])),
                summary=analysis.get("summary", ""),
                strengths=json.dumps(analysis.get("strengths", [])),
                weaknesses=json.dumps(analysis.get("weaknesses", [])),
                missing_skills=json.dumps(analysis.get("missing_skills", [])),
                ats_score=ats.get("ats_score", 0),
            )
            db.add(resume); db.commit()
            st.session_state["last_resume"] = analysis
            st.session_state["last_ats"]    = ats

    if "last_resume" in st.session_state:
        analysis = st.session_state["last_resume"]
        ats      = st.session_state["last_ats"]
        st.success("✅ Analysis complete!")

        c1, c2, c3 = st.columns(3)
        c1.metric("ATS Score",        f"{ats.get('ats_score', 0):.0f}/100")
        c2.metric("Skills Found",     len(analysis.get("skills", [])))
        c3.metric("Missing Skills",   len(analysis.get("missing_skills", [])))

        t1, t2, t3, t4 = st.tabs(["📝 Summary", "🛠️ Skills", "💪 Strengths / Gaps", "🔍 ATS Details"])

        with t1:
            st.markdown(analysis.get("summary", "No summary generated."))
            st.markdown("**Education:**")
            for e in analysis.get("education", []): st.markdown(f"- {e}")
            st.markdown("**Experience:**")
            for e in analysis.get("experience", []): st.markdown(f"- {e}")

        with t2:
            cols = st.columns(3)
            for i, sk in enumerate(analysis.get("skills", [])):
                cols[i % 3].markdown(f"✅ {sk}")
            if analysis.get("missing_skills"):
                st.markdown("**Suggested Skills to Add:**")
                for sk in analysis["missing_skills"]: st.markdown(f"🔸 {sk}")

        with t3:
            ca, cb = st.columns(2)
            ca.markdown("**Strengths:**")
            for s in analysis.get("strengths", []): ca.markdown(f"✅ {s}")
            cb.markdown("**Areas to Improve:**")
            for w in analysis.get("weaknesses", []): cb.markdown(f"⚠️ {w}")

        with t4:
            st.metric("ATS Score", f"{ats.get('ats_score', 0):.0f}/100")
            st.markdown("**Keywords Found:**")
            st.markdown(", ".join(ats.get("keywords_found", [])) or "None")
            st.markdown("**Missing Keywords:**")
            for k in ats.get("missing_keywords", []): st.markdown(f"- {k}")
            st.markdown("**Improvement Tips:**")
            for tip in ats.get("improvement_suggestions", []): st.markdown(f"💡 {tip}")

# ══════════════════════════════════════════════════════════════════════════════
# MOCK INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_interview():
    st.markdown("## 🎤 Mock Interview")
    st.markdown("---")

    if not st.session_state.interview_active and not st.session_state.interview_ended:
        c1, c2, c3 = st.columns(3)
        domain     = c1.selectbox("Domain", ["AI/ML", "Data Science", "Web Development", "System Design", "HR", "Python", "DSA"])
        difficulty = c2.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
        mode       = c3.selectbox("Mode", ["Technical", "HR", "Mixed"])

        if st.button("🚀 Start Interview", use_container_width=True):
            session = InterviewSession(
                user_id=st.session_state.user_id,
                domain=domain, difficulty=difficulty, mode=mode
            )
            db.add(session); db.commit()

            q_text = ask_claude(
                "You are an expert interviewer. Generate a single opening interview question. Return ONLY the question.",
                f"Domain:{domain} Difficulty:{difficulty} Mode:{mode} Question 1",
                max_tokens=200
            )
            q = InterviewQuestion(session_id=session.id, question_no=1, question=q_text)
            db.add(q); db.commit()

            st.session_state.interview_session_id = session.id
            st.session_state.current_question     = q_text
            st.session_state.current_question_id  = q.id
            st.session_state.question_no          = 1
            st.session_state.interview_active     = True
            st.session_state.interview_ended      = False
            st.rerun()

    elif st.session_state.interview_active:
        session = db.query(InterviewSession).get(st.session_state.interview_session_id)
        answered = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == st.session_state.interview_session_id,
            InterviewQuestion.user_answer != None
        ).count()

        prog = min(answered / 10, 1.0)
        st.progress(prog, text=f"Question {st.session_state.question_no} / 10")
        st.markdown(f"""
        <div class="card">
          <h4>Question {st.session_state.question_no}</h4>
          <p style="font-size:17px">{st.session_state.current_question}</p>
        </div>
        """, unsafe_allow_html=True)

        answer = st.text_area("Your Answer", height=150, placeholder="Type your answer here...")
        col_sub, col_end = st.columns([2, 1])

        if col_sub.button("✅ Submit Answer", use_container_width=True):
            if not answer.strip():
                st.warning("Please enter an answer."); return
            with st.spinner("Evaluating your answer..."):
                sys_eval = (
                    "You are an expert interview evaluator. Evaluate the answer and return JSON with: "
                    "technical_score(0-10), communication_score(0-10), confidence_score(0-10), "
                    "relevance_score(0-10), grammar_score(0-10), strengths(list), improvements(list), "
                    "overall_rating(0-10), detailed_feedback(string). Return ONLY valid JSON."
                )
                ev_resp = ask_claude(sys_eval,
                    f"Domain:{session.domain}\nQ:{st.session_state.current_question}\nA:{answer}",
                    max_tokens=1200)
                try:    ev = json.loads(ev_resp)
                except: ev = {"overall_rating": 5, "detailed_feedback": "Evaluation failed."}

                q_obj = db.query(InterviewQuestion).get(st.session_state.current_question_id)
                q_obj.user_answer    = answer
                q_obj.tech_score     = ev.get("technical_score", 0)
                q_obj.comm_score     = ev.get("communication_score", 0)
                q_obj.conf_score     = ev.get("confidence_score", 0)
                q_obj.relevance_score = ev.get("relevance_score", 0)
                q_obj.grammar_score  = ev.get("grammar_score", 0)
                q_obj.strengths      = json.dumps(ev.get("strengths", []))
                q_obj.improvements   = json.dumps(ev.get("improvements", []))
                q_obj.overall_rating = ev.get("overall_rating", 0)
                q_obj.feedback       = ev.get("detailed_feedback", "")
                db.commit()

                st.session_state["last_eval"] = ev

                if st.session_state.question_no < 10:
                    next_q = ask_claude(
                        "You are an expert interviewer. Generate a single follow-up question. Return ONLY the question.",
                        f"Domain:{session.domain} Q{st.session_state.question_no+1} prev_q:{st.session_state.current_question}",
                        max_tokens=200
                    )
                    nq = InterviewQuestion(
                        session_id=session.id,
                        question_no=st.session_state.question_no + 1,
                        question=next_q
                    )
                    db.add(nq); db.commit()
                    st.session_state.current_question    = next_q
                    st.session_state.current_question_id = nq.id
                    st.session_state.question_no        += 1
                else:
                    st.session_state.interview_active = False
                    st.session_state.interview_ended  = True
                st.rerun()

        if col_end.button("🛑 End Interview", use_container_width=True):
            st.session_state.interview_active = False
            st.session_state.interview_ended  = True
            st.rerun()

        if "last_eval" in st.session_state:
            ev = st.session_state["last_eval"]
            with st.expander("📊 Last Answer Feedback", expanded=True):
                cc1, cc2, cc3, cc4, cc5 = st.columns(5)
                cc1.metric("Technical",    f"{ev.get('technical_score',0)*10:.0f}%")
                cc2.metric("Communication",f"{ev.get('communication_score',0)*10:.0f}%")
                cc3.metric("Confidence",   f"{ev.get('confidence_score',0)*10:.0f}%")
                cc4.metric("Relevance",    f"{ev.get('relevance_score',0)*10:.0f}%")
                cc5.metric("Grammar",      f"{ev.get('grammar_score',0)*10:.0f}%")
                st.markdown(f"**Feedback:** {ev.get('detailed_feedback','')}")
                if ev.get("strengths"):
                    st.markdown("✅ **Strengths:** " + " · ".join(ev["strengths"]))
                if ev.get("improvements"):
                    st.markdown("⚠️ **Improve:** " + " · ".join(ev["improvements"]))

    elif st.session_state.interview_ended:
        session = db.query(InterviewSession).get(st.session_state.interview_session_id)
        qs = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id,
            InterviewQuestion.overall_rating != None
        ).all()
        if qs:
            session.overall_score       = sum(q.overall_rating or 0 for q in qs) / len(qs)
            session.technical_score     = sum(q.tech_score    or 0 for q in qs) / len(qs)
            session.communication_score = sum(q.comm_score    or 0 for q in qs) / len(qs)
            session.confidence_score    = sum(q.conf_score    or 0 for q in qs) / len(qs)
            session.total_questions     = len(qs)
            session.ended_at            = datetime.utcnow()
            db.commit()

        st.success("🎉 Interview Complete!")
        st.balloons()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall Score",    f"{(session.overall_score or 0)*10:.1f}%")
        c2.metric("Technical",        f"{(session.technical_score or 0)*10:.1f}%")
        c3.metric("Communication",    f"{(session.communication_score or 0)*10:.1f}%")
        c4.metric("Questions Done",   session.total_questions)

        if st.button("🔄 Start New Interview", use_container_width=True):
            st.session_state.interview_active = False
            st.session_state.interview_ended  = False
            if "last_eval" in st.session_state: del st.session_state["last_eval"]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# INTERVIEW HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def page_history():
    st.markdown("## 📜 Interview History")
    st.markdown("---")
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == st.session_state.user_id,
        InterviewSession.overall_score != None
    ).order_by(InterviewSession.started_at.desc()).limit(20).all()

    if not sessions:
        st.info("No interviews completed yet.")
        return

    df = pd.DataFrame([{
        "Domain":     s.domain,
        "Mode":       s.mode,
        "Difficulty": s.difficulty,
        "Score":      f"{(s.overall_score or 0)*10:.1f}%",
        "Questions":  s.total_questions,
        "Date":       s.started_at.strftime("%d %b %Y %H:%M"),
    } for s in sessions])
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    st.markdown("## 📈 Analytics")
    st.markdown("---")
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == st.session_state.user_id,
        InterviewSession.overall_score != None
    ).all()

    if not sessions:
        st.info("Complete some interviews to see analytics!"); return

    scores = [s.overall_score * 10 for s in sessions]
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Interviews", len(sessions))
    c2.metric("Average Score",    f"{sum(scores)/len(scores):.1f}%")
    c3.metric("Best Score",       f"{max(scores):.1f}%")

    # Trend
    st.markdown("#### Score Trend")
    sorted_s = sorted(sessions, key=lambda x: x.started_at)
    fig = px.line(
        x=[s.started_at.strftime("%d %b") for s in sorted_s],
        y=[round(s.overall_score*10,1) for s in sorted_s],
        markers=True, color_discrete_sequence=["#7c3aed"],
        labels={"x":"Date","y":"Score (%)"}
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#e6edf3", yaxis=dict(range=[0,100],gridcolor="#30363d"),
                      xaxis=dict(gridcolor="#30363d"))
    st.plotly_chart(fig, use_container_width=True)

    # Domain breakdown
    st.markdown("#### Domain Performance")
    domain_scores = {}
    for s in sessions: domain_scores.setdefault(s.domain, []).append(s.overall_score*10)
    domain_avg = {d: round(sum(v)/len(v),1) for d,v in domain_scores.items()}
    fig2 = px.bar(x=list(domain_avg.keys()), y=list(domain_avg.values()),
                  color_discrete_sequence=["#7c3aed"],
                  labels={"x":"Domain","y":"Avg Score (%)"})
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font_color="#e6edf3", yaxis_gridcolor="#30363d")
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# CAREER COACH
# ══════════════════════════════════════════════════════════════════════════════
def page_career():
    st.markdown("## 🎯 Career Coach")
    st.markdown("---")
    c1, c2 = st.columns(2)
    target_role = c1.text_input("Target Role", "Data Scientist")
    experience  = c2.selectbox("Experience Level", ["Fresher", "Junior", "Mid", "Senior"])
    skills_raw  = st.text_input("Your Current Skills (comma separated)", "Python, SQL, Machine Learning")

    if st.button("🎯 Get Career Guidance", use_container_width=True):
        with st.spinner("Generating personalized career roadmap..."):
            skills = [s.strip() for s in skills_raw.split(",")]
            sys_p  = (
                "You are an expert career counselor. Return JSON with: "
                "career_recommendations(list), skill_gaps(list), learning_roadmap(list), "
                "recommended_courses(list), suggested_projects(list), industry_skills(list), timeline_months(int). "
                "Return ONLY valid JSON."
            )
            resp = ask_claude(sys_p,
                f"Skills:{skills}\nTarget:{target_role}\nLevel:{experience}", max_tokens=2000)
            try:    guidance = json.loads(resp)
            except: guidance = {}

        t1,t2,t3,t4 = st.tabs(["🗺️ Roadmap","📚 Courses","💼 Projects","🏭 Industry Skills"])
        with t1:
            st.markdown("**Skill Gaps:**")
            for g in guidance.get("skill_gaps",[]): st.markdown(f"- ⚠️ {g}")
            st.markdown(f"\n**Estimated Timeline:** {guidance.get('timeline_months','?')} months")
            st.markdown("**Learning Steps:**")
            for i,step in enumerate(guidance.get("learning_roadmap",[]),1): st.markdown(f"{i}. {step}")
        with t2:
            for c in guidance.get("recommended_courses",[]): st.markdown(f"📖 {c}")
        with t3:
            for p in guidance.get("suggested_projects",[]): st.markdown(f"🔧 {p}")
        with t4:
            for s in guidance.get("industry_skills",[]): st.markdown(f"🏭 {s}")

# ══════════════════════════════════════════════════════════════════════════════
# ATS CHECKER
# ══════════════════════════════════════════════════════════════════════════════
def page_ats():
    st.markdown("## 🔍 ATS Resume Checker")
    st.markdown("---")
    uploaded = st.file_uploader("Upload Resume PDF", type=["pdf"])
    job_desc = st.text_area("Paste Job Description (optional)", height=120)

    if uploaded and st.button("🔍 Check ATS Score", use_container_width=True):
        with st.spinner("Running ATS analysis..."):
            raw = ""
            with pdfplumber.open(io.BytesIO(uploaded.read())) as pdf:
                for page in pdf.pages: raw += (page.extract_text() or "") + "\n"
            extra = f"\nJob Description: {job_desc}" if job_desc else ""
            sys_p = (
                "You are an ATS expert. Analyze the resume and return JSON with: "
                "ats_score(float 0-100), formatting_issues(list), keywords_found(list), "
                "missing_keywords(list), improvement_suggestions(list). Return ONLY valid JSON."
            )
            resp = ask_claude(sys_p, raw + extra, max_tokens=1500)
            try:    ats = json.loads(resp)
            except: ats = {"ats_score":0}

        score = ats.get("ats_score", 0)
        color = "🟢" if score >= 75 else ("🟡" if score >= 50 else "🔴")
        st.metric(f"{color} ATS Score", f"{score:.0f}/100")
        st.progress(int(score)/100)

        c1,c2 = st.columns(2)
        c1.markdown("**✅ Keywords Found:**")
        for k in ats.get("keywords_found",[]): c1.markdown(f"- {k}")
        c2.markdown("**❌ Missing Keywords:**")
        for k in ats.get("missing_keywords",[]): c2.markdown(f"- {k}")
        st.markdown("**💡 Improvement Suggestions:**")
        for tip in ats.get("improvement_suggestions",[]): st.markdown(f"- {tip}")

# ══════════════════════════════════════════════════════════════════════════════
# COVER LETTER
# ══════════════════════════════════════════════════════════════════════════════
def page_cover_letter():
    st.markdown("## ✉️ Cover Letter Generator")
    st.markdown("---")
    c1,c2 = st.columns(2)
    job_title = c1.text_input("Job Title", "Data Scientist")
    company   = c2.text_input("Company Name", "Google")
    job_desc  = st.text_area("Job Description", height=120)
    skills    = st.text_input("Your Skills (comma separated)", "Python, ML, SQL")
    user      = db.query(User).get(st.session_state.user_id)

    if st.button("✉️ Generate Cover Letter", use_container_width=True):
        with st.spinner("Writing your cover letter..."):
            sys_p = "You are an expert cover letter writer. Write a professional, compelling cover letter. Return ONLY the letter text."
            msg   = (f"Name:{user.name}\nJob:{job_title}\nCompany:{company}\n"
                     f"JD:{job_desc}\nSkills:{skills}")
            letter = ask_claude(sys_p, msg, max_tokens=1000)
            st.session_state["cover_letter"] = letter

    if "cover_letter" in st.session_state:
        st.markdown("---")
        st.text_area("Your Cover Letter", st.session_state["cover_letter"], height=350)
        # Download as txt
        st.download_button(
            "⬇️ Download Cover Letter",
            data=st.session_state["cover_letter"],
            file_name="cover_letter.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# PROFILE
# ══════════════════════════════════════════════════════════════════════════════
def page_profile():
    st.markdown("## 👤 Profile")
    st.markdown("---")
    user = db.query(User).get(st.session_state.user_id)
    c1, c2 = st.columns(2)
    name  = c1.text_input("Full Name",  value=user.name)
    email = c2.text_input("Email",      value=user.email, disabled=True)
    role  = st.text_input("Target Role", "")
    exp   = st.selectbox("Experience Level", ["Fresher","Junior","Mid","Senior"])
    skls  = st.text_input("Skills (comma separated)", "")

    if st.button("💾 Save Profile", use_container_width=True):
        user.name = name
        db.commit()
        st.success("Profile saved!")

# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    st.markdown("**API Configuration**")
    api_key = st.text_input("Anthropic API Key", type="password",
                            help="Set in .env or Streamlit secrets")
    st.info("💡 For Streamlit Cloud: add ANTHROPIC_API_KEY in App Settings → Secrets")
    st.markdown("**Interview Preferences**")
    st.selectbox("Default Domain",     ["AI/ML","Data Science","Web Development","System Design"])
    st.selectbox("Default Difficulty", ["Beginner","Intermediate","Advanced"])
    st.selectbox("Default Mode",       ["Technical","HR","Mixed"])
    if st.button("💾 Save Settings"): st.success("Settings saved!")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.logged_in:
        show_auth()
        return

    show_sidebar()
    page = st.session_state.page

    if   page == "Dashboard":         page_dashboard()
    elif page == "Resume Analyzer":   page_resume()
    elif page == "Mock Interview":    page_interview()
    elif page == "Interview History": page_history()
    elif page == "Analytics":         page_analytics()
    elif page == "Career Coach":      page_career()
    elif page == "ATS Checker":       page_ats()
    elif page == "Cover Letter":      page_cover_letter()
    elif page == "Profile":           page_profile()
    elif page == "Settings":          page_settings()

if __name__ == "__main__":
    main()
