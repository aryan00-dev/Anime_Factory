import os
import glob
import random
import gdown
import time
import numpy as np
import google.generativeai as genai
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip, TextClip, vfx, ColorClip
from instagrapi import Client

print("--- ߏ VEDA CLOUD FACTORY ENGINE (FULL AUTO-UPLOAD) STARTED ---")

# --- 1. API SETUP ---
API_KEY = "AIzaSyCmy7eNoUsqBXiN9tN3E-CEfC7RChOFAmo" 
genai.configure(api_key=API_KEY)

# --- 2. GOOGLE DRIVE FOLDER IDs ---
DRIVE_FOLDERS = {
    "Raw_Clips": "1Ka3dX7yI1OY3VVhjRI9wVS-iklGf0tc2",
    "Action": "1YVVpYmHrcYBONWklcgdv3NYiS5_SlJmZ",
    "Chill": "18i3mLxxYTTkPFzbV_746WqMw3pcteIrG",
    "Sad": "1XAatApMuEYAJvV7RGzc8mDIP-1R0k8VM",
    "Romance": "1ppfCxuDOBEG8jG2-zRKig9kKOh9ozxFw"
}

PAGE_NAME = "Asianimedaily.daily"

# --- 3. WORKSPACE SETUP ---
base_dir = "Factory_Workspace/"
raw_dir = base_dir + "Raw_Clips/"
audio_dir = base_dir + "Audio/"
output_dir = base_dir + "Final_Reels/"
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# --- 4. VIDEO DOWNLOADER ---
print("ߓ Google Drive se kachha episode utha raha hu...")
try:
    gdown.download_folder(f"https://drive.google.com/drive/folders/{DRIVE_FOLDERS['Raw_Clips']}", output=raw_dir, quiet=False, use_cookies=False)
except Exception as e:
    print("Download Warning:", e)

videos = glob.glob(raw_dir + "**/*.mp4", recursive=True) + glob.glob(raw_dir + "**/*.mkv", recursive=True)
if not videos:
    print("❌ Koi video nahi mili! Factory band ho rahi hai.")
    exit()

vid_path = videos[0]
print(f"ߎ Video mil gayi: {vid_path}")

# --- 5. GOD AI ANALYSIS ---
print("ߧ Video AI ke paas ja rahi hai analysis ke liye...")
try:
    video_file_ai = genai.upload_file(path=vid_path)
    while video_file_ai.state.name == 'PROCESSING':
        print('.', end='', flush=True)
        time.sleep(10)
    print("\n✅ AI ne video dekh li!")

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = f"""Watch this anime episode. Find the absolute best 30-second viral short scene with high attitude/emotion.
    Also, detect the exact MOOD of the scene. The MOOD must be ONLY ONE of these four words: Action, Chill, Sad, Romance.
    Reply ONLY in this exact format separated by '|':
    StartTimeInSeconds|ViralHook|AnimeName|ShortPlot|Rating|Mood
    Example: 320|Wait for it ߘ|Naruto|Epic ninja fight|9.5/10|Action"""
    
    response = model.generate_content([video_file_ai, prompt])
    ai_data = response.text.strip().split('|')
    
    if len(ai_data) < 6:
        raise ValueError("AI data format incorrect")
        
    start_time = int(ai_data[0])
    hook_text = ai_data[1]
    detected_mood = ai_data[5].strip()
    
    print(f"ߔ AI BINGO! Time: {start_time}s | Mood: {detected_mood} | Hook: {hook_text}")
    genai.delete_file(video_file_ai.name)

except Exception as e:
    print("⚠️ AI Error, backup plan chalu:", e)
    start_time, hook_text, detected_mood = 100, "Wait for it ߘ", "Action"

# --- 6. AUDIO DOWNLOADER ---
print(f"ߎ Detected Mood '{detected_mood}' hai. Drive se music nikal raha hu...")
mood_folder_id = DRIVE_FOLDERS.get(detected_mood, DRIVE_FOLDERS["Action"]) 

