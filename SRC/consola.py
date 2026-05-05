import os
import sys
import requests

SERVER_URL = "http://localhost:8000"

COLORES = {
    "verde":    "\033[92m",
    "amarillo": "\033[93m",
    "rojo":     "\033[91m",
    "azul":     "\033[94m",
    "cyan":     "\033[96m",
    "reset":    "\033[0m",
    "bold":     "\033[1m",
}

def color(texto, c):
    return f"{COLORES.get(c, '')}{texto}{COLORES['reset']}"

def banner():
    print(color("\n╔══════════════════════════════════╗", "verde"))
    print(color("║       ♻️  EcoCycle IA CLI          ║", "verde"))
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
        print(color("   Ejecuta: uvicorn SRC.server:app --reload\n", "cyan"))
        return False

def pedir_ruta_imagen():
    print(color("📂 Ingresa la ruta de la imagen a analizar:", "azul"))
    print(color("   (Ejemplo: C:/fotos/botella.jpg  o  ./imagenes/lata.png)\n", "cyan"))

    while True:
        ruta = input(color("   Ruta: ", "bold")).strip().strip('"').strip("'")

        if ruta.lower() in ("salir", "exit", "q"):
            print(color("\nHasta luego! ♻️\n", "verde"))
            sys.exit(0)

        if not os.path.exists(ruta):
            print(color(f"\n⚠️  No se encontró el archivo: {ruta}", "rojo"))
            print(color("   Intenta de nuevo o escribe 'salir' para cerrar.\n", "amarillo"))
            continue

        extension = os.path.splitext(ruta)[1].lower()
        if extension not in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"):
            print(color(f"\n⚠️  Formato no soportado: {extension}", "rojo"))
            print(color("   Usa: .jpg, .jpeg, .png, .webp\n", "amarillo"))
            continue

        return ruta

def mostrar_resultado(data: dict):
    clasificacion = data.get("clasificacion", "")

    # Color según clasificación
    if "Reciclable" in clasificacion:
        c_clasif = "verde"
    elif "Orgánico" in clasificacion:
        c_clasif = "amarillo"
    else:
        c_clasif = "rojo"

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

    if not verificar_servidor():
        sys.exit(1)

    print(color("💡 Escribe 'salir' en cualquier momento para cerrar.\n", "cyan"))

    while True:
        ruta = pedir_ruta_imagen()
        analizar_imagen(ruta)

        print(color("¿Analizar otra imagen? (Enter para continuar / 'salir' para cerrar)", "azul"))
        resp = input(color("   > ", "bold")).strip().lower()
        if resp in ("salir", "exit", "q"):
            print(color("\nHasta luego! ♻️\n", "verde"))
            break
        print()

if __name__ == "__main__":
    main()