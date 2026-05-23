import random
import numpy as np
import sqlite3
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sklearn.ensemble import RandomForestClassifier
import threading

TOKEN = "8905265253:AAEntIlXtscXQoXjyWnXqsY3MGM2DopqUjk"

print("🚀 BOT DEMARRÉ")

=========================

💾 DATABASE

=========================

class Database:
def init(self):
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

=========================

📡 MARKET

=========================

class MarketAPI:
def get_rounds(self):
return [random.uniform(1.0, 4.0) for _ in range(30)]

api = MarketAPI()

=========================

🧠 IA

=========================

class AI:
def init(self):
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

=========================

ANALYSE

=========================

def analyze(rounds):
last10 = rounds[-10:]
return {
"avg": np.mean(last10),
"volatility": max(last10) - min(last10),
"crashes": sum(1 for x in last10 if x < 1.2)
}

def score_market(data):
score = 100
score -= data["crashes"] * 15
score -= data["volatility"] * 10
if data["avg"] < 1.3:
score -= 20
return max(0, min(100, score))

def is_safe(data):
return not (
data["crashes"] >= 3 or
data["volatility"] > 4 or
data["avg"] < 1.4
)

def signal_engine(score):
if score < 45:
return None
if score > 80:
return 1.8, "HIGH"
if score > 60:
return 1.6, "MEDIUM"
return 1.5, "LOW"

def process():
rounds = api.get_rounds()

features = [  
    np.mean(rounds[-10:]),  
    np.std(rounds[-10:]),  
    sum(x < 1.2 for x in rounds[-10:])  
]  

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

=========================

🤖 TELEGRAM

=========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("🤖 SAAS FINAL BOT ONLINE")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
result = process()

if not result:  
    await update.message.reply_text("🚫 Aucun signal (marché dangereux)")  
    return  

db.save(result["cashout"], result["confidence"], result["score"])  

await update.message.reply_text(  
    f"🚨 SIGNAL\nCashout: {result['cashout']}x\nConfidence: {result['confidence']}\nScore: {result['score']}/100"  
)

=========================

🌐 FLASK

=========================

app = Flask(name)

@app.route("/")
def home():
return "SAAS FINAL SYSTEM ONLINE"

@app.route("/signals")
def signals():
return jsonify(db.get_all())

=========================

BOT START

=========================

def run_bot():
app_bot = Application.builder().token(TOKEN).build()

app_bot.add_handler(CommandHandler("start", start))  
app_bot.add_handler(CommandHandler("signal", signal))  

app_bot.run_polling()

if name == "main":
threading.Thread(target=run_bot).start()
app.run(host="0.0.0.0", port=8080)
