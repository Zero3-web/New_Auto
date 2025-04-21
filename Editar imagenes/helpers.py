import os
import shutil
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont  # Correct imports
from utils import wrap_text, check_disk_space, analyze_image_clarity

def log_message(message):
    """Registra un mensaje en el archivo de log."""
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def add_text_to_images(folder, lines, progress_var, progress_bar, font_name, font_size):
    output_folder = os.path.join(folder, "Resultados")  # Carpeta de salida
    os.makedirs(output_folder, exist_ok=True)  # Asegurarse de que la carpeta exista

    images = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total_images = len(images)
    log_message(f"Total de imágenes encontradas: {total_images}")

    # Dimensiones estándar para Instagram/Facebook (4:5 aspecto vertical)
    target_width = 1080
    target_height = 1350

    for i, filename in enumerate(images):
        if i >= len(lines):
            break  # Si no hay más líneas, dejamos de procesar imágenes

        image_path = os.path.join(folder, filename)
        text = lines[i].strip()  # Obtenemos la línea correspondiente
        try:
            log_message(f"Procesando imagen: {filename}")
            with Image.open(image_path) as img:
                # Redimensionar la imagen a las dimensiones estándar usando LANCZOS
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

                # Convertir a RGBA para soportar transparencias
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                # Crear una capa para el fondo semitransparente
                overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)

                # Configurar color del texto
                text_color = "white"

                draw = ImageDraw.Draw(img)
                # Adjusted margins for text positioning
                margin_x = int(img.width * 0.05)  # 5% margin from the sides
                margin_y = int(img.height * 0.05)  # 5% margin from the top and bottom

                # Ensure the font is initialized before use
                try:
                    font = ImageFont.truetype(font_name, font_size)
                except IOError:
                    font = ImageFont.load_default()  # Use a default font if the specified font is not found

                # Dividing the text into lines with adjusted max width
                max_width = img.width - 2 * margin_x
                wrapped_text = wrap_text(text, font, max_width, draw)

                # Calculate total text height
                text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text) + (len(wrapped_text) - 1) * 5
                position = (margin_x, (img.height - text_height) // 2)

                # Draw semi-transparent black background
                background_bbox = (
                    margin_x,
                    position[1] - 20,
                    img.width - margin_x,
                    position[1] + text_height + 20
                )
                overlay_draw.rectangle(background_bbox, fill=(0, 0, 0, 120))

                # Combine the overlay with the original image
                img = Image.alpha_composite(img, overlay)

                # Draw text line by line with adjusted margins
                draw = ImageDraw.Draw(img)
                y_offset = position[1]
                for line in wrapped_text:
                    line_width = draw.textbbox((0, 0), line, font=font)[2]
                    x_offset = (img.width - line_width) // 2
                    draw.text((x_offset, y_offset), line, font=font, fill=text_color)
                    y_offset += draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] + 5

                # Ensure the logo font is initialized before use
                logo_font_size = int(img.width * 0.03)
                try:
                    logo_font = ImageFont.truetype(font_name, logo_font_size)
                except IOError:
                    logo_font = ImageFont.load_default()  # Use a default font if the specified font is not found

                # Draw the logo "@emotivaX" at the bottom with adjusted margins
                logo_text = "@emotivaX"
                logo_width, logo_height = draw.textbbox((0, 0), logo_text, font=logo_font)[2:]
                logo_position = ((img.width - logo_width) // 2, img.height - logo_height - margin_y)
                draw.text(logo_position, logo_text, font=logo_font, fill="white")

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

def process_images(progress_var, progress_bar, folder, font, font_size):
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
        output_folder = add_text_to_images(folder, lines, progress_var, progress_bar, font, font_size)
        messagebox.showinfo("Proceso completado", f"Las imágenes editadas se guardaron en: {output_folder}")
    except Exception as e:
        log_message(f"Error durante el procesamiento: {e}")
        messagebox.showerror("Error", f"Hubo un problema al procesar las imágenes: {e}")
