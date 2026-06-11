# Face Comparison API (Memory Optimized)

A standalone, high-performance, and lightweight Face Comparison API built with **FastAPI**, **InsightFace** (using the CPU-optimized `buffalo_s` model bundle), and **ONNX Runtime**. 

This application is specifically designed and configured to run within **Render's Free Tier (512MB RAM Limit)** without triggering Out-of-Memory (OOM) failures, by leveraging advanced ONNX runtime modifications and selective model initialization.

---

## 🐳 Docker Desktop Quick Install (Windows PowerShell)

For Windows users setting up Docker Desktop, run **PowerShell as an Administrator** and follow these instructions.

### Option 1: All-in-One Script
Copy and execute this script to download, install, update WSL, clean up, and launch Docker Desktop automatically:

```powershell
# 1. Download Docker Desktop Installer
Write-Host "Downloading Docker Desktop Installer..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -OutFile "DockerDesktopInstaller.exe"

# 2. Run installer silently with WSL-2 backend
Write-Host "Installing Docker Desktop (this may take a few minutes)..." -ForegroundColor Cyan
Start-Process -FilePath ".\DockerDesktopInstaller.exe" -ArgumentList "install", "--quiet", "--accept-license", "--backend=wsl-2" -Wait -NoNewWindow

# 3. Clean up the installer executable
Write-Host "Cleaning up installation files..." -ForegroundColor Cyan
Remove-Item "DockerDesktopInstaller.exe" -ErrorAction SilentlyContinue

# 4. Update WSL (recommended for WSL 2 backend)
Write-Host "Updating WSL..." -ForegroundColor Cyan
wsl --update

# 5. Start Docker Desktop
Write-Host "Launching Docker Desktop..." -ForegroundColor Cyan
Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe"

Write-Host "Installation completed! Please wait a moment for Docker to fully initialize, then run 'docker info' to verify." -ForegroundColor Green
```

### Option 2: Step-by-Step Installation

#### **Step 1: Download the Installer**
```powershell
Invoke-WebRequest -Uri "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -OutFile "DockerDesktopInstaller.exe"
```

#### **Step 2: Run the Installer Silently**
```powershell
Start-Process -FilePath ".\DockerDesktopInstaller.exe" -ArgumentList "install", "--quiet", "--accept-license", "--backend=wsl-2" -Wait -NoNewWindow
```

#### **Step 3: Clean Up & Update WSL (Recommended)**
```powershell
Remove-Item "DockerDesktopInstaller.exe"
wsl --update
```

#### **Step 4: Launch Docker Desktop**
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

#### **Step 5: Verify if it is Ready**
Wait a few seconds for Docker to spin up, then run:
```powershell
docker info
```

---

## 🚀 Key Features

* **Flexible Formats**: Supports comparing local image uploads or remote image URLs.
* **Dual URL Methods**: Support for both `POST` (JSON body) and `GET` (query parameter) URL comparisons.
* **Production Ready**: Full CORS middleware enabled for integration with mobile and web clients.
* **Super-Efficient Execution**:
  - **Thread Constrained**: Restricts ONNX Runtime to strict single-threaded CPU execution. This prevents thread-spawning spikes from crashing multi-core host machines.
  - **Memory Arena Disabled**: Immediately releases unused CPU buffers back to the operating system.
  - **Selective Model Initialization**: Loads only `detection` and `recognition` sub-models, skipping 3D-landmark, 2D-landmark, and age/gender estimation models (saving ~50MB RAM).
  - **Aggressive Garbage Collection**: Forces Python garbage collection (`gc.collect()`) after processing to clean image arrays and temporary tensors immediately.

---

## 🛠️ Local Setup & Running

### Prerequisites
* Python 3.10 or 3.12+
* CMake and C++ Compiler tools (required for building InsightFace compiled extensions)

### 1. Clone & Enter Directory
```bash
cd /Users/sudhanshu/Desktop/CBO_SFA/face_verifiaction
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the API Server
Run the API locally using Uvicorn:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📡 API Endpoints

### 1. Health Status
Check if the API and the face recognition models are initialized and active.
* **Method**: `GET`
* **Path**: `/`
* **Response**:
  ```json
  {
    "status": "online",
    "model_loaded": true,
    "message": "Face Comparison API (buffalo_s) is running."
  }
  ```

---

### 2. Compare Local Files
Compare two binary images uploaded directly.
* **Method**: `POST`
* **Path**: `/compare`
* **Request Format**: `multipart/form-data`
  * `image1`: File (binary image)
  * `image2`: File (binary image)
* **Response**:
  ```json
  {
    "success": true,
    "match": true,
    "confidence": 72.92,
    "similarity": 0.7292,
    "threshold": 0.4,
    "message": "Faces compared successfully."
  }
  ```

---

### 3. Compare Image URLs (POST JSON)
Compare two faces programmatically via their remote URLs using a JSON payload.
* **Method**: `POST`
* **Path**: `/compare-url`
* **Headers**: `Content-Type: application/json`
* **Payload**:
  ```json
  {
    "url1": "https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg",
    "url2": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Official_portrait_of_Barack_Obama.jpg"
  }
  ```
* **Response**:
  ```json
  {
    "success": true,
    "match": true,
    "confidence": 72.92,
    "similarity": 0.7292,
    "threshold": 0.4,
    "message": "Faces compared successfully."
  }
  ```

---

### 4. Compare Image URLs (GET Query Params)
Ideal for testing directly in web browsers or simple integrations using URL parameters.
* **Method**: `GET`
* **Path**: `/compare-url`
* **Query Parameters**:
  * `url1`: The URL of the first image
  * `url2`: The URL of the second image
* **Example URL**:
  `http://127.0.0.1:8000/compare-url?url1=https://example.com/face1.jpg&url2=https://example.com/face2.jpg`

---

## 🧪 Running Automated Local Tests

We have included a comprehensive 4-stage validation script inside the workspace. To run it, make sure the local Uvicorn server is running on port 8000, and execute:

```bash
python run_face_comparison_tests.py
```

This will automatically download target faces, run comparison comparisons (matches, non-matches, URL POST, and URL GET), and assert the correctness of each API response.

---

## ☁️ Deploying to Render (Free Tier)

This repository includes a multi-stage `Dockerfile` optimized for memory footprint. 

1. Push all code to your GitHub repository:
   ```bash
   git add main.py requirements.txt run_face_comparison_tests.py README.md
   git commit -m "Docs: add README instructions and finalize URL endpoints"
   git push origin main
   ```
2. Log in to your **Render Dashboard** and select **New** -> **Web Service**.
3. Link your GitHub repository.
4. Set the runtime environment to **Docker**.
5. Choose the **Free Instance Type** (512MB RAM).
6. Click **Deploy Web Service**.

*The Dockerfile pre-downloads and caches the models during the build stage. On startup, the monkey-patch and global threading configurations ensure the service boots and operates well under the 512MB RAM ceiling.*
