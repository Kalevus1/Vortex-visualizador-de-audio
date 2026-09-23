# -*- coding: utf-8 -*-
"""
Visualizador de Voxel de Sonido — Día 13
Cada instante de sonido se convierte en un PUNTO en un espacio 3D, ubicado por sus
características (frecuencia, intensidad, brillo…). Al unir los puntos en el tiempo se ven
las "RUTAS" del sonido — ideal para estudiar el canto de las aves: cada canto tiene un
patrón y un lugar, y aquí se ven como puntos y trayectorias en el espacio.

La ruta se dibuja EN VIVO mientras se reproduce el audio (no hay que esperar a que analice todo).

Es "5D": 3 ejes (X, Y, Z) + color (frecuencia) + tamaño (intensidad).

Modos:
  • Ruta (tiempo):     X=tiempo · Y=frecuencia (Hz) · Z=intensidad
  • Espacio (rasgos):  X=brillo · Y=frecuencia · Z=ancho de banda

Autor: KALEVI LATVA AIJO ALEGRIA
"""
import os
import sys
import time
import numpy as np

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame,
    QFileDialog, QComboBox, QSlider, QCheckBox, QMessageBox,
)
import pyqtgraph.opengl as gl

WIN = 2048
HOP = 512
FMIN, FMAX = 200, 12000
CUBO = 100.0


def _guard_pythonw():
    # En modo pythonw (sin consola) sys.stdout/stderr son None. OJO: con pyqtgraph+OpenGL,
    # redirigir a os.devnull hace crashear la app -> usar un archivo temporal real.
    if sys.stdout is None or sys.stderr is None:
        import tempfile
        try:
            d = open(os.path.join(tempfile.gettempdir(), "visualizador_audio.log"), "w", encoding="utf-8")
        except Exception:
            d = open(os.devnull, "w")
        sys.stdout = sys.stdout or d
        sys.stderr = sys.stderr or d


def _norm(v, lo, hi):
    return np.clip((v - lo) / (hi - lo + 1e-9), 0, 1)


def color_por_freq(fn):
    """fn: array 0..1 -> RGBA (azul grave → rojo agudo)."""
    sp = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    rgb = np.array([[0.25, 0.35, 1.0], [0.0, 0.85, 1.0], [0.2, 1.0, 0.35],
                    [1.0, 0.85, 0.0], [1.0, 0.25, 0.25]])
    out = np.ones((len(fn), 4), dtype=np.float32)
    for c in range(3):
        out[:, c] = np.interp(fn, sp, rgb[:, c])
    return out


class Vista3D(gl.GLViewWidget):
    """Vista 3D con zoom (rueda) limitado: se puede acercar mucho, pero no alejar de más.
    El zoom es independiente del espaciado de los puntos."""
    DIST_MAX = 4000.0
    DIST_MIN = 2.0

    def _clamp(self):
        d = self.opts.get("distance", self.DIST_MAX)
        nd = min(max(d, self.DIST_MIN), self.DIST_MAX)
        if nd != d:
            self.setCameraPosition(distance=nd)

    def wheelEvent(self, ev):
        super().wheelEvent(ev)
        self._clamp()


class Reproductor:
    def __init__(self):
        self.data = None; self.sr = 44100; self.pos = 0; self.stream = None; self.playing = False

    def cargar(self, ruta):
        import soundfile as sf
        data, sr = sf.read(ruta, dtype="float32", always_2d=False)
        if data.ndim > 1:
            data = data.mean(axis=1)
        self.data = np.ascontiguousarray(data, dtype=np.float32); self.sr = sr; self.pos = 0

    @property
    def duracion(self):
        return len(self.data) / self.sr if self.data is not None else 0

    def _cb(self, outdata, frames, t, status):
        import sounddevice as sd
        if self.data is None or self.pos >= len(self.data):
            outdata[:] = 0; raise sd.CallbackStop
        end = min(self.pos + frames, len(self.data))
        ch = self.data[self.pos:end]
        outdata[:len(ch), 0] = ch
        if len(ch) < frames:
            outdata[len(ch):, 0] = 0
        self.pos = end

    def play(self, al_terminar=None):
        import sounddevice as sd
        if self.data is None:
            return
        if self.pos >= len(self.data):
            self.pos = 0
        self.stream = sd.OutputStream(samplerate=self.sr, channels=1, blocksize=1024,
                                      callback=self._cb, finished_callback=al_terminar)
        self.stream.start(); self.playing = True

    def pausa(self):
        if self.stream:
            self.stream.stop(); self.stream.close(); self.stream = None
        self.playing = False

    def detener(self):
        self.pausa(); self.pos = 0


