import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
import cv2
import json
import time
from pathlib import Path
from PIL import Image, ImageTk, ImageOps
from src.video_source import fuentevideo
from src.motion_detector import detector_de_movimiento
from src.config import UMBRAL_MOVIMIENTO, PUNTOS_POR_MOVIMIENTO
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

    self.fondo_original = Image.open(FONDO_MINECRAFT).convert('RGB')
    self.fondo_label = tk.Label(
        self.root, bd=0, highlightthickness=0, bg='#FFF9EB'
    )
    self.fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
    self.root.bind('<Configure>', self._actualizar_fondo)
    self.root.after(100, self._actualizar_fondo)

    # Panel centrado, sin borde rosa. El fondo se mezcla con el paisaje
    # desde _actualizar_fondo para dar el efecto translúcido.
    centro = tk.Frame(
        self.root, bg='#F4EDE1', bd=0,
        highlightthickness=0, padx=48, pady=34
    )
    centro.place(relx=0.5, rely=0.5, anchor='center')

    tk.Label(
        centro, text='CONTADOR DE AURA',
        bg='#F4EDE1', fg='#263D32',
        font=fuente_pixel(25, True)
    ).pack(pady=(0, 8))

    tk.Label(
        centro, text='EICO N°1  ·  SURVIVAL MODE',
        bg='#F4EDE1', fg='#7C9449',
        font=fuente_pixel(11, True)
    ).pack(pady=(0, 38))

    tk.Label(
        centro, text='NOMBRE DEL JUGADOR',
        bg='#F4EDE1', fg='#365545',
        font=fuente_pixel(10, True)
    ).pack(pady=(0, 12))

    self.nombre = tk.Entry(
        centro, font=fuente_pixel(11), justify='center',
        relief='flat', bd=0, bg='#F7CCD3', fg='#263D32',
        insertbackground='#263D32', width=38
    )
    self.nombre.pack(ipady=12, pady=(0, 24))
    self.nombre.insert(0, '')
    self.nombre.bind('<Return>', lambda event: self.iniciar())

    PixelButton(
        centro, 'INICIAR', self.iniciar,
        width=550, height=70
    ).pack(pady=9)

    PixelButton(
        centro, 'VER CLASIFICACION', self.mostrar_ranking,
        width=550, height=70
    ).pack(pady=9)

    tk.Label(
        self.root, text='EICO N°1  ·  CALETA OLIVIA  ·  4° AÑO',
        bg='#FFF9EB', fg='#365545',
        font=fuente_pixel(9)
    ).place(relx=0.01, rely=0.98, anchor='sw')

    self.nombre.focus_set()


