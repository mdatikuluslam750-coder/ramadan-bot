import telebot
import requests
import google.generativeai as genai

# আপনার তথ্যসমূহ
BOT_TOKEN = "8331922661:AAFUePbGdJk-X07wk4QiOninnAmf_Cea_O4"
GEMINI_API_KEY = "AIzaSyAfZ0klixqrTGD0yaDHEN-iG386G8i--PU"

bot = telebot.TeleBot(BOT_TOKEN)

# AI সেটআপ
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@bot.message_handler(commands=['start'])
def start(message):
    hadiyth = "✨ রাসূলুল্লাহ (সাঃ) বলেছেন: 'যে ব্যক্তি সওয়াবের আশায় রমজানের রোজা রাখবে, তার পূর্ববর্তী সকল গুনাহ ক্ষমা করা হবে।'"
    welcome_text = (
        f"{hadiyth}\n\n"
        "📍 সময় জানতে জেলার নাম লিখুন (যেমন: ঢাকা)\n"
        "🤖 যেকোনো ইসলামিক প্রশ্ন করতে পারেন!\n\n"
        "👨‍💻 উৎপাদক: @Md_atiqul_islam0"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_text = message.text.strip()
    
    # জেলা চেক করার জন্য API
    api_url = f"https://bd-ramadan-api.vercel.app/api/{user_text}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            reply = (f"📍 জেলা: {user_text}\n"
                     f"📅 তারিখ: {data['date']}\n"
                     f"⏳ সেহরির শেষ সময়: {data['sehri']}\n"
                     f"🍎 ইফতারের সময়: {data['iftar']}\n\n"
                     f"👨‍💻 উৎপাদক: @Md_atiqul_islam0")
            bot.reply_to(message, reply)
        else:
            # যদি জেলা না হয়, তবে AI (জেমিনি) উত্তর দিবে
            prompt = f"You are a polite Islamic Assistant. Answer in Bengali only. Stay respectful. User asked: {user_text}"
            ai_res = model.generate_content(prompt)
            # এআই উত্তরের নিচেও আপনার নাম থাকবে
            bot.reply_to(message, f"{ai_res.text}\n\n👨‍💻 উৎপাদক: @Md_atiqul_islam0")
    except Exception as e:
        bot.reply_to(message, "⚠️ দুঃখিত, আমি ঠিক বুঝতে পারিনি। জেলা বা সঠিক প্রশ্ন লিখুন।\n\n👨‍💻 উৎপাদক: @Md_atiqul_islam0")

bot.polling()
