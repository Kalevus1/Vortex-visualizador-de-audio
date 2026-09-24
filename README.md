# 🐦 Visualizador de Voxel de Sonido

Autor / Author / Tekijä: **KALEVI LATVA AIJO ALEGRIA** · Windows · 100 % local

> 🇪🇸 Español · 🇬🇧 English · 🇫🇮 Suomi — el mismo documento en tres idiomas más abajo.

---

## 🇪🇸 Español

Convierte cada instante de un sonido en un **punto en un espacio 3D**, ubicado por sus
características (frecuencia, intensidad, brillo…). Al unir los puntos en el tiempo se ven las
**rutas** del sonido — pensado para estudiar el **canto de las aves**: cada canto tiene un patrón
y un lugar, y aquí se ven como puntos y trayectorias en el espacio. La ruta se **dibuja en vivo**
mientras suena el audio.

Es una visualización **"5D"**: 3 ejes (X, Y, Z) + **color** (frecuencia) + **tamaño** (intensidad).

### ✨ Qué hace
- **Modo Ruta**: X = tiempo · Y = frecuencia (Hz) · Z = intensidad → el recorrido del canto.
- **Modo Espacio**: X = brillo · Y = frecuencia · Z = ancho de banda → los sonidos que se repiten
  se agrupan en "lugares" (el patrón).
- **Estirar ejes** (X, Y, Z por separado) para separar los puntos; **zoom** aparte con la rueda.
- **Voxelizar** (rejilla), **umbral de silencio**, y **ver la coordenada** (Hz) sobre cada punto.
- Estilo **minimalista blanco y negro**: el único color está en la nube/ruta del sonido.

### ▶️ Cómo usarlo
1. Ejecuta **`instalar.bat`** una vez.
2. Abre con **`Abrir-visualizador.bat`**.
3. **📂 Abrir audio** (mp3/wav/flac/ogg) → **▶** y mira la ruta formarse. Gira/zoom con el mouse.

### 🔨 Generar el .exe
`crear_exe.bat` crea **dos** versiones: **carpeta** (`dist\Visualizador\`) y **empaquetada**
(`dist\Visualizador.exe`).

---

## 🇬🇧 English

Turns each instant of a sound into a **point in 3D space**, placed by its features (frequency,
loudness, brightness…). Connecting the points over time reveals the **routes** of the sound —
made to study **bird song**: each call has a pattern and a place, shown here as points and
trajectories in space. The route is **drawn live** as the audio plays.

It is a **"5D"** visualization: 3 axes (X, Y, Z) + **color** (frequency) + **size** (loudness).

### ✨ What it does
- **Route mode**: X = time · Y = frequency (Hz) · Z = loudness → the path of the song.
- **Space mode**: X = brightness · Y = frequency · Z = bandwidth → repeated sounds cluster into
  "places" (the pattern).
- **Stretch axes** (X, Y, Z independently) to spread the points; **zoom** separately with the wheel.
- **Voxelize** (grid), **silence threshold**, and **show the coordinate** (Hz) above each point.
- **Minimalist black & white** style: the only color is in the sound cloud/route.

### ▶️ How to use
1. Run **`instalar.bat`** once.
2. Open with **`Abrir-visualizador.bat`**.
3. **📂 Open audio** (mp3/wav/flac/ogg) → **▶** and watch the route form. Rotate/zoom with the mouse.

### 🔨 Build the .exe
`crear_exe.bat` builds **two** versions: **folder** (`dist\Visualizador\`) and **single-file**
(`dist\Visualizador.exe`).

---

## 🇫🇮 Suomi

Muuttaa äänen jokaisen hetken **pisteeksi 3D-tilassa**, sijoitettuna sen ominaisuuksien mukaan
(taajuus, voimakkuus, kirkkaus…). Kun pisteet yhdistetään ajassa, näkyvät äänen **reitit** —
tarkoitettu **linnunlaulun** tutkimiseen: jokaisella laululla on kuvio ja paikka, jotka näkyvät
tässä pisteinä ja liikeratoina tilassa. Reitti **piirtyy suorana** äänen soidessa.

Se on **"5D"**-visualisointi: 3 akselia (X, Y, Z) + **väri** (taajuus) + **koko** (voimakkuus).

### ✨ Mitä se tekee
- **Reitti-tila**: X = aika · Y = taajuus (Hz) · Z = voimakkuus → laulun reitti.
- **Tila-tila**: X = kirkkaus · Y = taajuus · Z = kaistanleveys → toistuvat äänet ryhmittyvät
  "paikkoihin" (kuvio).
- **Venytä akseleita** (X, Y, Z erikseen) erottaaksesi pisteet; **zoomaus** erikseen rullalla.
- **Voxelointi** (ruudukko), **hiljaisuuden kynnys** ja **koordinaatin näyttö** (Hz) kunkin
  pisteen päällä.
- **Minimalistinen mustavalkoinen** tyyli: ainoa väri on äänipilvessä/reitissä.

### ▶️ Käyttö
1. Aja **`instalar.bat`** kerran.
2. Avaa **`Abrir-visualizador.bat`**-tiedostolla.
3. **📂 Avaa ääni** (mp3/wav/flac/ogg) → **▶** ja katso reitin muodostuvan. Pyöritä/zoomaa hiirellä.

### 🔨 Luo .exe
`crear_exe.bat` luo **kaksi** versiota: **kansio** (`dist\Visualizador\`) ja **yhden tiedoston**
(`dist\Visualizador.exe`).

---

## 🧩 Tecnología / Technology / Teknologia

**Python** · **PySide6** (Qt 6) · **pyqtgraph** + **PyOpenGL** (3D en tiempo real) ·
**sounddevice** (reproducción) · **soundfile** · **NumPy** (FFT).

## 🌐 Web / Pages

La visualización 3D en tiempo real **no se replica en la web** (necesita OpenGL y audio local),
así que la carpeta `web/` y la página de GitHub Pages (`docs/`) son una **presentación
informativa** del proyecto, no la app en sí.

---

Hecho con cariño para ver el canto de las aves — **KALEVI LATVA AIJO ALEGRIA**
