import os
import urllib.request
import requests

# API URL
URL = "http://127.0.0.1:8000"

# Sample images
IMAGES = {
    "obama1.jpg": "https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg",
    "obama2.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Official_portrait_of_Barack_Obama.jpg",
    "trump.jpg": "https://upload.wikimedia.org/wikipedia/commons/5/56/Donald_Trump_official_portrait.jpg"
}

def download_images():
    print("📥 Downloading sample face images for verification...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for filename, url in IMAGES.items():
        if not os.path.exists(filename):
            try:
                print(f"  Downloading {filename}...")
                r = requests.get(url, headers=headers, timeout=15)
                r.raise_for_status()
                with open(filename, "wb") as f:
                    f.write(r.content)
                print(f"  ✅ Saved {filename}")
            except Exception as e:
                print(f"  ❌ Failed to download {filename}: {e}")
        else:
            print(f"  ✅ {filename} already exists")

def run_tests():
    print("\n🚀 Starting Face Comparison API verification tests...")

    # 1. Test Match (Obama1 vs Obama2)
    print("\n--- Test Case 1: Match (Barack Obama vs Barack Obama) ---")
    if os.path.exists("obama1.jpg") and os.path.exists("obama2.jpg"):
        try:
            with open("obama1.jpg", "rb") as img1, open("obama2.jpg", "rb") as img2:
                files = {
                    "image1": ("obama1.jpg", img1, "image/jpeg"),
                    "image2": ("obama2.jpg", img2, "image/jpeg")
                }
                response = requests.post(f"{URL}/compare", files=files)
                print(f"HTTP Status: {response.status_code}")
                data = response.json()
                print("Response JSON:")
                for k, v in data.items():
                    print(f"  {k}: {v}")
                
                # Assertions
                if data.get("success") and data.get("match") is True:
                    print("🎉 SUCCESS: Match correctly identified!")
                else:
                    print("❌ FAILURE: Match was not identified.")
        except Exception as e:
            print(f"❌ Error during test: {e}")
    else:
        print("❌ Test files missing.")

    # 2. Test Non-Match (Obama1 vs Trump)
    print("\n--- Test Case 2: Non-Match (Barack Obama vs Donald Trump) ---")
    if os.path.exists("obama1.jpg") and os.path.exists("trump.jpg"):
        try:
            with open("obama1.jpg", "rb") as img1, open("trump.jpg", "rb") as img2:
                files = {
                    "image1": ("obama1.jpg", img1, "image/jpeg"),
                    "image2": ("trump.jpg", img2, "image/jpeg")
                }
                response = requests.post(f"{URL}/compare", files=files)
                print(f"HTTP Status: {response.status_code}")
                data = response.json()
                print("Response JSON:")
                for k, v in data.items():
                    print(f"  {k}: {v}")
                
                # Assertions
                if data.get("success") and data.get("match") is False:
                    print("🎉 SUCCESS: Non-match correctly identified!")
                else:
                    print("❌ FAILURE: Non-match failed to identify.")
        except Exception as e:
            print(f"❌ Error during test: {e}")
    else:
        print("❌ Test files missing.")

if __name__ == "__main__":
    download_images()
    run_tests()
