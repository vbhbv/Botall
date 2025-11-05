import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")

# ===== رسالة البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ===== تحميل الفيديو/صوت =====
def download_media(url: str, audio_only=False, resolution=None):
    filename = "downloads/media.%(ext)s"
    ydl_opts = {
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
    }

    if audio_only:
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # اختيار جودة محددة إذا تم تحديدها
        if resolution:
            ydl_opts["format"] = f"bestvideo[height<={resolution}]+bestaudio/best"
        else:
            ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio/best"

    os.makedirs("downloads", exist_ok=True)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        ext = "mp3" if audio_only else "mp4"
        return f"downloads/media.{ext}", info.get("title", "فيديو بدون عنوان")
    except Exception as e:
        print(f"❌ خطأ أثناء التحميل: {e}")
        return None, None

# ===== التعامل مع YouTube مع أزرار الفيديو/صوت =====
async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    keyboard = [
        [InlineKeyboardButton("🎬 تحميل الفيديو", callback_data=f"video|{url}")],
        [InlineKeyboardButton("🎵 تحميل الصوت", callback_data=f"audio|{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)

# ===== التعامل مع الرسائل =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await update.message.reply_video(video=open(video_path, "rb"), caption=f"✅ تم التحميل من {platform}\n🎬 {title}")
            os.remove(video_path)
        else:
            await update.message.reply_text("❌ لم أتمكن من تحميل الفيديو. تحقق من الرابط.")

# ===== التعامل مع أزرار Inline =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    mode, url = data.split("|")
    audio_only = True if mode == "audio" else False

    await query.edit_message_text(f"⏳ جاري التحميل ({mode}) من YouTube...")

    video_path, title = await asyncio.to_thread(download_media, url, audio_only=audio_only)

    if video_path and os.path.exists(video_path):
        if audio_only:
            await query.message.reply_document(document=open(video_path, "rb"), caption=f"✅ تم تحميل الصوت: {title}")
        else:
            await query.message.reply_video(video=open(video_path, "rb"), caption=f"✅ تم تحميل الفيديو: {title}")
        os.remove(video_path)
    else:
        await query.message.reply_text("❌ فشل التحميل. تحقق من الرابط.")

# ===== التشغيل =====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🚀 البوت الشامل Ultimate Media Downloader يعمل الآن")
    app.run_polling()

if __name__ == "__main__":
    main()
