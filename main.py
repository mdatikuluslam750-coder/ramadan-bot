import telebot
import time
import json
import os
from telebot import types
from datetime import datetime

# ১. আপনার তথ্য
TOKEN = '8306608574:AAGWdhtMgE762ErstofYs_u0vdaVbBLes_0'
ADMIN_ID = 8402780798
BKASH_NUM = '01858480246'

bot = telebot.TeleBot(TOKEN)
DB_FILE = 'users_db.json'

# ডাটাবেস ফাংশন
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

users_db = load_data()

# মেইন মেনু বাটন
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    status = "Premium 👑" if users_db[uid].get('is_paid') else "Free Trial ⏳"
    markup.add('📂 My Vault', '📝 Secure Note')
    markup.add('🔗 My Referral', f'ℹ️ Status: {status}')
    markup.add('🔒 Lock Vault')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    bot.send_message(uid, "🔍 [SYSTEM CHECKING...] █▒▒▒▒▒▒▒▒▒ 10%")
    time.sleep(0.4)
    
    if uid not in users_db:
        # নতুন ইউজার হলে রেফারেল সিস্টেম সেট করা
        ref_by = None
        if len(message.text.split()) > 1:
            ref_by = message.text.split()[1] # রেফার কোড

        users_db[uid] = {
            'pin': None, 
            'reg_date': datetime.now().strftime("%Y-%m-%d"), 
            'is_paid': False, 
            'vault': [], 
            'refer_by': ref_by,
            'refer_count': 0
        }
        
        # যদি কেউ রেফার করে থাকে তার কাউন্ট বাড়ানো
        if ref_by and ref_by in users_db:
            users_db[ref_by]['refer_count'] += 1
            bot.send_message(ref_by, "🔔 কেউ আপনার রেফার কোড ব্যবহার করে জয়েন করেছে!")
            
        save_data(users_db)
        bot.send_message(uid, "⚠️ **UNAUTHORIZED ACCESS.**\nভল্ট সিকিউর করতে একটি ৪-সংখ্যার PIN দিন:")
        bot.register_next_step_handler(message, set_pin)
    else:
        bot.send_message(uid, "🛡️ **ENTER PIN TO UNLOCK:**")
        bot.register_next_step_handler(message, check_pin)

def set_pin(message):
    uid = str(message.chat.id)
    pin_text = message.text
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass

    if pin_text.isdigit() and len(pin_text) == 4:
        users_db[uid]['pin'] = pin_text
        save_data(users_db)
        bot.send_message(uid, "✅ PIN সেট করা হয়েছে। আপনার ভল্ট এখন সম্পূর্ণ ব্যক্তিগত।", reply_markup=main_menu(uid))
    else:
        bot.send_message(uid, "❌ ভুল! শুধু ৪টি সংখ্যা দিন:")
        bot.register_next_step_handler(message, set_pin)

def check_pin(message):
    uid = str(message.chat.id)
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass

    if message.text == users_db[uid]['pin']:
        bot.send_message(uid, "🔓 ACCESS GRANTED.", reply_markup=main_menu(uid))
    else:
        bot.send_message(uid, "❌ WRONG PIN. আবার চেষ্টা করুন:")
        bot.register_next_step_handler(message, check_pin)

# রেফারেল ইনফো
@bot.message_handler(func=lambda m: m.text == '🔗 My Referral')
def referral(message):
    uid = str(message.chat.id)
    ref_link = f"https://t.me/allhighsecurity_bot?start={uid}"
    count = users_db[uid].get('refer_count', 0)
    bot.send_message(uid, f"🎁 **Refer & Earn**\n\nআপনার রেফারেল লিঙ্ক:\n`{ref_link}`\n\nমোট রেফারেল: {count} জন।\n(৫ জন রেফার করলে ১ মাস ফ্রি পাবেন - অ্যাডমিনকে জানান)", parse_mode="Markdown")

# ফাইল সেভ করা
@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_files(message):
    uid = str(message.chat.id)
    if uid not in users_db or not users_db[uid]['pin']: return
    
    file_id = ""
    if message.content_type == 'photo': file_id = message.photo[-1].file_id
    elif message.content_type == 'video': file_id = message.video.file_id
    elif message.content_type == 'document': file_id = message.document.file_id
    
    users_db[uid]['vault'].append({'type': message.content_type, 'file_id': file_id})
    save_data(users_db)
    bot.reply_to(message, "📥 আপনার ফাইলটি আপনার ব্যক্তিগত ভল্টে সুরক্ষিতভাবে রাখা হয়েছে।")

@bot.message_handler(func=lambda m: m.text == '📂 My Vault')
def view_vault(message):
    uid = str(message.chat.id)
    files = users_db[uid].get('vault', [])
    if not files:
        bot.send_message(uid, "আপনার ভল্ট বর্তমানে খালি।")
    else:
        bot.send_message(uid, f"📦 আপনার ভল্টে {len(files)} টি ফাইল আছে।")
        for f in files:
            if f['type'] == 'photo': bot.send_photo(uid, f['file_id'])
            elif f['type'] == 'video': bot.send_video(uid, f['file_id'])
            elif f['type'] == 'document': bot.send_document(uid, f['file_id'])

@bot.message_handler(func=lambda m: m.text == '🔒 Lock Vault')
def lock(message):
    bot.send_message(message.chat.id, "🔐 Vault Locked. আবার ঢুকতে /start দিন।", reply_markup=types.ReplyKeyboardRemove())

print("System is Online...")
bot.infinity_polling()
                     
