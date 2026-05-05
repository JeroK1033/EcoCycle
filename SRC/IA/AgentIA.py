import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analizar_residuo(ruta_imagen):
    # Cargamos la imagen desde la carpeta local
    img = Image.open(ruta_imagen)
    
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
        model="gemini-3.1-flash-lite",
        contents=[instruccion, img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1 # Baja para que sea consistente
        )
    )
    return response.text