def _actualizar_fondo(self, event=None):
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

    # Oscurecimiento muy leve para que el panel y los botones contrasten.
    capa = Image.new('RGB', imagen.size, (30, 25, 24))
    imagen = Image.blend(imagen, capa, 0.08)

    # Panel crema translúcido, sin contorno ni marco rosa.
    panel_w = min(900, int(ancho * 0.82))
    panel_h = min(680, int(alto * 0.82))
    x1 = (ancho - panel_w) // 2
    y1 = (alto - panel_h) // 2
    recorte = imagen.crop((x1, y1, x1 + panel_w, y1 + panel_h))
    crema = Image.new('RGB', recorte.size, '#FFF9EB')
    panel = Image.blend(recorte, crema, 0.86)
    imagen.paste(panel, (x1, y1))

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

    # Barra superior rosa con el modo centrado.
    barra_modo = tk.Frame(self.root, bg='#F7CCD3', height=76)
    barra_modo.pack(fill='x')
    barra_modo.pack_propagate(False)
    tk.Label(
        barra_modo, text='MODO SUPERVIVENCIA',
        bg='#F7CCD3', fg='#365545',
        font=fuente_pixel(16, True)
    ).pack(expand=True)

    panel = tk.Frame(self.root, bg='#FFF9EB')
    panel.pack(fill='both', expand=True, padx=24, pady=24)

    zona_juego = tk.Frame(panel, bg='#FFF9EB')
    zona_juego.pack(fill='both', expand=True)

    # Aura y tiempo a la izquierda, sin tarjetas ni resaltados.
    hud = tk.Frame(zona_juego, bg='#FFF9EB', width=220)
    hud.pack(side='left', fill='y', padx=(0, 24))
    hud.pack_propagate(False)

    bloque_aura = tk.Frame(hud, bg='#FFF9EB')
    bloque_aura.pack(fill='both', expand=True)
    tk.Label(
        bloque_aura, text='AURA', bg='#FFF9EB', fg='#365545',
        font=fuente_pixel(14, True)
    ).pack(anchor='w', padx=8, pady=(24, 8))
    self.marcador = tk.Label(
        bloque_aura, text='0', bg='#FFF9EB', fg='#263D32',
        font=fuente_pixel(42, True)
    )
    self.marcador.pack(anchor='w', padx=8)

    tk.Frame(hud, bg='#B5C56D', height=4).pack(
        fill='x', padx=8, pady=16
    )

    bloque_tiempo = tk.Frame(hud, bg='#FFF9EB')
    bloque_tiempo.pack(fill='both', expand=True)
    tk.Label(
        bloque_tiempo, text='TIEMPO', bg='#FFF9EB', fg='#7C9449',
        font=fuente_pixel(14, True)
    ).pack(anchor='w', padx=8, pady=(28, 8))
    self.reloj = tk.Label(
        bloque_tiempo, text='00:20', bg='#FFF9EB', fg='#263D32',
        font=fuente_pixel(34, True)
    )
    self.reloj.pack(anchor='w', padx=8)

    # La cámara ocupa el centro y el marco queda sobre su borde.
    self.vista = tk.Label(
        zona_juego, bg='#FFF9EB', bd=0, highlightthickness=0,
        anchor='center'
    )
    self.vista.pack(side='left', fill='both', expand=True)

    # Steve mediano, separado de la cámara y alineado hacia abajo.
    lateral_steve = tk.Frame(zona_juego, bg='#FFF9EB', width=210)
    lateral_steve.pack(side='right', fill='y', padx=(18, 0))
    lateral_steve.pack_propagate(False)
    try:
        steve = Image.open(STEVE).convert('RGBA')
        steve.thumbnail((195, 440), Image.Resampling.LANCZOS)
        self.steve_juego_img = ImageTk.PhotoImage(steve)
        tk.Label(
            lateral_steve, image=self.steve_juego_img,
            bg='#FFF9EB', bd=0, highlightthickness=0
        ).pack(side='bottom', anchor='center', pady=(0, 12))
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

        # Recorte centrado para que la imagen llene el espacio de la cámara
        # y no queden franjas negras por diferencias de proporción.
        proporcion_objetivo = ancho / alto
        proporcion_frame = ancho_original / alto_original
        if proporcion_frame > proporcion_objetivo:
            nuevo_ancho = int(alto_original * proporcion_objetivo)
            inicio_x = max(0, (ancho_original - nuevo_ancho) // 2)
            frame = frame[:, inicio_x:inicio_x + nuevo_ancho]
        else:
            nuevo_alto = int(ancho_original / proporcion_objetivo)
            inicio_y = max(0, (alto_original - nuevo_alto) // 2)
            frame = frame[inicio_y:inicio_y + nuevo_alto, :]

        frame = cv2.resize(frame, (ancho, alto), interpolation=cv2.INTER_AREA)

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

        # Marco de madera del recurso enviado: solo el borde; la cámara queda
        # dentro y el marco no agrega tamaño exterior a la imagen.
        try:
            textura = Image.open(MARCO_MINECRAFT).convert('RGBA')
            ancho_img, alto_img = imagen_pil.size
            grosor = max(12, min(24, ancho_img // 55, alto_img // 35))
            esquina = textura.crop((0, 0, 25, 25)).resize(
                (grosor, grosor), Image.Resampling.NEAREST
            )
            borde = Image.new('RGBA', (ancho_img, alto_img), (0, 0, 0, 0))
            # Esquinas pixeladas.
            borde.paste(esquina, (0, 0))
            borde.paste(esquina.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                        (ancho_img-grosor, 0))
            borde.paste(esquina.transpose(Image.Transpose.FLIP_TOP_BOTTOM),
                        (0, alto_img-grosor))
            borde.paste(esquina.transpose(Image.Transpose.ROTATE_180),
                        (ancho_img-grosor, alto_img-grosor))
            # Tramos superior/inferior y laterales tomados del mismo marco.
            tramo_h = textura.crop((25, 0, 200, 25)).resize(
                (max(1, ancho_img-2*grosor), grosor), Image.Resampling.NEAREST
            )
            tramo_v = textura.crop((0, 25, 25, 200)).resize(
                (grosor, max(1, alto_img-2*grosor)), Image.Resampling.NEAREST
            )
            borde.alpha_composite(tramo_h, (grosor, 0))
            borde.alpha_composite(tramo_h.transpose(Image.Transpose.FLIP_TOP_BOTTOM),
                                  (grosor, alto_img-grosor))
            borde.alpha_composite(tramo_v, (0, grosor))
            borde.alpha_composite(tramo_v.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                                  (ancho_img-grosor, grosor))
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

    def resultados(self, lista):
        self.limpiar()
        fondo = '#FFF9EB'
        contenido = tk.Frame(self.root, bg=fondo)
        contenido.pack(fill='both', expand=True, padx=70, pady=24)

        tk.Label(
            contenido, text='PARTIDA TERMINADA', bg=fondo,
            fg='#365545', font=fuente_pixel(17, True)
        ).pack(pady=(2, 4))
        tk.Label(
            contenido, text='RESULTADOS', bg=fondo,
            fg='#7C9449', font=fuente_pixel(14, True)
        ).pack(pady=(0, 8))
        tk.Label(
            contenido, text=f'{self.jugador.upper()}  ·  {self.puntos} AURA',
            bg=fondo, fg='#365545', font=fuente_pixel(11, True)
        ).pack(pady=(0, 16))

        # Tierlist compacta, centrada y alineada: cabecera verde, tarjetas
        # alternadas rosa suave/crema y texto oscuro de alto contraste.
        ranking = tk.Frame(contenido, bg=fondo)
        ranking.pack(fill='both', expand=True, padx=55)

        tabla = tk.Frame(ranking, bg='#365545', padx=2, pady=2)
        tabla.pack(fill='x', pady=(0, 8))
        encabezado = tk.Frame(tabla, bg='#365545', height=40)
        encabezado.pack(fill='x')
        encabezado.pack_propagate(False)

        tk.Label(
            encabezado, text='PUESTO', width=10, anchor='center',
            bg='#365545', fg='#E5C64A', font=fuente_pixel(10, True)
        ).pack(side='left', padx=6)
        tk.Label(
            encabezado, text='JUGADOR', anchor='w',
            bg='#365545', fg='#FFF9EB', font=fuente_pixel(10, True)
        ).pack(side='left', padx=12, expand=True, fill='x')
        tk.Label(
            encabezado, text='AURA', width=12, anchor='e',
            bg='#365545', fg='#FFF9EB', font=fuente_pixel(10, True)
        ).pack(side='right', padx=16)

        for i, dato in enumerate(lista[:8], 1):
            color_fila = '#F7CCD3' if i % 2 else '#F3E8D9'
            fila = tk.Frame(tabla, bg=color_fila, height=48)
            fila.pack(fill='x', pady=2)
            fila.pack_propagate(False)

            tk.Label(
                fila, text=f'{i:02}', width=10, anchor='center',
                bg=color_fila, fg='#7C9449' if i > 1 else '#A67C22',
                font=fuente_pixel(11, True)
            ).pack(side='left', padx=6)
            tk.Label(
                fila, text=str(dato.get('nombre', 'Jugador')).upper(),
                anchor='w', bg=color_fila, fg='#263D32',
                font=fuente_pixel(11, True)
            ).pack(side='left', padx=12, expand=True, fill='x')
            tk.Label(
                fila, text=str(dato.get('puntos', 0)),
                width=12, anchor='e', bg=color_fila, fg='#365545',
                font=fuente_pixel(11, True)
            ).pack(side='right', padx=16)

        self.boton(contenido, 'JUGAR DE NUEVO  ↻',
                   self.pantalla_inicio).pack(pady=(12, 0))

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
