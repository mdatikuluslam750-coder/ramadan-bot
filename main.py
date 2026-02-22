import telebot
import time
import json
import os
from datetime import datetime, timedelta

# আপনার কনফিগারেশন
TOKEN = '8306608574:AAGWdhtMgE762ErstofYs_u0vdaVbBLes_0'
ADMIN_ID = 8402780798
BKASH_NUM = '01858480246'

bot = telebot.TeleBot(TOKEN)

# ডাটাবেস ফাইল ম্যানেজমেন্ট
DB_FILE = 'users_db.json'

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ইউজার ডাটা লোড করা
users_db = load_data()

@bot.message_handler(commands=['start'])
def start_terminal(message):
    user_id = str(message.chat.id)
    
    # হ্যাকিং থিম অ্যানিমেশন
    msg = bot.send_message(user_id, "🔍 [SYSTEM CHECKING...] █▒▒▒▒▒▒▒▒▒ 10%")
    time.sleep(0.5)
    bot.edit_message_text("🔍 [DECRYPTING...] ██████▒▒▒▒ 60%", chat_id=user_id, message_id=msg.message_id)
    time.sleep(0.5)
    bot.edit_message_text("✅ [ACCESS GRANTED] ██████████ 100%\n\n**TERMINAL ACTIVATED.**", chat_id=user_id, message_id=msg.message_id, parse_mode="Markdown")

    if user_id not in users_db:
        users_db[user_id] = {
            'pin': None,
            'reg_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_paid': False
        }
        save_data(users_db)
        bot.send_message(user_id, "⚠️ **NEW USER DETECTED.**\n\nআপনার ভল্ট সুরক্ষিত করতে একটি ৪-ডিজিটের **SECURITY PIN** সেট করুন (যেমন: 5050):", parse_mode="Markdown")
        bot.register_next_step_handler(message, set_pin)
    else:
        check_vault_status(message)

def set_pin(message):
    user_id = str(message.chat.id)
    pin = message.text
    if len(pin) == 4 and pin.isdigit():
        users_db[user_id]['pin'] = pin
        save_data(users_db)
        bot.send_message(user_id, "🔐 **PIN ENCRYPTED SUCCESSFULLY.**\n\nপ্রথম ৩০ দিন আপনি ভল্টটি সম্পূর্ণ ফ্রি ব্যবহার করতে পারবেন।")
    else:
        bot.send_message(user_id, "❌ **ERROR:** PIN অবশ্যই ৪ সংখ্যার হতে হবে। আবার ট্রাই করুন:")
        bot.register_next_step_handler(message, set_pin)

def check_vault_status(message):
    user_id = str(message.chat.id)
    user_data = users_db[user_id]
    
    reg_date = datetime.strptime(user_data['reg_date'], "%Y-%m-%d %H:%M:%S")
    days_used = (datetime.now() - reg_date).days
    
    if days_used >= 30 and not user_data['is_paid']:
        bot.send_message(user_id, f"🔒 **VAULT LOCKED: TRIAL EXPIRED.**\n\nআপনার ফ্রি ট্রায়াল শেষ। আনলক করতে ২০ টাকা বিকাশ করুন:\n\n📞 **bKash (Send Money):** `{BKASH_NUM}`\n\nটাকা পাঠিয়ে TrxID টি এখানে দিন:", parse_mode="Markdown")
        bot.register_next_step_handler(message, process_payment)
    else:
        bot.send_message(user_id, "🛡️ **ENTER SECURITY PIN TO UNLOCK:**")
        bot.register_next_step_handler(message, unlock_vault)

def unlock_vault(message):
    user_id = str(message.chat.id)
    if message.text == users_db[user_id]['pin']:
        bot.send_message(user_id, "🔓 **ACCESS GRANTED.**\n\nআপনার সিক্রেট ভল্ট ওপেন হয়েছে।")
    else:
        bot.send_message(user_id, "❌ **WRONG PIN.** ACCESS DENIED.")

def process_payment(message):
    user_id = str(message.chat.id)
    trx_id = message.text
    admin_msg = f"🔔 **NEW PAYMENT!**\n\nUser ID: `{user_id}`\nTrxID: `{trx_id}`"
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    bot.send_message(user_id, "⌛ **PENDING...**\n\nঅ্যাডমিন আপনার TrxID ভেরিফাই করলেই ভল্ট আনলক হবে।")

print("System is Online...")
bot.infinity_polling()
