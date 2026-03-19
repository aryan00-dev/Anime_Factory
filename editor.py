import os
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

print("🎬 Phase 5: Hacker Edit Logic Test Shuru...")

try:
    # 1. Dummy Video (Testing ke liye 5 second ka neela video)
    print("⏳ Original Video process ho rahi hai...")
    dummy_clip = ColorClip(size=(1080, 720), color=(50, 50, 255)).set_duration(5)

    # 2. HACKER EDIT: Speed 1.05x aur Color +5%
    dummy_clip = dummy_clip.fx(vfx.speedx, 1.05)
    dummy_clip = dummy_clip.fx(vfx.colorx, 1.05)

    # 3. BACKGROUND: Instagram Reels size (1080x1920) White Canvas
    print("🖼️ White Canvas set kar rahe hain...")
    bg = ColorClip(size=(1080, 1920), color=(255, 255, 255)).set_duration(dummy_clip.duration)

    # 4. TEXT: Upar 2 line ka text
    print("✍️ Anime ka naam aur Episode likh rahe hain...")
    text_str = "Demon Slayer\nSeason 2 - Episode 10"
    txt_clip = TextClip(text_str, fontsize=70, color='black', size=(900, None), method='caption')
    txt_clip = txt_clip.set_position(('center', 250)).set_duration(dummy_clip.duration)

    # 5. MIXING: Background + Beech mein Video + Upar Text
    final_video = CompositeVideoClip([
        bg, 
        dummy_clip.set_position("center"), 
        txt_clip
    ])

    # 6. EXPORT
    print("💾 Final Reel save kar rahe hain... (isme 10-20 sec lagenge)")
    final_video.write_videofile("final_reel.mp4", fps=24, codec="libx264")
    
    print("✅ SUCCESS! Hacker Edit 100% kaam kar raha hai! Video Ready!")

except Exception as e:
    print("❌ Error aa gaya:", e)
