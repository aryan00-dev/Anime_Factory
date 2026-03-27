import os
import glob
import random
import gdown
import time
import google.generativeai as genai
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip, TextClip, vfx

print("--- 🏭 VEDA CLOUD FACTORY ENGINE STARTED ---")

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

# --- 3. CLOUD WORKSPACE SETUP ---
base_dir = "Factory_Workspace/"
raw_dir = base_dir + "Raw_Clips/"
audio_dir = base_dir + "Audio/"
output_dir = base_dir + "Final_Reels/"
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# --- 4. VIDEO DOWNLOADER ---
print("📥 Google Drive se kachha episode utha raha hu...")
try:
    gdown.download_folder(f"https://drive.google.com/drive/folders/{DRIVE_FOLDERS['Raw_Clips']}", output=raw_dir, quiet=False, use_cookies=False)
except Exception as e:
    print("Download Warning:", e)

videos = glob.glob(raw_dir + "**/*.mp4", recursive=True) + glob.glob(raw_dir + "**/*.mkv", recursive=True)
if not videos:
    print("❌ Koi video nahi mili! Factory band ho rahi hai.")
    exit()

vid_path = videos[0]
print(f"🎬 Video mil gayi: {vid_path}")

# --- 5. GOD AI ANALYSIS (WITH MOOD DETECTION) ---
print("🧠 Video AI ke paas ja rahi hai...")
try:
    video_file_ai = genai.upload_file(path=vid_path)
    while video_file_ai.state.name == 'PROCESSING':
        print('.', end='', flush=True)
        time.sleep(5)
    print("\n✅ AI ne video dekh li!")

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = """Watch this anime episode. Find the best 30-second viral short scene. 
    Also, detect the exact MOOD of the scene. The MOOD must be ONLY ONE of these four words: Action, Chill, Sad, Romance.
    Reply ONLY in this exact format separated by '|':
    StartTimeInSeconds|ViralHook|AnimeName|ShortPlot|Rating|Mood
    Example: 320|Wait for it 😱|Naruto|Epic ninja fight|9.5/10|Action"""
    
    response = model.generate_content([video_file_ai, prompt])
    ai_data = response.text.strip().split('|')
    
    start_time = int(ai_data[0])
    hook_text = ai_data[1]
    anime_name = ai_data[2]
    plot_text = ai_data[3]
    rating = ai_data[4]
    detected_mood = ai_data[5].strip()
    
    print(f"🔥 AI BINGO! Time: {start_time}s | Mood: {detected_mood} | Hook: {hook_text}")
    genai.delete_file(video_file_ai.name)

except Exception as e:
    print("⚠️ AI Error, backup plan on:", e)
    start_time, hook_text, anime_name, plot_text, rating, detected_mood = 100, "Wait for it 😱", "Epic Anime", "Watch this!", "10/10", "Action"

# --- 6. AUDIO DOWNLOADER (BASED ON MOOD) ---
print(f"🎵 Mood '{detected_mood}' hai. Drive se '{detected_mood}' wala music nikal raha hu...")
mood_folder_id = DRIVE_FOLDERS.get(detected_mood, DRIVE_FOLDERS["Action"]) # Default to action if error

try:
    gdown.download_folder(f"https://drive.google.com/drive/folders/{mood_folder_id}", output=audio_dir, quiet=False, use_cookies=False)
except Exception as e:
    print("Audio Download Warning:", e)

audio_files = glob.glob(audio_dir + "**/*.mp3", recursive=True) + glob.glob(audio_dir + "**/*.m4a", recursive=True)
selected_audio = random.choice(audio_files) if audio_files else None
if selected_audio:
    print(f"🎧 AI ne yeh gaana chuna: {selected_audio}")
else:
    print("⚠️ Koi music nahi mila folder mein!")

# --- 7. THE ANTI-COPYRIGHT VIDEO EDITOR ---
print("✂️ Kainchi chal rahi hai aur Hacker Effects lag rahe hain...")
end_time = start_time + 30 
vid_clip = VideoFileClip(vid_path).subclip(start_time, end_time)

# Hacker Effect 1: 5% Zoom (Crop center)
w, h = vid_clip.size
vid_clip = vid_clip.crop(x_center=w/2, y_center=h/2, width=w*0.95, height=h*0.95).resize(newsize=(w, h))
# Hacker Effect 2: Color Shift
vid_clip = vid_clip.fx(vfx.colorx, 1.05) 

# Audio Mix
if selected_audio:
    bg_music = AudioFileClip(selected_audio).subclip(0, 30).volumex(0.3)
    if vid_clip.audio:
        final_audio = CompositeAudioClip([vid_clip.audio.volumex(0.8), bg_music])
        vid_clip = vid_clip.set_audio(final_audio)
    else:
        vid_clip = vid_clip.set_audio(bg_music)

# Resize for Reel
resized_vid = vid_clip.resize(width=1080).set_position(("center", "center"))

clips_to_add = [resized_vid]

# Text layer attempt
try:
    txt_hook = TextClip(hook_text, fontsize=60, color='white', bg_color='black', size=(900, None), method='caption').set_position(('center', 200)).set_duration(30)
    clips_to_add.append(txt_hook)
except:
    print("⚠️ Text engine skip hua (GitHub imageMagick issue), video continue ho rahi hai.")

final_reel = CompositeVideoClip(clips_to_add, size=(1080, 1920)).set_duration(30)

# --- 8. RENDER REEL ---
output_file = output_dir + f"Viral_{detected_mood}_Reel.mp4"
print(f"🔥 Final Reel Tandoor mein hai...")
final_reel.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=30, preset="ultrafast", threads=2)

print(f"✅ BOOM! Factory ka kaam khatam! Reel yahan save hai: {output_file}")
