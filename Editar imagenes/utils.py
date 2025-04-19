import cv2
import numpy as np
import shutil

def wrap_text(text, font, max_width, draw):
    """Divide el texto en líneas para que se ajuste al ancho máximo."""
    lines = []
    words = text.split()
    while words:
        line = words.pop(0)
        while words and draw.textbbox((0, 0), line + " " + words[0], font=font)[2] <= max_width:
            line += " " + words.pop(0)
        lines.append(line)
    return lines

def check_disk_space(folder):
    """Verifica si hay suficiente espacio en disco para procesar las imágenes."""
    total, used, free = shutil.disk_usage(folder)
    # Requiere al menos 100 MB de espacio libre
    if free < 100 * 1024 * 1024:
        raise Exception("Espacio en disco insuficiente para procesar las imágenes.")

def analyze_image_clarity(image_path):
    """Determina si una imagen es clara u oscura."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise Exception(f"No se pudo cargar la imagen: {image_path}")
    mean_brightness = np.mean(image)
    return mean_brightness < 128  # Devuelve True si la imagen es oscura
