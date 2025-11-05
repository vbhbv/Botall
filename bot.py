import os
import yt_dlp
import asyncio
import json
import shutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ===== إعدادات البوت =====
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6166700051  # معرفك الرقمي
USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json"

# ===== تنظيف مجلد downloads =====
if os.path.exists("downloads"):
    shutil.rmtree("downloads")
os.makedirs("downloads", exist_ok=True)

# ===== تحميل المستخدمين والإعدادات =====
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
else:
    settings = {"force_subscribe": False, "channel_id": ""}

# ===== حفظ المستخدمين =====
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# ===== حفظ الإعدادات =====
def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# ===== رسالة البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in users:
        users[user_id] = {"id": user_id}
        save_users()

    # التحقق من الاشتراك الإجباري
    if settings.get("force_subscribe") and settings.get("channel_id"):
        try:
            member = await context.bot.get_chat_member(settings["channel_id"], user_id)
            if member.status in ["left", "kicked"]:
                await update.message.reply_text(
                    f"⚠️ يجب الاشتراك في القناة أولاً: {settings['channel_id']}"
                )
                return
        except:
            pass

    await update.message.reply_text(
        "👋 أهلاً بك!\n"
        "أنا بوت التحميل الشامل Ultimate Media Downloader 🔥\n"
        "أرسل أي رابط من المنصات التالية:\n"
        "📘 Facebook\n📸 Instagram\n🎵 TikTok\n▶️ YouTube\n🐦 Twitter/X\n\n"
        "سأقوم بتحميله لك!"
    )

# ===== اكتشاف المنصة =====
def detect_platform(url: str):
    if "facebook.com" in url or "fb.watch" in url:
        return "Facebook"
    elif "instagram.com" in url:
        return "Instagram"
    elif "tiktok.com" in url:
        return "TikTok"
    elif "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    elif "twitter.com" in url or "x.com" in url:
        return "Twitter"
    else:
        return None

# ===== تحميل الفيديو أو الصوت =====
def download_media(url: str, audio_only=False, resolution=None):
    filename = "downloads/media.%(ext)s"
    ydl_opts = {"outtmpl": filename, "quiet": True, "noplaylist": True}

    if audio_only:
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        if resolution:
            ydl_opts["format"] = f"bestvideo[height<={resolution}]+bestaudio/best"
        else:
            ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        ext = "mp3" if audio_only else "mp4"
        return f"downloads/media.{ext}", info.get("title", "فيديو بدون عنوان")
    except Exception as e:
        print(f"❌ خطأ أثناء التحميل: {e}")
        return None, None

# ===== لوحة تحكم Admin Panel =====
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

# ===== التعامل مع روابط YouTube مع أزرار الفيديو/صوت =====
async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    keyboard = [
        [InlineKeyboardButton("🎬 تحميل الفيديو", callback_data=f"video|{url}")],
        [InlineKeyboardButton("🎵 تحميل الصوت", callback_data=f"audio|{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)

# ===== التعامل مع الرسائل =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in users:
        users[user_id] = {"id": user_id}
        save_users()

    url = update.message.text.strip()
    platform = detect_platform(url)

    if not platform:
        await update.message.reply_text("⚠️ أرسل رابط من Facebook / Instagram / TikTok / YouTube / Twitter فقط.")
        return

    if platform == "YouTube":
        await handle_youtube(update, context, url)
    else:
        await update.message.reply_text(f"⏳ جاري تحميل الفيديو من {platform}...")
        video_path, title = await asyncio.to_thread(download_media, url)
        if video_path and os.path.exists(video_path):
            await update.message.reply_video(open(video_path, "rb"), caption=f"✅ تم التحميل من {platform}\n🎬 {title}")
            os.remove(video_path)
        else:
            await update.message.reply_text("❌ لم أتمكن من تحميل الفيديو. تحقق من الرابط.")

# ===== التعامل مع أزرار لوحة التحكم والInline =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # ===== إدارة YouTube (الفيديو/صوت) =====
    if "|" in data:
        mode, url = data.split("|")
        audio_only = True if mode == "audio" else False
        await query.edit_message_text(f"⏳ جاري التحميل ({mode}) من YouTube...")
        video_path, title = await asyncio.to_thread(download_media, url, audio_only=audio_only)
        if video_path and os.path.exists(video_path):
            if audio_only:
                await query.message.reply_document(open(video_path, "rb"), caption=f"✅ تم تحميل الصوت: {title}")
            else:
                await query.message.reply_video(open(video_path, "rb"), caption=f"✅ تم تحميل الفيديو: {title}")
            os.remove(video_path)
        else:
            await query.message.reply_text("❌ فشل التحميل. تحقق من الرابط.")
        return

    # ===== لوحة التحكم =====
    if update.callback_query.from_user.id != ADMIN_ID:
        await query.message.reply_text("❌ ليس لديك صلاحية الوصول للوحة التحكم.")
        return

    if data == "manage_subscription":
        # تبديل الاشتراك الإجباري
        settings["force_subscribe"] = not settings.get("force_subscribe", False)
        save_settings()
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

# ===== إرسال الإذاعة =====
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("broadcast"):
        message = update.message.text
        count = 0
        for user_id in users:
            try:
                await context.bot.send_message(chat_id=int(user_id), text=message)
                count += 1
            except:
                continue
        await update.message.reply_text(f"✅ تم إرسال الرسالة إلى {count} مستخدمين.")
        context.user_data["broadcast"] = False
