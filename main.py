import os
import gdown
import google.generativeai as genai

print("--- CLOUD FACTORY ENGINE STARTED ---")

# --- 1. API SETUP ---
# (Yahan hum apni Gemini API Key daalenge)
API_KEY = "AIzaSyCmy7eNoUsqBXiN9tN3E-CEfC7RChOFAmo" # Tumhari Gemini Key
genai.configure(api_key=API_KEY)

# --- 2. GOOGLE DRIVE FOLDER IDs ---
# Jo links tumne diye the, unki IDs yahan lock kar di hain
DRIVE_FOLDERS = {
    "Raw_Clips": "1Ka3dX7yI1OY3VVhjRI9wVS-iklGf0tc2",
    "Action_Audio": "1YVVpYmHrcYBONWklcgdv3NYiS5_SlJmZ",
    "Chill_Audio": "18i3mLxxYTTkPFzbV_746WqMw3pcteIrG",
    "Sad_Audio": "1XAatApMuEYAJvV7RGzc8mDIP-1R0k8VM",
    "Romance_Audio": "1ppfCxuDOBEG8jG2-zRKig9kKOh9ozxFw"
}

# --- 3. CLOUD STORAGE SETUP ---
# GitHub ke computer mein folders banana
base_dir = "Factory_Workspace/"
os.makedirs(base_dir, exist_ok=True)
os.makedirs(base_dir + "Raw_Clips", exist_ok=True)
os.makedirs(base_dir + "Audio", exist_ok=True)

print("✅ Folders aur API setup done! Drive se connect karne ke liye ready hain.")

# --- 4. GOOGLE DRIVE SE KACHHA MAAL (VIDEO) NIKALNA ---
print("Google Drive se kachha episode utha raha hu...")

# Raw_Clips folder ka URL banana
raw_folder_url = f"https://drive.google.com/drive/folders/{DRIVE_FOLDERS['Raw_Clips']}"

# gdown engine se poora folder download karna
try:
    gdown.download_folder(raw_folder_url, output=base_dir + "Raw_Clips", quiet=False, use_cookies=False)
    print("✅ Download Complete! Raw video Factory mein aa chuki hai.")
except Exception as e:
    print("❌ Download fail ho gaya! Error:", e)

# Download hone ke baad check karna ki konsi video aayi hai
import glob
downloaded_videos = glob.glob(base_dir + "Raw_Clips/**/*.mp4", recursive=True)

if len(downloaded_videos) > 0:
    vid_path = downloaded_videos[0]
    print(f"🎬 Factory ne yeh video pakdi: {vid_path}")
else:
    print("⚠️ Koi .mp4 video nahi mili Drive folder mein!")
