import google.generativeai as genai
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, ColorClip, ImageClip, TextClip, CompositeAudioClip
import os
import shutil
import time

print("--- Anime Factory: SMART NAMING AUTO-LOOP ---")

# --- AI SETUP ---
# ⚠️ WARNING: Never put your real API key on GitHub!
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)

# Folders 
base_dir = "/sdcard/Anime_Factory/"
raw_folder = base_dir + "Raw_Clips/"
audio_folder = base_dir + "Audio/"
output_folder = base_dir + "Final_Reels/"
completed_folder = base_dir + "Completed_Episodes/"
dp_path = base_dir + "dp.jpg"

# --- THE INFINITE LOOP ---
while True:
    all_videos = [f for f in os.listdir(raw_folder) if f.endswith(('.mp4', '.mkv'))]
    if len(all_videos) == 0:
        print("\n🎉 Factory ka saara raw material khatam! Bot sone ja raha hai 😴")
        break
        
    video_file = all_videos[0]
    vid_path = raw_folder + video_file
    
    file_name_only = os.path.splitext(video_file)[0]
    
    print(f"\n🎬 Factory ne nayi video uthayi: {video_file}")
    
    try:
        audio_file = os.listdir(audio_folder)[0]
    except:
        print("⚠️ Audio folder khali hai! Background music daal de bhai.")
        break

    print("Video Cloud par ja rahi hai...")
    try:
        video_file_ai = genai.upload_file(path=vid_path)
        print("AI dimaag laga raha hai...")
        
        while video_file_ai.state.name == 'PROCESSING':
            print('.', end='', flush=True)
            time.sleep(5)
        print()

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Text layout prompt
        prompt = """Watch this anime episode. Find the best viral scene. 
        Reply ONLY in this format: StartTimeInSeconds|ViralHookText
        Example: 320|Wait for the epic ending 😱"""
        
        response = model.generate_content([video_file_ai, prompt])
        ai_data = response.text.strip().split('|')
        
        start_time = int(ai_data[0])
        viral_hook = ai_data[1]
        
        print(f"🔥 AI BINGO! Time: {start_time}s | Hook: {viral_hook}")
        genai.delete_file(video_file_ai.name)

    except Exception as e:
        print("God AI Error:", e)
        print("Backup plan laga raha hu...")
        start_time = 300
        viral_hook = "Wait for it 😱"

    end_time = start_time + 30 

    # --- KAINCHI & LAYOUT ---
    print("Kainchi chal rahi hai aur Text lag raha hai...")
    vid = VideoFileClip(vid_path)
    aud = AudioFileClip(audio_folder + audio_file)

    cut_vid = vid.subclipped(start_time, end_time)
    final_aud = aud.subclipped(0, 30).with_volume_scaled(0.2)

    if cut_vid.audio is not None:
        mixed_audio = CompositeAudioClip([cut_vid.audio, final_aud])
        cut_vid = cut_vid.with_audio(mixed_audio)
    else:
        cut_vid = cut_vid.with_audio(final_aud)

    bg_clip = ColorClip(size=(1080, 1920), color=(255, 255, 255), duration=30)
    resized_vid = cut_vid.resized(width=1080).with_position(("center", "center"))
    clips_to_add = [bg_clip, resized_vid]

    if os.path.exists(dp_path):
        dp = ImageClip(dp_path).resized(width=150).with_position((80, 120)).with_duration(30)
        clips_to_add.append(dp)

    try:
        txt_hook = TextClip(viral_hook, fontsize=60, color='black', size=(900, None), method='caption').with_position(('center', 200)).with_duration(30)
        clips_to_add.append(txt_hook)
    except:
        pass

    final_reel = CompositeVideoClip(clips_to_add, size=(1080, 1920))
    
    final_reel_name = f"{file_name_only}_Reel.mp4"
    
    print(f"🔥 {final_reel_name} Tandoor mein hai...")
    # Ultrafast render settings applied
    final_reel.write_videofile(output_folder + final_reel_name, codec="libx264", audio_codec="aac", fps=30, preset="ultrafast", threads=4)

    try:
        shutil.move(vid_path, completed_folder + video_file)
        print(f"✅ Purana episode hata diya. {final_reel_name} Ready!")
    except:
        pass
