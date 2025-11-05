import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, MessageHandler, filters

USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json"
ADMIN_ID = 6166700051  # معرف حسابك

# ===== تحميل وحفظ البيانات =====
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"force_subscribe": False, "channel_id": ""}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# ===== لوحة التحكم =====
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ ليس لديك صلاحية الوصول للوحة التحكم.")
        return

    keyboard = [
        [InlineKeyboardButton("⚡ إدارة الاشتراك الإجباري", callback_data="manage_subscription")],
        [InlineKeyboardButton("📢 إذاعة الرسالة", callback_data="broadcast")],
        [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data="manage_users")],
        [InlineKeyboardButton("⚙️ إعدادات البوت", callback_data="bot_settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔧 لوحة التحكم:", reply_markup=reply_markup)

# ===== التعامل مع أزرار لوحة التحكم =====
async def admin_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("❌ ليس لديك صلاحية الوصول للوحة التحكم.")
        return

    data = query.data
    settings = load_settings()
    users = load_users()

    # إدارة الاشتراك الإجباري
    if data == "manage_subscription":
        settings["force_subscribe"] = not settings.get("force_subscribe", False)
        save_settings(settings)
        status = "✅ مفعل" if settings["force_subscribe"] else "❌ معطل"
        text = f"⚡ الاشتراك الإجباري الآن: {status}\n"
        if settings["force_subscribe"] and not settings.get("channel_id"):
            text += "📝 لم يتم تعيين قناة، الرجاء إرسال معرف القناة الآن."
            context.user_data["set_channel"] = True
        await query.edit_message_text(text)

    # إذاعة الرسائل
    elif data == "broadcast":
        await query.edit_message_text("📢 أرسل الرسالة للإذاعة لجميع المستخدمين:")
        context.user_data["broadcast"] = True

    # إدارة المستخدمين
    elif data == "manage_users":
        total = len(users)
        await query.edit_message_text(f"👥 عدد المستخدمين المسجلين: {total}")

    # إعدادات البوت
    elif data == "bot_settings":
        channel = settings.get("channel_id", "لم يتم تعيينه")
        text = (
            f"⚙️ إعدادات البوت الحالية:\n"
            f"✅ الاشتراك الإجباري: {settings.get('force_subscribe')}\n"
            f"📌 قناة الاشتراك: {channel}"
        )
        await query.edit_message_text(text)

# ===== التعامل مع الرسائل للإدارة =====
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        return

    # تعيين قناة الاشتراك الإجباري
    if context.user_data.get("set_channel"):
        channel_id = update.message.text.strip()
        settings = load_settings()
        settings["channel_id"] = channel_id
        save_settings(settings)
        await update.message.reply_text(f"✅ تم تعيين القناة للاشتراك الإجباري: {channel_id}")
        context.user_data["set_channel"] = False
        return

    # إرسال إذاعة
    if context.user_data.get("broadcast"):
        message = update.message.text
        users = load_users()
        count = 0
        for uid in users:
            try:
                await context.bot.send_message(chat_id=int(uid), text=message)
                count += 1
            except:
                continue
        await update.message.reply_text(f"✅ تم إرسال الرسالة إلى {count} مستخدمين.")
        context.user_data["broadcast"] = False
