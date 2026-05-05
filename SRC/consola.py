import os
import sys
import requests
import subprocess
import time
import tkinter as tk
from tkinter import filedialog

SERVER_URL = "http://localhost:8000"

COLORES = {
    "verde":    "\033[92m",
    "amarillo": "\033[93m",
    "rojo":     "\033[91m",
    "azul":     "\033[94m",
    "cyan":     "\033[96m",
    "blanco":   "\033[97m",  # Añadido para mostrar_resultado
    "negro":    "\033[90m",  # Añadido para mostrar_resultado (gris oscuro para que se vea en consola negra)
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
    try:
        r = requests.get(f"{SERVER_URL}/", timeout=3)
        if r.status_code == 200:
            print(color("✅ Servidor conectado correctamente\n", "verde"))
            return True
    except requests.ConnectionError:
        print(color("❌ No se pudo conectar al servidor.", "rojo"))
        print(color(f"   Asegúrate de que esté corriendo en {SERVER_URL}", "amarillo"))
        return False

def pedir_ruta_imagen():
    print(color("📂 Abriendo explorador de archivos para seleccionar la imagen...", "azul"))
    
    # Inicializar y ocultar la ventana principal de tkinter
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) # Asegura que la ventana salga por encima
    
    # Abrir el explorador
    ruta = filedialog.askopenfilename(
        title="Selecciona la imagen para EcoCycle",
        filetypes=[
            ("Archivos de imagen", "*.jpg *.jpeg *.png *.webp *.gif *.bmp"),
            ("Todos los archivos", "*.*")
        ]
    )
    
    if not ruta:
        print(color("\n⚠️  Operación cancelada: No se seleccionó ninguna imagen.", "amarillo"))
        return None

    return ruta

def mostrar_resultado(data: dict):
    clasificacion = data.get("clasificacion", "")

    # Color según clasificación
    if "Reciclable" in clasificacion:
        c_clasif = "blanco"
    elif "Orgánico" in clasificacion:
        c_clasif = "verde"
    else:
        c_clasif = "negro"

    print(color("\n╔══════════════ RESULTADO ══════════════╗", "cyan"))
    print(color(f"║  🗑️  Objeto      : ", "cyan") + color(data.get('objeto', '-'), "bold"))
    print(color(f"║  🧪 Material    : ", "cyan") + data.get('material', '-'))
    print(color(f"║  ♻️  Clasificación: ", "cyan") + color(clasificacion, c_clasif))
    print(color(f"║  📋 Instrucción : ", "cyan") + data.get('instruccion', '-'))
    print(color(f"║  ⭐ Puntos      : ", "cyan") + color(str(data.get('puntos', 0)) + " pts", "amarillo"))
    print(color("╚═══════════════════════════════════════╝\n", "cyan"))

def analizar_imagen(ruta: str):
    print(color(f"\n🔍 Analizando imagen: {os.path.basename(ruta)} ...", "azul"))

    with open(ruta, "rb") as f:
        mime = "image/jpeg"
        ext = os.path.splitext(ruta)[1].lower()
        if ext == ".png":
            mime = "image/png"
        elif ext == ".webp":
            mime = "image/webp"

        try:
            response = requests.post(
                f"{SERVER_URL}/analizar",
                files={"imagen": (os.path.basename(ruta), f, mime)},
                timeout=30
            )
        except requests.ConnectionError:
            print(color("❌ Se perdió la conexión con el servidor.", "rojo"))
            return

    if response.status_code == 200:
        mostrar_resultado(response.json())
    else:
        print(color(f"❌ Error del servidor ({response.status_code}): {response.text}", "rojo"))

def main():
    banner()
    servidor = None

    try:
        # 1. Iniciar Uvicorn en segundo plano
        print(color("⏳ Iniciando el servidor de Inteligencia Artificial en segundo plano...", "cyan"))
        servidor = subprocess.Popen([sys.executable, "-m", "uvicorn", "SRC.server:app", "--reload"])
        
        # Darle 3 segundos al servidor para que levante completamente
        time.sleep(3) 

        # 2. Verificar que haya iniciado bien
        if not verificar_servidor():
            sys.exit(1)

        print(color("💡 Cancela la selección de archivos en cualquier momento para salir.\n", "cyan"))

        # 3. Ciclo principal
        while True:
            ruta = pedir_ruta_imagen()
            
            if not ruta:
                # Si cierra la ventana sin elegir nada, preguntamos si quiere salir
                print(color("¿Deseas salir del programa? (s/n)", "azul"))
                resp = input(color("   > ", "bold")).strip().lower()
                if resp in ("s", "si", "y", "yes"):
                    print(color("\nHasta luego! ♻️\n", "verde"))
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

    except KeyboardInterrupt:
        print(color("\nCerrando aplicación de forma segura...", "amarillo"))
    finally:
        # 4. Apagar el servidor al terminar
        if servidor:
            print(color("\nApagando el servidor Uvicorn...", "cyan"))
            servidor.terminate()

if __name__ == "__main__":
    main()