try:
    gdown.download_folder(f"https://drive.google.com/drive/folders/{mood_folder_id}", output=audio_dir, quiet=False, use_cookies=False)
except Exception as e:
    print("Audio Download Warning:", e)

audio_files = glob.glob(audio_dir + "**/*.mp3", recursive=True) + glob.glob(audio_dir + "**/*.m4a", recursive=True)
selected_audio = random.choice(audio_files) if audio_files else None

# --- 7. THE EDITOR (SAFE EFFECTS) ---
print("✂️ Kainchi chal rahi hai aur Safe Hacker Effects lag rahe hain...")
REEL_DURATION = 30
end_time = start_time + REEL_DURATION 

vid_clip = VideoFileClip(vid_path).subclip(start_time, end_time)

# Effect 1: 5% Zoom (Anti-copyright)
w, h = vid_clip.size
vid_clip = vid_clip.crop(x_center=w/2, y_center=h/2, width=w*0.95, height=h*0.95).resize(newsize=(w, h))

# Effect 2: Moody Aesthetic Filter
vid_clip = vid_clip.fx(vfx.colorx, 1.1)

# Audio Mix
if selected_audio:
    bg_music = AudioFileClip(selected_audio).subclip(0, REEL_DURATION).volumex(0.35).fadein(1).fadeout(1)
    if vid_clip.audio:
        final_audio = CompositeAudioClip([vid_clip.audio.volumex(0.7), bg_music])
        vid_clip = vid_clip.set_audio(final_audio)
    else:
        vid_clip = vid_clip.set_audio(bg_music)

resized_vid = vid_clip.resize(width=1080).set_position(("center", "center"))
w_reel, h_reel = 1080, 1920 

clips_to_add = [resized_vid]

# Branding & Texts
try:
    txt_branding = TextClip(PAGE_NAME, fontsize=45, color='white', bg_color=None, font='Arial-Bold').set_position(('center', 1700)).set_duration(REEL_DURATION)
    clips_to_add.append(txt_branding)
    
    progress_bar = ColorClip(size=(1080, 8), color=(0,255,255)).set_position((0, 1600)).set_duration(REEL_DURATION)
    clips_to_add.append(progress_bar)
    
    txt_hook = TextClip(hook_text, fontsize=65, color='white', bg_color='black', size=(950, None), font='Arial-Bold', method='caption').set_position(('center', 250)).set_duration(REEL_DURATION)
    clips_to_add.append(txt_hook)
except Exception as e:
    print("⚠️ Visual Layers skip huye:", e)

final_reel = CompositeVideoClip(clips_to_add, size=(w_reel, h_reel)).set_duration(REEL_DURATION)

# --- 8. RENDER REEL ---
output_file = output_dir + f"Viral_{detected_mood}_Reel.mp4"
print(f"ߔ Final Reel Tandoor mein paka raha hu... Time: {time.ctime()}")

final_reel.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=30, preset="ultrafast", threads=2)
print(f"✅ BOOM! Factory ka kaam khatam! Reel yahan save hai: {output_file}")

# --- 9. INSTAGRAM AUTO-UPLOAD ---
print("\nߚ Video taiyar! Ab Instagram par upload ki baari...")
session_id = os.environ.get("IG_SESSION_ID")

if session_id:
    try:
        cl = Client()
        cl.login_by_sessionid(session_id)
        caption = f"ߔ Best {detected_mood} Anime Moment! ߎ\n\nDrop a like if you loved this! ❤️\n\n#anime #animeedit #animereels #{detected_mood.lower()} #asianimedaily"
        
        print("⏳ Instagram par Reel upload ho rahi hai... (Kripya intezaar karein)")
        cl.clip_upload(output_file, caption)
        print("✅ BOOM! Reel successfully Instagram par upload ho gayi!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
else:
    print("⚠️ IG_SESSION_ID nahi mila. Upload cancel ho gaya. GitHub Secrets check karo.")
