class App:
    def __init__(self):
        self.text_margins = {"left": 0, "right": 0, "top": 0, "bottom": 0}

    def set_text_margins(self, left=0, right=0, top=0, bottom=0):
        """Configura los márgenes del texto."""
        self.text_margins = {"left": left, "right": right, "top": top, "bottom": bottom}

    def render_text(self, text):
        """Renderiza el texto con los márgenes configurados."""
        margins = self.text_margins
        # Aplica los márgenes al texto (esto depende de cómo se renderice el texto en tu aplicación)
        print(f"Rendering text with margins: {margins}")
        # ...lógica para renderizar el texto con márgenes...