import requests
import os

class PexelsAPI:
    BASE_URL = "https://api.pexels.com/v1/search"
    API_KEY = "1ZF4LecyKsuchp1BB90NjfwL9jvqnCJAlRgrFeWDQVqM51XbLK1dtGK1"  # Reemplaza con tu clave de API de Pexels
    ID_FILE = "downloaded_ids.txt"

    @staticmethod
    def fetch_images(query, per_page=5):
        headers = {"Authorization": PexelsAPI.API_KEY}
        params = {"query": query, "per_page": per_page}
        response = requests.get(PexelsAPI.BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            photos = response.json().get("photos", [])
            return PexelsAPI.filter_new_images(photos)
        else:
            print(f"Error en la API: {response.status_code} - {response.text}")
            return []

    @staticmethod
    def filter_new_images(photos):
        # Asegurarse de que el archivo de IDs existe
        if not os.path.exists(PexelsAPI.ID_FILE):
            open(PexelsAPI.ID_FILE, "w").close()

        # Leer IDs ya descargados
        try:
            with open(PexelsAPI.ID_FILE, "r") as file:
                downloaded_ids = set(file.read().splitlines())
        except Exception as e:
            print(f"Error al leer el archivo de IDs: {e}")
            downloaded_ids = set()

        # Filtrar imágenes nuevas
        new_photos = [photo for photo in photos if str(photo["id"]) not in downloaded_ids]
        return new_photos

    @staticmethod
    def save_image_ids(photos):
        try:
            with open(PexelsAPI.ID_FILE, "a") as file:
                for photo in photos:
                    file.write(f"{photo['id']}\n")
            print(f"Guardados {len(photos)} IDs en {PexelsAPI.ID_FILE}")
        except Exception as e:
            print(f"Error al guardar IDs en el archivo: {e}")
