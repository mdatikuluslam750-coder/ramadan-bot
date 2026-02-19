import telebot
import os
from flask import Flask, request

# আপনার বটের টোকেন এখানে দিন
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# জেলা অনুযায়ী সময়সূচীর একটি স্যাম্পল ডাটা (আপনি আপনার মতো সময় বাড়াতে পারেন)
ramadan_data = {
    "dhaka": {"sehri": "05:02 AM", "iftar": "06:05 PM"},
    "chittagong": {"sehri": "04:58 AM", "iftar": "06:01 PM"},
    "sylhet": {"sehri": "04:55 AM", "iftar": "05:58 PM"},
    # আরও জেলা এখানে যোগ করতে পারেন
}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "✨ আসসালামু আলাইকুম!\n📍 ইফতার ও সেহরির সময় জানতে আপনার জেলার নাম ইংরেজিতে লিখুন (যেমন: Dhaka)")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.lower().strip()
    
    if user_input in ramadan_data:
        data = ramadan_data[user_input]
        response = f"📍 জেলা: {user_input.capitalize()}\n🌅 সেহরির শেষ সময়: {data['sehri']}\n🌇 ইফতারের সময়: {data['iftar']}"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "⚠️ দুঃখিত, এই জেলার নাম আমার তালিকায় নেই। দয়া করে সঠিক বানান লিখুন (যেমন: Dhaka)।")

# Render এর জন্য Flask অংশ
@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    # আপনার Render এর URL এখানে দিন (যেমন: https://ramadan-bot-1.onrender.com/)
    bot.set_webhook(url='https://আপনার-লিঙ্ক.onrender.com/' + API_TOKEN)
    return "Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    
    
