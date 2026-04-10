import os
import glob
import random
import time
import requests
import gdown
import google.generativeai as genai
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip, TextClip, ColorClip, vfx

print("--- 🚀 VEDA CLOUD FACTORY ENGINE (100% COMPLETE & SECURE) STARTED ---", flush=True)

# --- 1. API & SECRETS SETUP ---
API_KEY = os.environ.get("GEMINI_API_KEY")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID")

if not all([API_KEY, META_ACCESS_TOKEN, IG_ACCOUNT_ID]):
    print("❌ CRITICAL ERROR: GitHub Secrets missing! Factory band ho rahi hai.", flush=True)
    exit()

genai.configure(api_key=API_KEY)

# --- 2. FOLDERS & IDs ---
DRIVE_FOLDERS = {
    "Raw_Clips": "1Ka3dX7yI1OY3VVhjRI9wVS-iklGf0tc2",
    "Action": "1YVVpYmHrcYBONWklcgdv3NYiS5_SlJmZ",
    "Chill": "18i3mLxxYTTkPFzbV_746WqMw3pcteIrG",
    "Sad": "1XAatApMuEYAJvV7RGzc8mDIP-1R0k8VM",
    "Romance": "1ppfCxuDOBEG8jG2-zRKig9kKOh9ozxFw"
}

PAGE_NAME = "Asianimedaily.daily"
base_dir = "workspace/"
raw_dir = base_dir + "raw/"
audio_dir = base_dir + "audio/"
output_dir = base_dir + "output/"
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# --- 3. RAW VIDEO DOWNLOADER ---
print("📥 Google Drive se raw episode utha raha hu...", flush=True)
try:
    gdown.download_folder(f"https://drive.google.com/drive/folders/{DRIVE_FOLDERS['Raw_Clips']}", output=raw_dir, quiet=True, use_cookies=False)
except Exception as e:
    print("⚠️ Download Warning:", e, flush=True)

videos = glob.glob(raw_dir + "**/*.mp4", recursive=True) + glob.glob(raw_dir + "**/*.mkv", recursive=True)
if not videos:
    print("❌ Koi video nahi mili! Engine band.", flush=True)
    exit()
vid_path = videos[0]
print(f"🎬 Video mil gayi: {vid_path}", flush=True)

# --- 4. GOD AI ANALYSIS ---
print("🧠 God AI video scan kar raha hai...", flush=True)
try:
    video_file_ai = genai.upload_file(path=vid_path)
    
    # FIX: Naya loop jo status update karega
    while video_file_ai.state.name == 'PROCESSING':
        print("⏳ AI processing mein hai, 5 seconds wait...", flush=True)
        time.sleep(5)
        video_file_ai = genai.get_file(video_file_ai.name) # Naya status fetch karne ka command
    
    if video_file_ai.state.name == 'FAILED':
        raise Exception("AI failed to process video.")

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = """Watch this anime. Find the absolute best 30-second viral short scene.
    Detect the exact MOOD: Action, Chill, Sad, or Romance.
    Reply ONLY in this exact format separated by '|':
    StartTimeInSeconds|ViralHook|Mood"""
    
    response = model.generate_content([video_file_ai, prompt])
    ai_data = response.text.strip().split('|')
    start_time = int(ai_data[0])
    hook_text = ai_data[1]
    detected_mood = ai_data[2].strip()
    print(f"🎯 AI BINGO! Time: {start_time}s | Mood: {detected_mood} | Hook: {hook_text}", flush=True)
    genai.delete_file(video_file_ai.name)
except Exception as e:
    print("⚠️ AI Error, backup data use kar rahe hain:", e, flush=True)
    start_time, hook_text, detected_mood = 100, "Wait for it 🤯", "Action"

# --- 5. AUDIO DOWNLOADER ---
print(f"🎵 Mood '{detected_mood}' ke hisab se audio nikal raha hu...", flush=True)
mood_folder_id = DRIVE_FOLDERS.get(detected_mood, DRIVE_FOLDERS["Action"])
try:
    gdown.download_folder(f"https://drive.google.com/drive/folders/{mood_folder_id}", output=audio_dir, quiet=True, use_cookies=False)
except Exception as e:
    print("⚠️ Audio Download Warning:", e, flush=True)

