import os
import re
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

from youtube import (
    get_videos,
    get_channel_id,
    get_channel_info,
    search_videos,
)

from analyzer import upload_stats, calculate_viral_score

# ================= ENV =================
load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

# ================= MENU =================
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("🔍 Analiz"),
    KeyboardButton("🤖 AI Yordamchi"),
    KeyboardButton("🧠 Keyword Generator"),
    KeyboardButton("🖼 Thumbnail AI"),
    KeyboardButton("🎨 Prompt Generator"),
    KeyboardButton("ℹ️ Yordam"),
    KeyboardButton("💰 Premium")
)

# ================= STATES =================
ai_mode = {}
keyword_mode = {}
thumbnail_mode = {}
prompt_mode = {}
waiting_photo = {}

# ================= RESET =================
def reset_modes(user_id):
    ai_mode[user_id] = False
    keyword_mode[user_id] = False
    thumbnail_mode[user_id] = False
    prompt_mode[user_id] = False
    waiting_photo[user_id] = False

# ================= AI =================
def ask_ai(text):
    text = text.lower()

    if "yo‘nalish" in text:
        return "🔥 Shorts, AI, Motivation, Pul ishlash eng tez o‘sadi"

    if "pul" in text:
        return "💰 Monetizatsiya + Affiliate + Sponsor = daromad"

    if "youtube" in text:
        return "📈 Har kuni video + CTR + trend = growth"

    return "🤖 Savolni aniqroq yoz"

# ================= PROMPT =================
def generate_prompt(topic):
    return f"""YouTube thumbnail, {topic},
ultra realistic, cinematic lighting,
high contrast, big bold text,
vibrant colors, clickbait style,
shocked face, dramatic scene,
4k, trending youtube thumbnail"""

# ================= SMART TEXT =================
def extract_main_text(text):
    words = re.findall(r"\w+", text.lower())
    ignore = ["youtube","thumbnail","ultra","realistic","lighting","high","contrast","style"]
    words = [w for w in words if w not in ignore]
    return " ".join(words[:3]).upper()

# ================= THUMBNAIL =================
def make_thumbnail(text, use_image=False):

    clean_text = extract_main_text(text)

    if use_image and os.path.exists("input.jpg"):
        img = Image.open("input.jpg").convert("RGB")
    else:
        colors = [(255,0,0), (0,0,0), (0,102,204), (255,140,0)]
        img = Image.new("RGB", (1280, 720), random.choice(colors))

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()

    # TEXT CENTER FIX
    bbox = draw.textbbox((0,0), clean_text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (1280 - w) // 2
    y = (720 - h) // 2

    # OUTLINE EFFECT (PRO LOOK)
    for dx in [-3,3]:
        for dy in [-3,3]:
            draw.text((x+dx,y+dy), clean_text, font=font, fill=(0,0,0))

    draw.text((x,y), clean_text, font=font, fill=(255,255,0))

    img.save("output.jpg")
    return "output.jpg"

# ================= KEYWORDS =================
def extract_keywords_from_videos(videos):
    text = ""
    for v in videos:
        text += v["title"] + " " + v["description"] + " "

    words = re.findall(r"\w+", text.lower())
    stop_words = ["the","and","for","with","this","that","you","from"]

    words = [w for w in words if w not in stop_words and len(w) > 3]

    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:30]

# ================= VIRAL =================
def generate_viral_titles(topic):
    topic = topic.title()
    templates = [
        f"{topic} – You Won’t Believe This!",
        f"I Tried {topic}… Crazy Result!",
        f"{topic} Challenge (Insane)",
        f"{topic} Gone Wrong!",
        f"{topic} vs Reality",
        f"Top 5 {topic} Moments"
    ]
    return random.sample(templates, 3)

# ================= SEO =================
def generate_full_seo(topic, keywords):
    base = " ".join(re.findall(r"\w+", topic.lower())[:4])

    title = f"{base.title()} Challenge! (Extreme Test)"

    tags = [k[0] for k in keywords[:10]]
    tags += [f"{base} gameplay", f"{base} viral", f"{base} trending"]

    tags = list(dict.fromkeys(tags))[:20]

    desc = f"""
🔥 {base.title()} Video!

👉 Like & Subscribe
🚀 Viral content
"""

    return title, tags, desc

