from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("yt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("👋 Send me a YouTube link and choose what to download.")

@app.on_message(filters.text & filters.private)
def yt_handler(client, message):
    url = message.text.strip()
    if "youtu" not in url:
        return message.reply("❌ That doesn't look like a YouTube link.")
    
    buttons = [
        [InlineKeyboardButton("🎥 Download Video", callback_data=f"video|{url}")],
        [InlineKeyboardButton("🎵 Audio Only", callback_data=f"audio|{url}")],
    ]
    message.reply("👇 Choose an option:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
def callback(client, callback_query):
    format_type, url = callback_query.data.split("|", 1)
    msg = callback_query.message
    msg.edit_text("⏬ Downloading... Please wait.")

    ydl_opts = {'outtmpl': 'download.%(ext)s'}

    if format_type == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'download.%(ext)s'
        })
    else:
        ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)
            if format_type == "audio":
                file_name = file_name.rsplit(".", 1)[0] + ".mp3"

        client.send_document(callback_query.message.chat.id, file_name)
        os.remove(file_name)
        msg.edit_text("✅ Done!")
    except Exception as e:
        msg.edit_text(f"⚠️ Error: {e}")

app.run()