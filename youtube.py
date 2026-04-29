import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)

# ================= CHANNEL ID =================
def get_channel_id(url):
    if "@" in url:
        username = url.split("@")[1]

        res = youtube.search().list(
            part="snippet",
            q=username,
            type="channel",
            maxResults=1
        ).execute()

        return res["items"][0]["snippet"]["channelId"]

    if "channel/" in url:
        return url.split("channel/")[1].split("/")[0]

    if "youtube.com" in url:
        res = youtube.search().list(
            part="snippet",
            q=url,
            type="channel",
            maxResults=1
        ).execute()

        return res["items"][0]["snippet"]["channelId"]

    return url


# ================= GET VIDEOS =================
def get_videos(channel_id):
    res = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=20,
        order="date"
    ).execute()

    videos = []

    for item in res.get("items", []):
        if item["id"]["kind"] == "youtube#video":
            videos.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"]
            })

    return videos


# ================= SEARCH VIDEOS =================
def search_videos(query):
    res = youtube.search().list(
        part="snippet",
        q=query,
        maxResults=20,
        type="video"
    ).execute()

    videos = []

    for item in res.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"]
        })

    return videos


# ================= CHANNEL INFO =================
def get_channel_info(channel_id):
    res = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    ).execute()

    item = res["items"][0]

    return {
        "title": item["snippet"]["title"],
        "subs": item["statistics"].get("subscriberCount", "0")
    }