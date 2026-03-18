import base64
import uuid

import httpx
from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from config import PROCESSING_SERVICE_URL, supabase

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"}
STORAGE_BUCKET = "infrared-images"


def _extract_token(authorization: str) -> str:
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization


async def _get_current_user(authorization: str) -> dict:
    try:
        token = _extract_token(authorization)
        user_response = supabase.auth.get_user(token)
        return {"id": str(user_response.user.id), "email": user_response.user.email}
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


@router.post("/upload", summary="Upload an infrared image for target detection")
async def upload_image(
    file: UploadFile = File(...),
    algorithm: str = Form(default="DW-LCM"),
    authorization: str = Header(...),
):
    user = await _get_current_user(authorization)

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not supported. Use JPEG, PNG, BMP, TIFF, or WebP.",
        )

    if algorithm.upper() not in ("DW-LCM", "MW-IPI"):
        raise HTTPException(status_code=400, detail="Algorithm must be 'DW-LCM' or 'MW-IPI'")

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Upload original image to Supabase storage
    original_path = f"{user['id']}/{uuid.uuid4()}/original_{file.filename}"
    supabase.storage.from_(STORAGE_BUCKET).upload(
        original_path, image_bytes, {"content-type": file.content_type}
    )
    original_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(original_path)

    # Insert pending detection record
    record = (
        supabase.table("detections")
        .insert(
            {
                "user_id": user["id"],
                "original_image_url": original_url,
                "algorithm": algorithm.upper(),
                "status": "processing",
            }
        )
        .execute()
    )
    detection_id = record.data[0]["id"]

    # Send to processing service
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{PROCESSING_SERVICE_URL}/process",
                files={"file": (file.filename, image_bytes, file.content_type)},
                data={"algorithm": algorithm.upper()},
            )
    except httpx.RequestError as exc:
        supabase.table("detections").update({"status": "failed"}).eq("id", detection_id).execute()
        raise HTTPException(status_code=503, detail="Processing service unavailable") from exc

    if response.status_code != 200:
        supabase.table("detections").update({"status": "failed"}).eq("id", detection_id).execute()
        raise HTTPException(status_code=500, detail="Image processing failed")

    result = response.json()

    # Upload processed image
    processed_url = original_url
    if result.get("processed_image"):
        processed_bytes = base64.b64decode(result["processed_image"])
        processed_path = f"{user['id']}/{uuid.uuid4()}/processed_{file.filename}"
        supabase.storage.from_(STORAGE_BUCKET).upload(
            processed_path, processed_bytes, {"content-type": "image/png"}
        )
        processed_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(processed_path)

    # Update detection record
    supabase.table("detections").update(
        {
            "processed_image_url": processed_url,
            "targets": result.get("targets", []),
            "target_count": result.get("target_count", 0),
            "status": "completed",
        }
    ).eq("id", detection_id).execute()

    return {
        "id": detection_id,
        "original_image_url": original_url,
        "processed_image_url": processed_url,
        "targets": result.get("targets", []),
        "target_count": result.get("target_count", 0),
        "algorithm": algorithm.upper(),
        "status": "completed",
    }


@router.get("/", summary="List all detections for the current user")
async def list_images(authorization: str = Header(...)):
    user = await _get_current_user(authorization)
    response = (
        supabase.table("detections")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return {"detections": response.data}


@router.get("/{detection_id}", summary="Get a specific detection result")
async def get_image(detection_id: str, authorization: str = Header(...)):
    user = await _get_current_user(authorization)
    response = (
        supabase.table("detections")
        .select("*")
        .eq("id", detection_id)
        .eq("user_id", user["id"])
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Detection not found")
    return response.data[0]


@router.delete("/{detection_id}", summary="Delete a detection record")
async def delete_image(detection_id: str, authorization: str = Header(...)):
    user = await _get_current_user(authorization)
    response = (
        supabase.table("detections")
        .select("id")
        .eq("id", detection_id)
        .eq("user_id", user["id"])
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Detection not found")
    supabase.table("detections").delete().eq("id", detection_id).execute()
    return {"message": "Detection deleted"}
