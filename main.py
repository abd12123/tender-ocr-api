from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import Optional
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import requests
import os

app = FastAPI()

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if needed
POPPLER_PATH = r"C:\Users\Varun S\Desktop\txt from img\poppler-24.08.0\Library\bin"


def ocr_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image, lang='eng')

@app.post("/parse")
async def parse_tender(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None)
):
    if file:
        content = await file.read()
    elif url:
        response = requests.get(url)
        if response.status_code != 200:
            return JSONResponse(status_code=400, content={"error": "Invalid URL"})
        content = response.content
    else:
        return JSONResponse(status_code=400, content={"error": "No file or URL provided"})

    try:
        images = convert_from_bytes(content, poppler_path=POPPLER_PATH)  # ✅ key fix
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"PDF processing failed: {str(e)}"})

    full_text = ""
    for i, img in enumerate(images):
        text = ocr_image(img)
        full_text += f"\n\n--- Page {i+1} ---\n{text}"

    return {
        "pages": len(images),
        "text": full_text[:10000]
    }
