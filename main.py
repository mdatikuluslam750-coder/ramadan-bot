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
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

# --- প্রিমিয়াম অ্যানিমেশন ---
def run_premium_anim(chat_id, steps):
    msg = bot.send_message(chat_id, "⚙️ [INITIALIZING...]")
    for step in steps:
        try:
            time.sleep(0.4)
            bot.edit_message_text(step, chat_id, msg.message_id)
        except: pass
    return msg.message_id

# --- মেইন মেনু কীবোর্ড (সব বাটন এখানে আছে) ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    users_db = load_data()
    status = "Premium 👑" if users_db.get(uid, {}).get('is_paid') else "Free Trial ⏳"
    
    btn1 = types.KeyboardButton('📂 My Vault')
    btn2 = types.KeyboardButton('📝 Secure Note')
    btn3 = types.KeyboardButton('🔗 My Referral')
    btn4 = types.KeyboardButton(f'ℹ️ Status: {status}')
    btn5 = types.KeyboardButton('🔒 Lock Vault')
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    users_db = load_data()
    
    run_premium_anim(uid, ["📡 [BOOTING...]", "🛰️ [ENCRYPTING...]", "✅ [READY]"])
    
    if uid not in users_db:
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        users_db[uid] = {
            'pin': None, 
            'is_paid': False, 
            'vault': [], 
            'notes': [],
            'refer_count': 0, 
            'ref_by': ref_by, 
            'reg_date': datetime.now().strftime("%Y-%m-%d")
        }
        if ref_by and ref_by in users_db:
            users_db[ref_by]['refer_count'] += 1
            save_data(users_db)
            bot.send_message(ref_by, "🎉 অভিনন্দন! কেউ আপনার লিঙ্কে জয়েন করেছে।")
        
        save_data(users_db)
        bot.send_message(uid, "🛡️ **SECURITY PROTOCOL:**\nভল্ট ও নোটের জন্য একটি ৪-সংখ্যার PIN সেট করুন:")
        bot.register_next_step_handler(message, set_pin)
    else:
        p_msg = bot.send_message(uid, "🔐 **ENTER PIN TO ACCESS:**")
        bot.register_next_step_handler(message, check_pin, p_msg.message_id, "login")

def set_pin(message):
    uid = str(message.chat.id)
    if message.text.isdigit() and len(message.text) == 4:
        users_db = load_data()
        users_db[uid]['pin'] = message.text
        save_data(users_db)
        try: bot.delete_message(uid, message.message_id)
        except: pass
        bot.send_message(uid, "✅ PIN সফলভাবে সেট করা হয়েছে!", reply_markup=main_menu(uid))
    else:
        bot.send_message(uid, "❌ ভুল! শুধু ৪ সংখ্যার PIN দিন:")
        bot.register_next_step_handler(message, set_pin)

# --- পিন চেক সিস্টেম (ভল্ট ও নোট দুটোর জন্যই) ---
def check_pin(message, prompt_id, mode):
    uid = str(message.chat.id)
    users_db = load_data()
    pin_attempt = message.text
    
    try:
        bot.delete_message(uid, message.message_id)
        bot.delete_message(uid, prompt_id)
    except: pass

    if pin_attempt == users_db[uid]['pin']:
        if mode == "login":
            bot.send_message(uid, "🔓 **ভল্ট আনলক হয়েছে।**", reply_markup=main_menu(uid))
        elif mode == "view_vault":
            show_vault_contents(uid)
        elif mode == "view_notes":
            bot.send_message(uid, "📝 **আপনার সিকিউর নোটস:**\n\n" + ("\n".join(users_db[uid]['notes']) if users_db[uid]['notes'] else "কোনো নোট নেই।"))
    else:
        m = bot.send_message(uid, "❌ ভুল পিন! আবার চেষ্টা করুন:")
        bot.register_next_step_handler(message, check_pin, m.message_id, mode)

