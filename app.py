# app.py

import os
import time
import random

import pandas as pd
import streamlit as st

from core import  (
    Question,
    Learner,
    build_question_bank,
    load_questions_from_json_bytes,
)

# ==========================================================
# Streamlit Page Setup
# ==========================================================
st.set_page_config(
    page_title="MSU Adaptive STEM Study Game",
    page_icon="🐶",
    layout="wide",
)


# ==========================================================
# High-Contrast MSU Theme (light background)
# ==========================================================

def apply_theme():
    st.markdown("""
    <style>

    /* FORCE Override Entire Page Background */
    html, body, .stApp {
        background-color: #ffffff !important; /* pure white */
        color: #111111 !important; /* very dark text */
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f2f2f2 !important;
        color: #111111 !important;
    }

    /* Radio buttons & labels */
    label, .stRadio label, .stRadio div {
        color: #111111 !important;
        font-size: 16px;
        font-weight: 600;
    }

    /* Text for all inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #ffffff !important;
        color: #111111 !important;
        font-size: 16px;
    }

    /* Heading colors */
    h1, h2, h3, h4 {
        color: #660000 !important; /* MSU maroon */
        font-weight: 900 !important;
    }

    /* Buttons */
    .stButton>button {
        background: #660000 !important;
        color: #ffffff !important;
        font-weight: 700;
        border-radius: 8px;
        border: none;
        padding: 8px 20px;
        font-size: 17px;
    }
    .stButton>button:hover {
        background: #8b0000 !important;
    }

    /* Question card */
    .question-card {
        background: #ffffff !important;
        border-radius: 12px;
        padding: 20px;
        border: 2px solid #66000044;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        color: #111111 !important;
    }

    </style>
    """, unsafe_allow_html=True)

# ==========================================================
# Helper: Save Session to CSV
# ==========================================================
def save_user_session_to_disk():
    """Save current session log as CSV in data/user_logs/."""
    if not st.session_state.log:
        return None

    df = pd.DataFrame(st.session_state.log)
    os.makedirs("data/user_logs", exist_ok=True)

    user_id = st.session_state.email or st.session_state.learner.name.replace(" ", "_")
    filename = f"data/user_logs/{user_id}_session.csv"
    df.to_csv(filename, index=False)
    return filename


# ==========================================================
# Question Selection (simple adaptive logic)
# ==========================================================
def choose_next_question(questions, difficulty_choice, last_correct, last_question):
    """Pick the next question with simple difficulty adaptation + no repeats."""
    if not questions:
        return None

    # Pick difficulty
    if difficulty_choice == "mixed":
        if last_correct is True:
            preferred = ["medium", "hard"]
        elif last_correct is False:
            preferred = ["easy"]
        else:
            preferred = ["easy", "medium"]
        candidates = [q for q in questions if q.difficulty in preferred] or questions
    else:
        candidates = [q for q in questions if q.difficulty == difficulty_choice] or questions

    # Avoid repeating exact same prompt back-to-back
    if last_question is not None:
        non_repeat = [q for q in candidates if q.prompt != last_question.prompt]
        if non_repeat:
            candidates = non_repeat

    return random.choice(candidates)


# ==========================================================
# Session State Defaults
# ==========================================================
_defaults = {
    "learner": None,
    "email": None,
    "questions": [],
    "score": 0,
    "current_question": None,
    "last_result": "",
    "log": [],
    "last_correct": None,
    "phase": "style_quiz",  # or "study"
    "learning_style": None,
    "question_start_time": None,
    "page": "Study Mode",
}

for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ==========================================================
# Sidebar – Navigation & Setup
# ==========================================================
st.sidebar.title("Login Setup")

page = st.sidebar.radio("Navigation", ["Study Mode", "Analytics"], index=0)
st.session_state.page = page

name = st.sidebar.text_input(
    "Name *",
    value=st.session_state.learner.name if st.session_state.learner else "",
)

email = st.sidebar.text_input(
    "MSU Email (optional)",
    value=st.session_state.email or "",
)

difficulty = st.sidebar.selectbox("Difficulty:", ["mixed", "easy", "medium", "hard"])

st.sidebar.markdown("**Questions:**")
source = st.sidebar.radio(
    "",
    ["Built-in only", "Built-in + JSON"],
    index=0,
)

uploaded_file = None
if "JSON" in source:
    uploaded_file = st.sidebar.file_uploader("Upload questions.json", type=["json"])

