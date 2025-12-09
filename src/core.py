# src/core.py

import json
import random
from collections import defaultdict


# =====================================================
# Question Class
# =====================================================
class Question:
    def __init__(self, subject, qtype, prompt, answer,
                 choices=None, difficulty="medium"):
        """
        subject:   e.g., 'math', 'linux', 'cyber'
        qtype:     'recall', 'mcq', or 'problem'
        prompt:    question text
        answer:    correct answer (string)
        choices:   list of options for MCQ (or None)
        difficulty: 'easy' | 'medium' | 'hard'
        """
        self.subject = subject
        self.qtype = qtype
        self.prompt = prompt
        self.answer = answer
        self.choices = choices or []
        self.difficulty = difficulty


# =====================================================
# Learner Class – Performance Tracking
# =====================================================
class Learner:
    def __init__(self, name, email=None):
        self.name = name
        self.email = email
        # (subject, qtype) -> {correct, total, time}
        self.stats = defaultdict(lambda: {"correct": 0, "total": 0, "time": 0.0})

    def update(self, subject, qtype, correct, elapsed):
        """Update basic performance stats for this learner."""
        key = (subject, qtype)
        s = self.stats[key]
        s["total"] += 1
        s["time"] += elapsed
        if correct:
            s["correct"] += 1

    def accuracy(self, subject, qtype):
        s = self.stats[(subject, qtype)]
        return s["correct"] / s["total"] if s["total"] else 0.0

    def learning_style_summary(self):
        """Text summary of accuracy by subject + type."""
        if not self.stats:
            return "Not enough data yet."
        lines = []
        for (subject, qtype), s in self.stats.items():
            acc = self.accuracy(subject, qtype)
            lines.append(f"{subject} — {qtype}: {acc:.0%} correct")
        return "\n".join(lines)

    def simple_style_label(self):
        """Heuristic label based on which qtype they answer correctly most."""
        totals = {"recall": 0, "mcq": 0, "problem": 0}
        for (subject, qtype), s in self.stats.items():
            if qtype in totals:
                totals[qtype] += s["correct"]

        # If they haven't answered anything, default label:
        if all(v == 0 for v in totals.values()):
            return "Not enough data"

        label_map = {
            "recall": "Memory / definition-focused learner",
            "mcq": "Visual-choice / recognition learner",
            "problem": "Analytical / problem-solving learner",
        }
        best_qtype = max(totals, key=totals.get)
        return label_map.get(best_qtype, "Mixed learner")


# =====================================================
# Question Bank (MSU STEM – math / linux / cyber)
# =====================================================
def build_question_bank():
    q = []

    # ---------- MATH ----------
    q.append(Question(
        subject="math",
        qtype="recall",
        prompt="What is 12 × 12?",
        answer="144",
        choices=["100", "124", "144", "142"],
        difficulty="easy",
    ))

    q.append(Question(
        subject="math",
        qtype="problem",
        prompt="Solve for x: 5x - 10 = 15",
        answer="5",
        difficulty="medium",
    ))

    q.append(Question(
        subject="math",
        qtype="recall",
        prompt="What is the derivative of f(x) = x² ?",
        answer="2x",
        choices=["x", "2x", "x²", "2"],
        difficulty="medium",
    ))

    # ---------- LINUX ----------
    q.append(Question(
        subject="linux",
        qtype="recall",
        prompt="Which command lists files in the current directory?",
        answer="ls",
        choices=["cd", "ls", "rm", "pwd"],
        difficulty="easy",
    ))

    q.append(Question(
        subject="linux",
        qtype="problem",
        prompt="Fix this command: mkdr test → ?",
        answer="mkdir test",
        difficulty="easy",
    ))

    q.append(Question(
        subject="linux",
        qtype="mcq",
        prompt="Which command deletes a file?",
        answer="rm",
        choices=["rm", "mv", "mkdir", "ls"],
        difficulty="medium",
    ))

    # ---------- CYBERSECURITY ----------
    q.append(Question(
        subject="cyber",
        qtype="mcq",
        prompt="What does MFA stand for?",
        answer="Multi-Factor Authentication",
        choices=[
            "Multi-Factor Authentication",
            "Master File Access",
            "Multi-File Authorization",
            "Main Firewall Admin",
        ],
        difficulty="easy",
    ))

    q.append(Question(
        subject="cyber",
        qtype="recall",
        prompt="In cybersecurity, what does CIA stand for?",
        answer="Confidentiality, Integrity, Availability",
        difficulty="medium",
    ))

    q.append(Question(
        subject="cyber",
        qtype="problem",
        prompt="Which Linux command can show active network connections?",
        answer="netstat",
        difficulty="hard",
    ))

    return q


# =====================================================
# JSON Loader (optional extra questions)
# =====================================================
def load_questions_from_json_bytes(file_bytes):
    """Load additional questions from a JSON file uploaded in Streamlit."""
    try:
        data = json.loads(file_bytes.decode("utf-8"))
        questions = []
        for item in data:
            questions.append(Question(
                subject=item["subject"],
                qtype=item["qtype"],
                prompt=item["prompt"],
                answer=item["answer"],
                choices=item.get("choices"),
                difficulty=item.get("difficulty", "medium"),
            ))
        return questions
    except Exception as e:
        raise ValueError(f"Invalid JSON: {e}")
