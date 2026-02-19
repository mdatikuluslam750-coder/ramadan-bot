import os
import pytz
import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CallbackQueryHandler, filters, CommandHandler

# আপনার দেওয়া নতুন টোকেন
TOKEN = "8331922661:AAHsxItKbrKIKKv_bpdOqtgmClGLx2H02uw"

districts = {
    "ঢাকা": "Dhaka", "চট্টগ্রাম": "Chittagong", "রাজশাহী": "Rajshahi", "খুলনা": "Khulna", 
    "সিলেট": "Sylhet", "বরিশাল": "Barisal", "রংপুর": "Rangpur", "ময়মনসিংহ": "Mymensingh",
    "কুমিল্লা": "Comilla", "ফেনী": "Feni", "ব্রাহ্মণবাড়িয়া": "Brahmanbaria", "নোয়াখালী": "Noakhali",
    "চাঁদপুর": "Chandpur", "লক্ষ্মীপুর": "Lakshmipur", "কক্সবাজার": "Cox's Bazar", "খাগড়াছড়ি": "Khagrachhari",
    "রাঙ্গামাটি": "Rangamati", "বান্দরবান": "Bandarban", "সিরাজগঞ্জ": "Sirajganj", "পাবনা": "Pabna",
    "বগুড়া": "Bogra", "নাটোর": "Natore", "জয়পুরহাট": "Joypurhat", "চাঁপাইনবাবগঞ্জ": "Chapainawabganj",
    "নওগাঁ": "Naogaon", "যশোর": "Jessore", "সাতক্ষীরা": "Satkhira", "মেহেরপুর": "Meherpur",
    "নড়াইল": "Narail", "চুয়াডাঙ্গা": "Chuadanga", "কুষ্টিয়া": "Kushtia", "মাগুরা": "Magura",
    "বাগেরহাট": "Bagerhat", "ঝিনাইদহ": "Jhenaidah", "ঝালকাঠি": "Jhalokati", "পটুয়াখালী": "Patuakhali",
    "পিরোজপুর": "Pirojpur", "ভোলা": "Bhola", "বরগুনা": "Barguna", "পঞ্চগড়": "Panchagarh",
    "দিনাজপুর": "Dinajpur", "লালমনিরহাট": "Lalmonirhat", "নীলফামারী": "Nilphamari", "কুড়িগ্রাম": "Kurigram",
    "ঠাকুরগাঁও": "Thakurgaon", "গাইবান্ধা": "Gaibandha", "শেরপুর": "Sherpur", "জামালপুর": "Jamalpur",
    "নেত্রকোনা": "Netrokona", "কিশোরগঞ্জ": "Kishoreganj", "সুনামগঞ্জ": "Sunamganj", "হবিগঞ্জ": "Habiganj",
    "মৌলভীবাজার": "Moulvibazar", "গোপালগঞ্জ": "Gopalganj", "মাদারীপুর": "Madaripur", "শরীয়তপুর": "Shariatpur",
    "রাজবাড়ী": "Rajbari", "ফরিদপুর": "Faridpur", "টাঙ্গাইল": "Tangail", "মানিকগঞ্জ": "Manikganj",
    "মুন্সীগঞ্জ": "Munshiganj", "নরসিংদী": "Narsingdi", "নারায়ণগঞ্জ": "Narayanganj", "গাজীপুর": "Gazipur"
}

def get_buttons():
    buttons = []
    keys = list(districts.keys())
    for i in range(0, len(keys), 3):
        row = [InlineKeyboardButton(keys[j], callback_data=keys[j]) for j in range(i, min(i+3, len(keys)))]
        buttons.append(row)
    return buttons

def get_times(city):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Bangladesh&method=1"
        r = requests.get(url).json()
        return r["data"]["timings"]["Fajr"], r["data"]["timings"]["Maghrib"]
    except:
        return "N/A", "N/A"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup(get_buttons())
    await update.message.reply_text("🌙 আসসালামু আলাইকুম! ইফতার ও সেহরির সময় জানতে আপনার জেলা বেছে নিন:", reply_markup=kb)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    district = query.data
    fajr, maghrib = get_times(districts[district])
    tz = pytz.timezone("Asia/Dhaka")
    today = datetime.datetime.now(tz).strftime("%d-%m-%Y")
    msg = f"📍 জেলা: {district}\n📅 তারিখ: {today}\n\n🌅 সেহরির শেষ সময়: {fajr}\n🌇 ইফতার সময়: {maghrib}\n\nউৎপাদক: @Md_atiqul_islam0"
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(get_buttons()))

async def text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text in districts:
        fajr, maghrib = get_times(districts[text])
        tz = pytz.timezone("Asia/Dhaka")
        today = datetime.datetime.now(tz).strftime("%d-%m-%Y")
        await update.message.reply_text(f"📍 জেলা: {text}\n📅 তারিখ: {today}\n\n🌅 সেহরি: {fajr}\n🌇 ইফতার: {maghrib}")
    else:
        await update.message.reply_text("⚠️ সঠিক জেলার নাম লিখুন বা নিচের বাটন ব্যবহার করুন।")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))
    print("Bot is running...")
    app.run_polling()
        
