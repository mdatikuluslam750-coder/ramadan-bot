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

# AI সেটআপ
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# জেলাগুলোর সঠিক লিস্ট (যাতে ভুল না হয়)
BD_DISTRICTS = ["dhaka", "faridpur", "gazipur", "gopalganj", "kishoreganj", "madaripur", "manikganj", "munshiganj", "narayanganj", "narsingdi", "rajbari", "shariatpur", "tangail", "barishal", "bhola", "jhalokati", "patuakhali", "pirojpur", "barguna", "chattogram", "bandarban", "brahmanbaria", "chandpur", "cumilla", "coxsbazar", "feni", "khagrachhari", "lakshmipur", "noakhali", "rangamati", "khulna", "bagherhat", "chuadanga", "jashore", "jhenaidah", "kushtia", "magura", "meherpur", "narail", "satkhira", "mymensingh", "jamalpur", "netrokona", "sherpur", "rajshahi", "bogura", "joypurhat", "naogaon", "natore", "chapainawabganj", "pabna", "sirajganj", "rangpur", "dinajpur", "gaibandha", "kurigram", "lalmonirhat", "nilphamari", "panchagarh", "thakurgaon", "sylhet", "habiganj", "moulvibazar", "sunamganj"]

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "✨ আসসালামু আলাইকুম!\n\n"
        "📍 ইফতার ও সেহরির সময় জানতে আপনার জেলার নাম ইংরেজিতে লিখুন (যেমন: Dhaka, Khulna)।\n"
        "🤖 ইসলামিক যেকোনো বিষয়ে আমাকে প্রশ্ন করতে পারেন।\n\n"
        "👨‍💻 উৎপাদক: @Md_atiqul_islam0"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_text = message.text.strip().lower()
    
    # যদি ব্যবহারকারী জেলার নাম লিখে
    if user_text in BD_DISTRICTS:
        api_url = f"https://bd-ramadan-api.vercel.app/api/{user_text}"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                reply = (f"📍 জেলা: {user_text.capitalize()}\n"
                         f"📅 তারিখ: {data['date']}\n"
                         f"⏳ সেহরির শেষ সময়: {data['sehri']}\n"
                         f"🍎 ইফতারের সময়: {data['iftar']}\n\n"
                         f"👨‍💻 উৎপাদক: @Md_atiqul_islam0")
                bot.reply_to(message, reply)
                return
        except:
            pass

    # যদি জেলা না হয়, তবে AI উত্তর দিবে
    try:
        prompt = f"You are an Islamic Assistant. Answer in Bengali only. Question: {user_text}"
        response = model.generate_content(prompt)
        bot.reply_to(message, f"{response.text}\n\n👨‍💻 উৎপাদক: @Md_atiqul_islam0")
    except Exception as e:
        bot.reply_to(message, "⚠️ দুঃখিত, আমি ঠিক বুঝতে পারিনি। দয়া করে জেলার নাম ইংরেজিতে লিখুন।")

# Render এর জন্য Flask সার্ভার (PORT সমস্যা দূর করতে)
app = Flask(__name__)
@app.route('/')
def index(): return "Bot is Alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
    
