import os
import json
import re
import subprocess
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google import genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import moviepy.video.fx.all as vfx

print("🚀 BRAHMASTRA PHASE: Anime Factory Start Ho Raha Hai...")

# --- 1. KEYS & CONFIG ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GDRIVE_JSON_STR = os.environ.get("GDRIVE_CREDENTIALS_JSON")
RAW_FOLDER_ID = '1Ka3dX7yI1OY3VVhjRI9wVS-iklGf0tc2'
FINAL_FOLDER_ID = '1zcVBLuoOql2FVvrIEmtovIJJ9eWuhFG9'

if not GEMINI_API_KEY or not GDRIVE_JSON_STR:
    print("❌ Error: API Key ya Drive JSON nahi mila!")
    exit()

# --- 2. DRIVE CONNECTION & DOWNLOAD ---
print("🔌 Cloud Godown se connect kar rahe hain...")
creds_dict = json.loads(GDRIVE_JSON_STR)
creds = service_account.Credentials.from_service_account_info(creds_dict)
drive_service = build('drive', 'v3', credentials=creds)

results = drive_service.files().list(q=f"'{RAW_FOLDER_ID}' in parents and mimeType contains 'video/'", fields="files(id, name)").execute()
files = results.get('files', [])

if not files:
    print("❌ Error: Raw folder mein koi video nahi mili!")
    exit()

video_file = files[0]
print(f"🎥 Episode mil gaya: {video_file['name']}. Download shuru...")

import io
request = drive_service.files().get_media(fileId=video_file['id'])
fh = io.FileIO("raw_episode.mp4", 'wb')
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
print("✅ Episode Download Complete!")

# --- 3. FFMPEG AUDIO/SUBTITLE EXTRACTION ---
print("✂️ FFmpeg se Audio aur Subtitles nikal rahe hain (Bina server crash kiye)...")
# Extract Audio
subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-vn", "-acodec", "libmp3lame", "-q:a", "2", "audio.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
# Try to extract subtitles (agar hardcoded nahi hain)
subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-map", "0:s:0?", "subs.srt"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
print("✅ Audio nikal aayi!")

# --- 4. GEMINI ANALYSIS (THE BRAHMASTRA) ---
print("🧠 Gemini episode sun/padh raha hai best scene ke liye...")
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    # Upload audio to Gemini
    audio_file = client.files.upload(file="audio.mp3")
    print("⏳ Audio processing ka wait kar rahe hain...")
    time.sleep(10) # Thoda wait taaki file process ho jaye
    
    prompt = """
    Listen to this anime episode audio. Find the most badass, hype, or emotional 30 to 45 seconds scene.
    Return ONLY a JSON format exactly like this, nothing else:
    {"start_time": "00:12:10", "end_time": "00:12:45", "hook_text": "Duniya mein 3 tarah ke log hote hain...\\nWait for it!"}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[audio_file, prompt]
    )
    
    response_text = response.text.strip().replace('
