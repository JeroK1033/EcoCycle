import os
import sys
import requests
import tkinter as tk
from tkinter import filedialog

SERVER_URL = "https://ecocycle-eqjc.onrender.com"

COLORES = {
    "verde":    "\033[92m",
    "amarillo": "\033[93m",
    "rojo":     "\033[91m",
    "azul":     "\033[94m",
    "cyan":     "\033[96m",
    "blanco":   "\033[97m",
    "negro":    "\033[90m",
    "reset":    "\033[0m",
    "bold":     "\033[1m",
}

def color(texto, c):
    return f"{COLORES.get(c, '')}{texto}{COLORES['reset']}"

def banner():
    print(color("\n╔══════════════════════════════════╗", "verde"))
    print(color("║       ♻️  EcoCycle IA CLI         ║", "verde"))
    print(color("╚══════════════════════════════════╝\n", "verde"))

def verificar_servidor():
    print(color(f"Conectando al servidor en la nube: {SERVER_URL} ...", "cyan"))
    try:
        r = requests.get(f"{SERVER_URL}/", timeout=10) # Timeout más largo por si el internet está lento
        if r.status_code == 200:
            print(color("✅ Conexión establecida correctamente\n", "verde"))
            return True
    except requests.ConnectionError:
        print(color("❌ No se pudo conectar a la nube.", "rojo"))
        print(color("   Verifica tu conexión a internet o el estado del servidor.", "amarillo"))
        return False

def pedir_ruta_imagen():
    print(color("📂 Abriendo explorador de archivos...", "azul"))
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) 
    
    ruta = filedialog.askopenfilename(
        title="Selecciona la imagen para EcoCycle",
        filetypes=[
            ("Archivos de imagen", "*.jpg *.jpeg *.png *.webp *.gif *.bmp"),
            ("Todos los archivos", "*.*")
        ]
    )
    
    if not ruta:
        print(color("\n⚠️  Operación cancelada.", "amarillo"))
        return None
    return ruta

def mostrar_resultado(data: dict):
    clasificacion = data.get("clasificacion", "")
    c_clasif = "blanco" if "Reciclable" in clasificacion else "verde" if "Orgánico" in clasificacion else "negro"

    print(color("\n╔══════════════ RESULTADO ══════════════╗", "cyan"))
    print(color(f"║  🗑️  Objeto      : ", "cyan") + color(data.get('objeto', '-'), "bold"))
    print(color(f"║  🧪 Material    : ", "cyan") + data.get('material', '-'))
    print(color(f"║  ♻️  Clasificación: ", "cyan") + color(clasificacion, c_clasif))
    print(color(f"║  📋 Instrucción : ", "cyan") + data.get('instruccion', '-'))
    print(color(f"║  ⭐ Puntos      : ", "cyan") + color(str(data.get('puntos', 0)) + " pts", "amarillo"))
    print(color("╚═══════════════════════════════════════╝\n", "cyan"))

def analizar_imagen(ruta: str):
    print(color(f"\n🔍 Enviando imagen a la nube para análisis...", "azul"))
    with open(ruta, "rb") as f:
        mime = "image/jpeg"
        ext = os.path.splitext(ruta)[1].lower()
        if ext == ".png": mime = "image/png"
        elif ext == ".webp": mime = "image/webp"

        try:
            response = requests.post(
                f"{SERVER_URL}/analizar",
                files={"imagen": (os.path.basename(ruta), f, mime)},
                timeout=60 # Damos buen tiempo para la subida de la foto y procesamiento
            )
        except requests.ConnectionError:
            print(color("❌ Se perdió la conexión.", "rojo"))
            return

    if response.status_code == 200:
        mostrar_resultado(response.json())
    else:
        print(color(f"❌ Error del servidor ({response.status_code})", "rojo"))

def main():
    banner()
    if not verificar_servidor():
        sys.exit(1)

    while True:
        ruta = pedir_ruta_imagen()
        
        if not ruta:
            print(color("¿Deseas salir del programa? (s/n)", "azul"))
            resp = input(color("   > ", "bold")).strip().lower()
            if resp in ("s", "si", "y", "yes"):
                break
            else:
                continue

        analizar_imagen(ruta)

        print(color("¿Analizar otra imagen? (Enter para continuar / 'salir' para cerrar)", "azul"))
        resp = input(color("   > ", "bold")).strip().lower()
        if resp in ("salir", "exit", "q"):
            print(color("\nHasta luego! ♻️\n", "verde"))
            break
        print()

if __name__ == "__main__":
    main()