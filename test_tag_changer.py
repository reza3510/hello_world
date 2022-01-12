import os
import io
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
from PIL import Image
from music_tag import load_file


BOT_TOKEN = ("5024515341:AAEVklYIIzFRKoC-T5UL7srye4kPyQpqG0s")
API_ID = ("3333892")
API_HASH = ("826d2b476d299f6937649a88383e0a48")

Bot = Client(
    "MusicEditorBot",
    bot_token = BOT_TOKEN,
    api_id = API_ID,
    api_hash = API_HASH
)

START_TXT = """
سلام {}ی کصکش. من یه ربات تگ چینجر نسخه ی فاکینگ اول هستم . 
یه موزیک برام بفرست تا کیرمو بکنم توش و چینجش کنم .
"""

START_BTN = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Our robot sponsor:', url='https://t.me/favoritelist_Reza0_04'),
        ]]
    )


@Bot.on_message(filters.command(["start"]))
async def start(bot, update):
    text = START_TXT.format(update.from_user.mention)
    reply_markup = START_BTN
    await update.reply_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )

   
@Bot.on_message(filters.private & filters.audio)
async def tag(bot, m):
    mes = await m.reply("`Downloading...`", parse_mode='md')
    await m.download(f"temp/{m.audio.file_name}.mp3")
    music = load_file(f"temp/{m.audio.file_name}.mp3")

    try:
        artwork = music['artwork']
        image_data = artwork.value.data
        img = Image.open(io.BytesIO(image_data))
        img.save("temp/artwork.jpg")
    except ValueError:
        image_data = None

    await mes.delete()
    fname = await bot.ask(m.chat.id,'`Send the Filename`', filters=filters.text, parse_mode='Markdown')
    title = await bot.ask(m.chat.id,'`Send the Title name`', filters=filters.text, parse_mode='Markdown')
    artist = await bot.ask(m.chat.id,'`Send the Artist(s) name`', filters=filters.text, parse_mode='Markdown')
    answer = await bot.ask(m.chat.id,'`Send the Artwork or` /skip', filters=filters.photo | filters.text, parse_mode='Markdown')
    music.remove_tag('artist')
    music.remove_tag('title')
    music['artist'] = artist.text
    music['title'] = title.text

    if answer.photo:
        await bot.download_media(message=answer.photo, file_name="temp/artwork.jpg")
        music.remove_tag('artwork')
        with open('temp/artwork.jpg', 'rb') as img_in:
            music['artwork'] = img_in.read()
    music.save()

    try:
        await bot.send_audio(chat_id=m.chat.id, file_name=fname.text, performer=artist.text, title=title.text, duration=m.audio.duration, audio=f"temp/{m.audio.file_name}.mp3", thumb='temp/artwork.jpg' if answer.photo or image_data else None)
    except Exception as e:
        print(e)
        return
    os.remove(f"temp/{m.audio.file_name}.mp3")


Bot.run()