class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizador de Voxel de Sonido")
        self.resize(1200, 760)
        self.setStyleSheet(QSS)
        self.rep = Reproductor()
        self.umbral_db = -55.0
        self.labels = []
        self._reset_datos()
        self._ui()
        self.timer = QTimer(self); self.timer.timeout.connect(self._tick)

    def _reset_datos(self):
        self.t = []; self.f0 = []; self.loud = []; self.cent = []; self.spread = []
        self._next = 0
        self._pos_cache = np.zeros((0, 3), dtype=np.float32)
        self.labels_pt = getattr(self, "labels_pt", [])
        self._last_lbl = 0.0

    # ---------- UI
    def _ui(self):
        root = QHBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        izq = QFrame(); izq.setObjectName("izq"); izq.setFixedWidth(295)
        L = QVBoxLayout(izq); L.setContentsMargins(20, 18, 20, 18); L.setSpacing(10)
        t = QLabel("🐦 Voxel de Sonido"); t.setObjectName("h1"); L.addWidget(t)
        sub = QLabel("Cada sonido es un punto en el espacio. La ruta del canto se dibuja mientras suena.")
        sub.setObjectName("sub"); sub.setWordWrap(True); L.addWidget(sub)

        self.b_cargar = QPushButton("📂  Abrir audio"); self.b_cargar.setObjectName("accent")
        self.b_cargar.clicked.connect(self._cargar); L.addWidget(self.b_cargar)
        self.f_lbl = QLabel("Ningún archivo"); self.f_lbl.setObjectName("sub"); self.f_lbl.setWordWrap(True); L.addWidget(self.f_lbl)

        fila = QHBoxLayout(); fila.setSpacing(8)
        self.b_play = QPushButton("▶"); self.b_play.setObjectName("accent"); self.b_play.clicked.connect(self._play_pause); self.b_play.setEnabled(False)
        self.b_stop = QPushButton("⏹"); self.b_stop.setObjectName("ghost"); self.b_stop.clicked.connect(self._detener); self.b_stop.setEnabled(False)
        fila.addWidget(self.b_play); fila.addWidget(self.b_stop); L.addLayout(fila)
        self.tiempo = QLabel("00:00 / 00:00"); self.tiempo.setObjectName("sub"); self.tiempo.setAlignment(Qt.AlignmentFlag.AlignCenter); L.addWidget(self.tiempo)

        L.addWidget(self._sep())
        L.addWidget(QLabel("Modo de espacio"))
        self.modo = QComboBox(); self.modo.addItems(["Ruta (tiempo · Hz · intensidad)",
                                                     "Espacio (brillo · Hz · ancho)"])
        self.modo.currentIndexChanged.connect(self._rebuild)
        self.modo.currentIndexChanged.connect(self._refrescar_ejes); L.addWidget(self.modo)

        self.chk_ruta = QCheckBox("Mostrar rutas"); self.chk_ruta.setChecked(True); self.chk_ruta.toggled.connect(self._rebuild); L.addWidget(self.chk_ruta)
        self.chk_voxel = QCheckBox("Voxelizar (rejilla)"); self.chk_voxel.toggled.connect(self._rebuild); L.addWidget(self.chk_voxel)
        self.chk_coord = QCheckBox("Ver coordenada de cada punto"); self.chk_coord.setChecked(False); self.chk_coord.toggled.connect(self._toggle_coord); L.addWidget(self.chk_coord)

        L.addWidget(QLabel("Estirar ejes (separa los puntos)"))
        r, self.sl_x = self._slider_eje("X"); L.addLayout(r)
        r, self.sl_y = self._slider_eje("Y"); L.addLayout(r)
        r, self.sl_z = self._slider_eje("Z"); L.addLayout(r)
        for s in (self.sl_x, self.sl_y, self.sl_z):
            s.valueChanged.connect(self._escala_cambio)

        L.addWidget(QLabel("Umbral de silencio (dB)"))
        self.sl_umbral = QSlider(Qt.Orientation.Horizontal); self.sl_umbral.setRange(-80, -20); self.sl_umbral.setValue(-55)
        self.sl_umbral.valueChanged.connect(self._umbral_cambio); L.addWidget(self.sl_umbral)
        self.lbl_umbral = QLabel("-55 dB"); self.lbl_umbral.setObjectName("sub"); L.addWidget(self.lbl_umbral)

        L.addWidget(QLabel("Tamaño de punto"))
        self.sl_tam = QSlider(Qt.Orientation.Horizontal); self.sl_tam.setRange(3, 26); self.sl_tam.setValue(3)
        self.sl_tam.valueChanged.connect(self._rebuild); L.addWidget(self.sl_tam)

        self.info = QLabel("Abre un audio y pulsa ▶ para ver la ruta formarse."); self.info.setObjectName("sub"); self.info.setWordWrap(True); L.addWidget(self.info)
        L.addStretch()
        self.leyenda = QLabel(""); self.leyenda.setObjectName("sub"); self.leyenda.setWordWrap(True); L.addWidget(self.leyenda)
        cred = QLabel("KALEVI LATVA AIJO ALEGRIA"); cred.setObjectName("cred"); cred.setAlignment(Qt.AlignmentFlag.AlignCenter); L.addWidget(cred)
        root.addWidget(izq)

        self.view = Vista3D(); self.view.setBackgroundColor("#000000")
        self.view.setCameraPosition(distance=520, elevation=22, azimuth=-70)
        # solo las 3 líneas de los ejes (X, Y, Z); se estiran junto con los puntos
        self.ejes_lineas = gl.GLLinePlotItem(pos=np.zeros((0, 3)), color=(0.55, 0.55, 0.55, 0.9),
                                             width=1.6, mode="lines", antialias=True)
        self.view.addItem(self.ejes_lineas)
        self.scatter = gl.GLScatterPlotItem(pos=np.zeros((0, 3)), size=1, pxMode=True); self.view.addItem(self.scatter)
        self.rutas = gl.GLLinePlotItem(pos=np.zeros((0, 3)), width=1.6, mode="lines", antialias=True); self.view.addItem(self.rutas)
        self.marcador = gl.GLScatterPlotItem(pos=np.zeros((0, 3)), size=24, color=(1, 1, 1, 1), pxMode=True); self.view.addItem(self.marcador)
        self._actualizar_ejes()
        root.addWidget(self.view, 1)

    def _sep(self):
        s = QFrame(); s.setObjectName("hr"); s.setFixedHeight(1); return s

    def _slider_eje(self, nombre):
        row = QHBoxLayout(); row.setContentsMargins(0, 0, 0, 0); row.setSpacing(8)
        lbl = QLabel(nombre); lbl.setObjectName("sub"); lbl.setFixedWidth(12)
        s = QSlider(Qt.Orientation.Horizontal); s.setRange(5, 60); s.setValue(15)   # 0.5x .. 6x
        row.addWidget(lbl); row.addWidget(s)
        return row, s

    # ---------- análisis de un frame
    def _prep(self):
        self._hann = np.hanning(WIN).astype(np.float32)
        fr = np.fft.rfftfreq(WIN, 1 / self.rep.sr)
        self._band = (fr >= FMIN) & (fr <= min(FMAX, self.rep.sr / 2))
        self._fsel = fr[self._band]

    def _frame(self, i):
        d = self.rep.data
        seg = d[i * HOP:i * HOP + WIN]
        if len(seg) < WIN:
            return None
        seg = seg * self._hann
        rms = np.sqrt(np.mean(seg * seg))
        db = 20 * np.log10(rms + 1e-9)
        if db < self.umbral_db:
            return None
        mag = np.abs(np.fft.rfft(seg))[self._band]
        s = mag.sum()
        if s < 1e-6:
            return None
        k = int(np.argmax(mag))
        cent = float((self._fsel * mag).sum() / s)
        spr = float(np.sqrt(((self._fsel - cent) ** 2 * mag).sum() / s))
        return i * HOP / self.rep.sr, float(self._fsel[k]), float(db), cent, spr

    # ---------- carga
    def _cargar(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Abrir audio",
                                              filter="Audio (*.mp3 *.wav *.flac *.ogg *.aiff);;Todos (*.*)")
        if not ruta:
            return
        try:
            self.rep.detener(); self.rep.cargar(ruta); self._prep()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No pude abrir el audio:\n{e}"); return
        self.f_lbl.setText(os.path.basename(ruta))
        self.b_play.setEnabled(True); self.b_stop.setEnabled(True)
        self._reset_datos(); self._rebuild(); self._actualizar_tiempo()
        self.info.setText("Listo. Pulsa ▶ y la ruta se dibujará mientras suena.")

    # ---------- construcción de la nube
    def _coords_de(self, t, f0, loud, cent, spread):
        fn = _norm(np.log10(f0 + 1), np.log10(FMIN), np.log10(FMAX))
        ln = _norm(loud, self.umbral_db, 0.0)
        if self.modo.currentIndex() == 0:
            dur = max(self.rep.duracion, 1e-6)
            x = np.clip(t / dur, 0, 1); y = fn; z = ln
            self.leyenda.setText("Ejes → X: tiempo · Y: frecuencia (Hz) · Z: intensidad\nColor: frecuencia · Tamaño: intensidad")
        else:
            x = _norm(cent, FMIN, FMAX); y = fn; z = _norm(spread, 0, (FMAX - FMIN) * 0.5)
            self.leyenda.setText("Ejes → X: brillo · Y: frecuencia (Hz) · Z: ancho de banda\nColor: frecuencia · Tamaño: intensidad")
        sx = self.sl_x.value() / 10.0; sy = self.sl_y.value() / 10.0; sz = self.sl_z.value() / 10.0
        pos = np.column_stack([x * sx, y * sy, z * sz]).astype(np.float32) * CUBO
        if self.chk_voxel.isChecked():
            for k, sk in enumerate((sx, sy, sz)):
                paso = (CUBO * sk) / 34.0
                pos[:, k] = np.round(pos[:, k] / paso) * paso
        col = color_por_freq(fn); col[:, 3] = np.clip(0.35 + ln * 0.65, 0, 1)
        tam = (self.sl_tam.value() * (0.5 + ln)).astype(np.float32)
        return pos, col, tam

    def _rebuild(self):
        if not self.t:
            self.scatter.setData(pos=np.zeros((0, 3))); self.rutas.setData(pos=np.zeros((0, 3)))
            self._pos_cache = np.zeros((0, 3), dtype=np.float32)
            return
        t = np.array(self.t, dtype=np.float32); f0 = np.array(self.f0, dtype=np.float32)
        loud = np.array(self.loud, dtype=np.float32); cent = np.array(self.cent, dtype=np.float32)
        spread = np.array(self.spread, dtype=np.float32)
        pos, col, tam = self._coords_de(t, f0, loud, cent, spread)
        self.scatter.setData(pos=pos, color=col, size=tam, pxMode=True)
        self._pos_cache = pos
        if self.chk_ruta.isChecked() and len(pos) > 1:
            gap = (HOP / self.rep.sr) * 4
            segs, segc = [], []
            for i in range(len(pos) - 1):
                if t[i + 1] - t[i] <= gap:
                    segs.append(pos[i]); segs.append(pos[i + 1])
                    c = col[i].copy(); c[3] = 0.5; segc.append(c); segc.append(c)
            if segs:
                self.rutas.setData(pos=np.array(segs, dtype=np.float32), color=np.array(segc, dtype=np.float32), mode="lines", width=1.8)
            else:
                self.rutas.setData(pos=np.zeros((0, 3)))
        else:
            self.rutas.setData(pos=np.zeros((0, 3)))
        # etiquetas por punto (con throttle para no trabar durante la reproducción)
        if self.chk_coord.isChecked() and ((not self.rep.playing) or (time.monotonic() - self._last_lbl > 0.5)):
            self._etiquetas_puntos()

    # ---------- ejes
    def _escalas(self):
        return self.sl_x.value() / 10.0, self.sl_y.value() / 10.0, self.sl_z.value() / 10.0

    def _actualizar_ejes(self):
        sx, sy, sz = self._escalas()
        X, Y, Z = CUBO * sx, CUBO * sy, CUBO * sz
        pos = np.array([[0, 0, 0], [X, 0, 0],
                        [0, 0, 0], [0, Y, 0],
                        [0, 0, 0], [0, 0, Z]], dtype=np.float32)
        self.ejes_lineas.setData(pos=pos, mode="lines")

    def _escala_cambio(self):
        self._actualizar_ejes()
        self._rebuild()

    def _refrescar_ejes(self):
        # Sin valores en los ejes (estilo limpio). Los valores se ven por punto
        # con la opción "Ver coordenada de cada punto".
        for lb in self.labels:
            self.view.removeItem(lb)
        self.labels = []

    # ---------- etiqueta (valor) por punto
    MAX_LABELS = 180

    def _fmt_hz(self, fr):
        return f"{fr/1000:.1f}k" if fr >= 1000 else f"{int(fr)}"

    def _etiquetas_puntos(self):
        for lb in self.labels_pt:
            self.view.removeItem(lb)
        self.labels_pt = []
        if not self.chk_coord.isChecked() or not self.t or len(self._pos_cache) == 0:
            return
        pos = self._pos_cache
        n = len(pos)
        paso = max(1, (n + self.MAX_LABELS - 1) // self.MAX_LABELS)   # submuestrea si hay muchos
        dz = CUBO * 0.03
        for i in range(0, n, paso):
            it = gl.GLTextItem(pos=np.array([pos[i, 0], pos[i, 1], pos[i, 2] + dz], dtype=np.float32),
                               text=self._fmt_hz(self.f0[i]), color=(240, 240, 240, 255))
            self.view.addItem(it); self.labels_pt.append(it)
        self._last_lbl = time.monotonic()

    def _toggle_coord(self, on):
        if on:
            self._etiquetas_puntos()
        else:
            for lb in self.labels_pt:
                self.view.removeItem(lb)
            self.labels_pt = []

    # ---------- reproducción / progresivo
    def _play_pause(self):
        if self.rep.data is None:
            return
        if self.rep.playing:
            self.rep.pausa(); self.timer.stop(); self.b_play.setText("▶")
        else:
            if self.rep.pos <= 0:
                self._reset_datos(); self._rebuild()
            self.rep.play(al_terminar=self._fin); self.timer.start(33); self.b_play.setText("⏸")

    def _detener(self):
        self.rep.detener(); self.timer.stop(); self.b_play.setText("▶")
        self._reset_datos(); self._rebuild()
        self.marcador.setData(pos=np.zeros((0, 3))); self._actualizar_tiempo()

    def _fin(self):
        QTimer.singleShot(0, lambda: (self.timer.stop(), self.b_play.setText("▶")))

    def _umbral_cambio(self, v):
        self.umbral_db = float(v); self.lbl_umbral.setText(f"{v} dB")

    def _tick(self):
        self._actualizar_tiempo()
        if self.rep.data is None:
            return
        objetivo = self.rep.pos
        nuevos = 0
        while (self._next * HOP + WIN) <= objetivo and nuevos < 400:
            r = self._frame(self._next)
            self._next += 1
            if r is not None:
                self.t.append(r[0]); self.f0.append(r[1]); self.loud.append(r[2]); self.cent.append(r[3]); self.spread.append(r[4])
                nuevos += 1
        if nuevos:
            self._rebuild()
            self.info.setText(f"{len(self.t)} puntos de sonido dibujados.")
        if len(self._pos_cache):
            self.marcador.setData(pos=self._pos_cache[-1:])

    def _fmt(self, s):
        return f"{int(s)//60:02d}:{int(s)%60:02d}"

    def _actualizar_tiempo(self):
        cur = self.rep.pos / self.rep.sr if self.rep.data is not None else 0
        self.tiempo.setText(f"{self._fmt(cur)} / {self._fmt(self.rep.duracion)}")


QSS = """
* { font-family: 'Segoe UI'; font-size: 13px; }
QWidget { background: #ffffff; color: #111111; }
QLabel { background: transparent; color: #111111; }
QFrame#izq { background: #ffffff; border-right: 1px solid #e6e6e6; }
QFrame#hr { background: #e6e6e6; }
QLabel#h1 { font-size: 18px; font-weight: 800; color: #000000; }
QLabel#sub { color: #6b6b6b; font-size: 12px; }
QLabel#cred { color: #b3b3b3; font-size: 10px; }
QPushButton { background: #ffffff; color: #111111; border: 1px solid #d0d0d0; border-radius: 10px; padding: 11px 14px; font-weight: 700; font-size: 15px; }
QPushButton:hover { background: #f2f2f2; }
QPushButton:disabled { color: #bcbcbc; border-color: #eeeeee; }
QPushButton#accent { background: #111111; color: #ffffff; border: 1px solid #111111; }
QPushButton#accent:hover { background: #2b2b2b; }
QPushButton#accent:disabled { background: #cfcfcf; color: #ffffff; border-color: #cfcfcf; }
QPushButton#ghost { background: #ffffff; color: #111111; border: 1px solid #d0d0d0; }
QPushButton#ghost:hover { background: #f2f2f2; }
QComboBox { background: #ffffff; border: 1px solid #d0d0d0; border-radius: 8px; padding: 7px 10px; color: #111111; }
QComboBox QAbstractItemView { background: #ffffff; color: #111111; selection-background-color: #111111; selection-color: #ffffff; }
QCheckBox { color: #111111; }
QSlider::groove:horizontal { height: 4px; background: #e0e0e0; border-radius: 2px; }
QSlider::handle:horizontal { background: #111111; width: 16px; margin: -7px 0; border-radius: 8px; }
"""


def main():
    _guard_pythonw()
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    v = Ventana(); v.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
