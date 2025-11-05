import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

# ===== رسالة البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك!\n"
        "أنا بوت التحميل الشامل 🔥\n"
        "أرسل أي رابط من المنصات التالية:\n"
        "📘 Facebook\n📸 Instagram\n🎵 TikTok\n▶️ YouTube\n\n"
        "سأقوم بتحميله لك!"
    )

# ===== تحديد المنصة =====
def detect_platform(url: str):
    if "facebook.com" in url or "fb.watch" in url:
        return "Facebook"
    elif "instagram.com" in url:
        return "Instagram"
    elif "tiktok.com" in url:
        return "TikTok"
    elif "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    else:
        return None

# ===== دالة التحميل =====
def download_video(url: str, audio_only=False):
    output_path = "video.mp4" if not audio_only else "audio.mp3"
    ydl_opts = {
        "outtmpl": output_path,
        "quiet": True,
        "format": "bestaudio/best" if audio_only else "bestvideo[ext=mp4]+bestaudio/best",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if audio_only else [],
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path
    except Exception as e:
        print(f"❌ خطأ أثناء التحميل: {e}")
        return None

# ===== التعامل مع روابط YouTube =====
async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    keyboard = [
        [InlineKeyboardButton("🎬 تحميل الفيديو", callback_data=f"video|{url}")],
        [InlineKeyboardButton("🎵 تحميل الصوت", callback_data=f"audio|{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)

# ===== التعامل مع أي رسالة =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    platform = detect_platform(url)

    if not platform:
        await update.message.reply_text("⚠️ أرسل رابط من Facebook / Instagram / TikTok / YouTube فقط.")
        return

    if platform == "YouTube":
        await handle_youtube(update, context, url)
    else:
        await update.message.reply_text(f"⏳ جاري تحميل الفيديو من {platform}...")
        video_path = await asyncio.to_thread(download_video, url)
        if video_path and os.path.exists(video_path):
            await update.message.reply_video(video=open(video_path, "rb"), caption=f"✅ تم التحميل من {platform}")
            os.remove(video_path)
        else:
            await update.message.reply_text("❌ لم أتمكن من تحميل الفيديو. تحقق من الرابط.")

# ===== التعامل مع أزرار Inline =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    mode, url = data.split("|")
    await query.edit_message_text(f"⏳ جاري التحميل ({mode}) من YouTube...")

    audio_only = True if mode == "audio" else False
    file_path = await asyncio.to_thread(download_video, url, audio_only=audio_only)

    if file_path and os.path.exists(file_path):
        if audio_only:
            await query.message.reply_document(document=open(file_path, "rb"), caption="✅ تم تحميل الصوت بنجاح!")
        else:
            await query.message.reply_video(video=open(file_path, "rb"), caption="✅ تم تحميل الفيديو بنجاح!")
        os.remove(file_path)
    else:
        await query.message.reply_text("❌ فشل التحميل. تحقق من الرابط.")

# ===== التشغيل =====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🚀 البوت الشامل يعمل الآن مع دعم YouTube + زر الصوت/الفيديو")
    app.run_polling()

if __name__ == "__main__":
    main()
