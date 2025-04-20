import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import io
import requests
import os
from pexels_api import PexelsAPI
import threading
from tkinter.ttk import Progressbar
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Editar imagenes")))
from helpers import process_images

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Buscador de Imágenes")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        self.photos = []  # Almacena las imágenes obtenidas en la búsqueda
        self.theme = "light"  # Tema inicial
        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        # Menú superior
        menu_bar = tk.Menu(self.root)

        # Menú Archivo
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.root.quit)
        menu_bar.add_cascade(label="Archivo", menu=file_menu)

        # Menú Ayuda
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        menu_bar.add_cascade(label="Ayuda", menu=help_menu)

        # Menú Tema
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Tema Claro", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Tema Oscuro", command=lambda: self.change_theme("dark"))
        menu_bar.add_cascade(label="Tema", menu=theme_menu)

        self.root.config(menu=menu_bar)

    def create_widgets(self):
        # Título
        title_label = ttk.Label(
            self.root, text="Buscador de Imágenes", font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=10)

        # Descripción
        description_label = ttk.Label(
            self.root,
            text="Ingrese una categoría y el número de imágenes que desea buscar.\n"
                 "Las imágenes ya descargadas no se volverán a mostrar.",
            font=("Helvetica", 12),
            justify="center",
        )
        description_label.pack(pady=10)

        # Frame para los inputs
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=20)

        # Input para categoría
        category_label = ttk.Label(input_frame, text="Categoría:")
        category_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.category_entry = ttk.Entry(input_frame, width=40)
        self.category_entry.grid(row=0, column=1, padx=5, pady=5)

        # Input para número de imágenes
        num_label = ttk.Label(input_frame, text="Número de imágenes:")
        num_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.num_entry = ttk.Entry(input_frame, width=10)
        self.num_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Botones
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        # Botón único para procesar (buscar, descargar y editar)
        self.process_button = ttk.Button(self.root, text="Procesar", command=self.process_all)
        self.process_button.pack(pady=10)

        # Barra de progreso
        self.progress_var = tk.IntVar()
        self.progress_bar = Progressbar(self.root, orient="horizontal", length=400, mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(pady=10)

        # Área de estado
        self.status_label = ttk.Label(self.root, text="", font=("Helvetica", 10))
        self.status_label.pack(pady=5)

        # Frame para mostrar imágenes
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.pack(pady=20, fill="both", expand=True)

        # Scrollbar para imágenes
        self.canvas = tk.Canvas(self.image_frame)
        self.scrollbar = ttk.Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def process_all(self):
        """Realiza la búsqueda, descarga y procesamiento de imágenes."""
        query = self.category_entry.get()
        num_images = self.num_entry.get()

        if not query:
            messagebox.showerror("Error", "Por favor, ingrese una categoría.")
            return

        if not num_images.isdigit() or int(num_images) <= 0:
            messagebox.showerror("Error", "Por favor, ingrese un número válido de imágenes.")
            return

        num_images = int(num_images)
        self.status_label.config(text="Buscando imágenes...")

        # Iniciar un hilo para evitar que la UI se congele
        thread = threading.Thread(target=self._process_all_background, args=(query, num_images))
        thread.start()

    def _process_all_background(self, query, num_images):
        """Lógica de procesamiento en un hilo separado."""
        try:
            # Buscar imágenes
            self.photos = PexelsAPI.fetch_images(query, per_page=num_images)
            if not self.photos:
                self.status_label.config(text="")
                messagebox.showinfo("Sin resultados", "No se encontraron imágenes nuevas para esta categoría.")
                return

            # Guardar IDs de imágenes descargadas
            PexelsAPI.save_image_ids(self.photos)

            # Descargar imágenes
            self.status_label.config(text="Descargando imágenes...")
            download_folder = os.path.join(os.path.dirname(__file__), "../descargas")
            download_folder = os.path.abspath(download_folder)  # Convertir a ruta absoluta
            os.makedirs(download_folder, exist_ok=True)

            for photo in self.photos:
                img_url = photo["src"]["original"]
                img_name = f"{photo['id']}.jpg"
                img_path = os.path.join(download_folder, img_name)
                try:
                    response = requests.get(img_url)
                    with open(img_path, "wb") as img_file:
                        img_file.write(response.content)
                except Exception as e:
                    print(f"Error al descargar la imagen {img_name}: {e}")

            # Procesar imágenes
            self.status_label.config(text="Procesando imágenes...")
            process_images(self.progress_var, self.progress_bar, download_folder)

            # Actualizar estado
            self.status_label.config(text="Proceso completado.")
            messagebox.showinfo("Completado", f"Las imágenes procesadas se guardaron en: {download_folder}")

        except Exception as e:
            with open("log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"Error durante el procesamiento: {e}\n")
            messagebox.showerror("Error", f"Error durante el procesamiento: {e}")

    def clear_images(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="")

    def change_theme(self, theme):
        self.theme = theme
        if theme == "dark":
            self.root.tk_setPalette(background="#2e2e2e", foreground="#ffffff")
        else:
            self.root.tk_setPalette(background="#ffffff", foreground="#000000")

    def show_about(self):
        messagebox.showinfo("Acerca de", "Buscador de Imágenes\nVersión 1.0\nDesarrollado por GitHub Copilot")

    def run(self):
        self.root.mainloop()
