import telebot
import time

# আপনার ইনফরমেশন
TOKEN = '8306608574:AAGWdhtMgE762ErstofYs_u0vdaVbBLes_0'
ADMIN_ID = 8402780798
BKASH_NUM = '01858480246'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(user_id, "⚙️ [SYSTEM] INITIALIZING SECURE TERMINAL...")
    time.sleep(1)
    bot.send_message(user_id, "🔐 আপনার ভল্ট সুরক্ষিত করতে একটি ৪-সংখ্যার পিন (PIN) দিন:")
    bot.register_next_step_handler(message, set_pin)

def set_pin(message):
    pin = message.text
    if pin.isdigit() and len(pin) == 4:
        bot.send_message(message.chat.id, f"✅ পিন সেট হয়েছে! প্রথম ৩০ দিন ফ্রি।\nবিকাশ নম্বর: {BKASH_NUM}")
    else:
        bot.send_message(message.chat.id, "❌ ভুল পিন! আবার চেষ্টা করুন:")
        bot.register_next_step_handler(message, set_pin)

bot.infinity_polling()
