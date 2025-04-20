import os
import shutil
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
from utils import wrap_text, check_disk_space, analyze_image_clarity

def log_message(message):
    """Registra un mensaje en el archivo de log."""
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def add_text_to_images(folder, lines, progress_var, progress_bar):
    output_folder = os.path.join(folder, "Resultados")  # Carpeta de salida
    os.makedirs(output_folder, exist_ok=True)  # Asegurarse de que la carpeta exista

    images = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total_images = len(images)
    log_message(f"Total de imágenes encontradas: {total_images}")

    for i, filename in enumerate(images):
        if i >= len(lines):
            break  # Si no hay más líneas, dejamos de procesar imágenes

        image_path = os.path.join(folder, filename)
        text = lines[i].strip()  # Obtenemos la línea correspondiente
        try:
            log_message(f"Procesando imagen: {filename}")
            with Image.open(image_path) as img:
                # Convertir a RGBA para soportar transparencias
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                # Crear una capa para el fondo semitransparente
                overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)

                # Analizar claridad de la imagen
                is_image_dark = analyze_image_clarity(image_path)

                # Configurar color del texto
                text_color = "white" if is_image_dark else "black"

                draw = ImageDraw.Draw(img)
                max_width = int(img.width * 0.6)  # Reducir el ancho máximo del texto al 60% del ancho de la imagen
                max_height = int(img.height * 0.15)  # El texto ocupará como máximo el 15% de la altura de la imagen

                # Ajustar dinámicamente el tamaño de la fuente
                font_size = 1
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()  # Usa una fuente predeterminada si no se encuentra arial.ttf

                while True:
                    wrapped_text = wrap_text(text, font, max_width, draw)
                    text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text) + (len(wrapped_text) - 1) * 5
                    if text_height > max_height or any(draw.textbbox((0, 0), line, font=font)[2] > max_width for line in wrapped_text):
                        break
                    font_size += 1
                    font = ImageFont.truetype("arial.ttf", font_size)
                font_size -= 1  # Reducir el tamaño para que no exceda los límites
                font = ImageFont.truetype("arial.ttf", font_size)

                # Dividir el texto en líneas si es necesario
                wrapped_text = wrap_text(text, font, max_width, draw)

                # Calcular el tamaño total del texto
                text_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in wrapped_text)
                text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text) + (len(wrapped_text) - 1) * 5
                position = ((img.width - text_width) // 2, (img.height - text_height) // 2)

                # Dibujar fondo negro semitransparente si el texto es blanco
                if text_color == "white":
                    padding = 40  # Aumentar el padding para centrar mejor el texto
                    background_bbox = (
                        position[0] - padding,
                        position[1] - padding,
                        position[0] + text_width + padding,
                        position[1] + text_height + padding
                    )
                    overlay_draw.rectangle(background_bbox, fill=(0, 0, 0, 80))  # Fondo negro más transparente

                # Combinar la capa de fondo con la imagen original
                img = Image.alpha_composite(img, overlay)

                # Dibujar texto línea por línea sobre la imagen combinada
                draw = ImageDraw.Draw(img)  # Redibujar sobre la imagen combinada
                y_offset = position[1]
                for line in wrapped_text:
                    line_width = draw.textbbox((0, 0), line, font=font)[2]
                    line_height = draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]
                    x_offset = (img.width - line_width) // 2
                    draw.text((x_offset, y_offset), line, font=font, fill=text_color)
                    y_offset += line_height + 5  # Espaciado entre líneas

                # Dibujar el logo "@emotivaX" un poco más arriba
                logo_font_size = int(img.width * 0.03)  # Tamaño de fuente proporcional al ancho de la imagen
                logo_font = ImageFont.truetype("arial.ttf", logo_font_size)
                logo_text = "@emotivaX"
                logo_width, logo_height = draw.textbbox((0, 0), logo_text, font=logo_font)[2:]
                logo_position = ((img.width - logo_width) // 2, img.height - logo_height - 50)  # 50px desde el borde inferior
                draw.text(logo_position, logo_text, font=logo_font, fill="white")  # Texto blanco para el logo

                # Guardar la imagen procesada
                img = img.convert("RGB")  # Convertir de nuevo a RGB para guardar como JPEG
                img.save(os.path.join(output_folder, filename))  # Guardar en la carpeta de salida

            # Actualizar barra de progreso
            progress_var.set((i + 1) / total_images * 100)
            progress_bar.update()

        except Exception as e:
            log_message(f"Error al procesar la imagen '{filename}': {e}")
            print(f"Error al procesar la imagen '{filename}': {e}")
            continue  # Continuar con la siguiente imagen
    return output_folder

def process_images(progress_var, progress_bar, folder):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    text_file = os.path.join(script_dir, "frases.txt")

    try:
        check_disk_space(folder)  # Verificar espacio en disco
    except Exception as e:
        log_message(f"Error de espacio en disco: {e}")
        messagebox.showerror("Error", str(e))
        return

    if not os.path.exists(folder):
        messagebox.showerror("Error", f"No se encontró la carpeta de imágenes en: {folder}")
        return

    if not os.path.exists(text_file):
        messagebox.showerror("Error", "No se encontró el archivo 'frases.txt' en el directorio del script.")
        return

    try:
        with open(text_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except Exception as e:
        log_message(f"Error al leer el archivo de texto: {e}")
        messagebox.showerror("Error", f"No se pudo leer el archivo de texto: {e}")
        return

    if not lines:
        messagebox.showerror("Error", "El archivo de texto está vacío.")
        return

    try:
        output_folder = add_text_to_images(folder, lines, progress_var, progress_bar)
        messagebox.showinfo("Proceso completado", f"Las imágenes editadas se guardaron en: {output_folder}")
    except Exception as e:
        log_message(f"Error durante el procesamiento: {e}")
        messagebox.showerror("Error", f"Hubo un problema al procesar las imágenes: {e}")
