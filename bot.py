import os
import json
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google import genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import moviepy.video.fx.all as vfx

print("🚀 Phase 7: Anime Factory Bot Start Ho Raha Hai...")

# --- 1. CONFIGURATION & KEYS ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GDRIVE_JSON_STR = os.environ.get("GDRIVE_CREDENTIALS_JSON")

RAW_FOLDER_ID = '1Ka3dX7yI1OY3VVhjRI9wVS-iklGf0tc2'
FINAL_FOLDER_ID = '1zcVBLuoOql2FVvrIEmtovIJJ9eWuhFG9'

if not GEMINI_API_KEY or not GDRIVE_JSON_STR:
    print("❌ Error: API Key ya Drive JSON nahi mila! GitHub Secrets check karo.")
    exit()

# --- 2. GOOGLE DRIVE CONNECTION ---
print("🔌 Cloud Godown se connect kar rahe hain...")
creds_dict = json.loads(GDRIVE_JSON_STR)
creds = service_account.Credentials.from_service_account_info(creds_dict)
drive_service = build('drive', 'v3', credentials=creds)

# --- 3. DOWNLOAD RAW VIDEO ---
print("📥 Raw folder se video dhoondh rahe hain...")
results = drive_service.files().list(q=f"'{RAW_FOLDER_ID}' in parents and mimeType contains 'video/'", fields="files(id, name)").execute()
files = results.get('files', [])

if not files:
    print("❌ Error: Raw folder mein koi video nahi mili!")
    exit()

video_file = files[0] # Pehli video uthao
print(f"🎥 Video mil gayi: {video_file['name']}. Download kar rahe hain...")

import io
request = drive_service.files().get_media(fileId=video_file['id'])
fh = io.FileIO("raw_video.mp4", 'wb')
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()

print("✅ Download Complete!")

# --- 4. GEMINI MAGIC (SCENE DETECTION) ---
print("🧠 Gemini video dekh raha hai...")
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    # Abhi ke liye hum Gemini ko context de rahe hain kyunki video upload API mein time lagta hai
    prompt = "Main ek anime edit bana raha hu. Mujhe ek badass, motivational ya funny 2-line ka quote do jo anime reels par viral ho sake. Sirf quote likhna, aur kuch nahi."
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    hook_text = response.text.strip().replace('"', '')
    print(f"✍️ Gemini ne likha: {hook_text}")
except Exception as e:
    print("⚠️ Gemini error, default text use kar rahe hain.")
    hook_text = "Wait for the end...\nPure Goosebumps!"

# --- 5. THE VIRAL BLUR EDIT (MOVIEPY) ---
print("🎬 Hacker Edit shuru ho raha hai...")
try:
    clip = VideoFileClip("raw_video.mp4")
    
    # Meta Bypass: 1.05x speed
    clip = clip.fx(vfx.speedx, 1.05)
    
    # Background (Blurred & Resized to 1080x1920)
    bg_clip = clip.resize(height=1920).crop(x_center=clip.w/2, width=1080).fx(vfx.colorx, 0.5)
    
    # Hook Text Box (Upar Banner)
    txt_clip = TextClip(hook_text, fontsize=60, color='white', font='Arial-Bold', bg_color='rgba(0,0,0,0.6)', size=(1000, None), method='caption')
    txt_clip = txt_clip.set_position(('center', 150)).set_duration(clip.duration)
    
    # Main Video (Center)
    main_clip = clip.resize(width=1080).set_position('center')
    
    final_video = CompositeVideoClip([bg_clip, main_clip, txt_clip])
    
    print("💾 Final Reel render ho rahi hai (Isme time lagega)...")
    final_video.write_videofile("final_reel.mp4", fps=24, codec="libx264", audio_codec="aac")
    print("✅ Video Rendered!")
except Exception as e:
    print("❌ Editing Error:", e)
    exit()

# --- 6. UPLOAD TO FINAL FOLDER ---
print("📤 Final Reel Drive mein upload kar rahe hain...")
file_metadata = {'name': f"Edited_{video_file['name']}", 'parents': [FINAL_FOLDER_ID]}
media = MediaFileUpload("final_reel.mp4", mimetype='video/mp4')
drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

print("🎉 BUMM! Mission Complete! Video tumhare Final Folder mein aa chuki hai!")
