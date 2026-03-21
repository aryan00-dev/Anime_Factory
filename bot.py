import os
import json
import subprocess
import time
import random
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google import genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
from gtts import gTTS

print("🚀 BRAHMASTRA PHASE: True Final Smart Factory Start...")

# --- 1. KEYS & FOLDER CONFIG ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GDRIVE_JSON_STR = os.environ.get("GDRIVE_CREDENTIALS_JSON")
RAW_FOLDER_ID = '1Ka3dX7yI1OY3VVhjRI9wVS-iklGf0tc2'

GENRE_FOLDERS = {
    "Action": "1YVVpYmHrcYBONWklcgdv3NYiS5_SlJmZ",
    "Chill": "18i3mLxxYTTkPFzbV_746WqMw3pcteIrG",
    "Romance": "1ppfCxuDOBEG8jG2-zRKig9kKOh9ozxFw",
    "Sad": "1XAatApMuEYAJvV7RGzc8mDIP-1R0k8VM_"
}

if not GEMINI_API_KEY or not GDRIVE_JSON_STR:
    print("❌ Error: Keys missing!"); exit()

# --- 2. DRIVE CONNECTION ---
creds_dict = json.loads(GDRIVE_JSON_STR)
creds = service_account.Credentials.from_service_account_info(creds_dict)
drive_service = build('drive', 'v3', credentials=creds)

# --- 3. DOWNLOAD RAW EPISODE ---
results = drive_service.files().list(q=f"'{RAW_FOLDER_ID}' in parents and mimeType contains 'video/'", fields="files(id, name)").execute()
files = results.get('files', [])
if not files: print("❌ Video nahi mili!"); exit()

video_file = files[0]
print(f"🎥 Downloading Episode: {video_file['name']}")
request = drive_service.files().get_media(fileId=video_file['id'])
fh = io.FileIO("raw_episode.mp4", 'wb')
downloader = MediaIoBaseDownload(fh, request); done = False
while not done: status, done = downloader.next_chunk()
print("✅ Episode Download Complete!")

# --- 4. AUDIO EXTRACTION ---
subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-vn", "-acodec", "libmp3lame", "-q:a", "2", "audio.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# --- 5. GEMINI ANALYSIS (Strict 2-Line Rule Added) ---
client = genai.Client(api_key=GEMINI_API_KEY)
try:
    audio_file = client.files.upload(file="audio.mp3")
    print("🧠 Gemini mood aur scene pehchan raha hai...")
    time.sleep(15) 
    # Yahan humne AI ko strict order diya hai exactly 2 lines ke liye
    prompt = """Listen to this anime audio. Find a badass 30-40s scene, Identify Anime Name, and Detect Genre: [Action, Chill, Romance, Sad].
CRITICAL RULE for hook_text: It MUST be exactly 2 short lines. Not more, not less. Use '\\n' to separate the two lines. Example: "Wait for the end...\\nPure Goosebumps!"
Return ONLY JSON: {"start_time": "00:05:10", "end_time": "00:05:45", "hook_text": "First line here...\\nSecond line here!", "anime_name": "Name", "genre": "Action"}"""
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=[audio_file, prompt])
    scene_data = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    start_t, end_t = scene_data["start_time"], scene_data["end_time"]
    hook_text, anime_name, genre = scene_data["hook_text"], scene_data["anime_name"], scene_data.get("genre", "Action")
    print(f"🎯 Genre: {genre} | Anime: {anime_name}")
    print(f"✍️ Hook Text: {hook_text}")
except Exception as e:
    print(f"⚠️ Gemini Error: {e}"); start_t, end_t, hook_text, anime_name, genre = "00:02:00", "00:02:30", "Wait for it...\\nPure Goosebumps!", "Anime", "Action"

# --- 6. FFMPEG CUT ---
subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-ss", start_t, "-to", end_t, "-c:v", "copy", "-c:a", "copy", "cut_scene.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
if not os.path.exists("cut_scene.mp4") or os.path.getsize("cut_scene.mp4") < 50000:
    subprocess.run(["ffmpeg", "-y", "-i", "raw_episode.mp4", "-ss", "00:01:00", "-to", "00:01:30", "-c:v", "copy", "-c:a", "copy", "cut_scene.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# --- 7. SMART BGM PICKER ---
bgm_folder_id = GENRE_FOLDERS.get(genre, GENRE_FOLDERS["Action"])
bgm_results = drive_service.files().list(q=f"'{bgm_folder_id}' in parents and mimeType contains 'audio/'", fields="files(id, name)").execute()
bgm_files = bgm_results.get('files', [])
has_bgm = False
if bgm_files:
    random_bgm = random.choice(bgm_files)
    request = drive_service.files().get_media(fileId=random_bgm['id'])
    bh = io.FileIO("bgm.mp3", 'wb'); downloader = MediaIoBaseDownload(bh, request); done = False
    while not done: status, done = downloader.next_chunk()
    has_bgm = True

# --- 8. MOVIEPY EDITING (Safe Blur Fix + Better Text Size) ---
print("🎬 Viral Editing Shuru...")
clip = VideoFileClip("cut_scene.mp4").fx(vfx.speedx, 1.05)

# Background Heavy Blur with fallback
try:
    bg_clip = clip.resize(height=1920).crop(x_center=clip.w/2, width=1080).fx(vfx.gaussian_blur, 50).fx(vfx.colorx, 0.5)
except:
    print("⚠️ Blur failed, using alternate stretch-blur...")
    bg_clip = clip.resize(height=1920).crop(x_center=clip.w/2, width=1080).fx(vfx.resize, 0.1).fx(vfx.resize, 10.0).fx(vfx.colorx, 0.5)

main_clip = clip.resize(width=1080).set_position('center')

# Text ki chaudaai (width) thodi kam ki hai (950) taaki screen ke edges par na chipke, aur size thoda adjust kiya hai.
txt_clip = TextClip(hook_text, fontsize=55, color='white', font='Arial-Bold', bg_color='rgba(0,0,0,0.5)', size=(950, None), method='caption').set_position(('center', 280)).set_duration(clip.duration)

final_video = CompositeVideoClip([bg_clip, main_clip, txt_clip])

# Audio Mix
original_audio = clip.audio.volumex(0.4)
if has_bgm:
    bgm_audio = AudioFileClip("bgm.mp3").volumex(1.0).set_duration(clip.duration)
    from moviepy.audio.AudioClip import CompositeAudioClip
    final_video = final_video.set_audio(CompositeAudioClip([original_audio, bgm_audio]))
else:
    final_video = final_video.set_audio(original_audio)

# --- 9. AI VOICE OUTRO ---
tts = gTTS(text=f"Anime name is {anime_name}", lang='en')
tts.save("outro.mp3")
outro_audio = AudioFileClip("outro.mp3")
outro_bg = ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(outro_audio.duration + 0.5)
outro_txt = TextClip(f"ANIME NAME:\n{anime_name}", fontsize=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).set_position('center').set_duration(outro_bg.duration)
outro_clip = CompositeVideoClip([outro_bg, outro_txt]).set_audio(outro_audio)

# --- 10. FINAL MERGE ---
final_merged = concatenate_videoclips([final_video, outro_clip])
final_merged.write_videofile("final_with_music.mp4", fps=24, codec="libx264", audio_codec="aac")
print("🎉 MISSION COMPLETE!")
