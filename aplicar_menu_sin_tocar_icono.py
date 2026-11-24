from pathlib import Path
import re, hashlib, json
H=Path('app/src/main/assets/index.html'); M=Path('app/src/main/AndroidManifest.xml'); R=Path('app/src/main/res'); G=Path('app/build.gradle')
for p in (H,M,R,G):
    if not p.exists(): raise SystemExit('Falta '+str(p))
# Snapshot manifest and ALL image/vector launcher-like resources. They MUST remain byte-identical.
protected=[M]
for p in R.rglob('*'):
    if p.is_file() and ('icon' in p.name.lower() or 'launcher' in p.name.lower()): protected.append(p)
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
h=H.read_text(encoding='utf-8')
# Menu grid override only.
css='''.menu-panel{position:fixed!important;left:12px!important;right:12px!important;top:88px!important;width:auto!important;max-width:760px!important;margin:0 auto!important;padding:14px!important;background:rgba(255,255,255,.94)!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important;border-radius:22px!important;box-shadow:0 18px 48px rgba(0,0,0,.28)!important;backdrop-filter:blur(5px)!important}.menu-panel.hidden{display:none!important}.menu-panel button{aspect-ratio:1.08/1!important;margin:0!important;padding:12px 8px!important;border-radius:18px!important;display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;font-weight:800!important;background:#f4f8fa!important;border:1px solid #dbe5ec!important;color:#142738!important}@media(min-width:620px){.menu-panel{grid-template-columns:repeat(3,minmax(0,1fr))!important}}'''
if 'grid-template-columns:repeat(2,minmax(0,1fr))!important' not in h:
    h=h.replace('</style>',css+'</style>',1)
# Remove WhatsApp button ONLY inside menuPanel.
a=h.find('<div id="menuPanel"');b=h.find('</div>',a)
if a<0 or b<0: raise SystemExit('No encuentro menuPanel')
menu=h[a:b]
menu=re.sub(r'<button\b[^>]*>.*?WhatsApp.*?</button>','',menu,flags=re.I|re.S)
menu=re.sub(r'<button\b[^>]*(?:id|data-menu)="[^"]*whats?[^"]*"[^>]*>.*?</button>','',menu,flags=re.I|re.S)
h=h[:a]+menu+h[b:]
H.write_text(h,encoding='utf-8')
# versionCode only
btxt=G.read_text(); mt=re.search(r'versionCode\s+(\d+)',btxt); code=int(mt.group(1))+1 if mt else 1
G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',btxt,1))
# Verify untouched icon/manifest byte-for-byte.
for pstr,digest in before.items():
    p=Path(pstr)
    if not p.exists(): raise SystemExit('ERROR: se elimino recurso de icono: '+pstr)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=digest: raise SystemExit('ERROR: se modifico icono/manifest: '+pstr)
# Verify UI requested.
h2=H.read_text();a=h2.index('<div id="menuPanel"');b=h2.index('</div>',a);menu2=h2[a:b].lower()
assert 'whatsapp' not in menu2
assert 'grid-template-columns:repeat(2,minmax(0,1fr))!important' in h2
if 'elementActionWhatsApp' not in h2: print('AVISO: el proyecto actual no contiene elementActionWhatsApp; el parche no lo inventa ni lo elimina')
print('OK: icono actual CONSERVADO byte a byte; menu cuadrados; WhatsApp quitado del menu. versionCode',code)
