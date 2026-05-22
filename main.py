import os
import cv2
import numpy as np
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from insightface.app import FaceAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("face-comparison-api")

app = FastAPI(title="Face Comparison API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Initializing InsightFace with buffalo_s model...")
try:
    # Use buffalo_s, root="." stores model weights in the local directory
    model = FaceAnalysis(name="buffalo_s", root=".")
    model.prepare(ctx_id=-1, det_size=(320, 320))
    logger.info("InsightFace model loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load InsightFace model: {str(e)}")
    model = None

@app.get("/")
def read_root():
    return {
        "status": "online",
        "model_loaded": model is not None,
        "message": "Face Comparison API (buffalo_s) is running."
    }

@app.post("/compare")
async def compare_faces(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...)
):
    if model is None:
        raise HTTPException(status_code=500, detail="Face detection model not initialized.")

    try:
        img1_bytes = await image1.read()
        img2_bytes = await image2.read()

        nparr1 = np.frombuffer(img1_bytes, np.uint8)
        nparr2 = np.frombuffer(img2_bytes, np.uint8)

        img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

        if img1 is None:
            return {"success": False, "match": False, "confidence": 0.0, "similarity": 0.0, "message": "Failed to decode Image 1"}
        if img2 is None:
            return {"success": False, "match": False, "confidence": 0.0, "similarity": 0.0, "message": "Failed to decode Image 2"}

        faces1 = model.get(img1)
        faces2 = model.get(img2)

        if len(faces1) == 0:
            return {"success": True, "match": False, "confidence": 0.0, "similarity": 0.0, "message": "No face detected in Image 1"}
        if len(faces2) == 0:
            return {"success": True, "match": False, "confidence": 0.0, "similarity": 0.0, "message": "No face detected in Image 2"}

        emb1 = faces1[0].embedding
        emb2 = faces2[0].embedding

        dot_product = np.dot(emb1, emb2)
        norm_emb1 = np.linalg.norm(emb1)
        norm_emb2 = np.linalg.norm(emb2)

        if norm_emb1 == 0 or norm_emb2 == 0:
            similarity = 0.0
        else:
            similarity = float(dot_product / (norm_emb1 * norm_emb2))

        # 0.40 is the standard cosine similarity threshold for buffalo_s on CPU
        threshold = 0.40
        is_match = similarity >= threshold
        confidence = max(0.0, min(100.0, similarity * 100.0))

        return {
            "success": True,
            "match": is_match,
            "confidence": round(confidence, 2),
            "similarity": round(similarity, 4),
            "threshold": threshold,
            "message": "Faces compared successfully."
        }

    except Exception as e:
        logger.error(f"Error during face comparison: {str(e)}")
        return {"success": False, "match": False, "confidence": 0.0, "similarity": 0.0, "message": f"Server error: {str(e)}"}
