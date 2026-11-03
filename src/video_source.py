import cv2

from src.config import CAMARA_ID, ANCHO_CAMARA, ALTO_CAMARA


class VideoSource:
    """Gestiona la captura de imágenes de la cámara."""

    def __init__(self):
        self.camara = None

    def abrir_camara(self):
        """Intenta abrir la cámara predeterminada."""
        self.camara = cv2.VideoCapture(CAMARA_ID)

        if not self.camara.isOpened():
            self.camara.release()
            self.camara = None
            print("No se pudo abrir la cámara.")
            return False

        self.camara.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO_CAMARA)
        self.camara.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO_CAMARA)

        print("Cámara abierta correctamente.")
        return True

    def obtener_frame(self):
        """Devuelve una imagen de la cámara."""
        if self.camara is None:
            return False, None

        return self.camara.read()

    def cerrar_camara(self):
        """Libera la cámara cuando terminamos."""
        if self.camara is not None:
            self.camara.release()
            self.camara = None