# --- রেফারেল সিস্টেম (ফিক্সড) ---
@bot.message_handler(func=lambda m: m.text == '🔗 My Referral')
def referral_fix(message):
    uid = str(message.chat.id)
    users_db = load_data()
    ref_link = f"https://t.me/allhighsecurity_bot?start={uid}"
    count = users_db[uid].get('refer_count', 0)
    
    text = (f"🎁 **রেফারেল স্ট্যাটাস**\n\n"
            f"🔗 আপনার লিঙ্ক: `{ref_link}`\n"
            f"👥 মোট রেফার: {count} জন\n\n"
            f"📢 ২০ জন রেফার করলে পরের এক মাস ফ্রি ট্রায়াল পাবেন!")
    bot.send_message(uid, text, parse_mode="Markdown")

# --- সিকিউর নোট (পিন প্রোটেক্টেড) ---
@bot.message_handler(func=lambda m: m.text == '📝 Secure Note')
def note_request(message):
    uid = str(message.chat.id)
    p_msg = bot.send_message(uid, "🔐 **SECURITY:** নোট দেখতে PIN দিন:")
    bot.register_next_step_handler(message, check_pin, p_msg.message_id, "view_notes")

# --- ভল্ট রিকোয়েস্ট ---
@bot.message_handler(func=lambda m: m.text == '📂 My Vault')
def vault_req(message):
    uid = str(message.chat.id)
    p_msg = bot.send_message(uid, "🔐 **SECURITY:** ভল্ট খুলতে PIN দিন:")
    bot.register_next_step_handler(message, check_pin, p_msg.message_id, "view_vault")

def show_vault_contents(uid):
    users_db = load_data()
    files = users_db[uid].get('vault', [])
    if not files:
        bot.send_message(uid, "ভল্ট খালি।")
    else:
        sent_ids = []
        for f in files:
            try:
                if f['type'] == 'photo': m = bot.send_photo(uid, f['id'])
                elif f['type'] == 'video': m = bot.send_video(uid, f['id'])
                else: m = bot.send_document(uid, f['id'])
                sent_ids.append(m.message_id)
            except: pass
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("✅ Done / দেখা শেষ", callback_data=f"clear_{','.join(map(str, sent_ids))}")
        markup.add(btn)
        bot.send_message(uid, "⚠️ দেখা শেষ হলে ক্লিয়ার করুন।", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('clear_'))
def clear_vault_session(call):
    uid = call.message.chat.id
    msg_ids = call.data.split('_')[1].split(',')
    for mid in msg_ids:
        try: bot.delete_message(uid, int(mid))
        except: pass
    try: bot.delete_message(uid, call.message.message_id)
    except: pass
    bot.send_message(uid, "🔒 **চ্যাট পরিষ্কার করা হয়েছে।**")

# --- লক ভল্ট ---
@bot.message_handler(func=lambda m: m.text == '🔒 Lock Vault')
def lock(message):
    run_premium_anim(message.chat.id, ["🔐 [LOCKING...]", "💤 [OFFLINE]"])
    bot.send_message(message.chat.id, "ভল্ট লক করা হয়েছে।", reply_markup=types.ReplyKeyboardRemove())

# --- স্ট্যাটাস বাটন ---
@bot.message_handler(func=lambda m: 'Status:' in m.text)
def status_info(message):
    uid = str(message.chat.id)
    users_db = load_data()
    is_paid = users_db[uid].get('is_paid', False)
    text = (f"ℹ️ **অ্যাকাউন্ট স্ট্যাটাস**\n\n"
            f"💎 টাইপ: {'Premium 👑' if is_paid else 'Free Trial ⏳'}\n"
            f"📞 বিকাশ: `{BKASH_NUM}`\n"
            f"💡 পেমেন্ট করলে বা ২০ জন রেফার করলে প্রিমিয়াম পাবেন।")
    bot.send_message(uid, text, parse_mode="Markdown")

print("All Systems Operational...")
bot.infinity_polling()
