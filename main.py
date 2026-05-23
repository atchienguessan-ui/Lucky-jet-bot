import random
import numpy as np
import sqlite3
from flask import Flask, jsonify
from telegram.ext import Updater, CommandHandler
from sklearn.ensemble import RandomForestClassifier

TOKEN = 8905265253:AAEntIlXtscXQoXjyWnXqsY3MGM2DopqUjk

# =========================
# 💾 DATABASE SIMPLE
# =========================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("saas.db", check_same_thread=False)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY,
            cashout REAL,
            confidence TEXT,
            score REAL
        )
        """)
        self.conn.commit()

    def save(self, cashout, confidence, score):
        self.conn.execute(
            "INSERT INTO signals (cashout, confidence, score) VALUES (?, ?, ?)",
            (cashout, confidence, score)
        )
        self.conn.commit()

    def get_all(self):
        return list(self.conn.execute("SELECT * FROM signals"))


db = Database()

# =========================
# 📡 MARKET DATA (API READY)
# =========================
class MarketAPI:
    def get_rounds(self):
        # ⚠️ Remplace par vraie API si tu en trouves une
        return [random.uniform(1.0, 4.0) for _ in range(30)]


api = MarketAPI()

# =========================
# 🧠 IA SIMPLE
# =========================
class AI:
    def __init__(self):
        self.model = RandomForestClassifier()
        self.train()

    def train(self):
        X = [
            [1.5,0.3,2],
            [1.2,0.2,5],
            [1.8,0.5,1],
            [1.1,0.1,6]
        ]
        y = [1,0,1,0]
        self.model.fit(X, y)

    def predict(self, features):
        return self.model.predict([features])[0]


ai = AI()

# =========================
# 📊 ANALYSE MARCHÉ
# =========================
def analyze(rounds):
    last10 = rounds[-10:]

    return {
        "avg": np.mean(last10),
        "volatility": max(last10) - min(last10),
        "crashes": sum(1 for x in last10 if x < 1.2),
        "score": 0
    }

# =========================
# 📈 SCORE 0–100
# =========================
def score_market(data):
    score = 100
    score -= data["crashes"] * 15
    score -= data["volatility"] * 10
    if data["avg"] < 1.3:
        score -= 20
    return max(0, min(100, score))

# =========================
# 🚫 FILTRE INTELLIGENT
# =========================
def is_safe(data):
    if data["crashes"] >= 3:
        return False
    if data["volatility"] > 4:
        return False
    if data["avg"] < 1.4:
        return False
    return True

# =========================
# 🎯 SIGNAL ENGINE
# =========================
def signal_engine(score):
    if score < 45:
        return None
    if score > 80:
        return 1.8, "HIGH"
    if score > 60:
        return 1.6, "MEDIUM"
    return 1.5, "LOW"

# =========================
# 🧠 PROCESS SIGNAL
# =========================
def process():
    rounds = api.get_rounds()

    features = [np.mean(rounds[-10:]), np.std(rounds[-10:]), sum(x < 1.2 for x in rounds[-10:])]

    if ai.predict(features) == 0:
        return None

    data = analyze(rounds)
    score = score_market(data)

    if not is_safe(data):
        return None

    sig = signal_engine(score)

    if not sig:
        return None

    return {
        "cashout": sig[0],
        "confidence": sig[1],
        "score": score
    }

# =========================
# 🤖 TELEGRAM BOT
# =========================
def start(update, context):
    update.message.reply_text("🤖 SAAS FINAL BOT ONLINE")


def signal(update, context):
    result = process()

    if not result:
        update.message.reply_text("🚫 Aucun signal (marché dangereux)")
        return

    db.save(result["cashout"], result["confidence"], result["score"])

    update.message.reply_text(f"""
🚨 SAAS FINAL SIGNAL

Cashout: {result['cashout']}x
Confidence: {result['confidence']}
Score: {result['score']}/100

Saved to database 📊
""")


# =========================
# 🌐 DASHBOARD (OPTIONAL)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "SAAS FINAL SYSTEM ONLINE"

@app.route("/signals")
def signals():
    return jsonify(db.get_all())


# =========================
# ▶️ RUN
# =========================
def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("signal", signal))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    import threading

    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
