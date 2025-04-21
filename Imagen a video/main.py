import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

# Bloqueo para sincronizar el acceso a recursos compartidos
lock = threading.Lock()

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)

def create_video_thread():
    # Ejecutar la creación de videos en un hilo separado
    thread = threading.Thread(target=create_videos_in_parallel)
    thread.daemon = True  # Permitir que el hilo se cierre al cerrar la aplicación
    thread.start()

def create_videos_in_parallel():
    try:
        folder = folder_path.get()
        duration = duration_var.get()

        if not folder:
            messagebox.showerror("Error", "Por favor selecciona una carpeta.")
            return

        if not duration.isdigit() or int(duration) <= 0:
            messagebox.showerror("Error", "Por favor ingresa una duración válida en segundos.")
            return

        duration = int(duration)
        images = [img for img in os.listdir(folder) if img.endswith((".png", ".jpg", ".jpeg"))]
        if not images:
            messagebox.showerror("Error", "No se encontraron imágenes en la carpeta seleccionada.")
            return

        images.sort()  # Ordenar las imágenes alfabéticamente

        # Configurar la barra de progreso
        progress_bar["maximum"] = len(images)
        progress_bar["value"] = 0
        progress_label.config(text="Procesando videos...")
        root.update()

        # Dividir las imágenes en lotes para procesarlas en paralelo
        num_threads = min(4, len(images))  # Usar un máximo de 4 hilos o menos si hay pocas imágenes
        batches = [images[i::num_threads] for i in range(num_threads)]
        threads = []

        for batch in batches:
            thread = threading.Thread(target=process_batch, args=(batch, folder, duration))
            threads.append(thread)
            thread.start()

        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()

        progress_label.config(text="Videos creados exitosamente.")
        root.update()
        messagebox.showinfo("Éxito", "Videos creados exitosamente en la carpeta seleccionada.")
    except Exception as e:
        progress_label.config(text="Error durante el procesamiento.")
        root.update()
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

def process_batch(batch, folder, duration):
    for image in batch:
        img_path = os.path.join(folder, image)
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"Advertencia: No se pudo leer la imagen {image}.")
            continue  # Saltar si no se puede leer la imagen

        # Validar dimensiones de la imagen
        height, width, layers = frame.shape
        if height == 0 or width == 0:
            print(f"Advertencia: La imagen {image} tiene dimensiones inválidas.")
            continue

        video_name = os.path.join(folder, f"{os.path.splitext(image)[0]}_video.avi")
        out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))

        try:
            # Escribir el mismo frame varias veces para crear un video con la duración especificada
            for _ in range(30 * duration):  # 30 fps * duración en segundos
                out.write(frame)
        finally:
            out.release()  # Asegurar que el archivo de video se cierre correctamente

        # Actualizar la barra de progreso de forma segura
        with lock:
            progress_bar["value"] += 1
            root.update()

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Imágenes a Video")

folder_path = tk.StringVar()
duration_var = tk.StringVar(value="3")  # Duración predeterminada de 3 segundos

tk.Label(root, text="Selecciona una carpeta con imágenes:").pack(pady=10)
tk.Entry(root, textvariable=folder_path, width=50).pack(pady=5)
tk.Button(root, text="Seleccionar carpeta", command=select_folder).pack(pady=5)

tk.Label(root, text="Duración del video (en segundos):").pack(pady=10)
tk.Entry(root, textvariable=duration_var, width=10).pack(pady=5)

tk.Button(root, text="Crear videos", command=create_video_thread).pack(pady=20)

# Barra de progreso
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Etiqueta para mostrar el progreso
progress_label = tk.Label(root, text="")
progress_label.pack(pady=10)

root.mainloop()
