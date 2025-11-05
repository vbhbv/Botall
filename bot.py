import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# ===== رسالة البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك!\n"
        "أنا بوت التحميل الشامل 🔥\n"
        "أرسل لي أي رابط من المنصات التالية وسأحمّله لك:\n\n"
        "📘 Facebook\n📸 Instagram\n🎵 TikTok\n▶️ YouTube\n\n"
        "كل ما عليك هو إرسال الرابط فقط 💥"
    )

# ===== دالة التحميل =====
def download_video(url: str):
    output_path = "video.mp4"
    ydl_opts = {
        "outtmpl": output_path,
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        return output_path, info.get("title", "فيديو بدون عنوان")
    except Exception as e:
        print(f"❌ خطأ أثناء التحميل: {e}")
        return None, None

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

# ===== التعامل مع الرسائل =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    platform = detect_platform(url)

    if not platform:
        await update.message.reply_text("⚠️ أرسل لي رابط من Facebook أو Instagram أو TikTok أو YouTube فقط.")
        return

    await update.message.reply_text(f"⏳ جاري تحميل الفيديو من {platform}...")

    video_path, title = await asyncio.to_thread(download_video, url)

    if video_path and os.path.exists(video_path):
        await update.message.reply_video(video=open(video_path, "rb"), caption=f"✅ تم التحميل من {platform}\n🎬 {title}")
        os.remove(video_path)
    else:
        await update.message.reply_text("❌ لم أستطع تحميل الفيديو. تأكد أن الرابط عام أو صالح.")

# ===== التشغيل =====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 البوت الشامل يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
