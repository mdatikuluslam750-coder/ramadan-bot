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

# --- প্রফেশনাল অ্যানিমেশন ---
def run_premium_anim(chat_id, steps):
    msg = bot.send_message(chat_id, "⚙️ [INITIALIZING...]")
    for step in steps:
        try:
            time.sleep(0.4)
            bot.edit_message_text(step, chat_id, msg.message_id)
        except: pass
    return msg.message_id

# --- মেইন কিবোর্ড ---
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
    run_premium_anim(uid, ["📡 [BOOTING SYSTEM...]", "🛰️ [ENCRYPTING CHANNEL...]", "✅ [TERMINAL READY]"])
    
    if uid not in users_db:
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        users_db[uid] = {
            'pin': None, 'is_paid': False, 'vault': [], 
            'refer_count': 0, 'ref_by': ref_by, 'reg_date': datetime.now().strftime("%Y-%m-%d")
        }
        if ref_by and ref_by in users_db:
            users_db[ref_by]['refer_count'] += 1
            if users_db[ref_by]['refer_count'] >= 20:
                bot.send_message(ADMIN_ID, f"🔔 User `{ref_by}` ২০টি রেফার পূর্ণ করেছে!")
        save_data(users_db)
        bot.send_message(uid, "🛡️ **NEW USER DETECTED.**\nভল্ট সুরক্ষিত করতে একটি ৪-সংখ্যার PIN সেট করুন:")
        bot.register_next_step_handler(message, set_pin)
    else:
        p_msg = bot.send_message(uid, "🔐 **ENTER PIN TO UNLOCK:**")
        bot.register_next_step_handler(message, check_pin, p_msg.message_id, "login")

def set_pin(message):
    uid = str(message.chat.id)
    if message.text.isdigit() and len(message.text) == 4:
        users_db[uid]['pin'] = message.text
        save_data(users_db)
        run_premium_anim(uid, ["🔐 [ENCRYPTING PIN...]", "💎 [PIN SECURED SUCCESSFULLY]"])
        try: bot.delete_message(uid, message.message_id)
        except: pass
        bot.send_message(uid, "🔓 ভল্ট এখন প্রস্তুত!", reply_markup=main_menu(uid))
    else:
        bot.send_message(uid, "❌ ভুল! শুধু ৪টি সংখ্যা দিন:")
        bot.register_next_step_handler(message, set_pin)

# --- পিন চেক ও এক্সপায়ারি চেক ---
def check_pin(message, prompt_id, mode):
    uid = str(message.chat.id)
    pin_attempt = message.text
    
    # এক্সপায়ারি চেক (৩০ দিন)
    reg_date_str = users_db[uid].get('reg_date', datetime.now().strftime("%Y-%m-%d"))
    reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d")
    days_passed = (datetime.now() - reg_date).days

    if days_passed > 30 and not users_db[uid].get('is_paid', False):
        bot.send_message(uid, f"🚫 **ট্রায়াল শেষ!**\n\nবটটি সচল করতে ২০ টাকা বিকাশ করুন অথবা ২০ জন রেফার করুন।\n📞 বিকাশ: `{BKASH_NUM}`", parse_mode="Markdown")
        return

    try:
        bot.delete_message(uid, message.message_id)
        bot.delete_message(uid, prompt_id)
    except: pass

    if pin_attempt == users_db[uid]['pin']:
        anim_id = run_premium_anim(uid, ["🔑 [VERIFYING...]", "🔓 [ACCESS GRANTED]"])
        time.sleep(0.5)
        bot.delete_message(uid, anim_id)
        if mode == "login":
            bot.send_message(uid, "🔓 **ভল্ট ওপেন হয়েছে।**", reply_markup=main_menu(uid))
        elif mode == "view_vault":
            show_vault_contents(uid)
    else:
        m = bot.send_message(uid, "❌ ভুল পিন! আবার চেষ্টা করুন:")
        bot.register_next_step_handler(message, check_pin, m.message_id, mode)

# --- ফাইল অটো ডিলিট ও সেভ ---
@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_files(message):
    uid = str(message.chat.id)
    if uid not in users_db or not users_db[uid]['pin']: return

    f_type = message.content_type
    f_id = message.photo[-1].file_id if f_type == 'photo' else (message.video.file_id if f_type == 'video' else message.document.file_id)
    
    users_db[uid]['vault'].append({'type': f_type, 'id': f_id})
    save_data(users_db)
    
    try: bot.delete_message(uid, message.message_id) # পাঠানো ফাইল সাথে সাথে ডিলিট
    except: pass
    bot.send_message(uid, "📥 **ফাইলটি আপনার এনক্রিপ্টেড ভল্টে সেভ করা হয়েছে।**")

