import tkinter as tk
from tkinter import messagebox
import cv2
import json
import time
from pathlib import Path
from PIL import Image, ImageTk
from src.video_source import fuentevideo
from src.motion_detector import detector_de_movimiento
from src.config import UMBRAL_MOVIMIENTO, PUNTOS_POR_MOVIMIENTO
NEGRO = '#101510'
PANEL = '#202820'
AMARILLO = '#F2D51D'
VERDE = '#164B2B'
BLANCO = '#F4F4E8'
DURACION = 20
CUENTA = 3
BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / 'ranking_aura.json'
LOGO = BASE_DIR / 'assets' / 'logo_eico.png'
STEVE = BASE_DIR / 'assets' / 'steve_eico.png'

class ContadorAura:

    def __init__(self, root):
        self.root = root
        self.root.title('CONTADOR DE AURA | EICO N°1')
        self.root.geometry('1100x720')
        self.root.minsize(850, 600)
        self.root.configure(bg=NEGRO)
        self.root.protocol('WM_DELETE_WINDOW', self.cerrar)
        self.video = None
        self.detector = None
        self.after_id = None
        self.estado = 'inicio'
        self.puntos = 0
        self.jugador = ''
        self.pantalla_inicio()

    def texto(self, padre, contenido, color=BLANCO, tam=12, fondo=None):
        return tk.Label(padre, text=contenido, bg=fondo or NEGRO, fg=color, font=('Consolas', tam, 'bold'))

    def boton(self, padre, contenido, accion, color=AMARILLO):
        return tk.Button(padre, text=contenido, command=accion, bg=color, fg=NEGRO, activebackground=BLANCO, activeforeground=NEGRO, relief='flat', bd=0, font=('Consolas', 12, 'bold'), padx=22, pady=10, cursor='hand2')

    def limpiar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def encabezado(self, subtitulo=''):
        barra = tk.Frame(self.root, bg=VERDE, padx=18, pady=8)
        barra.pack(fill='x')
        try:
            logo = Image.open(LOGO).convert('RGBA')
            logo.thumbnail((58, 58), Image.Resampling.LANCZOS)
            pixeles = logo.load()
            for y in range(logo.height):
                for x in range(logo.width):
                    r, g, b, a = pixeles[x, y]
                    if r > 245 and g > 245 and (b > 245):
                        pixeles[x, y] = (r, g, b, 0)
            self.logo_img = ImageTk.PhotoImage(logo)
            tk.Label(barra, image=self.logo_img, bg=VERDE).pack(side='left', padx=(0, 12))
        except (FileNotFoundError, OSError):
            self.logo_img = None
        tk.Label(barra, text='CONTADOR DE AURA', bg=VERDE, fg=AMARILLO, font=('Consolas', 22, 'bold')).pack(side='left')
        tk.Label(barra, text='EICO N°1  ·  CALETA OLIVIA', bg=VERDE, fg=BLANCO, font=('Consolas', 10, 'bold')).pack(side='right')
        if subtitulo:
            self.texto(self.root, subtitulo, BLANCO, 10).pack(pady=(8, 0))

    def pantalla_inicio(self):
        self.estado = 'inicio'
        self.limpiar()
        self.encabezado('4° AÑO · INFORMÁTICA PROFESIONAL Y PERSONAL')
        centro = tk.Frame(self.root, bg=PANEL, padx=45, pady=35)
        centro.pack(expand=True, padx=60, pady=25)
        try:
            personaje = Image.open(STEVE).convert('RGBA')
            personaje.thumbnail((175, 205), Image.Resampling.LANCZOS)
            self.steve_img = ImageTk.PhotoImage(personaje)
            print("IMAGEN CARGADA:", personaje.size)
            print("RUTA:", STEVE)
            tk.Label(centro, image=self.steve_img, bg=PANEL).pack(pady=5)
        except (FileNotFoundError, OSError):
            self.steve_img = None
            self.texto(centro, 'No se encontró assets/steve_eico.png', AMARILLO, 9, PANEL).pack()
        self.texto(centro, 'PREPARATE PARA JUGAR', AMARILLO, 23, PANEL).pack(pady=(5, 12))
        self.texto(centro, 'Movete frente a la cámara y sumá puntos de aura.', BLANCO, 11, PANEL).pack(pady=5)
        self.texto(centro, 'Ingresá tu nombre para comenzar', BLANCO, 11, PANEL).pack(pady=(22, 8))
        self.nombre = tk.Entry(centro, font=('Consolas', 15), justify='center', relief='flat', width=24, bg=BLANCO, fg=NEGRO)
        self.nombre.pack(ipady=8, pady=10)
        self.nombre.bind('<Return>', lambda event: self.iniciar())
        self.boton(centro, '▶  START', self.iniciar).pack(pady=10)
        self.texto(centro, '20 SEGUNDOS  ·  3 SEGUNDOS DE PREPARACIÓN', VERDE, 10, PANEL).pack(pady=12)
        self.nombre.focus_set()

    def iniciar(self):
        self.jugador = self.nombre.get().strip()[:22]
        if not self.jugador:
            messagebox.showwarning('Nombre', 'Escribí tu nombre para jugar.')
            return
        try:
            self.video = fuentevideo()
            if not self.video.abrir_camara():
                self.video = None
                messagebox.showerror('Cámara', 'No se pudo abrir la cámara.')
                return
            self.detector = detector_de_movimiento(UMBRAL_MOVIMIENTO)
        except Exception as error:
            if self.video:
                try:
                    self.video.cerrar_camara()
                except Exception:
                    pass
                self.video = None
            messagebox.showerror('Error al iniciar', str(error))
            return
        self.puntos = 0
        self.estado = 'cuenta'
        self.inicio_cuenta = time.monotonic()
        self.mensaje_inicio_hasta = 0
        self.limpiar()
        self.encabezado('PARTIDA EN CURSO')
        panel = tk.Frame(self.root, bg=NEGRO)
        panel.pack(fill='both', expand=True, padx=28, pady=15)
        datos = tk.Frame(panel, bg=PANEL, padx=15, pady=10)
        datos.pack(fill='x', pady=(0, 10))
        self.texto(datos, f'JUGADOR: {self.jugador.upper()}', BLANCO, 11, PANEL).pack(side='left')
        self.reloj = self.texto(datos, '00:20', AMARILLO, 17, PANEL)
        self.reloj.pack(side='right')
        self.marcador = self.texto(datos, 'AURA: 0', VERDE, 15, PANEL)
        self.marcador.pack(side='right', padx=20)
        self.vista = tk.Label(panel, bg='#090D09')
        self.vista.pack(fill='both', expand=True)
        self.actualizar()

    def actualizar(self):
        if not self.video:
            return
        try:
            ok, frame = self.video.obtener_frame()
        except Exception:
            self.terminar(error=True)
            return
        if not ok or frame is None:
            self.terminar(error=True)
            return

        ahora = time.monotonic()
        texto_superpuesto = None

        if self.estado == 'cuenta':
            falta = CUENTA - int(ahora - self.inicio_cuenta)
            if falta > 0:
                texto_superpuesto = str(falta)
            else:
                self.estado = 'jugando'
                self.inicio_partida = ahora
                self.mensaje_inicio_hasta = ahora + 0.6
                texto_superpuesto = 'YA!'
        elif self.estado == 'jugando':
            try:
                self.detector.detectar(frame)
                self.puntos = int(self.detector.puntos * PUNTOS_POR_MOVIMIENTO)
            except Exception as error:
                messagebox.showerror('Detector', f'No se pudo procesar el movimiento:\\n{error}')
                self.terminar(error=True)
                return
            self.marcador.config(text=f'AURA: {self.puntos}')
            falta = max(0, DURACION - int(ahora - self.inicio_partida))
            self.reloj.config(text=f'00:{falta:02d}')
            if falta <= 0:
                self.terminar()
                return
            if ahora < self.mensaje_inicio_hasta:
                texto_superpuesto = 'YA!'

        alto_original, ancho_original = frame.shape[:2]
        ancho = max(400, self.vista.winfo_width() - 10)
        alto = max(250, self.vista.winfo_height() - 10)
        escala = min(ancho / ancho_original, alto / alto_original)
        nuevo = (int(ancho_original * escala), int(alto_original * escala))
        frame = cv2.resize(frame, nuevo)

        # Cuenta regresiva dibujada directamente sobre la imagen de la cámara.
        if texto_superpuesto:
            fuente = cv2.FONT_HERSHEY_DUPLEX
            escala_texto = max(3, min(frame.shape[1], frame.shape[0]) / 180)
            grosor = max(6, int(escala_texto * 3))
            (ancho_texto, alto_texto), _ = cv2.getTextSize(
                texto_superpuesto, fuente, escala_texto, grosor
            )
            x = (frame.shape[1] - ancho_texto) // 2
            y = (frame.shape[0] + alto_texto) // 2
            cv2.putText(frame, texto_superpuesto, (x, y), fuente, escala_texto,
                        (0, 0, 0), grosor + 10, cv2.LINE_AA)
            cv2.putText(frame, texto_superpuesto, (x, y), fuente, escala_texto,
                        (29, 213, 242), grosor, cv2.LINE_AA)

        imagen = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.vista.config(image=imagen)
        self.vista.image = imagen
        self.after_id = self.root.after(30, self.actualizar)

    def ranking(self):
        try:
            lista = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else []
            if not isinstance(lista, list):
                lista = []
        except (OSError, json.JSONDecodeError):
            lista = []
        lista.append({'nombre': self.jugador, 'puntos': self.puntos})
        lista.sort(key=lambda dato: int(dato.get('puntos', 0)), reverse=True)
        lista = lista[:20]
        DATA.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding='utf-8')
        return lista

    def terminar(self, error=False):
        if self.estado == 'final':
            return
        self.estado = 'final'
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.video:
            try:
                self.video.cerrar_camara()
            except Exception:
                pass
            self.video = None
        if error:
            messagebox.showerror('Cámara', 'Se perdió la conexión con la cámara.')
        self.resultados(self.ranking())

    def resultados(self, lista):
        self.limpiar()
        self.encabezado('RESULTADOS')
        caja = tk.Frame(self.root, bg=NEGRO)
        caja.pack(fill='both', expand=True, padx=35, pady=20)
        self.texto(caja, '¡PARTIDA TERMINADA!', AMARILLO, 23).pack(pady=5)
        self.texto(caja, self.jugador.upper(), BLANCO, 13).pack()
        self.texto(caja, f'{self.puntos} PUNTOS DE AURA', VERDE, 21).pack(pady=10)
        tabla = tk.Frame(caja, bg=PANEL, padx=25, pady=12)
        tabla.pack(fill='both', expand=True, padx=45, pady=10)
        self.texto(tabla, 'RANKING DE JUGADORES', AMARILLO, 13, PANEL).pack(pady=8)
        for i, dato in enumerate(lista[:8], 1):
            fondo = '#293329' if i % 2 else PANEL
            fila = tk.Frame(tabla, bg=fondo)
            fila.pack(fill='x', pady=2)
            self.texto(fila, f'{i:02}', AMARILLO if i == 1 else BLANCO, 11, fondo).pack(side='left', padx=10, pady=5)
            self.texto(fila, str(dato.get('nombre', 'Jugador')), BLANCO, 10, fondo).pack(side='left', expand=True)
            self.texto(fila, str(dato.get('puntos', 0)), VERDE, 11, fondo).pack(side='right', padx=10)
        self.boton(caja, '↻  REINICIAR', self.pantalla_inicio).pack(pady=12)

    def cerrar(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.video:
            try:
                self.video.cerrar_camara()
            except Exception:
                pass
        self.root.destroy()
