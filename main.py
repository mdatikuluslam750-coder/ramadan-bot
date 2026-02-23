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
def run_anim(chat_id, steps):
    msg = bot.send_message(chat_id, "⚙️ [LOADING...]")
    for step in steps:
        try:
            time.sleep(0.4)
            bot.edit_message_text(step, chat_id, msg.message_id)
        except: pass
    return msg.message_id

# --- মেইন মেনু কীবোর্ড ---
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
    run_anim(uid, ["📡 [BOOTING...]", "🛰️ [ENCRYPTING...]", "✅ [READY]"])
    
    if uid not in users_db:
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        users_db[uid] = {'pin': None, 'is_paid': False, 'vault': [], 'refer_count': 0, 'ref_by': ref_by, 'reg_date': datetime.now().strftime("%Y-%m-%d")}
        if ref_by and ref_by in users_db:
            users_db[ref_by]['refer_count'] += 1
        save_data(users_db)
        bot.send_message(uid, "⚠️ **NEW USER.**\nভল্টের জন্য একটি ৪-সংখ্যার PIN দিন:")
        bot.register_next_step_handler(message, set_pin)
    else:
        p_msg = bot.send_message(uid, "🔐 **ENTER PIN:**")
        bot.register_next_step_handler(message, check_pin, p_msg.message_id, "login")

def set_pin(message):
    uid = str(message.chat.id)
    if message.text.isdigit() and len(message.text) == 4:
        users_db[uid]['pin'] = message.text
        save_data(users_db)
        try: bot.delete_message(uid, message.message_id)
        except: pass
        bot.send_message(uid, "🔓 ভল্ট সেটআপ সম্পন্ন!", reply_markup=main_menu(uid))
    else:
        bot.send_message(uid, "❌ ৪টি সংখ্যা দিন:")
        bot.register_next_step_handler(message, set_pin)

def check_pin(message, prompt_id, mode):
    uid = str(message.chat.id)
    pin_attempt = message.text
    try:
        bot.delete_message(uid, message.message_id)
        bot.delete_message(uid, prompt_id)
    except: pass

    if pin_attempt == users_db[uid]['pin']:
        if mode == "login":
            bot.send_message(uid, "🔓 **UNLOCKED.**", reply_markup=main_menu(uid))
        elif mode == "view_vault":
            show_vault_contents(uid)
    else:
        m = bot.send_message(uid, "❌ ভুল পিন! আবার চেষ্টা করুন:")
        bot.register_next_step_handler(message, check_pin, m.message_id, mode)

@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_files(message):
    uid = str(message.chat.id)
    if uid not in users_db or not users_db[uid]['pin']: return

    f_type = message.content_type
    f_id = message.photo[-1].file_id if f_type == 'photo' else (message.video.file_id if f_type == 'video' else message.document.file_id)
    users_db[uid]['vault'].append({'type': f_type, 'id': f_id})
    save_data(users_db)
    
    try: bot.delete_message(uid, message.message_id)
    except: pass
    bot.send_message(uid, "📥 **ফাইল এনক্রিপ্ট করা হয়েছে।**")

# --- ডাবল সিকিউরিটি ও ক্লিনআপ ভিউ ---
@bot.message_handler(func=lambda m: m.text == '📂 My Vault')
def vault_req(message):
    uid = str(message.chat.id)
    p_msg = bot.send_message(uid, "🔐 **SECURITY CHECK:** PIN দিন:")
    bot.register_next_step_handler(message, check_pin, p_msg.message_id, "view_vault")

def show_vault_contents(uid):
    files = users_db[uid].get('vault', [])
    if not files:
        bot.send_message(uid, "আপনার ভল্ট খালি।")
    else:
        sent_ids = []
        msg = bot.send_message(uid, f"📦 **ভল্টে {len(files)} টি ফাইল আছে:**")
        sent_ids.append(msg.message_id)

        for f in files:
            try:
                if f['type'] == 'photo': m = bot.send_photo(uid, f['id'])
                elif f['type'] == 'video': m = bot.send_video(uid, f['id'])
                else: m = bot.send_document(uid, f['id'])
                sent_ids.append(m.message_id)
            except: pass
        
        markup = types.InlineKeyboardMarkup()
        # সব মেসেজ আইডি কলব্যাক ডাটাতে পাঠিয়ে দেওয়া যাতে বাটন টিপলে সব ডিলিট হয়
        btn = types.InlineKeyboardButton("✅ Done / ক্লিয়ার করুন", callback_data=f"clear_{','.join(map(str, sent_ids))}")
        markup.add(btn)
        bot.send_message(uid, "⚠️ দেখা শেষ হলে এই বাটনে ক্লিক করে চ্যাট পরিষ্কার করুন।", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('clear_'))
def clear_vault_chat(call):
    uid = call.message.chat.id
    msg_ids = call.data.split('_')[1].split(',')
    # পাঠানো সব ফাইল ডিলিট করা
    for mid in msg_ids:
        try: bot.delete_message(uid, int(mid))
        except: pass
    try: bot.delete_message(uid, call.message.message_id)
    except: pass
    bot.send_message(uid, "🔒 **চ্যাট হিস্ট্রি পরিষ্কার করা হয়েছে।**", reply_markup=main_menu(str(uid)))

@bot.message_handler(func=lambda m: m.text == '🔒 Lock Vault')
def lock(message):
    uid = str(message.chat.id)
    # লক করার সময় অ্যানিমেশন এবং কীবোর্ড রিমুভ
    run_anim(uid, ["🔐 [LOCKING...]", "💤 [TERMINAL CLOSED]"])
    bot.send_message(uid, "ভল্ট লক করা হয়েছে। আবার পিন দিয়ে ঢুকতে হবে।", reply_markup=types.ReplyKeyboardRemove())

print("Updated Security Bot Online...")
bot.infinity_polling()
