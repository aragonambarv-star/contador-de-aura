import cv2
import mediapipe as mp 

class detector_de_movimiento:
    """Detecta movimiento comparando imágenes consecutivas."""

    def __init__(self, umbral=20):
        self.puntos = 0
        self.ultimo_estado = {}
        self.umbral = umbral
        self.frame_anterior = None
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.alturas_anteriores = {}
        self.umbral_muñeca = 0.015

    def detectar(self, frame):
        """Devuelve la cantidad de movimiento y la imagen procesada."""

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gris = cv2.GaussianBlur(gris, (21, 21), 0)
        # Detectar manos con MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado = self.hands.process(rgb)

        if resultado.multi_hand_landmarks:

            for landmarks, lado in zip(
                resultado.multi_hand_landmarks,
                resultado.multi_handedness
            ):

                nombre = lado.classification[0].label

                if nombre == "Left":
                    nombre = "Izquierda"
                else:
                    nombre = "Derecha"

                muñeca = landmarks.landmark[0]

                indice = landmarks.landmark[8]
                medio = landmarks.landmark[12]
                anular = landmarks.landmark[16]
                meñique = landmarks.landmark[20]

                # Comprobar orientación de la palma
                palma_arriba = (
                    indice.y < muñeca.y and
                    medio.y < muñeca.y and
                    anular.y < muñeca.y and
                    meñique.y < muñeca.y
                )

                if palma_arriba:

                    altura_actual = muñeca.y

                    if nombre in self.alturas_anteriores:

                        diferencia = (
                            self.alturas_anteriores[nombre] - altura_actual
                        )

                        if diferencia > self.umbral_muñeca:
                            movimiento_muñeca = "SUBIENDO"

                        elif diferencia < -self.umbral_muñeca:
                            movimiento_muñeca = "BAJANDO"

                        else:
                            movimiento_muñeca = "QUIETA"
                        if movimiento_muñeca != "QUIETA":
                            if self.ultimo_estado.get(nombre) != movimiento_muñeca:
                                self.puntos += 1

                        self.ultimo_estado[nombre] = movimiento_muñeca
                        
                        cv2.putText(
                            frame,
                            f"{nombre}: {movimiento_muñeca}",
                            (10, 60 if nombre == "Izquierda" else 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
                        )

                    self.alturas_anteriores[nombre] = altura_actual

                else:
                    self.alturas_anteriores.pop(nombre, None)

                self.mp_drawing.draw_landmarks(
                    frame,
                    landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

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
