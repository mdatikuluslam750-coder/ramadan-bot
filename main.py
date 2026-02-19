import telebot
import requests
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# আপনার তথ্যসমূহ
BOT_TOKEN = "8331922661:AAFUePbGdJk-X07wk4QiOninnAmf_Cea_O4"
GEMINI_API_KEY = "AIzaSyAfZ0klixqrTGD0yaDHEN-iG386G8i--PU"

bot = telebot.TeleBot(BOT_TOKEN)

# AI সেটআপ (নিরাপত্তা ও ইসলামিক নির্দেশনাসহ)
genai.configure(api_key=GEMINI_API_KEY)

# সিস্টেম ইন্সট্রাকশন: এখানে বটকে বলে দেওয়া হয়েছে সে কীভাবে আচরণ করবে
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# সেফটি সেটিংস: অশ্লীল বা ক্ষতিকর উত্তর বন্ধ করার জন্য
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "✨ আসসালামু আলাইকুম!\n\n"
        "📍 ইফতার ও সেহরির সময় জানতে জেলার নাম ইংরেজিতে লিখুন (যেমন: Dhaka)\n"
        "🤖 যেকোনো ইসলামিক প্রশ্ন বা হাদিস জানতে চাইলে মেসেজ দিন।\n\n"
        "⚠️ দ্রষ্টব্য: এই বটটি কেবল ইসলামিক ও শিক্ষামূলক আলোচনার জন্য।"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_text = message.text.strip().lower()
    
    # ১. প্রথমে জেলা চেক করা (ইফতার-সেহরির সময়ের জন্য)
    api_url = f"https://bd-ramadan-api.vercel.app/api/{user_text}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            reply = (f"📍 জেলা: {user_text.capitalize()}\n"
                     f"📅 তারিখ: {data['date']}\n"
                     f"⏳ সেহরির শেষ সময়: {data['sehri']}\n"
                     f"🍎 ইফতারের সময়: {data['iftar']}\n\n"
                     "👨‍💻 উৎপাদক: @Md_atiqul_islam0")
            bot.reply_to(message, reply)
            return
    except:
        pass

    # ২. জেলা না হলে AI এর মাধ্যমে ইসলামিক উত্তর দেওয়া
    try:
        # AI-কে কড়া নির্দেশ দেওয়া হচ্ছে যাতে সে অশ্লীল উত্তর না দেয়
        prompt = (f"You are a dedicated Islamic Assistant. Provide answers based on Quran and Sahih Hadith. "
                  f"Always answer in Bengali. Do not answer any vulgar, offensive, or non-Islamic inappropriate questions. "
                  f"If the question is inappropriate, politely refuse. User question: {user_text}")
        
        ai_res = model.generate_content(prompt)
        bot.reply_to(message, f"{ai_res.text}\n\n👨‍💻 উৎপাদক: @Md_atiqul_islam0")
    except Exception as e:
        bot.reply_to(message, "⚠️ দুঃখিত, আমি এই বিষয়ে উত্তর দিতে পারছি না। দয়া করে সঠিক ও মার্জিত প্রশ্ন করুন।")

# Render এর পোর্ট সমস্যা সমাধানের জন্য Flask
app = Flask(__name__)
@app.route('/')
def index(): return "Islamic Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
    
