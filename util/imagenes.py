"""Carga de imágenes de platos y personal (con Pillow si está instalado)."""
import os
import re
import unicodedata
import tkinter as tk

try:
    from PIL import Image, ImageOps, ImageTk
    HAY_PILLOW = True
except ImportError:
    HAY_PILLOW = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_PLATOS = os.path.join(BASE, "img", "platos")
CARPETA_PERSONAL = os.path.join(BASE, "img", "personal")
EXTENSIONES = (".png", ".jpg", ".jpeg", ".gif", ".webp")
_cache = {}


def slug(texto):
    """'Arroz Chaufa de Pollo' -> 'arroz-chaufa-de-pollo'."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def _buscar(carpeta, nombre):
    for ext in EXTENSIONES:
        ruta = os.path.join(carpeta, nombre + ext)
        if os.path.exists(ruta):
            return ruta
    return None


def _absoluta(ruta):
    if not ruta:
        return None
    ruta = ruta if os.path.isabs(ruta) else os.path.join(BASE, ruta)
    return ruta if os.path.exists(ruta) else None


def ruta_plato(plato):
    """Usa Plato.imagen si existe; si no, busca img/platos/<nombre-del-plato>.png/.jpg"""
    return _absoluta(plato.imagen) or _buscar(CARPETA_PLATOS, slug(plato.nombre))


def ruta_usuario(usuario):
    return _absoluta(usuario.foto) or _buscar(CARPETA_PERSONAL, str(usuario.id))


def cargar(ruta, ancho, alto):
    """Devuelve un PhotoImage recortado a ancho x alto, o None si no se puede."""
    if not ruta:
        return None
    clave = (ruta, ancho, alto, os.path.getmtime(ruta))
    if clave in _cache:
        return _cache[clave]
    img = None
    try:
        if HAY_PILLOW:
            with Image.open(ruta) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                img = ImageTk.PhotoImage(ImageOps.fit(im, (ancho, alto)))
        elif ruta.lower().endswith((".png", ".gif")):
            foto = tk.PhotoImage(file=ruta)
            factor = max(1, foto.width() // ancho, foto.height() // alto)
            img = foto.subsample(factor, factor) if factor > 1 else foto
    except Exception:
        img = None
    _cache[clave] = img
    return img
