import base64

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from algorithms.dwlcm import detect_targets_dwlcm
from algorithms.mwipi import detect_targets_mwipi

app = FastAPI(
    title="InfraSight Processing Service",
    description="Infrared small target detection using DW-LCM and MW-IPI algorithms",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "processing"}


@app.post("/process", tags=["Processing"])
async def process_image(
    file: UploadFile = File(...),
    algorithm: str = Form(default="DW-LCM"),
):
    """
    Process an infrared image using the specified detection algorithm.

    - **DW-LCM**: Dual-Window Local Contrast Method (fast, good for single-scale targets)
    - **MW-IPI**: Multiscale Window Infrared Patch-Image Model (robust, multi-scale)
    """
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file received")

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Ensure a valid image format is sent.")

    algo_upper = algorithm.upper()
    if algo_upper == "DW-LCM":
        processed, targets = detect_targets_dwlcm(img)
    elif algo_upper == "MW-IPI":
        processed, targets = detect_targets_mwipi(img)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown algorithm '{algorithm}'. Supported: DW-LCM, MW-IPI",
        )

    _, buffer = cv2.imencode(".png", processed)
    processed_b64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "algorithm": algo_upper,
        "target_count": len(targets),
        "targets": targets,
        "processed_image": processed_b64,
    }
