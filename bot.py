from pyrogram import Client, filters
import os, asyncio

from config import *
from database import *
from utils import *
from queue_system import queue, worker

app = Client("ultimate-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 START WORKERS
async def start_workers():
    for _ in range(3):
        asyncio.create_task(worker())

# 🔹 MAIN PROCESS FUNCTION
async def process_file(client, message, user_id=None):

    try:
        file_path = await message.download()
    except Exception as e:
        print("Download error:", e)
        return

    count = await get_counter()
    user = await get_user(user_id) if user_id else {}

    prefix = user.get("prefix", DEFAULT_PREFIX)
    caption = user.get("caption", DEFAULT_CAPTION)
    thumb = user.get("thumb")

    new_name = rename(file_path, prefix, count)
    os.rename(file_path, new_name)

    # safe thumbnail
    thumb_file = thumb if thumb and os.path.exists(thumb) else None

    try:
        if user_id:
            await message.reply_document(
                document=new_name,
                caption=caption,
                thumb=thumb_file
            )
        else:
            await client.send_document(
                chat_id=TARGET_CHANNEL,
                document=new_name,
                caption=caption
            )
    except Exception as e:
        print("Upload error:", e)

    await update_counter(count + 1)

    if os.path.exists(new_name):
        os.remove(new_name)

# 🔹 CHANNEL AUTO
@app.on_message(filters.chat(SOURCE_CHANNELS) & (filters.document | filters.video | filters.audio))
async def channel_handler(client, message):
    await queue.put((process_file, (client, message, None)))

# 🔹 PRIVATE AUTO
@app.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def private_handler(client, message):

    try:
        await client.get_chat_member(FORCE_SUB_CHANNEL, message.from_user.id)
    except:
        await message.reply(f"👉 ആദ്യം join ചെയ്യൂ: {FORCE_SUB_LINK}")
        return

    await queue.put((process_file, (client, message, message.from_user.id)))

# 🔹 SET CAPTION
@app.on_message(filters.command("setcaption"))
async def set_caption_cmd(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /setcaption your text")
        return

    text = message.text.split(" ", 1)[1]
    await update_user(message.from_user.id, {"caption": text})
    await message.reply("✅ Caption saved")

# 🔹 SET PREFIX
@app.on_message(filters.command("setprefix"))
async def set_prefix_cmd(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /setprefix name")
        return

    text = message.text.split(" ", 1)[1]
    await update_user(message.from_user.id, {"prefix": text})
    await message.reply("✅ Prefix saved")

# 🔹 SET THUMBNAIL
@app.on_message(filters.photo & filters.private)
async def set_thumb(client, message):
    file = await message.download()
    await update_user(message.from_user.id, {"thumb": file})
    await message.reply("✅ Thumbnail saved")

# 🔹 START MENU
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "🔥 Welcome to Shebin Ultimate Bot",
        reply_markup={
            "inline_keyboard": [
                [{"text": "📢 Updates", "url": UPDATE_CHANNEL}],
                [{"text": "Help", "callback_data": "help"},
                 {"text": "About", "callback_data": "about"}]
            ]
        }
    )

# 🔹 CALLBACK
@app.on_callback_query()
async def cb(client, q):
    if q.data == "help":
        await q.message.edit_text(
            "📥 Send file → auto rename\n"
            "⚙️ /setcaption\n"
            "⚙️ /setprefix\n"
            "📸 Send photo → set thumbnail"
        )
    else:
        await q.message.edit_text("👨‍💻 Developer: Shebin")

# 🔹 RUN
async def main():
    await app.start()
    await start_workers()
    print("🔥 Bot Started Successfully!")
    await asyncio.Event().wait()

asyncio.run(main())
