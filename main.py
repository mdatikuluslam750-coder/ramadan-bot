import telebot
import os
from flask import Flask

# ১. এখানে আপনার আসল টোকেনটি খুব সাবধানে বসান (কোলন যেন থাকে)
API_TOKEN = 'আপনার_বট_টোকেন_এখানে_দিন' 

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

# রমজানের ডাটা (উদাহরণস্বরূপ ঢাকা)
ramadan_times = {
    "dhaka": {"sehri": "05:02 AM", "iftar": "06:05 PM"},
    "rajshahi": {"sehri": "05:08 AM", "iftar": "06:11 PM"}
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✨ আসসালামু আলাইকুম!\nইফতার ও সেহরির সময় জানতে জেলার নাম ইংরেজিতে লিখুন (যেমন: Dhaka)")

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    text = message.text.lower().strip()
    if text in ramadan_times:
        time = ramadan_times[text]
        bot.reply_to(message, f"📍 {text.capitalize()}\n🌅 সেহরি: {time['sehri']}\n🌇 ইফতার: {time['iftar']}")
    else:
        bot.reply_to(message, "⚠️ দুঃখিত, জেলাটি পাওয়া যায়নি। সঠিক বানান লিখুন (যেমন: Dhaka)।")

@server.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

# পোলিং মেথড (আপনার জন্য এটি সবচেয়ে সহজ হবে)
if __name__ == "__main__":
    print("বট সচল হচ্ছে...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
    
    
