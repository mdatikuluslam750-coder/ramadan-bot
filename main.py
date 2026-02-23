import telebot
import time
import json
import os
from telebot import types
from datetime import datetime

# --- সেটিংস ---
TOKEN = '8306608574:AAGWdhtMgE762ErstofYs_u0vdaVbBLes_0'
ADMIN_ID = 8402780798
BKASH_NUM = '01858480246'

bot = telebot.TeleBot(TOKEN)
DB_FILE = 'users_db.json'

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

users_db = load_data()

# --- অ্যানিমেশন ফাংশন ---
def run_animation(chat_id, text_list):
    msg = bot.send_message(chat_id, "⏳ [INITIALIZING...]")
    for text in text_list:
        try:
            time.sleep(0.4)
            bot.edit_message_text(text, chat_id, msg.message_id)
        except: pass
    return msg.message_id

# --- মেইন মেনু বাটন ---
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
    
    # স্টার্ট অ্যানিমেশন
    run_animation(uid, [
        "🔍 [SCANNING IDENTITY...]",
        "🛰️ [CONNECTING TO SERVER...]",
        "✅ [CONNECTION SECURE]"
    ])

    if uid not in users_db:
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        users_db[uid] = {
            'pin': None, 'is_paid': False, 'vault': [], 
            'refer_count': 0, 'ref_by': ref_by, 'reg_date': datetime.now().strftime("%Y-%m-%d")
        }
        if ref_by and ref_by in users_db:
            users_db[ref_by]['refer_count'] += 1
            if users_db[ref_by]['refer_count'] >= 20: users_db[ref_by]['is_paid'] = True
        save_data(users_db)
        bot.send_message(uid, "⚠️ **NEW TERMINAL DETECTED.**\nভল্ট ব্যবহারের জন্য একটি ৪-সংখ্যার PIN সেট করুন:")
        bot.register_next_step_handler(message, set_pin)
    else:
        p_msg = bot.send_message(uid, "🛡️ **ENTER PIN TO UNLOCK:**")
        bot.register_next_step_handler(message, check_pin, p_msg.message_id, "login")

def set_pin(message):
    uid = str(message.chat.id)
    if message.text.isdigit() and len(message.text) == 4:
        users_db[uid]['pin'] = message.text
        save_data(users_db)
        
        # পিন সেট করার অ্যানিমেশন
        run_animation(uid, [
            "🔐 [ENCRYPTING PIN...]",
            "💾 [SAVING TO DATABASE...]",
            "✨ [PIN ENCRYPTED SUCCESSFULLY!]"
        ])
        
        try: bot.delete_message(uid, message.message_id)
        except: pass
        bot.send_message(uid, "🔓 ভল্ট এখন ব্যবহারের জন্য প্রস্তুত!", reply_markup=main_menu(uid))
    else:
        bot.send_message(uid, "❌ পিন অবশ্যই ৪ সংখ্যার হতে হবে:")
        bot.register_next_step_handler(message, set_pin)

def check_pin(message, prompt_id, mode):
    uid = str(message.chat.id)
    pin_attempt = message.text
    
    # ইউজারের পিন মেসেজ এবং প্রম্পট ডিলিট করা
    try:
        bot.delete_message(uid, message.message_id)
        bot.delete_message(uid, prompt_id)
    except: pass

    if pin_attempt == users_db[uid]['pin']:
        # আনলকিং অ্যানিমেশন
        anim_id = run_animation(uid, [
            "🔑 [VERIFYING PIN...]",
            "🔓 [DECRYPTING FILES...]",
            "✅ [ACCESS GRANTED]"
        ])
        time.sleep(0.5)
        bot.delete_message(uid, anim_id) # অ্যানিমেশন মেসেজ মুছে ফেলা চ্যাট পরিষ্কার রাখার জন্য

        if mode == "login":
            bot.send_message(uid, "🔓 **ভল্ট আনলক হয়েছে।**", reply_markup=main_menu(uid))
        elif mode == "view_vault":
            show_vault_contents(uid)
    else:
        m = bot.send_message(uid, "❌ ভুল পিন! আবার চেষ্টা করুন:")
        bot.register_next_step_handler(message, check_pin, m.message_id, mode)

# --- ফাইল অটো ডিলিট ও সেভ সিস্টেম ---
@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_vault_files(message):
    uid = str(message.chat.id)
    if uid not in users_db or not users_db[uid]['pin']: return

    # ফাইল টাইপ অনুযায়ী আইডি নেওয়া
    if message.content_type == 'photo': f_id = message.photo[-1].file_id
    elif message.content_type == 'video': f_id = message.video.file_id
    else: f_id = message.document.file_id
    
    users_db[uid]['vault'].append({'type': message.content_type, 'id': f_id})
    save_data(users_db)
    
    # আপলোড অ্যানিমেশন
    up_id = run_animation(uid, [
        "📥 [UPLOADING FILE...]",
        "🔒 [ENCRYPTING DATA...]",
        "✅ [FILE SECURED & DELETED]"
    ])
    
    # চ্যাট থেকে অরিজিনাল ফাইল মুছে ফেলা
    try: bot.delete_message(uid, message.message_id)
    except: pass
    time.sleep(1)
    bot.delete_message(uid, up_id)
    bot.send_message(uid, "📥 ফাইলটি সফলভাবে আপনার ভল্টে জমা হয়েছে।")

# --- ভল্ট অ্যাক্সেস (ডাবল পিন লেয়ার) ---
@bot.message_handler(func=lambda m: m.text == '📂 My Vault')
def vault_access_request(message):
    uid = str(message.chat.id)
    p_msg = bot.send_message(uid, "🔐 **সিকিউরিটি চেক:** ভল্ট ওপেন করতে পুনরায় PIN দিন:")
    bot.register_next_step_handler(message, check_pin, p_msg.message_id, "view_vault")

def show_vault_contents(uid):
    files = users_db[uid].get('vault', [])
    if not files:
        bot.send_message(uid, "আপনার ভল্ট বর্তমানে খালি।")
    else:
        bot.send_message(uid, f"📦 **আপনার ভল্টে {len(files)} টি ফাইল আছে:**")
        for f in files:
            if f['type'] == 'photo': bot.send_photo(uid, f['id'])
            elif f['type'] == 'video': bot.send_video(uid, f['id'])
            else: bot.send_document(uid, f['id'])
        bot.send_message(uid, "⚠️ দেখা শেষ হলে 'Lock Vault' বাটনে ক্লিক করে চ্যাট পরিষ্কার করুন।")

@bot.message_handler(func=lambda m: m.text == '🔒 Lock Vault')
def lock(message):
    # লক করার সময় ছোট অ্যানিমেশন
    run_animation(message.chat.id, ["🔐 [LOCKING VAULT...]", "💤 [TERMINAL CLOSED]"])
    bot.send_message(message.chat.id, "ভল্ট লক করা হয়েছে।", reply_markup=types.ReplyKeyboardRemove())

print("Animated Security Terminal Online...")
bot.infinity_polling()
    