# ================= START =================
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer("👋 YouTuberchi BOT 🚀", reply_markup=menu)

# ================= PHOTO =================
@dp.message_handler(content_types=['photo'])
async def handle_photo(msg: types.Message):
    user_id = msg.from_user.id

    if not waiting_photo.get(user_id):
        return

    file = await bot.get_file(msg.photo[-1].file_id)
    downloaded = await bot.download_file(file.file_path)

    with open("input.jpg", "wb") as f:
        f.write(downloaded.read())

    waiting_photo[user_id] = False
    thumbnail_mode[user_id] = True

    await msg.answer("✍️ Endi text yoz")

# ================= MAIN =================
@dp.message_handler(lambda msg: msg.text)
async def handle(msg: types.Message):
    raw = msg.text.strip()
    text = raw.lower()
    user_id = msg.from_user.id

    # MENU
    if text == "ℹ️ yordam":
        reset_modes(user_id)
        await msg.answer("📌 Kanal → analiz\n🧠 Keyword → SEO\n🖼 Thumbnail → rasm yoki text")
        return

    if text == "💰 premium":
        reset_modes(user_id)
        await msg.answer("💰 Premium tez orada 😎")
        return

    if text == "🔍 analiz":
        reset_modes(user_id)
        await msg.answer("📌 Kanal link yubor")
        return

    # PROMPT
    if text == "🎨 prompt generator":
        reset_modes(user_id)
        prompt_mode[user_id] = True
        await msg.answer("✍️ Mavzu yoz")
        return

    if prompt_mode.get(user_id):
        await msg.answer(f"🎨 PRO PROMPT:\n\n{generate_prompt(raw)}")
        prompt_mode[user_id] = False
        return

    # THUMBNAIL
    if text == "🖼 thumbnail ai":
        reset_modes(user_id)
        waiting_photo[user_id] = True
        await msg.answer("🖼 Rasm yubor yoki text yoz")
        return

    if thumbnail_mode.get(user_id):
        path = make_thumbnail(raw, use_image=True)
        await msg.answer_photo(open(path,"rb"))
        thumbnail_mode[user_id] = False
        return

    if waiting_photo.get(user_id):
        path = make_thumbnail(raw, use_image=False)
        await msg.answer_photo(open(path,"rb"))
        waiting_photo[user_id] = False
        return

    # AI
    if text == "🤖 ai yordamchi":
        reset_modes(user_id)
        ai_mode[user_id] = True
        await msg.answer("Savol yoz (/stop)")
        return

    if ai_mode.get(user_id):
        await msg.answer("🤖 O‘ylayapman...")
        await msg.answer(ask_ai(raw))
        return

    # KEYWORD
    if text == "🧠 keyword generator":
        reset_modes(user_id)
        keyword_mode[user_id] = True
        await msg.answer("✍️ Mavzu yoz")
        return

    if keyword_mode.get(user_id):
        await msg.answer("🔎 Analiz...")

        try:
            videos = search_videos(raw)
            keywords = extract_keywords_from_videos(videos)

            title, tags, desc = generate_full_seo(raw, keywords)
            viral = generate_viral_titles(raw)

            result = f"🔥 SEO PACK\n\n🎯 {title}\n\n🔥 TAGS:\n"

            result += ", ".join(tags)

            result += "\n\n🚀 VIRAL:\n"
            for v in viral:
                result += f"• {v}\n"

            result += f"\n📝 {desc}"

            await msg.answer(result)

        except Exception as e:
            await msg.answer("❌ " + str(e))

        keyword_mode[user_id] = False
        return

    # ANALIZ
    await msg.answer("⏳ Analiz...")

    try:
        if not ("youtube" in raw or "@" in raw):
            await msg.answer("❌ YouTube link yubor")
            return

        channel_id = get_channel_id(raw)
        videos = get_videos(channel_id)

        info = get_channel_info(channel_id)
        stats = upload_stats(videos)
        viral = calculate_viral_score(videos)

        await msg.answer(f"""
📺 {info['title']}
👥 {info['subs']}

📈 {stats['avg_daily']}
🚀 {viral}/100
""")

    except Exception as e:
        await msg.answer("❌ " + str(e))


# ================= RUN =================
if __name__ == "__main__":
    print("🔥 BOSS LEVEL BOT ISHLADI")
    executor.start_polling(dp, skip_updates=True)