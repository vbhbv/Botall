# admin.py
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json"
ADMIN_ID = 6166700051

# تحميل المستخدمين والإعدادات
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

    if update.callback_query.from_user.id != ADMIN_ID:
        await query.message.reply_text("❌ ليس لديك صلاحية الوصول للوحة التحكم.")
        return

    data = query.data
    settings = load_settings()
    users = load_users()

    if data == "manage_subscription":
        settings["force_subscribe"] = not settings.get("force_subscribe", False)
        save_settings(settings)
        status = "✅ مفعل" if settings["force_subscribe"] else "❌ معطل"
        await query.edit_message_text(f"⚡ الاشتراك الإجباري الآن: {status}")

    elif data == "broadcast":
        await query.edit_message_text("📢 أرسل الرسالة للإذاعة لجميع المستخدمين:")
        context.user_data["broadcast"] = True

    elif data == "manage_users":
        total = len(users)
        await query.edit_message_text(f"👥 عدد المستخدمين: {total}")

    elif data == "bot_settings":
        await query.edit_message_text(f"⚙️ إعدادات البوت الحالية:\nاشتراك إجباري: {settings.get('force_subscribe')}")