audio_files = glob.glob(audio_dir + "**/*.mp3", recursive=True) + glob.glob(audio_dir + "**/*.m4a", recursive=True)
selected_audio = random.choice(audio_files) if audio_files else None

# --- 6. THE EDITOR ---
print("✂️ Kainchi, Audio aur Hacker Effects lag rahe hain...", flush=True)
REEL_DURATION = 30
end_time = start_time + REEL_DURATION 

vid_clip = VideoFileClip(vid_path).subclip(start_time, end_time).fx(vfx.speedx, 1.02)
w_reel, h_reel = 1080, 1920

if selected_audio:
    temp_bgm = AudioFileClip(selected_audio)
    if temp_bgm.duration < REEL_DURATION:
        REEL_DURATION = int(temp_bgm.duration) - 1
        vid_clip = vid_clip.subclip(0, REEL_DURATION)
    
    bg_music = temp_bgm.subclip(0, REEL_DURATION).volumex(0.35)
    if vid_clip.audio:
        final_audio = CompositeAudioClip([vid_clip.audio.volumex(0.7), bg_music])
        vid_clip = vid_clip.set_audio(final_audio)
    else:
        vid_clip = vid_clip.set_audio(bg_music)

bg_clip = vid_clip.resize(height=h_reel).crop(x_center=vid_clip.w/2, width=w_reel).fx(vfx.colorx, 0.4)
fg_clip = vid_clip.resize(width=1080).set_position(("center", "center"))

flicker = ColorClip(size=(w_reel, h_reel), color=(0,0,0)).set_duration(0.1).set_start(15)

clips_to_add = [bg_clip, fg_clip, flicker]

try:
    progress_bar = ColorClip(size=(1080, 8), color=(0,255,255)).set_position((0, 1600)).set_duration(REEL_DURATION)
    txt_branding = TextClip(PAGE_NAME, fontsize=45, color='white', font='Arial-Bold').set_position(('center', 1700)).set_duration(REEL_DURATION)
    txt_hook = TextClip(hook_text, fontsize=65, color='white', bg_color='black', font='Arial-Bold').set_position(('center', 250)).set_duration(REEL_DURATION)
    clips_to_add.extend([progress_bar, txt_branding, txt_hook])
except Exception as e:
    print("⚠️ Visual Layers skip huye (ImageMagick error ho sakta hai).", flush=True)

final_reel = CompositeVideoClip(clips_to_add, size=(w_reel, h_reel)).set_duration(REEL_DURATION)
output_file = output_dir + f"Viral_{detected_mood}_Reel.mp4"

print("🔥 Final Reel Render ho rahi hai...", flush=True)
final_reel.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=30, preset="ultrafast", threads=2)

# --- 7. URL GENERATOR & UPLOAD ---
print("☁️ Meta API ke liye public link bana raha hu...", flush=True)
def get_direct_url(filepath):
    try:
        with open(filepath, 'rb') as f:
            res = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f})
        if res.status_code == 200:
            return res.json()['data']['url'].replace('tmpfiles.org/', 'tmpfiles.org/dl/')
    except Exception as e:
        print("⚠️ Upload Error:", e, flush=True)
    return None

public_video_url = get_direct_url(output_file)

if public_video_url:
    print(f"🔗 Public URL ready. Instagram par upload shuru...", flush=True)
    caption = f"🔥 Best {detected_mood} Anime Moment! 🎬\n\nDrop a like! ❤️\n\n#anime #animeedit #animereels #{detected_mood.lower()} #asianimedaily"
    
    container_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
    payload = {"media_type": "REELS", "video_url": public_video_url, "caption": caption, "access_token": META_ACCESS_TOKEN}
    
    res = requests.post(container_url, data=payload).json()
    if 'id' in res:
        creation_id = res['id']
        print(f"⏳ Container (ID: {creation_id}) ban gaya. Meta server rendering... 30 sec wait.", flush=True)
        time.sleep(30) 
        
        publish_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"
        pub_payload = {"creation_id": creation_id, "access_token": META_ACCESS_TOKEN}
        pub_res = requests.post(publish_url, data=pub_payload).json()
        
        if 'id' in pub_res:
            print("✅ BOOM! Reel successfully Instagram par POST ho gayi!", flush=True)
        else:
            print("❌ Publish Failed:", pub_res, flush=True)
    else:
        print("❌ Container Failed:", res, flush=True)
else:
    print("❌ Public URL nahi ban paya.", flush=True)
