from pathlib import Path
import re,hashlib
H=Path('app/src/main/assets/index.html');G=Path('app/build.gradle')
if not H.exists():raise SystemExit('Falta '+str(H))
# Snapshot launcher icons before any change, and refuse any icon mutation.
icons=list(Path('app/src/main/res').glob('mipmap-*/ic_launcher.png'))
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in icons}
h=H.read_text(encoding='utf-8')
# Preserve exact splash photo and framing as main background.
h=re.sub(r"background:#(?:f3f7fa|000) url\('[^']+'\) [^;]+;", "background:#000 url('splash_nova_limia.jpg') center center/cover fixed no-repeat;",h,count=1)
if "url('splash_nova_limia.jpg')" not in h:h=h.replace('body{margin:0;',"body{margin:0;background:#000 url('splash_nova_limia.jpg') center center/cover fixed no-repeat;",1)
h=re.sub(r'body\{background-position:left center;background-size:auto 100%;background-color:#eef4f1\}', 'body{background-position:center center;background-size:cover;background-attachment:fixed;background-color:#eef4f1}',h)
# Tile menu styling only. Does not alter menu items, WA, Earth, Maps, splash JS, icons.
css='''.menu-panel{position:fixed!important;left:12px!important;right:12px!important;top:88px!important;width:auto!important;max-width:760px;margin:0 auto;padding:14px!important;background:rgba(255,255,255,.94)!important;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;border-radius:22px!important;box-shadow:0 18px 48px rgba(0,0,0,.28)!important;backdrop-filter:blur(5px)}.menu-panel.hidden{display:none!important}.menu-panel button{aspect-ratio:1.1/1;margin:0!important;padding:14px 10px!important;border-radius:18px!important;text-align:center!important;display:flex;align-items:center;justify-content:center;font-weight:800!important;font-size:15px;line-height:1.25;background:rgba(244,248,250,.96)!important;border:1px solid #dbe5ec!important;color:#142738!important}.menu-panel button:active{transform:scale(.98);background:#eaf3ef!important}@media(min-width:620px){.menu-panel{grid-template-columns:repeat(3,minmax(0,1fr));top:98px!important}.menu-panel button{aspect-ratio:1.25/1}}'''
if 'grid-template-columns:repeat(2,minmax(0,1fr))' not in h:h=h.replace('</style>',css+'</style>',1)
H.write_text(h,encoding='utf-8')
# version only
if G.exists():
 g=G.read_text();m=re.search(r'versionCode\s+(\d+)',g);n=int(m.group(1))+1 if m else 1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {n}',g,1))
# verify icon byte-for-byte unchanged
for pstr,digest in before.items():
 p=Path(pstr)
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise SystemExit('ERROR: icono modificado: '+pstr)
print('OK: fondo/menu aplicados; iconos launcher NO modificados')
