import telebot
import requests
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# আপনার দেওয়া নতুন তথ্যসমূহ
BOT_TOKEN = "8331922661:AAFZoxvctIg4jm2uX9DMAe5ME2ziCnKgjVs"
GEMINI_API_KEY = "AIzaSyAfZ0klixqrTGD0yaDHEN-iG386G8i--PU" # আপনার আগের এপিআই কি-টি এখানে কাজ করবে

bot = telebot.TeleBot(BOT_TOKEN)

# AI সেটআপ (নিরাপত্তা ও ইসলামিক নির্দেশনাসহ)
genai.configure(api_key=GEMINI_API_KEY)

# সেফটি সেটিংস: অশ্লীল বা বাজে উত্তর বন্ধ করার জন্য
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    safety_settings=safety_settings
)

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "✨ আসসালামু আলাইকুম!\n\n"
        "🌙 রমজানুল মোবারক। এই বটটি আপনার ইসলামিক সহযোগী।\n\n"
        "📍 সেহরি ও ইফতারের সময় জানতে আপনার জেলার নাম ইংরেজিতে লিখুন (যেমন: Dhaka, Bogura)।\n"
        "🤖 যেকোনো ইসলামিক প্রশ্ন বা মাসলা-মাসায়েল জিজ্ঞেস করতে পারেন।\n"
        "⏰ সেহরি ও ইফতারের জন্য এটি আপনাকে সঠিক তথ্য দিয়ে সাহায্য করবে।\n\n"
        "👨‍💻 উৎপাদক: @Md_atiqul_islam0"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_text = message.text.strip().lower()
    
    # ১. প্রথমে জেলা চেক করা (৬৪ জেলার ইফতার-সেহরির সময়ের জন্য API)
    api_url = f"https://bd-ramadan-api.vercel.app/api/{user_text}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            reply = (f"📍 জেলা: {user_text.capitalize()}\n"
                     f"📅 তারিখ: {data['date']}\n"
                     f"⏳ সেহরির শেষ সময়: {data['sehri']}\n"
                     f"🍎 ইফতারের সময়: {data['iftar']}\n\n"
                     "📢 সময়মতো সেহরি ও ইফতার করুন।\n"
                     "👨‍💻 উৎপাদক: @Md_atiqul_islam0")
            bot.reply_to(message, reply)
            return
    except:
        pass

    # ২. জেলা না হলে AI এর মাধ্যমে ইসলামিক উত্তর দেওয়া
    try:
        # AI-কে কড়া নির্দেশ: শুধুমাত্র ইসলামিক, রমজান বিষয়ক এবং শালীন উত্তর দিবে
        prompt = (f"You are a strict Islamic Assistant for the month of Ramadan. "
                  f"Answer only Islamic, Quran, Hadith, and Ramadan related questions in Bengali. "
                  f"Strictly refuse to answer any vulgar, sexual, offensive, or inappropriate questions. "
                  f"If someone asks something bad, say: 'দুঃখিত, আমি কেবল ইসলামিক ও রমজান বিষয়ক প্রশ্নের উত্তর দিই।' "
                  f"User question: {user_text}")
        
        ai_res = model.generate_content(prompt)
        bot.reply_to(message, f"{ai_res.text}\n\n👨‍💻 উৎপাদক: @Md_atiqul_islam0")
    except Exception:
        bot.reply_to(message, "⚠️ দুঃখিত, আমি এই প্রশ্নের উত্তর দিতে পারছি না। দয়া করে মার্জিত ও ইসলামিক প্রশ্ন করুন।")

# Render এর পোর্ট সমস্যা সমাধানের জন্য Flask সার্ভার
app = Flask(__name__)
@app.route('/')
def index(): return "Islamic Ramadan Bot is Active!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

if __name__ == "__main__":
    # ফোন বা সার্ভারে সেহরির সময় অ্যালার্ম ফিট করার জন্য নির্দেশনা মনে করিয়ে দেওয়া
    print("Bot is starting...")
    Thread(target=run).start()
    bot.infinity_polling()
    
