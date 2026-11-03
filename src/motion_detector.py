import cv2


class MotionDetector:
    """Detecta movimiento comparando imágenes consecutivas."""

    def __init__(self, umbral=20):
        self.umbral = umbral
        self.frame_anterior = None

    def detectar(self, frame):
        """Devuelve la cantidad de movimiento y la imagen procesada."""

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gris = cv2.GaussianBlur(gris, (21, 21), 0)

        if self.frame_anterior is None:
            self.frame_anterior = gris
            return 0, frame

        diferencia = cv2.absdiff(self.frame_anterior, gris)
        _, mascara = cv2.threshold(
            diferencia,
            self.umbral,
            255,
            cv2.THRESH_BINARY
        )

        mascara = cv2.dilate(mascara, None, iterations=2)
        contornos, _ = cv2.findContours(
            mascara,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        cantidad_movimiento = 0

        for contorno in contornos:
            area = cv2.contourArea(contorno)

            if area > 500:
                cantidad_movimiento += int(area)

                x, y, ancho, alto = cv2.boundingRect(contorno)
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + ancho, y + alto),
                    (0, 255, 0),
                    2
                )

        self.frame_anterior = gris

        return cantidad_movimiento, frame
