
import cv2
import mediapipe as mp
from pathlib import Path


class detectarpose:
    def __init__(self):
        # Buscar el modelo dentro de la carpeta assets/models
        ruta_modelo = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "models"
            / "hand_landmarker.task"
        )

        self.mp_vision = mp.tasks.vision

        # Configurar el detector de manos
        opciones = self.mp_vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(ruta_modelo)
            ),
            running_mode=self.mp_vision.RunningMode.VIDEO,
            num_hands=2
        )

        # Crear el detector
        self.detector = self.mp_vision.HandLandmarker.create_from_options(
            opciones
        )

    def detectar(self, frame, tiempo_ms):
        # Convertir el frame de OpenCV a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        imagen = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        # Detectar las manos en el video
        resultado = self.detector.detect_for_video(
            imagen,
            tiempo_ms
        )

        return resultado

    def cerrar(self):
        # Cerrar el detector
        self.detector.close()
