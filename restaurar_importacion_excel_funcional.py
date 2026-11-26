from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
if not p.exists():
    raise SystemExit('No existe app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# 1) Restore the exact old working flow: menu icon opens Datos screen, then the HTML file input is used.
patterns = [
    r'<button\s+id="importMenu"\s+class="menu-tile"[^>]*>\s*<img\s+src="xlsx\.jfif"[^>]*>\s*</button>',
    r'<button\s+[^>]*id="importMenu"[^>]*>.*?</button>',
]
replacement = '<button data-go="datos" class="menu-tile" aria-label="Importar datos" title="Importar datos"><img src="xlsx.jfif" alt="Importar datos"></button>'
changed = False
for pat in patterns:
    ns, n = re.subn(pat, replacement, s, count=1, flags=re.S)
    if n:
        s = ns
        changed = True
        break
# If already restored, leave it.
if 'data-go="datos"' in s and 'xlsx.jfif' in s:
    changed = True
if not changed:
    raise SystemExit('No localizo el boton Importar actual; no modifico el archivo para evitar regresiones.')

# 2) Restore SheetJS exactly as in the previously working version.
cdn = '<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>'
if 'xlsx.full.min.js' not in s:
    s = s.replace('</style>', '</style>' + cdn, 1)

# 3) Remove only the native direct-import JS block introduced later, if present.
# The old working route must remain: $('#file').onchange -> XLSX.read(...)
s = re.sub(r"\$\('#importMenu'\)\.onclick=.*?(?=\$\('#earthMenu'\)\.onclick)", '', s, count=1, flags=re.S)
s = re.sub(r"window\.receiveImportedRows=.*?(?=\$\('#earthMenu'\)\.onclick)", '', s, count=1, flags=re.S)
s = re.sub(r"window\.importError=.*?(?=\$\('#earthMenu'\)\.onclick)", '', s, count=1, flags=re.S)

# Hard checks: old importer + current menu visuals/features must coexist.
required = [
    'data-go="datos"', 'xlsx.jfif', 'destino.png', 'google earth.jfif',
    'id="file" type="file"', 'XLSX.read', "$('#file').onchange",
    'splash_nova_limia.jpg', 'earthMenu', 'AndroidMaps', 'id="aWa"'
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit('Faltan elementos obligatorios tras el parche: ' + ', '.join(missing))

p.write_text(s, encoding='utf-8')
print('OK: restaurada importacion antigua funcional mediante input file + XLSX.read')
print('OK: menu e iconos XLSX/Destino/Google Earth conservados')
print('OK: splash, fondo, Maps, Earth y WhatsApp conservados')
