
import cv2

from src.video_source import fuentevideo
from src.motion_detector import detector_de_movimiento
from src.config import UMBRAL_MOVIMIENTO, PUNTOS_POR_MOVIMIENTO


def main():
    print("==============================")
    print("       CONTADOR DE AURA")
    print("==============================")

    video = fuentevideo()
    detector = detector_de_movimiento(UMBRAL_MOVIMIENTO)

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

            puntos = detector.puntos * PUNTOS_POR_MOVIMIENTO

            cv2.putText(
                frame,
                f"AURA: {puntos}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2
            )

            cv2.imshow("CONTADOR DE AURA", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        video.cerrar_camara()
        cv2.destroyAllWindows()
        print("Prueba finalizada.")


if __name__ == "__main__":
    main()
