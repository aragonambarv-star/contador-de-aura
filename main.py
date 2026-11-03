import cv2

from src.video_source import VideoSource
from src.motion_detector import MotionDetector
from src.config import UMBRAL_MOVIMIENTO


def main():
    print("==============================")
    print("       CONTADOR DE AURA")
    print("==============================")

    video = VideoSource()
    detector = MotionDetector(UMBRAL_MOVIMIENTO)

    if not video.abrir_camara():
        print("Revisá que la cámara esté conectada y disponible.")
        return

    print("Presioná Q para cerrar la prueba.")

    try:
        while True:
            lectura_correcta, frame = video.obtener_frame()

            if not lectura_correcta:
                print("No se pudo obtener la imagen de la cámara.")
                break

            cantidad_movimiento, frame = detector.detectar(frame)

            cv2.putText(
                frame,
                f"Movimiento: {cantidad_movimiento}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow("Contador de Aura - Prueba de movimiento", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        video.cerrar_camara()
        cv2.destroyAllWindows()
        print("Prueba finalizada.")


if __name__ == "__main__":
    main()
