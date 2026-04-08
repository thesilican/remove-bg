from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from io import BytesIO
from os import environ
from PIL import Image
from withoutbg import OpenSourceModel
import asyncio

load_dotenv()
ETHGLOBAL_API_KEY = environ.get("ETHGLOBAL_API_KEY")

model = OpenSourceModel(
    depth_model_path="models/depth_anything_v2_vits_slim.onnx",
    isnet_model_path="models/isnet.onnx",
    matting_model_path="models/focus_matting_1.0.0.onnx",
    refiner_model_path="models/focus_refiner_1.0.0.onnx",
)

app = FastAPI()

executor = ThreadPoolExecutor(max_workers=1)


@app.get("/")
async def get_home():
    return "🌠 Welcome to ETHGlobal image background removal api 🌠"


@app.post("/api/image")
async def post_image(req: Request):
    # Check authorization
    auth = req.headers.get("Authorization")
    if auth != f"Bearer {ETHGLOBAL_API_KEY}":
        raise HTTPException(status_code=401)

    # Parse request body
    content_type = req.headers.get("Content-Type")
    if content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="expected image/png or image/jpeg")
    try:
        body = await req.body()
        image = Image.open(BytesIO(body))
    except Exception:
        raise HTTPException(status_code=400, detail="could not read image file")

    def remove_background(image: Image):
        image_out = model.remove_background(image)
        buf = BytesIO()
        image_out.save(buf, format="PNG")
        result = buf.getvalue()
        return result

    # Run background removal in worker thread
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, remove_background, image)
    return Response(content=result, media_type="image/png")
