from pathlib import Path

root = Path('.')
java_dir = root / 'app/src/main/java/es/riegocerca/maps'
assets = root / 'app/src/main/assets'
main = java_dir / 'MainActivity.java'
imp = java_dir / 'ImportBridge.java'
native = java_dir / 'NativeTabularImporter.java'
index = assets / 'index.html'

required = [main, imp, native, index]
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit('FALTAN ARCHIVOS DEL PROYECTO: ' + ', '.join(missing))

# Verify the currently integrated native import path is present, without rebuilding UI/menu.
main_text = main.read_text(encoding='utf-8')
index_text = index.read_text(encoding='utf-8')
imp_text = imp.read_text(encoding='utf-8')
native_text = native.read_text(encoding='utf-8')

checks = {
    'AndroidImport registrado': 'AndroidImport' in main_text and 'ImportBridge' in main_text,
    'onActivityResult presente': 'onActivityResult' in main_text,
    'NativeTabularImporter invocado': 'NativeTabularImporter' in main_text and '.read(uri)' in main_text,
    'ImportBridge importFile': 'importFile()' in imp_text,
    'Parser XLSX nativo': 'ZipInputStream' in native_text and 'sheet1.xml' in native_text,
    'Recepcion JS': 'receiveImportedRows' in index_text,
}
for label, ok in checks.items():
    print(('OK' if ok else 'ERROR') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('La ruta de importacion nativa no esta completa en el proyecto actual.')

# Remove the remote XLSX dependency so the current app cannot fall back to the old CDN path.
old = '<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>'
if old in index_text:
    index_text = index_text.replace(old, '')
    index.write_text(index_text, encoding='utf-8')
    print('OK: eliminada dependencia remota xlsx.full.min.js')
else:
    print('OK: no existe dependencia remota xlsx.full.min.js')

# Final hard gate: do not alter menu, splash, background, Maps/Earth/WhatsApp.
index_text = index.read_text(encoding='utf-8')
for token in ['xlsx.jfif','destino.png','google earth.jfif','splash_nova_limia.jpg','earthMenu','aWa','AndroidMaps']:
    if token not in index_text:
        raise SystemExit('ERROR: falta elemento existente que debe conservarse: ' + token)
print('OK: menu actual, splash, fondo, Maps, Earth y WhatsApp conservados')
