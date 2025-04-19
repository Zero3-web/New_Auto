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

        self.search_button = ttk.Button(button_frame, text="Buscar", command=self.search_images)
        self.search_button.grid(row=0, column=0, padx=10)

        self.clear_button = ttk.Button(button_frame, text="Limpiar", command=self.clear_images)
        self.clear_button.grid(row=0, column=1, padx=10)

        # Botón de descargar (inicialmente oculto)
        self.download_button = ttk.Button(self.root, text="Descargar", command=self.download_images)
        self.download_button.pack(pady=10)
        self.download_button.pack_forget()

        # Botón para procesar imágenes
        self.process_button = ttk.Button(self.root, text="Procesar Imágenes", command=self.start_processing)
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

    def search_images(self):
        """Busca imágenes basadas en la categoría y el número ingresados."""
        query = self.category_entry.get()
        num_images = self.num_entry.get()

        if not query:
            messagebox.showerror("Error", "Por favor, ingrese una categoría.")
            return

        if not num_images.isdigit() or int(num_images) <= 0:
            messagebox.showerror("Error", "Por favor, ingrese un número válido de imágenes.")
            return

        num_images = int(num_images)
        self.status_label.config(text="Cargando imágenes...")

        try:
            self.photos = PexelsAPI.fetch_images(query, per_page=num_images)
        except Exception as e:
            self.status_label.config(text="")
            messagebox.showerror("Error", f"Error al buscar imágenes: {e}")
            return

        if not self.photos:
            self.status_label.config(text="")
            messagebox.showinfo("Sin resultados", "No se encontraron imágenes nuevas para esta categoría.")
            return

        # Guardar IDs de imágenes descargadas
        try:
            PexelsAPI.save_image_ids(self.photos)
        except Exception as e:
            self.status_label.config(text="")
            messagebox.showerror("Error", f"Error al guardar IDs: {e}")
            return

        # Limpiar imágenes anteriores
        self.clear_images()

        # Mostrar imágenes
        for photo in self.photos:
            img_url = photo["src"]["medium"]
            try:
                response = requests.get(img_url)
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((150, 150))
                img_tk = ImageTk.PhotoImage(img)

                label = ttk.Label(self.scrollable_frame, image=img_tk)
                label.image = img_tk
                label.pack(side="left", padx=10, pady=10)
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")

        self.status_label.config(text="Imágenes cargadas exitosamente.")
        self.download_button.pack()  # Mostrar el botón de descarga

    def download_images(self):
        """Descarga las imágenes buscadas a una carpeta seleccionada por el usuario."""
        if not self.photos:
            messagebox.showerror("Error", "No hay imágenes para descargar.")
            return

        # Seleccionar carpeta de destino
        folder = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if not folder:
            return

        # Crear carpeta "descargas" si no existe
        download_folder = os.path.join(folder, "descargas")
        os.makedirs(download_folder, exist_ok=True)

        # Descargar imágenes
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

        messagebox.showinfo("Descarga completa", f"Las imágenes se han descargado en: {download_folder}")

    def clear_images(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="")
        self.download_button.pack_forget()

    def change_theme(self, theme):
        self.theme = theme
        if theme == "dark":
            self.root.tk_setPalette(background="#2e2e2e", foreground="#ffffff")
        else:
            self.root.tk_setPalette(background="#ffffff", foreground="#000000")

    def show_about(self):
        messagebox.showinfo("Acerca de", "Buscador de Imágenes\nVersión 1.0\nDesarrollado por GitHub Copilot")

    def start_processing(self):
        """Inicia el procesamiento de imágenes en un hilo separado."""
        try:
            folder = filedialog.askdirectory(title="Seleccionar carpeta de imágenes")  # Seleccionar carpeta
            if not folder:
                messagebox.showerror("Error", "No se seleccionó ninguna carpeta.")
                return
            thread = threading.Thread(target=process_images, args=(self.progress_var, self.progress_bar, folder))
            thread.start()
        except Exception as e:
            with open("log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"Error al iniciar el procesamiento: {e}\n")
            messagebox.showerror("Error", f"Error al iniciar el procesamiento: {e}")

    def run(self):
        self.root.mainloop()
