import cv2
import time

from src.video_source import fuentevideo
from src.pose_detector import detectarpose


def main():
    video = fuentevideo()
    detector = detectarpose()

    if not video.abrir_camara():
        print("No se pudo abrir la cámara.")
        detector.cerrar()
        return

    print("Mostrá tus manos frente a la cámara.")
    print("Probá el movimiento Six Seven.")
    print("Presioná Q para salir.")

    inicio = time.monotonic()

    try:
        while True:
            lectura_correcta, frame = video.obtener_frame()

            if not lectura_correcta:
                print("No se pudo obtener la imagen.")
                break

            tiempo_ms = int((time.monotonic() - inicio) * 1000)

            resultado = detector.detectar(frame, tiempo_ms)

            if resultado.hand_landmarks:

                for numero, mano in enumerate(resultado.hand_landmarks):

                    # Dibujar los 21 puntos de la mano
                    for punto in mano:
                        x = int(punto.x * frame.shape[1])
                        y = int(punto.y * frame.shape[0])

                        cv2.circle(
                            frame,
                            (x, y),
                            5,
                            (0, 255, 0),
                            -1
                        )

                    # Obtener la posición de la muñeca
                    muñeca = mano[0]

                    x_muñeca = int(muñeca.x * frame.shape[1])
                    y_muñeca = int(muñeca.y * frame.shape[0])

                    # Destacar la muñeca en rojo
                    cv2.circle(
                        frame,
                        (x_muñeca, y_muñeca),
                        12,
                        (0, 0, 255),
                        -1
                    )

                    # Mostrar la posición vertical
                    cv2.putText(
                        frame,
                        f"Mano {numero + 1}: Y={muñeca.y:.2f}",
                        (10, 65 + numero * 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 0),
                        2
                    )

                cv2.putText(
                    frame,
                    f"Manos detectadas: {len(resultado.hand_landmarks)}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

            else:
                cv2.putText(
                    frame,
                    "No se detectan manos",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

            cv2.imshow("Prueba de manos - Six Seven", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        video.cerrar_camara()
        detector.cerrar()
        cv2.destroyAllWindows()
        print("Prueba finalizada.")


if __name__ == "__main__":
    main()