# --- ডাবল সিকিউরিটি ও 'Done' বাটন ---
@bot.message_handler(func=lambda m: m.text == '📂 My Vault')
def vault_req(message):
    uid = str(message.chat.id)
    p_msg = bot.send_message(uid, "🔐 **সিকিউরিটি চেক:** ভল্ট খুলতে পুনরায় PIN দিন:")
    bot.register_next_step_handler(message, check_pin, p_msg.message_id, "view_vault")

def show_vault_contents(uid):
    files = users_db[uid].get('vault', [])
    if not files:
        bot.send_message(uid, "আপনার ভল্ট বর্তমানে খালি।")
    else:
        sent_ids = []
        msg = bot.send_message(uid, f"📦 **আপনার ভল্টে {len(files)} টি ফাইল আছে:**")
        sent_ids.append(msg.message_id)

        for f in files:
            try:
                if f['type'] == 'photo': m = bot.send_photo(uid, f['id'])
                elif f['type'] == 'video': m = bot.send_video(uid, f['id'])
                else: m = bot.send_document(uid, f['id'])
                sent_ids.append(m.message_id)
            except: pass
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("✅ Done Viewing / দেখা শেষ", callback_data=f"clear_{','.join(map(str, sent_ids))}")
        markup.add(btn)
        bot.send_message(uid, "⚠️ **সতর্কতা:** দেখা শেষ হলে নিচের বাটনে ক্লিক করুন। সব ছবি চ্যাট থেকে মুছে যাবে।", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('clear_'))
def clear_vault_chat(call):
    msg_ids = call.data.split('_')[1].split(',')
    for mid in msg_ids:
        try: bot.delete_message(call.message.chat.id, int(mid))
        except: pass
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, "🔒 **চ্যাট হিস্ট্রি পরিষ্কার করা হয়েছে।**")

@bot.message_handler(func=lambda m: m.text == '🔗 My Referral')
def referral(message):
    uid = str(message.chat.id)
    ref_link = f"https://t.me/allhighsecurity_bot?start={uid}"
    count = users_db[uid].get('refer_count', 0)
    text = (f"🎁 **রেফারেল প্রোগ্রাম**\n\n🔗 লিঙ্ক: `{ref_link}`\n👥 মোট রেফার: {count} জন\n\n"
            f"📢 ২০ জন রেফার করলে পরের মাস ফ্রি! নাহলে ২০ টাকা চার্জ দিতে হবে।")
    bot.send_message(uid, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: 'Status:' in m.text)
def check_status(message):
    uid = str(message.chat.id)
    text = (f"ℹ️ **স্ট্যাটাস চেক**\n\n💎 স্ট্যাটাস: {'Premium 👑' if users_db[uid]['is_paid'] else 'Free Trial ⏳'}\n"
            f"💡 ৩০ দিন পর ২০ টাকা বিকাশ করুন অথবা ২০ জন রেফার করুন।\n📞 বিকাশ: `{BKASH_NUM}`")
    bot.send_message(uid, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '🔒 Lock Vault')
def lock(message):
    run_premium_anim(message.chat.id, ["🔐 [LOCKING VAULT...]", "💤 [OFFLINE]"])
    bot.send_message(message.chat.id, "ভল্ট লক করা হয়েছে।", reply_markup=types.ReplyKeyboardRemove())

# অ্যাডমিন কমান্ড: /approve 12345678
@bot.message_handler(commands=['approve'])
def approve_user(message):
    if message.chat.id == ADMIN_ID:
        try:
            target_id = message.text.split()[1]
            users_db[target_id]['is_paid'] = True
            save_data(users_db)
            bot.send_message(ADMIN_ID, f"✅ User {target_id} approved!")
            bot.send_message(target_id, "🎉 অভিনন্দন! আপনার প্রিমিয়াম এক্সেস চালু হয়েছে।")
        except: bot.send_message(ADMIN_ID, "ব্যবহার: `/approve USER_ID`")

print("System is Online...")
bot.infinity_polling()
        
