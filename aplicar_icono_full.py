from pathlib import Path
from PIL import Image, ImageOps, ImageChops
import re

SRC = Path("icono_crnl_full.png")
RES = Path("app/src/main/res")
MANIFEST = Path("app/src/main/AndroidManifest.xml")
GRADLE = Path("app/build.gradle")

if not SRC.exists():
    raise SystemExit("Falta icono_crnl_full.png")

for p in (RES, MANIFEST, GRADLE):
    if not p.exists():
        raise SystemExit("Falta " + str(p))


# -------------------------------------------------------
# CARGAR IMAGEN ORIGINAL
# -------------------------------------------------------

im = Image.open(SRC).convert("RGBA")


# -------------------------------------------------------
# RECORTAR AUTOMATICAMENTE EL MARGEN EXTERIOR
# -------------------------------------------------------
# Se toma el color de las esquinas como fondo.
# Despues se localiza la zona realmente ocupada por
# la ilustracion y se elimina el espacio sobrante.
# -------------------------------------------------------

corner_pixels = [
    im.getpixel((0, 0)),
    im.getpixel((im.width - 1, 0)),
    im.getpixel((0, im.height - 1)),
    im.getpixel((im.width - 1, im.height - 1)),
]

bg_color = tuple(
    sum(pixel[i] for pixel in corner_pixels) // 4
    for i in range(4)
)

background = Image.new(
    "RGBA",
    im.size,
    bg_color
)

difference = ImageChops.difference(
    im,
    background
).convert("L")

# Ignorar pequenas variaciones del fondo
difference = difference.point(
    lambda x: 255 if x > 18 else 0
)

bbox = difference.getbbox()

if bbox:
    left, top, right, bottom = bbox

    # Pequeno margen de seguridad
    margin_x = max(2, int((right - left) * 0.015))
    margin_y = max(2, int((bottom - top) * 0.015))

    left = max(0, left - margin_x)
    top = max(0, top - margin_y)
    right = min(im.width, right + margin_x)
    bottom = min(im.height, bottom + margin_y)

    im = im.crop(
        (left, top, right, bottom)
    )


# -------------------------------------------------------
# HACER EL RECORTE CUADRADO
# -------------------------------------------------------

side = min(im.width, im.height)

left = (im.width - side) // 2
top = (im.height - side) // 2

im = im.crop(
    (
        left,
        top,
        left + side,
        top + side
    )
)


# -------------------------------------------------------
# GENERAR ICONOS ANDROID
# -------------------------------------------------------

sizes = [
    ("mdpi", 48),
    ("hdpi", 72),
    ("xhdpi", 96),
    ("xxhdpi", 144),
    ("xxxhdpi", 192),
]

for density, size in sizes:

    out = RES / f"mipmap-{density}"
    out.mkdir(
        parents=True,
        exist_ok=True
    )

    icon = ImageOps.fit(
        im,
        (size, size),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    ).convert("RGB")

    icon.save(
        out / "ic_launcher.png",
        quality=100
    )


# -------------------------------------------------------
# GUARDAR TAMBIEN VERSION GRANDE
# -------------------------------------------------------

assets = Path("app/src/main/assets")
assets.mkdir(
    parents=True,
    exist_ok=True
)

large_icon = ImageOps.fit(
    im,
    (1024, 1024),
    method=Image.Resampling.LANCZOS,
    centering=(0.5, 0.5)
).convert("RGB")

large_icon.save(
    assets / "icono_crnl_full.png",
    quality=100
)


# -------------------------------------------------------
# FORZAR USO DEL ICONO BITMAP
# -------------------------------------------------------

manifest = MANIFEST.read_text(
    encoding="utf-8"
)

manifest = re.sub(
    r'android:icon="[^"]+"',
    'android:icon="@mipmap/ic_launcher"',
    manifest
)

if "android:roundIcon=" in manifest:

    manifest = re.sub(
        r'android:roundIcon="[^"]+"',
        'android:roundIcon="@mipmap/ic_launcher"',
        manifest
    )

else:

    manifest = manifest.replace(
        "<application ",
        '<application android:roundIcon="@mipmap/ic_launcher" ',
        1
    )

MANIFEST.write_text(
    manifest,
    encoding="utf-8"
)


# -------------------------------------------------------
# AUMENTAR VERSIONCODE
# -------------------------------------------------------

gradle = GRADLE.read_text(
    encoding="utf-8"
)

match = re.search(
    r"versionCode\s+(\d+)",
    gradle
)

code = (
    int(match.group(1)) + 1
    if match
    else 28
)

gradle = re.sub(
    r"versionCode\s+\d+",
    f"versionCode {code}",
    gradle,
    count=1
)

GRADLE.write_text(
    gradle,
    encoding="utf-8"
)


print(
    "OK: icono CRNL recortado y ampliado. "
    "La ilustracion ocupa toda la superficie disponible."
)

print(
    "versionCode",
    code
)
