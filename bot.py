import os
import json
import subprocess
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google import genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import moviepy.video.fx.all as vfx

print("🚀 BRAHMASTRA PHASE: Anime Factory Start Ho Raha Hai...")

# --- 1. KEYS & CONFIG ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GDRIVE_JSON_STR = os.environ.get("GDRIVE_CREDENTIALS_JSON")
RAW_FOLDER_ID = '1Ka3dX7yI1OY3VVhjRI9wVS-iklGf0tc2'

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

# --- 3. FFMPEG AUDIO EXTRACTION ---
print("✂️ FFmpeg se Audio nikal rahe hain...")
subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-vn", "-acodec", "libmp3lame", "-q:a", "2", "audio.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
print("✅ Audio nikal aayi!")

# --- 4. GEMINI ANALYSIS (THE BRAHMASTRA) ---
print("🧠 Gemini episode sun raha hai best scene ke liye...")
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    audio_file = client.files.upload(file="audio.mp3")
    print("⏳ Audio processing ka wait kar rahe hain...")
    time.sleep(10) 
    
    prompt = """Listen to this anime audio. Find the most badass 30-second scene.
Return ONLY a JSON format. Use this structure but with REAL timestamps from the audio and a REAL custom quote:
{"start_time": "00:05:10", "end_time": "00:05:45", "hook_text": "Write a unique viral quote here!"}"""
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[audio_file, prompt]
    )
    
    response_text = response.text.strip().replace("```json", "").replace("```", "")
    scene_data = json.loads(response_text)
    
    start_t = scene_data.get("start_time", "00:02:00")
    end_t = scene_data.get("end_time", "00:02:30")
    hook_text = scene_data.get("hook_text", "Wait for it!")
    print(f"🎯 Gemini ne Scene dhoondh liya! Start: {start_t}, End: {end_t}")
    print(f"✍️ Hook Text: {hook_text}")

except Exception as e:
    print(f"⚠️ Gemini Error: {e}. Default 30 seconds cut kar rahe hain.")
    start_t = "00:02:00"
    end_t = "00:02:30"
    hook_text = "Pure Goosebumps!\nWait for the end..."

# --- 5. FFMPEG SURGEON CUT (WITH BULLETPROOF CHECK) ---
print("✂️ FFmpeg main episode ko kaat raha hai...")
subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-ss", start_t, "-to", end_t, "-c:v", "copy", "-c:a", "copy", "cut_scene.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

if not os.path.exists("cut_scene.mp4") or os.path.getsize("cut_scene.mp4") < 50000:
    print("🚨 AI ne galat time diya tha! Video khaali hai. Auto-Fixing to default scene...")
    start_t, end_t = "00:02:00", "00:02:30"
    hook_text = "Wait for the end...\nPure Goosebumps!"
    subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-ss", start_t, "-to", end_t, "-c:v", "copy", "-c:a", "copy", "cut_scene.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

print("✅ Scene Cut Complete!")

# --- 6. MOVIEPY VIRAL BLUR EDIT ---
print("🎬 MoviePy Viral Edit shuru kar raha hai (Extra Heavy Blur activated)...")
clip = VideoFileClip("cut_scene.mp4")
clip = clip.fx(vfx.speedx, 1.05) 

bg_clip = (clip.resize(height=1920)
           .crop(x_center=clip.w/2, width=1080)
           .fx(vfx.gaussian_blur, radius=50) 
           .fx(vfx.colorx, 0.5))              

main_clip = clip.resize(width=1080).set_position('center')

# Position update kar di hai ('center', 280) taaki ekdum semi jagah par aaye
txt_clip = TextClip(hook_text, fontsize=60, color='white', font='Arial-Bold', bg_color='rgba(0,0,0,0.6)', size=(1080, None), method='caption')
txt_clip = txt_clip.set_position(('center', 280)).set_duration(clip.duration)

final_video = CompositeVideoClip([bg_clip, main_clip, txt_clip])
final_video.write_videofile("final_reel.mp4", fps=24, codec="libx264", audio_codec="aac")
print("✅ Reel Edit Complete!")

# --- 7. BYPASS DRIVE UPLOAD ---
print("📤 Drive upload bypass kar rahe hain... Video GitHub par direct aayegi!")
print("🎉 BUMM! Mission Complete! GitHub Actions se apni video download kar lo!")
