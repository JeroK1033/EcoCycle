import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

app = FastAPI(title="EcoCycle IA API")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analizar_residuo(imagen_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(imagen_bytes))

    instruccion = """
    Actúa como un experto en gestión de residuos de EcoCycle.
    Analiza la imagen y clasifica el objeto. 
    Responde estrictamente en formato JSON con estas llaves:
    "objeto": nombre del objeto,
    "material": tipo de material predominante,
    "clasificacion": (Reciclable, Orgánico, No Aprovechable),
    "instruccion": cómo debe disponerse,
    "puntos": valor entero entre 5 y 20 según la dificultad de reciclaje.
    """

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=[instruccion, img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    return json.loads(response.text)


@app.get("/")
def root():
    return {"mensaje": "EcoCycle IA API funcionando ✅"}


@app.post("/analizar")
async def analizar(imagen: UploadFile = File(...)):
    # Validar que sea imagen
    if not imagen.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

    contenido = await imagen.read()

    try:
        resultado = analizar_residuo(contenido)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar la imagen: {str(e)}")

    return JSONResponse(content=resultado)