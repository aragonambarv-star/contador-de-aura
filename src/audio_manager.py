import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MUSICA = BASE_DIR / "assets" / "musica_fondo.mp3"


def iniciar_musica():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(str(MUSICA))
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)

        print("Musica iniciada correctamente")

    except Exception as error:
        print(f"Error al reproducir musica: {error}")


def detener_musica():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


def pausar_musica():
    if pygame.mixer.get_init():
        pygame.mixer.music.pause()


def reanudar_musica():
    if pygame.mixer.get_init():
        pygame.mixer.music.unpause()


if __name__ == "__main__":
    iniciar_musica()
    input("Presioná ENTER para salir...")
    