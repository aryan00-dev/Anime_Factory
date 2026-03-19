import os
from google import genai

# Tijori se chabi nikalna
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: Chabi nahi mili! GitHub Secrets check karo.")
else:
    try:
        print("⏳ Brahmastra Launch: Gemini 2.5 Flash-Lite se connect kar rahe hain...")
        client = genai.Client(api_key=API_KEY)
        
        # Brahmastra Model: Jo 100% free hai aur kabhi fail nahi hoga
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents="Ek anime fan ke style mein batao ki kya tum zinda ho aur kaam kar rahe ho? Sirf 2 line mein hindi mein."
        )
        
        print("✅ Success! Gemini zinda hai. Reply:")
        print(response.text)
    except Exception as e:
        print("❌ Error aa gaya:", e)
