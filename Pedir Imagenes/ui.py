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
        self.root.geometry("900x750")
        self.root.resizable(False, False)

        # Intentar cargar el icono, manejar el error si no existe
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            self.root.iconbitmap(icon_path)
        except tk.TclError:
            print("Advertencia: No se encontró el archivo 'icon.ico'. Usando el icono predeterminado.")

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
        # Header Section
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill="x", pady=10)

        title_label = ttk.Label(
            header_frame, text="Buscador de Imágenes", font=("Segoe UI", 24, "bold"), anchor="center"
        )
        title_label.pack(pady=10)

        # Description
        description_label = ttk.Label(
            self.root,
            text="Ingrese una categoría, el número de imágenes y el tipo de orientación que desea buscar.\n"
                 "Seleccione también la fuente y el tamaño del texto para las imágenes procesadas.",
            font=("Segoe UI", 12),
            justify="center",
        )
        description_label.pack(pady=10)

        # Input Section
        input_frame = ttk.LabelFrame(self.root, text="Parámetros de Búsqueda", padding=(10, 10))
        input_frame.pack(pady=20, padx=20, fill="x")

        # Input for Category
        category_label = ttk.Label(input_frame, text="Categoría:", font=("Segoe UI", 10))
        category_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.category_entry = ttk.Entry(input_frame, width=40)
        self.category_entry.grid(row=0, column=1, padx=5, pady=5)

        # Input for Number of Images
        num_label = ttk.Label(input_frame, text="Número de imágenes:", font=("Segoe UI", 10))
        num_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.num_entry = ttk.Entry(input_frame, width=10)
        self.num_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Orientation Selection
        orientation_label = ttk.Label(input_frame, text="Orientación:", font=("Segoe UI", 10))
        orientation_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        self.orientation_var = tk.StringVar(value="horizontal")
        orientation_frame = ttk.Frame(input_frame)
        orientation_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        horizontal_radio = ttk.Radiobutton(
            orientation_frame, text="Horizontal", variable=self.orientation_var, value="horizontal"
        )
        horizontal_radio.pack(side="left", padx=5)

        vertical_radio = ttk.Radiobutton(
            orientation_frame, text="Vertical", variable=self.orientation_var, value="vertical"
        )
        vertical_radio.pack(side="left", padx=5)

        # Font Selection
        font_label = ttk.Label(input_frame, text="Fuente:", font=("Segoe UI", 10))
        font_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")

        self.font_var = tk.StringVar(value="arial.ttf")
        font_dropdown = ttk.Combobox(input_frame, textvariable=self.font_var, state="readonly", width=37)
        font_dropdown["values"] = ["arial.ttf", "times.ttf", "courier.ttf"]  # Add more font options as needed
        font_dropdown.grid(row=3, column=1, padx=5, pady=5)

        # Font Size Selection
        font_size_label = ttk.Label(input_frame, text="Tamaño de fuente:", font=("Segoe UI", 10))
        font_size_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")

        self.font_size_var = tk.IntVar(value=20)
        font_size_spinbox = ttk.Spinbox(input_frame, from_=10, to=100, textvariable=self.font_size_var, width=10)
        font_size_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Process Button
        self.process_button = ttk.Button(self.root, text="Procesar", command=self.process_all)
        self.process_button.pack(pady=20)

        # Progress Bar
        self.progress_var = tk.IntVar()
        self.progress_bar = Progressbar(self.root, orient="horizontal", length=600, mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(pady=10)

        # Status Label
        self.status_label = ttk.Label(self.root, text="", font=("Segoe UI", 10), anchor="center")
        self.status_label.pack(pady=5)

        # Image Display Section
        self.image_frame = ttk.LabelFrame(self.root, text="Imágenes Descargadas", padding=(10, 10))
        self.image_frame.pack(pady=20, padx=20, fill="both", expand=True)

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

        # Footer Section
        footer_frame = ttk.Frame(self.root, style="Footer.TFrame")
        footer_frame.pack(fill="x", pady=10)

        footer_label = ttk.Label(
            footer_frame, text="Buscador de Imágenes - Versión 1.0 | Desarrollado por GitHub Copilot",
            font=("Segoe UI", 9), anchor="center"
        )
        footer_label.pack(pady=5)

    def process_all(self):
        """Realiza la búsqueda, descarga y procesamiento de imágenes."""
        query = self.category_entry.get()
        num_images = self.num_entry.get()
        orientation = self.orientation_var.get()
        font = self.font_var.get()
        font_size = self.font_size_var.get()

        if not query:
            messagebox.showerror("Error", "Por favor, ingrese una categoría.")
            return

        if not num_images.isdigit() or int(num_images) <= 0:
            messagebox.showerror("Error", "Por favor, ingrese un número válido de imágenes.")
            return

        num_images = int(num_images)
        self.status_label.config(text="Buscando imágenes...")

        # Iniciar un hilo para evitar que la UI se congele
        thread = threading.Thread(target=self._process_all_background, args=(query, num_images, orientation, font, font_size))
        thread.start()

    def _process_all_background(self, query, num_images, orientation, font, font_size):
        """Lógica de procesamiento en un hilo separado."""
        try:
            # Buscar imágenes
            self.photos = PexelsAPI.fetch_images(query, per_page=num_images, orientation=orientation)
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
            process_images(self.progress_var, self.progress_bar, download_folder, font, font_size)

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
