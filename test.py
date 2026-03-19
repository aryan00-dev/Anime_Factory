import os
import google.generativeai as genai

# Tijori se chabi nikalna
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: Chabi nahi mili! GitHub Secrets check karo.")
else:
    try:
        # Gemini ko chabi dena aur Flash model set karna
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Bot se pehla sawal puchna
        print("⏳ Gemini se connect kar rahe hain...")
        response = model.generate_content("Ek anime fan ke style mein batao ki kya tum zinda ho aur kaam kar rahe ho? Sirf 2 line mein hindi mein.")
        
        print("✅ Success! Gemini zinda hai. Reply:")
        print(response.text)
    except Exception as e:
        print("❌ Error aa gaya:", e)
