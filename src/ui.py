import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
import cv2
import numpy as np
import json
import time
from pathlib import Path
from PIL import Image, ImageTk, ImageOps
from src.video_source import fuentevideo
from src.motion_detector import detector_de_movimiento
from src.config import UMBRAL_MOVIMIENTO, PUNTOS_POR_MOVIMIENTO
from src.audio_manager import iniciar_musica, detener_musica
import pygame
NEGRO = '#FFF9EB'
PANEL = '#F7CCD3'
PANEL_CLARO = '#E8A4B5'
AMARILLO = '#E5C64A'
VERDE = '#7C9449'
ROSA = '#E8A4B5'
ROSA_CLARO = '#F7CCD3'
BLANCO = '#365545'
SECUNDARIO = '#7C9449'
DURACION = 20
CUENTA = 3
BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / 'ranking_aura.json'
LOGO = BASE_DIR / 'assets' / 'logo_eico.png'
STEVE = BASE_DIR / 'assets' / 'steve_eico.png'
FONDO_MINECRAFT = BASE_DIR / 'assets' / 'minecraft_menu_bg.jpg'
MARCO_MINECRAFT = BASE_DIR / 'assets' / 'marco_minecraft_fuente.png'



class RoundedPanel(tk.Frame):
    """Panel con esquinas redondeadas dibujadas en Canvas."""
    def __init__(self, master, bg=NEGRO, fill=PANEL, outline='#2B4133',
                 radius=24, padding=18, **kwargs):
        super().__init__(master, bg=bg, bd=0, highlightthickness=0, **kwargs)
        self.fill = fill
        self.outline = outline
        self.radius = radius
        self.padding = padding
        self.canvas = tk.Canvas(self, bg=bg, bd=0, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.body = tk.Frame(self.canvas, bg=fill, bd=0, highlightthickness=0)
        self.window = self.canvas.create_window(
            padding, padding, anchor='nw', window=self.body
        )
        self.bind('<Configure>', self._draw)
        self.canvas.bind('<Configure>', self._draw)

    def _draw(self, event=None):
        w = max(self.winfo_width(), 2)
        h = max(self.winfo_height(), 2)
        r = min(self.radius, w // 2, h // 2)
        points = [
            r, 0, w-r, 0, w, 0, w, r, w, h-r, w, h,
            w-r, h, r, h, 0, h, 0, h-r, 0, r, 0, 0
        ]
        self.canvas.delete('panel-bg')
        self.canvas.create_polygon(
            points, smooth=True, splinesteps=24, fill=self.fill,
            outline=self.outline, width=1, tags='panel-bg'
        )
        self.canvas.tag_lower('panel-bg')
        self.canvas.coords(self.window, self.padding, self.padding)
        self.canvas.itemconfigure(
            self.window,
            width=max(1, w - self.padding * 2),
            height=max(1, h - self.padding * 2)
        )


class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command, bg=AMARILLO, fg=NEGRO,
                 hover="#FEEA8F", width=190, height=48, **kwargs):
        super().__init__(master, width=width, height=height, bg=master.cget('bg'),
                         bd=0, highlightthickness=0, cursor='hand2')
        self.command = command
        self.text = text
        self.normal = bg
        self.hover = hover
        self.fg = fg
        self.width = width
        self.height = height
        self._paint(self.normal)
        self.bind('<Enter>', lambda e: self._paint(self.hover))
        self.bind('<Leave>', lambda e: self._paint(self.normal))
        self.bind('<Button-1>', lambda e: self.command())

    def _paint(self, color):
        self.delete('all')
        self.create_oval(0, 0, self.height, self.height, fill=color, outline=color)
        self.create_oval(self.width-self.height, 0, self.width, self.height,
                         fill=color, outline=color)
        self.create_rectangle(self.height/2, 0, self.width-self.height/2,
                              self.height, fill=color, outline=color)
        self.create_text(self.width/2, self.height/2, text=self.text,
                         fill=self.fg, font=('Segoe UI', 11, 'bold'))



class PixelButton(tk.Frame):
    """Botón rectangular pixelado, inspirado en los menús clásicos de Minecraft."""
    def __init__(self, master, text, command, width=360, height=42):
        super().__init__(master, bg='#111111', bd=0, highlightthickness=0,
                         width=width, height=height, cursor='hand2')
        self.pack_propagate(False)
        self.command = command
        self.canvas = tk.Canvas(self, width=width, height=height,
                                bg='#111111', bd=0, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.text = text
        self._draw(False)
        self.canvas.bind('<Enter>', lambda e: self._draw(True))
        self.canvas.bind('<Leave>', lambda e: self._draw(False))
        self.canvas.bind('<Button-1>', lambda e: self.command())

    def _draw(self, hover):
        c = self.canvas
        c.delete('all')
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10: w = int(c.cget('width'))
        if h < 10: h = int(c.cget('height'))
        fill = '#B77F98' if hover else '#78616F'
        top = '#F6D8E4' if hover else '#CDA9B9'
        bottom = '#3A3038'
        c.create_rectangle(1, 1, w-2, h-2, fill=fill, outline='#101010', width=2)
        c.create_line(3, 3, w-4, 3, fill=top, width=3)
        c.create_line(3, 3, 3, h-4, fill=top, width=3)
        c.create_line(3, h-4, w-4, h-4, fill=bottom, width=3)
        c.create_line(w-4, 3, w-4, h-4, fill=bottom, width=3)
        c.create_text(w//2, h//2, text=self.text,
                      fill='#263D32' if hover else '#263D32',
                      font=fuente_pixel(12, True))



def fuente_pixel(tamano=12, negrita=False):
    """Prioriza tipografías pixel/Minecraft instaladas y usa Consolas como respaldo."""
    try:
        familias = set(tkfont.families())
    except Exception:
        familias = set()
    for nombre in ("Minecraft", "Minecraftia", "Pixel Operator", "Press Start 2P"):
        if nombre in familias:
            return (nombre, tamano, "bold" if negrita else "normal")
    return ("Consolas", tamano, "bold" if negrita else "normal")


class ContadorAura:

    def __init__(self, root):
        self.root = root
        self.root.title('CONTADOR DE AURA | EICO N°1')
        # Abrir maximizada desde el primer momento.
        self.root.update_idletasks()
        try:
            self.root.state('zoomed')  # Windows
        except tk.TclError:
            ancho = self.root.winfo_screenwidth()
            alto = self.root.winfo_screenheight()
            self.root.geometry(f'{ancho}x{alto}+0+0')
        self.root.minsize(850, 600)
        self.root.configure(bg='#DCCBD3')
        self.root.protocol('WM_DELETE_WINDOW', self.cerrar)
        self.video = None
        self.detector = None
        self.after_id = None
        self.estado = 'inicio'
        self.puntos = 0
        self.jugador = ''
        self.fondo_frames = []
        self.fondo_frame_index = 0
        self.fondo_after_id = None
        # Detector facial liviano para ubicar el nombre sobre la cabeza.
        self.detector_rostros = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        iniciar_musica()
        self.pantalla_inicio()

    def texto(self, padre, contenido, color=BLANCO, tam=12, fondo=None):
        return tk.Label(
            padre, text=contenido, bg=fondo or NEGRO, fg=color,
            font=('Segoe UI', tam, 'bold')
        )

    def boton(self, padre, contenido, accion, color=AMARILLO):
        return RoundedButton(padre, contenido, accion, bg=color)

    def limpiar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def encabezado(self, subtitulo=''):
        barra = tk.Frame(self.root, bg=NEGRO, padx=30, pady=14)
        barra.pack(fill='x')
        marca = tk.Frame(barra, bg=NEGRO)
        marca.pack(side='left')
        try:
            logo = Image.open(LOGO).convert('RGBA')
            logo.thumbnail((48, 48), Image.Resampling.LANCZOS)
            pixeles = logo.load()
            for y in range(logo.height):
                for x in range(logo.width):
                    r, g, b, a = pixeles[x, y]
                    if r > 245 and g > 245 and b > 245:
                        pixeles[x, y] = (r, g, b, 0)
            self.logo_img = ImageTk.PhotoImage(logo)
            tk.Label(marca, image=self.logo_img, bg=NEGRO).pack(side='left', padx=(0, 12))
        except (FileNotFoundError, OSError):
            self.logo_img = None
        tk.Label(marca, text='CONTADOR DE AURA', bg='#DCCBD3', fg='#2F2029',
                 font=('Segoe UI', 19, 'bold')).pack(side='left')
        tk.Label(barra, text='EICO N°1  ·  CALETA OLIVIA', bg=NEGRO,
                 fg=SECUNDARIO, font=('Segoe UI', 9, 'bold')).pack(side='right')
        if subtitulo:
            tk.Label(self.root, text=subtitulo.upper(), bg=NEGRO, fg=VERDE,
                     font=('Segoe UI', 9, 'bold')).pack(pady=(0, 8))

    def pantalla_inicio(self):
        self.estado = 'inicio'
        self.limpiar()

        # Fondo de cerezos a pantalla completa.
        try:
            self.fondo_original = Image.open(FONDO_MINECRAFT).convert('RGB')
            self.fondo_label = tk.Label(
                self.root, bd=0, highlightthickness=0, bg='#FFF9EB'
            )
            self.fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.root.bind('<Configure>', self._actualizar_fondo)
            self.root.after(100, self._actualizar_fondo)
        except (FileNotFoundError, OSError):
            self.root.configure(bg='#FFF9EB')

        self.root.update_idletasks()
        ancho = max(900, self.root.winfo_width())
        alto = max(600, self.root.winfo_height())

        # Panel translúcido real: el paisaje queda suavemente visible debajo.
        panel_w = min(770, int(ancho * 0.49))
        panel_h = min(590, int(alto * 0.66))
        panel_w = max(560, panel_w)
        panel_h = max(420, panel_h)
        x = (ancho - panel_w) // 2
        y = (alto - panel_h) // 2

        fondo_panel = ImageOps.fit(
            self.fondo_original, (ancho, alto),
            method=Image.Resampling.LANCZOS
        ).crop((x, y, x + panel_w, y + panel_h))
        crema = Image.new('RGB', fondo_panel.size, '#FFF9EB')
        panel_img = Image.blend(fondo_panel, crema, 0.80)
        self.panel_inicio_img = ImageTk.PhotoImage(panel_img)

        # El Label funciona como superficie con la imagen translúcida.
        centro = tk.Label(
            self.root, image=self.panel_inicio_img,
            bd=0, highlightthickness=0
        )
        centro.place(x=x, y=y, width=panel_w, height=panel_h)

        escala = min(panel_w / 770, panel_h / 590)
        color_panel = '#F4EDE1'

        def etiqueta(texto, y_base, tam, color='#365545', negrita=True):
            lbl = tk.Label(
                centro, text=texto, bg=color_panel, fg=color,
                font=fuente_pixel(max(8, int(tam * escala)), negrita),
                bd=0, highlightthickness=0
            )
            lbl.place(relx=0.5, y=int(y_base * escala), anchor='center')

        etiqueta('CONTADOR DE AURA', 82, 31, '#365545')
        etiqueta('EICO N°1  ·  SURVIVAL MODE', 155, 12, '#7C9449')
        etiqueta('NOMBRE DEL JUGADOR', 225, 11, '#365545')

        # Campo rosa suave con texto guía pequeño y puntos suspensivos.
        entry_w = int(550 * escala)
        entry_h = int(60 * escala)
        self.nombre = tk.Entry(
            centro, font=fuente_pixel(max(8, int(11 * escala))),
            justify='center', relief='flat', bd=0,
            bg='#F7CCD3', fg='#806575',
            insertbackground='#263D32'
        )
        self.nombre.place(
            relx=0.5, y=int(290 * escala), anchor='center',
            width=entry_w, height=entry_h
        )
        placeholder = 'ESCRIBI TU NOMBRE...'
        self.nombre.insert(1, placeholder)

        def quitar_placeholder(event=None):
            if self.nombre.get() == placeholder:
                self.nombre.delete(0, 'end')
                self.nombre.config(fg='#263D32')

        def poner_placeholder(event=None):
            if not self.nombre.get().strip():
                self.nombre.insert(0, placeholder)
                self.nombre.config(fg='#806575')

        self.nombre.bind('<FocusIn>', quitar_placeholder)
        self.nombre.bind('<FocusOut>', poner_placeholder)
        self.nombre.bind('<Return>', lambda event: self.iniciar())

        # Botones rectangulares tipo Minecraft, no redondeados ni amarillos.
        def boton_pixel(texto, y_base, color, accion):
            bw = int(550 * escala)
            bh = int(72 * escala)
            boton = tk.Canvas(
                centro, width=bw, height=bh,
                bg=color_panel, bd=0, highlightthickness=0,
                cursor='hand2'
            )
            boton.place(relx=0.5, y=int(y_base * escala), anchor='center')

            def dibujar(hover=False):
                boton.delete('all')
                w, h = bw, bh
                relleno = color
                if hover:
                    relleno = '#E8A4B5' if color == '#E8A4B5' else '#C5D58A'
                boton.create_rectangle(
                    2, 2, w-3, h-3, fill=relleno,
                    outline='#30232B', width=max(2, int(4 * escala))
                )
                boton.create_line(
                    6, 6, w-7, 6, fill='#F9E7ED',
                    width=max(2, int(5 * escala))
                )
                boton.create_line(
                    6, h-6, w-7, h-6, fill='#57404B',
                    width=max(2, int(5 * escala))
                )
                boton.create_text(
                    w//2, h//2, text=texto, fill='#365545',
                    font=fuente_pixel(max(9, int(13 * escala)), True)
                )

            dibujar()
            boton.bind('<Enter>', lambda e: dibujar(True))
            boton.bind('<Leave>', lambda e: dibujar(False))
            boton.bind('<Button-1>', lambda e: accion())

        boton_pixel('INICIAR', 390, '#E8A4B5', self.iniciar)
        boton_pixel(
            'VER CLASIFICACION', 480, '#B5C56D',
            self.mostrar_ranking
        )

        self.nombre.focus_set()

    def _actualizar_fondo(self, event=None):
        # Escala proporcional hasta cubrir la ventana; recorta solo el excedente
        # de los laterales/alto para evitar cualquier borde gris o vacío.
        if not hasattr(self, 'fondo_original') or not hasattr(self, 'fondo_label'):
            return
        if event is not None and event.widget is not self.root:
            return
        ancho = max(1, self.root.winfo_width())
        alto = max(1, self.root.winfo_height())
        imagen = ImageOps.fit(
            self.fondo_original, (ancho, alto),
            method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)
        )
        capa = Image.new('RGB', imagen.size, (20, 13, 22))
        imagen = Image.blend(imagen, capa, 0.05)
        self.fondo_inicio_img = ImageTk.PhotoImage(imagen)
        self.fondo_label.configure(image=self.fondo_inicio_img)

    def _animar_fondo(self):
        if self.estado != 'inicio' or not self.fondo_frames:
            return
        self.fondo_label.configure(image=self.fondo_frames[self.fondo_frame_index])
        self.fondo_frame_index = (self.fondo_frame_index + 1) % len(self.fondo_frames)
        # El archivo que llegó en este chat tiene un solo cuadro; si se reemplaza
        # por un GIF animado, el mismo código reproduce su secuencia.
        self.fondo_after_id = self.root.after(100, self._animar_fondo)

    def mostrar_ranking(self):
        try:
            lista = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else []
            if not isinstance(lista, list):
                lista = []
        except (OSError, json.JSONDecodeError):
            lista = []
        self.resultados(lista)

    def iniciar(self):
        
        self.jugador = self.nombre.get().strip()[:22]
        if self.jugador == 'ESCRIBI TU NOMBRE...':
            self.jugador = ''
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
        print("INTENTANDO INICIAR MUSICA")
        iniciar_musica()
        print("ESTADO DEL AUDIO:", pygame.mixer.music.get_busy())
        self.puntos = 0
        self.estado = 'cuenta'
        self.inicio_cuenta = time.monotonic()
        self.mensaje_inicio_hasta = 0
        self.limpiar()

  

        # Fondo crema de la paleta; distribución aireada y equilibrada.
        panel = tk.Frame(self.root, bg='#FFF9EB')
        panel.pack(fill='both', expand=True, padx=18, pady=14)

        tk.Label(
            panel, text='MODO SUPERVIVENCIA', bg='#FFF9EB', fg='#365545',
            font=fuente_pixel(15, True)
        ).pack(pady=(0, 12))

        zona_juego = tk.Frame(panel, bg='#FFF9EB')
        zona_juego.pack(fill='both', expand=True)

        hud = tk.Frame(zona_juego, bg='#FFF9EB', width=205)
        hud.pack(side='left', fill='y', padx=(0, 14))
        hud.pack_propagate(False)

        # Sin contornos de color ni resaltados: los dos indicadores comparten
        # el fondo crema y se distinguen por tipografía y jerarquía.
        bloque_aura = tk.Frame(hud, bg='#FFF9EB')
        bloque_aura.pack(fill='both', expand=True, pady=(0, 12))
        tk.Label(
            bloque_aura, text='AURA', bg='#FFF9EB', fg='#365545',
            font=fuente_pixel(13, True)
        ).pack(anchor='w', padx=12, pady=(18, 4))
        self.marcador = tk.Label(
            bloque_aura, text='0', bg='#FFF9EB', fg='#365545',
            font=fuente_pixel(38, True)
        )
        self.marcador.pack(anchor='w', padx=12, pady=(0, 12))

        bloque_tiempo = tk.Frame(hud, bg='#FFF9EB')
        bloque_tiempo.pack(fill='both', expand=True, pady=(0, 4))
        tk.Label(
            bloque_tiempo, text='TIEMPO', bg='#FFF9EB', fg='#7C9449',
            font=fuente_pixel(13, True)
        ).pack(anchor='w', padx=12, pady=(18, 4))
        self.reloj = tk.Label(
            bloque_tiempo, text='00:20', bg='#FFF9EB', fg='#365545',
            font=fuente_pixel(32, True)
        )
        self.reloj.pack(anchor='w', padx=12, pady=(0, 12))

        # Cámara centrada: el marco se dibuja dentro de los píxeles exteriores
        # de la propia imagen, por lo que no aumenta el tamaño de la cámara.
        self.vista = tk.Label(
            zona_juego, bg='#FFF9EB', bd=0, highlightthickness=0
        )
        self.vista.pack(side='left', fill='both', expand=True)

        # Steve de tamaño mediano, a la derecha, usando transparencia PNG real.
        lateral_steve = tk.Frame(zona_juego, bg='#FFF9EB', width=185)
        lateral_steve.pack(side='right', fill='y', padx=(12, 0))
        lateral_steve.pack_propagate(False)
        try:
            steve = Image.open(STEVE).convert('RGBA')
            steve.thumbnail((175, 430), Image.Resampling.LANCZOS)
            self.steve_juego_img = ImageTk.PhotoImage(steve)
            tk.Label(
                lateral_steve, image=self.steve_juego_img,
                bg='#FFF9EB', bd=0, highlightthickness=0
            ).pack(expand=True, anchor='center')
        except (FileNotFoundError, OSError):
            tk.Label(
                lateral_steve, text='STEVE', bg='#FFF9EB', fg='#365545',
                font=fuente_pixel(13, True)
            ).pack(expand=True)

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
            self.marcador.config(text=f'{self.puntos}')
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

        # Ajuste tipo "cover": recorta el excedente para llenar el interior
        # del marco de madera, sin franjas negras y sin deformar la cámara.
        frame_rgb = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_rgb = ImageOps.fit(
            frame_rgb, (ancho, alto),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)
        )
        frame = cv2.cvtColor(
            np.array(frame_rgb), cv2.COLOR_RGB2BGR
        )

        # Etiqueta estilo Minecraft: sigue la cara y muestra quién está jugando.
        if not self.detector_rostros.empty():
            gris_camara = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = self.detector_rostros.detectMultiScale(
                gris_camara, scaleFactor=1.12, minNeighbors=5,
                minSize=(max(35, frame.shape[1] // 14), max(35, frame.shape[1] // 14))
            )
            if len(rostros):
                # Si aparecen varias caras, etiqueta la más grande (jugador principal).
                x, y, w, h = max(rostros, key=lambda r: r[2] * r[3])
                etiqueta = self.jugador[:22].upper()
                fuente_etiqueta = cv2.FONT_HERSHEY_PLAIN
                escala_etiqueta = max(1.35, min(2.0, frame.shape[1] / 500))
                grosor_etiqueta = 2
                (tw, th), _ = cv2.getTextSize(
                    etiqueta, fuente_etiqueta, escala_etiqueta, grosor_etiqueta
                )
                margen_x, margen_y = 10, 6
                caja_w, caja_h = tw + margen_x * 2, th + margen_y * 2
                cx = max(2, min(frame.shape[1] - caja_w - 2, x + w // 2 - caja_w // 2))
                cy = max(2, y - caja_h - 12)
                # Solo fondo, sin contorno; texto en estilo pixelado sin suavizado.
                cv2.rectangle(frame, (cx, cy), (cx + caja_w, cy + caja_h),
                              (55, 43, 54), -1)
                cv2.putText(frame, etiqueta, (cx + margen_x, cy + th + margen_y - 1),
                            fuente_etiqueta, escala_etiqueta, (245, 222, 233),
                            grosor_etiqueta, cv2.LINE_8)

        # Cuenta regresiva dibujada directamente sobre la imagen de la cámara.
        if texto_superpuesto:
            fuente = cv2.FONT_HERSHEY_SIMPLEX
            escala_texto = max(2.6, min(frame.shape[1], frame.shape[0]) / 205)
            grosor = max(4, int(escala_texto * 1.7))
            (ancho_texto, alto_texto), _ = cv2.getTextSize(
                texto_superpuesto, fuente, escala_texto, grosor
            )
            x = (frame.shape[1] - ancho_texto) // 2
            y = (frame.shape[0] + alto_texto) // 2
            # Sombra corta y suave, sin caja ni contorno grueso.
            cv2.putText(frame, texto_superpuesto, (x + 2, y + 3), fuente,
                        escala_texto, (22, 38, 25), grosor, cv2.LINE_AA)
            cv2.putText(frame, texto_superpuesto, (x, y), fuente,
                        escala_texto, (74, 231, 244), grosor, cv2.LINE_AA)

        imagen_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert('RGBA')

        # Marco pixelado de madera Minecraft: el recurso se usa como textura
        # de los cuatro lados y las esquinas, sin tapar el centro de la cámara.
        try:
            textura = Image.open(MARCO_MINECRAFT).convert('RGBA')
            ancho_img, alto_img = imagen_pil.size
            grosor = max(14, min(22, ancho_img // 48, alto_img // 30))
            borde = Image.new('RGBA', (ancho_img, alto_img), (0, 0, 0, 0))

            # Tomar madera del interior de la textura (no el centro completo)
            # y escalarla con vecino más cercano para conservar los píxeles.
            margen = 16
            tramo_sup = textura.crop((margen, margen, 225-margen, 42)).resize(
                (max(1, ancho_img-2*grosor), grosor), Image.Resampling.NEAREST
            )
            tramo_inf = textura.crop((margen, 183, 225-margen, 225-margen)).resize(
                (max(1, ancho_img-2*grosor), grosor), Image.Resampling.NEAREST
            )
            tramo_izq = textura.crop((margen, 42, 42, 183)).resize(
                (grosor, max(1, alto_img-2*grosor)), Image.Resampling.NEAREST
            )
            tramo_der = textura.crop((183, 42, 225-margen, 183)).resize(
                (grosor, max(1, alto_img-2*grosor)), Image.Resampling.NEAREST
            )

            # Esquinas cuadradas y pixeladas.
            esquina_sup_izq = textura.crop((0, 0, 42, 42)).resize(
                (grosor, grosor), Image.Resampling.NEAREST
            )
            esquina_sup_der = textura.crop((183, 0, 225, 42)).resize(
                (grosor, grosor), Image.Resampling.NEAREST
            )
            esquina_inf_izq = textura.crop((0, 183, 42, 225)).resize(
                (grosor, grosor), Image.Resampling.NEAREST
            )
            esquina_inf_der = textura.crop((183, 183, 225, 225)).resize(
                (grosor, grosor), Image.Resampling.NEAREST
            )

            borde.alpha_composite(esquina_sup_izq, (0, 0))
            borde.alpha_composite(esquina_sup_der, (ancho_img-grosor, 0))
            borde.alpha_composite(esquina_inf_izq, (0, alto_img-grosor))
            borde.alpha_composite(esquina_inf_der, (ancho_img-grosor, alto_img-grosor))
            borde.alpha_composite(tramo_sup, (grosor, 0))
            borde.alpha_composite(tramo_inf, (grosor, alto_img-grosor))
            borde.alpha_composite(tramo_izq, (0, grosor))
            borde.alpha_composite(tramo_der, (ancho_img-grosor, grosor))

            imagen_pil = Image.alpha_composite(imagen_pil, borde)
        except (FileNotFoundError, OSError, ValueError):
            pass

        imagen = ImageTk.PhotoImage(imagen_pil.convert('RGB'))
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
        detener_musica()

    def resultados(self, lista):
        self.estado = 'final'
        self.limpiar()

        # Fondo de cerezos igual al inicio.
        try:
            self.fondo_original = Image.open(FONDO_MINECRAFT).convert('RGB')
            self.fondo_label = tk.Label(
                self.root, bd=0, highlightthickness=0, bg='#FFF9EB'
            )
            self.fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.root.bind('<Configure>', self._actualizar_fondo)
            self.root.after(100, self._actualizar_fondo)
        except (FileNotFoundError, OSError):
            self.root.configure(bg='#FFF9EB')

        self.root.update_idletasks()
        ancho = max(900, self.root.winfo_width())
        alto = max(600, self.root.winfo_height())

        panel_w = min(1000, int(ancho * 0.72))
        panel_h = min(760, int(alto * 0.86))
        x = (ancho - panel_w) // 2
        y = (alto - panel_h) // 2

        fondo_panel = ImageOps.fit(
            self.fondo_original, (ancho, alto),
            method=Image.Resampling.LANCZOS
        ).crop((x, y, x + panel_w, y + panel_h))
        panel_img = Image.blend(
            fondo_panel, Image.new('RGB', fondo_panel.size, '#FFF9EB'), 0.80
        )
        self.panel_resultados_img = ImageTk.PhotoImage(panel_img)

        panel = tk.Label(
            self.root, image=self.panel_resultados_img,
            bd=0, highlightthickness=0
        )
        panel.place(x=x, y=y, width=panel_w, height=panel_h)

        escala = min(panel_w / 1000, panel_h / 760)
        color_panel = '#F4EDE1'

        def etiqueta(texto, y_base, tam, color='#365545'):
            tk.Label(
                panel, text=texto, bg=color_panel, fg=color,
                font=fuente_pixel(max(8, int(tam * escala)), True),
                bd=0, highlightthickness=0
            ).place(relx=0.5, y=int(y_base * escala), anchor='center')

        etiqueta('PARTIDA TERMINADA', 55, 24, '#365545')
        etiqueta('RESULTADOS', 105, 20, '#7C9449')
        etiqueta(
            f'{self.jugador.upper()}  ·  {self.puntos} AURA',
            155, 13, '#365545'
        )

        # Tabla compacta, con la misma paleta del inicio.
        tabla = tk.Frame(panel, bg='#7C9449', bd=0)
        tabla.place(
            relx=0.5, y=int(195 * escala), anchor='n',
            width=int(820 * escala)
        )

        cabecera = tk.Frame(tabla, bg='#7C9449', height=int(48 * escala))
        cabecera.pack(fill='x')
        cabecera.pack_propagate(False)

        for texto, ancho_col in (('PUESTO', 130), ('JUGADOR', 480), ('AURA', 180)):
            tk.Label(
                cabecera, text=texto, bg='#7C9449', fg='#FFF9EB',
                font=fuente_pixel(max(8, int(12 * escala)), True),
                width=max(6, int(ancho_col * escala / 10))
            ).pack(side='left', expand=(texto == 'JUGADOR'), fill='both')

        lista_ordenada = sorted(
            lista,
            key=lambda dato: int(dato.get('puntos', 0)),
            reverse=True
        )

        colores_filas = ['#F7CCD3', '#E8A4B5', '#FFF9EB', '#E5E8C8', '#B5C56D']
        for i, dato in enumerate(lista_ordenada[:7], 1):
            color_fila = colores_filas[(i - 1) % len(colores_filas)]
            fila = tk.Frame(tabla, bg=color_fila, height=int(52 * escala))
            fila.pack(fill='x', pady=max(1, int(2 * escala)))
            fila.pack_propagate(False)

            tk.Label(
                fila, text=f'{i:02d}', bg=color_fila, fg='#365545',
                font=fuente_pixel(max(8, int(12 * escala)), True),
                width=max(5, int(13 * escala))
            ).pack(side='left', fill='y')

            tk.Label(
                fila, text=str(dato.get('nombre', 'Jugador')).upper(),
                bg=color_fila, fg='#263D32',
                font=fuente_pixel(max(8, int(12 * escala)), True),
                anchor='w'
            ).pack(side='left', expand=True, fill='both', padx=12)

            tk.Label(
                fila, text=str(dato.get('puntos', 0)),
                bg=color_fila, fg='#365545',
                font=fuente_pixel(max(8, int(12 * escala)), True),
                width=max(6, int(15 * escala))
            ).pack(side='right', fill='y')

        # Botones con el MISMO diseño rectangular pixelado del inicio.
        def boton_pixel(texto, y_base, color, accion):
            bw = int(360 * escala)
            bh = int(62 * escala)
            boton = tk.Canvas(
                panel, width=bw, height=bh, bg=color_panel,
                bd=0, highlightthickness=0, cursor='hand2'
            )
            boton.place(relx=0.5, y=int(y_base * escala), anchor='center')

            def dibujar(hover=False):
                boton.delete('all')
                w, h = bw, bh
                relleno = color
                if hover:
                    relleno = '#E8A4B5' if color == '#E8A4B5' else '#C5D58A'
                boton.create_rectangle(
                    2, 2, w-3, h-3, fill=relleno,
                    outline='#30232B', width=max(2, int(4 * escala))
                )
                boton.create_line(
                    6, 6, w-7, 6, fill='#F9E7ED',
                    width=max(2, int(5 * escala))
                )
                boton.create_line(
                    6, h-6, w-7, h-6, fill='#57404B',
                    width=max(2, int(5 * escala))
                )
                boton.create_text(
                    w//2, h//2, text=texto, fill='#365545',
                    font=fuente_pixel(max(8, int(12 * escala)), True)
                )

            dibujar()
            boton.bind('<Enter>', lambda e: dibujar(True))
            boton.bind('<Leave>', lambda e: dibujar(False))
            boton.bind('<Button-1>', lambda e: accion())

        boton_pixel('VOLVER AL INICIO', 650, '#E8A4B5', self.pantalla_inicio)
        boton_pixel('JUGAR DE NUEVO', 725, '#B5C56D', self.juego_nuevo)

    def cerrar(self):
        if self.fondo_after_id is not None:
            try:
                self.root.after_cancel(self.fondo_after_id)
            except Exception:
                pass
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.video:
            try:
                self.video.cerrar_camara()
            except Exception:
                pass
        self.root.destroy()