if st.sidebar.button("Start Session 🚀"):
    if not name.strip():
        st.sidebar.error("Please enter your name.")
    else:
        # Reset full session
        st.session_state.learner = Learner(name.strip(), email.strip() or None)
        st.session_state.email = email.strip() or None
        st.session_state.questions = []
        st.session_state.score = 0
        st.session_state.last_result = ""
        st.session_state.log = []
        st.session_state.current_question = None
        st.session_state.last_correct = None
        st.session_state.phase = "style_quiz"
        st.session_state.learning_style = None
        st.session_state.question_start_time = None

        # Built-in questions
        st.session_state.questions.extend(build_question_bank())

        # JSON questions (optional)
        if "JSON" in source and uploaded_file is not None:
            try:
                extra_q = load_questions_from_json_bytes(uploaded_file.read())
                st.session_state.questions.extend(extra_q)
                st.sidebar.success(f"Loaded {len(extra_q)} extra questions from JSON.")
            except Exception as e:
                st.sidebar.error(f"Error loading JSON: {e}")

        st.sidebar.success("Session started! Take the learning style quiz below.")


# ==========================================================
# Learning Style Quiz
# ==========================================================
def render_learning_style_quiz():
    st.subheader("Step 1: Learning Style Quiz")

    st.write(
        "Rate each statement from **1 (strongly disagree)** to "
        "**5 (strongly agree)**."
    )

    scale = [1, 2, 3, 4, 5]

    q1 = st.radio(
        "I remember diagrams, charts, and formulas easily.",
        scale,
        index=2,
        horizontal=True,
        key="lsq1",
    )
    q2 = st.radio(
        "I like working through step-by-step math or logic problems.",
        scale,
        index=2,
        horizontal=True,
        key="lsq2",
    )
    q3 = st.radio(
        "I learn best by typing commands or doing hands-on labs (like Linux).",
        scale,
        index=2,
        horizontal=True,
        key="lsq3",
    )
    q4 = st.radio(
        "Multiple-choice questions feel natural and low-stress to me.",
        scale,
        index=2,
        horizontal=True,
        key="lsq4",
    )
    q5 = st.radio(
        "I enjoy debugging or solving open-ended technical problems.",
        scale,
        index=2,
        horizontal=True,
        key="lsq5",
    )
    q6 = st.radio(
        "Security or networking labs sound interesting to me.",
        scale,
        index=2,
        horizontal=True,
        key="lsq6",
    )

    if st.button("Finish Learning Style Quiz"):
        visual_score = q1 + q4
        analytical_score = q2 + q5
        practical_score = q3 + q6

        scores = {
            "visual": visual_score,
            "analytical": analytical_score,
            "practical": practical_score,
        }
        style = max(scores, key=scores.get)
        st.session_state.learning_style = style
        st.session_state.phase = "study"

        style_map = {
            "visual": "Visual-choice learner (MCQ / diagrams)",
            "analytical": "Analytical learner (math / problem solving)",
            "practical": "Hands-on learner (Linux / labs / security)",
        }
        st.success(
            f"Your inferred learning style is: **{style_map.get(style, style)}**.\n\n"
            "Scroll down to begin the adaptive study session."
        )


# ==========================================================
# Custom Question Builder (optional)
# ==========================================================
def render_custom_question_builder():
    st.subheader("➕ Add Custom STEM Question")

    with st.form("custom_q_form"):
        c_subject = st.selectbox(
            "Subject:", ["math", "linux", "cyber", "custom"], key="c_subject"
        )
        c_qtype = st.selectbox(
            "Question type:", ["recall", "mcq", "problem"], key="c_qtype"
        )
        c_difficulty = st.selectbox(
            "Difficulty:", ["easy", "medium", "hard"], key="c_diff"
        )
        c_prompt = st.text_area("Question Prompt:", key="c_prompt")
        c_answer = st.text_input("Correct Answer:", key="c_answer")
        c_choices_raw = st.text_area(
            "MCQ choices (one per line, optional):", key="c_choices"
        )

        submitted = st.form_submit_button("Add Question")

        if submitted:
            if not c_subject or not c_prompt or not c_answer:
                st.error("Please fill subject, prompt, and answer.")
            else:
                choices = []
                if c_qtype == "mcq":
                    choices = [
                        line.strip()
                        for line in c_choices_raw.split("\n")
                        if line.strip()
                    ]
                q = Question(
                    subject=c_subject.lower().strip(),
                    qtype=c_qtype.lower().strip(),
                    prompt=c_prompt.strip(),
                    answer=c_answer.strip(),
                    choices=choices,
                    difficulty=c_difficulty,
                )
                st.session_state.questions.append(q)
                st.success("Custom question added to pool!")


