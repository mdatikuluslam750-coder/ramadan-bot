import os
import pytz
import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CallbackQueryHandler, filters

TOKEN = os.getenv("BOT_TOKEN")  # Env variable

districts = {
    "ঢাকা":"Dhaka","খুলনা":"Khulna","চট্টগ্রাম":"Chittagong","রাজশাহী":"Rajshahi",
    "সিলেট":"Sylhet","বরিশাল":"Barisal","রংপুর":"Rangpur","ময়মনসিংহ":"Mymensingh",
    "কক্সবাজার":"Cox's Bazar","বাগেরহাট":"Bagerhat","সাতক্ষীরা":"Satkhira","যশোর":"Jessore"
}

def get_buttons():
    buttons = []
    for d in districts.keys():
        buttons.append([InlineKeyboardButton(d, callback_data=d)])
    return buttons

def get_times(city):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Bangladesh&method=1"
    r = requests.get(url).json()
    fajr = r["data"]["timings"]["Fajr"]
    maghrib = r["data"]["timings"]["Maghrib"]
    return fajr, maghrib

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup(get_buttons())
    await update.message.reply_text("🌙 রমজান মোবারক! জেলা বেছে নিন:", reply_markup=kb)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    district = query.data
    city = districts[district]
    fajr, maghrib = get_times(city)
    tz = pytz.timezone("Asia/Dhaka")
    today = datetime.datetime.now(tz).strftime("%d-%m-%Y")
    msg = f"""
📍 জেলা: {district}
📅 তারিখ: {today}

🌙 সেহরির শেষ সময়: {fajr}
🍽️ ইফতার সময়: {maghrib}

উৎপাদক: @Md_atiqul_islam0
"""
    await query.edit_message_text(msg)

async def text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text in districts:
        city = districts[text]
        fajr, maghrib = get_times(city)
        tz = pytz.timezone("Asia/Dhaka")
        today = datetime.datetime.now(tz).strftime("%d-%m-%Y")
        msg = f"""
📍 জেলা: {text}
📅 তারিখ: {today}

🌙 সেহরির শেষ সময়: {fajr}
🍽️ ইফতার সময়: {maghrib}

উৎপাদক: @Md_atiqul_islam0
"""
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ জেলা লিখুন বা বাটন ব্যবহার করুন।")

from telegram.ext import CommandHandler
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))
app.run_polling()
