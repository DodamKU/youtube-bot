from collections import Counter
import re
from datetime import datetime


def analyze(videos):
    hashtags = []
    words = []
    hours = []
    video_keywords = {}

    # 🚫 keraksiz so‘zlar
    stop_words = [
        "the", "and", "is", "to", "of", "in", "for", "on", "a", "an",
        "this", "that", "with", "from", "your", "you", "are", "was"
    ]

    for v in videos:
        desc = v["description"]
        title = v["title"]

        # 🔥 hashtaglar
        hashtags += re.findall(r"#\w+", desc)

        # 🔑 description + title birga ishlaydi
        text = (desc + " " + title).lower()

        raw_words = re.findall(r"\b\w+\b", text)

        clean_words = [
            w for w in raw_words
            if w not in stop_words and len(w) > 3 and not w.isdigit()
        ]

        words += clean_words

        # 🎬 har video uchun keyword (top 5)
        top_video_words = Counter(clean_words).most_common(5)
        video_keywords[title] = top_video_words

        # ⏰ vaqt
        dt = datetime.fromisoformat(v["published"].replace("Z", ""))
        hours.append(dt.hour)

    # 📊 umumiy natijalar
    top_tags = Counter(hashtags).most_common(5)
    top_words = Counter(words).most_common(10)
    best_hour = Counter(hours).most_common(1)

    return top_tags, top_words, best_hour, video_keywords


# 📈 upload statistikasi
def upload_stats(videos):
    days = []
    months = []

    for v in videos:
        dt = datetime.fromisoformat(v["published"].replace("Z", ""))
        days.append(dt.date())
        months.append((dt.year, dt.month))

    # 📅 nechta kun faol
    unique_days = len(set(days))

    # 🗓 nechta oy faol
    unique_months = len(set(months))

    # 📊 o‘rtacha video/kun
    avg_daily = len(videos) / unique_days if unique_days else 0

    # 📊 o‘rtacha video/oy
    avg_monthly = len(videos) / unique_months if unique_months else 0

    return {
        "days": unique_days,
        "months": unique_months,
        "avg_daily": round(avg_daily, 2),
        "avg_monthly": round(avg_monthly, 2)
    }
def calculate_viral_score(videos):
    score = 0

    for v in videos:
        views = int(v.get("views", 0))
        likes = int(v.get("likes", 0))

        if views > 100000:
            score += 20
        elif views > 10000:
            score += 10

        if likes > 5000:
            score += 20
        elif likes > 1000:
            score += 10

    return min(score, 100)
import random

def generate_titles(keywords):
    templates = [
        "You Won’t Believe {kw}",
        "Top 5 {kw} Tricks That Work",
        "Stop Doing This With {kw}",
        "{kw} Changed My Life",
        "The Secret Behind {kw}",
        "How to Master {kw} Fast",
        "Nobody Talks About {kw}",
        "{kw} Explained in 5 Minutes"
    ]

    titles = []

    for i in range(5):
        kw = keywords[i][0] if i < len(keywords) else "this"
        t = random.choice(templates)
        titles.append(t.replace("{kw}", kw.title()))

    return titles