# ==========================================================
# PAGE: STUDY MODE
# ==========================================================
if st.session_state.page == "Study Mode":
    st.title("🐶 MSU Adaptive STEM Study Game")

    if not st.session_state.learner or not st.session_state.questions:
        st.info("Use the sidebar to start a session first.")
    else:
        # Phase 1: style quiz
        if st.session_state.phase == "style_quiz":
            render_learning_style_quiz()
        else:
            # Phase 2: Adaptive study session
            st.subheader("Step 2: Adaptive Study Session")

            # Pick first question if needed
            if st.session_state.current_question is None:
                st.session_state.current_question = choose_next_question(
                    st.session_state.questions,
                    difficulty_choice=difficulty,
                    last_correct=st.session_state.last_correct,
                    last_question=None,
                )
                st.session_state.question_start_time = time.time()

            q = st.session_state.current_question

            # ----- Question card -----
            st.markdown('<div class="question-card">', unsafe_allow_html=True)
            st.markdown(
                f"**Subject:** `{q.subject}`  |  **Type:** `{q.qtype}`  |  "
                f"**Difficulty:** `{q.difficulty}`"
            )
            st.write(q.prompt)

            if q.choices:
                user_answer = st.radio(
                    "Choose your answer:",
                    q.choices,
                    key=f"answer_{len(st.session_state.log)}",
                )
            else:
                user_answer = st.text_input(
                    "Your answer:", key=f"answer_{len(st.session_state.log)}"
                )

            st.markdown("</div>", unsafe_allow_html=True)

            # ----- Buttons -----
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Submit"):
                    if user_answer is None or user_answer == "":
                        st.warning("Please enter an answer before submitting.")
                    else:
                        start_t = (
                            st.session_state.question_start_time or time.time()
                        )
                        elapsed = time.time() - start_t

                        correct = (
                            str(user_answer).strip().lower()
                            == str(q.answer).strip().lower()
                        )

                        # Update learner stats
                        st.session_state.learner.update(
                            q.subject, q.qtype, correct, elapsed
                        )
                        st.session_state.last_correct = correct

                        # Log this question
                        st.session_state.log.append(
                            {
                                "name": st.session_state.learner.name,
                                "email": st.session_state.email,
                                "subject": q.subject,
                                "qtype": q.qtype,
                                "difficulty": q.difficulty,
                                "correct": correct,
                                "response_time": elapsed,
                                "learning_style_quiz": st.session_state.learning_style,
                            }
                        )

                        # Score + feedback
                        if correct:
                            st.session_state.score += 10
                            st.session_state.last_result = "✅ Correct! Great job!"
                            st.balloons()
                        else:
                            st.session_state.last_result = (
                                f"❌ Incorrect. Correct answer: {q.answer}"
                            )

                        # Immediately move to NEXT question
                        st.session_state.current_question = choose_next_question(
                            st.session_state.questions,
                            difficulty_choice=difficulty,
                            last_correct=st.session_state.last_correct,
                            last_question=q,
                        )
                        st.session_state.question_start_time = time.time()

            with col2:
                if st.button("Skip / Next Question"):
                    st.session_state.current_question = choose_next_question(
                        st.session_state.questions,
                        difficulty_choice=difficulty,
                        last_correct=st.session_state.last_correct,
                        last_question=st.session_state.current_question,
                    )
                    st.session_state.last_result = ""
                    st.session_state.question_start_time = time.time()

            # Score + summary
            st.markdown(f"**Score:** {st.session_state.score}")
            if st.session_state.last_result:
                st.write(st.session_state.last_result)

            st.markdown("---")
            st.subheader("🧠 Performance-based Summary")
            st.text(st.session_state.learner.learning_style_summary())
            st.write(
                f"**Heuristic learner type:** "
                f"{st.session_state.learner.simple_style_label()}"
            )

            # Session log table + download
            if st.session_state.log:
                df = pd.DataFrame(st.session_state.log)
                st.markdown("#### Session Log")
                st.dataframe(df, use_container_width=True)
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Session Log (CSV)",
                    data=csv_data,
                    file_name="session_log.csv",
                    mime="text/csv",
                )

            st.markdown("---")
            render_custom_question_builder()


# ==========================================================
# PAGE: ANALYTICS
# ==========================================================
if st.session_state.page == "Analytics":
    st.title("📊 Learning Analytics Dashboard")

    if not st.session_state.log:
        st.info("No data yet. Play in Study Mode first.")
    else:
        df_logs = pd.DataFrame(st.session_state.log)

        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.subheader("Overview")
        overall_acc = df_logs["correct"].mean() * 100
        total_q = len(df_logs)
        st.metric("Overall Accuracy", f"{overall_acc:.1f}%")
        st.metric("Total Questions Answered", str(total_q))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.subheader("Accuracy by Subject")
        acc_by_subj = df_logs.groupby("subject")["correct"].mean().sort_values(
            ascending=False
        )
        st.bar_chart(acc_by_subj)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.subheader("Accuracy by Question Type")
        acc_by_qtype = df_logs.groupby("qtype")["correct"].mean().sort_values(
            ascending=False
        )
        st.bar_chart(acc_by_qtype)
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# End Session Button
# ==========================================================
st.markdown("---")
if st.button("🔚 End Session & Save Data"):
    filename = save_user_session_to_disk()
    if filename:
        st.success(f"Saved session to {filename}")
    else:
        st.warning("No session data to save.")
