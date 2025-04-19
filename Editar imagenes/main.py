import os
import threading
from tkinter import Tk, Label, Button, messagebox, StringVar
from tkinter.ttk import Progressbar
from helpers import process_images

def start_processing(progress_var, progress_bar):
    """Inicia el procesamiento de imágenes en un hilo separado."""
    try:
        thread = threading.Thread(target=process_images, args=(progress_var, progress_bar))
        thread.start()
    except Exception as e:
        with open("log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Error al iniciar el procesamiento: {e}\n")
        messagebox.showerror("Error", f"Error al iniciar el procesamiento: {e}")

def main():
    root = Tk()
    root.title("Editor de Imágenes en Lote")
    root.geometry("500x250")
    root.resizable(False, False)

    progress_var = StringVar()
    progress_var.set(0)

    Label(root, text="Procesar imágenes desde la carpeta fija:").pack(pady=10)
    Label(root, text=r"C:\Users\burga\Desktop\descargas", fg="blue").pack(pady=5)

    progress_bar = Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_var)
    progress_bar.pack(pady=10)

    Button(root, text="Procesar Imágenes", command=lambda: start_processing(progress_var, progress_bar), bg="green", fg="white").pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
