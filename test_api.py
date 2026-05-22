import os
import sys
import time
import requests

# API URL
URL = "http://127.0.0.1:8000"

def test_api():
    print("=== Testing Face Comparison API ===")
    
    # 1. Test status endpoint
    try:
        response = requests.get(f"{URL}/")
        print(f"Status Endpoint GET '/':")
        print(f"  HTTP Code: {response.status_code}")
        print(f"  Response:  {response.json()}")
        if response.status_code == 200:
            print("✅ Status check passed!")
        else:
            print("❌ Status check failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print("Make sure the API server is running on http://127.0.0.1:8000")
        sys.exit(1)

    # 2. Check for test images
    img1_path = "test_image1.jpg"
    img2_path = "test_image2.jpg"

    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print("\n💡 Notice: Please place two test images ('test_image1.jpg' and 'test_image2.jpg') in this directory to test the face comparison endpoint '/compare'.")
        return

    # 3. Test compare endpoint
    print("\nTesting Compare Endpoint POST '/compare'...")
    try:
        with open(img1_path, "rb") as f1, open(img2_path, "rb") as f2:
            files = {
                "image1": (img1_path, f1, "image/jpeg"),
                "image2": (img2_path, f2, "image/jpeg")
            }
            response = requests.post(f"{URL}/compare", files=files)
            print(f"  HTTP Code: {response.status_code}")
            print(f"  Response:  {response.json()}")
            if response.status_code == 200:
                print("✅ Face comparison endpoint passed!")
            else:
                print("❌ Face comparison endpoint failed!")
    except Exception as e:
        print(f"❌ Error during face comparison request: {e}")

if __name__ == "__main__":
    test_api()
