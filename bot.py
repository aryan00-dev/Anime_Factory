import os
import json
import subprocess
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google import genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
from gtts import gTTS

print("🚀 BRAHMASTRA PHASE: Anime Factory (Voice Outro Edition) Start...")

# --- 1. KEYS & CONFIG ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GDRIVE_JSON_STR = os.environ.get("GDRIVE_CREDENTIALS_JSON")
RAW_FOLDER_ID = '1Ka3dX7yI1OY3VVhjRI9wVS-iklGf0tc2'

if not GEMINI_API_KEY or not GDRIVE_JSON_STR:
    print("❌ Error: API Key ya Drive JSON nahi mila!")
    exit()

# --- 2. DRIVE CONNECTION & DOWNLOAD ---
creds_dict = json.loads(GDRIVE_JSON_STR)
creds = service_account.Credentials.from_service_account_info(creds_dict)
drive_service = build('drive', 'v3', credentials=creds)
results = drive_service.files().list(q=f"'{RAW_FOLDER_ID}' in parents and mimeType contains 'video/'", fields="files(id, name)").execute()
files = results.get('files', [])

if not files:
    print("❌ Error: Video nahi mili!"); exit()

video_file = files[0]
print(f"🎥 Download shuru: {video_file['name']}")
import io
request = drive_service.files().get_media(fileId=video_file['id'])
fh = io.FileIO("raw_episode.mp4", 'wb')
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()

# --- 3. FFMPEG AUDIO EXTRACTION ---
subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-vn", "-acodec", "libmp3lame", "-q:a", "2", "audio.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# --- 4. GEMINI ANALYSIS (Identify Anime Name too) ---
client = genai.Client(api_key=GEMINI_API_KEY)
try:
    audio_file = client.files.upload(file="audio.mp3")
    time.sleep(10) 
    prompt = """Listen to this anime audio. Find the most badass 30-second scene. Identify the real Anime Name.
Return ONLY JSON: {"start_time": "00:05:10", "end_time": "00:05:45", "hook_text": "Quote", "anime_name": "Name Of Anime"}"""
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=[audio_file, prompt])
    scene_data = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    start_t, end_t = scene_data.get("start_time", "00:02:00"), scene_data.get("end_time", "00:02:30")
    hook_text, anime_name = scene_data.get("hook_text", "Wait for it!"), scene_data.get("anime_name", "Anime")
except Exception as e:
    start_t, end_t, hook_text, anime_name = "00:02:00", "00:02:30", "Pure Goosebumps!", "Anime"

# --- 5. FFMPEG CUT ---
subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-ss", start_t, "-to", end_t, "-c:v", "copy", "-c:a", "copy", "cut_scene.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
if not os.path.exists("cut_scene.mp4") or os.path.getsize("cut_scene.mp4") < 50000:
    subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-ss", "00:02:00", "-to", "00:02:30", "-c:v", "copy", "-c:a", "copy", "cut_scene.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# --- 6. MOVIEPY VIRAL EDIT ---
clip = VideoFileClip("cut_scene.mp4").fx(vfx.speedx, 1.05)
bg_clip = clip.resize(height=1920).crop(x_center=clip.w/2, width=1080).fx(vfx.gaussian_blur, radius=50).fx(vfx.colorx, 0.5)
main_clip = clip.resize(width=1080).set_position('center')
txt_clip = TextClip(hook_text, fontsize=60, color='white', font='Arial-Bold', bg_color='rgba(0,0,0,0.6)', size=(1080, None), method='caption').set_position(('center', 280)).set_duration(clip.duration)
final_video = CompositeVideoClip([bg_clip, main_clip, txt_clip])

# --- 7. CREATE AI VOICE OUTRO (2 Seconds) ---
print(f"🎙️ AI is speaking: Anime name is {anime_name}")
tts_text = f"Anime name is {anime_name}"
tts = gTTS(text=tts_text, lang='en')
tts.save("outro.mp3")

outro_audio = AudioFileClip("outro.mp3")
# Outro visual: Black background with Text
outro_bg = ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(outro_audio.duration + 0.5)
outro_txt = TextClip(f"ANIME NAME:\n{anime_name}", fontsize=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).set_position('center').set_duration(outro_bg.duration)
outro_clip = CompositeVideoClip([outro_bg, outro_txt]).set_audio(outro_audio)

# --- 8. MERGE REEL + OUTRO ---
print("🔗 Merging Reel and Outro...")
final_merged = concatenate_videoclips([final_video, outro_clip])
final_merged.write_videofile("final_with_outro.mp4", fps=24, codec="libx264", audio_codec="aac")

print("🎉 BUMM! AI Voice Outro ke sath Reel ready hai!")
