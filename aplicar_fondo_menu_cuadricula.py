from pathlib import Path
import re
H=Path('app/src/main/assets/index.html'); G=Path('app/build.gradle')
if not H.exists(): raise SystemExit('Falta app/src/main/assets/index.html')
h=H.read_text(encoding='utf-8')
# Same visual framing as splash: fixed full-screen img equivalent = cover + center, no mobile override movement.
# Replace body backgrounds and remove mobile position/size overrides that move/crop differently.
h=re.sub(r"background:#f3f7fa url\('[^']+'\) [^;]+;", "background:#000 url('splash_nova_limia.jpg') center center/cover fixed no-repeat;", h, count=1)
if "url('splash_nova_limia.jpg')" not in h:
    h=h.replace('body{margin:0;', "body{margin:0;background:#000 url('splash_nova_limia.jpg') center center/cover fixed no-repeat;",1)
h=re.sub(r'@media\(max-width:600px\)\{body\{background-position:[^}]+\}', '@media(max-width:600px){body{background-position:center center;background-size:cover;background-attachment:fixed}', h, count=1)
# menu panel becomes screen-wide grid of square-ish tiles, overlaying application background.
css='''.menu-panel{position:fixed!important;left:12px!important;right:12px!important;top:88px!important;width:auto!important;max-width:760px;margin:0 auto;padding:14px!important;background:rgba(255,255,255,.94)!important;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;border-radius:22px!important;box-shadow:0 18px 48px rgba(0,0,0,.28)!important;backdrop-filter:blur(5px)}.menu-panel.hidden{display:none!important}.menu-panel button{aspect-ratio:1.1/1;margin:0!important;padding:14px 10px!important;border-radius:18px!important;text-align:center!important;display:flex;align-items:center;justify-content:center;font-weight:800!important;font-size:15px;line-height:1.25;background:rgba(244,248,250,.96)!important;border:1px solid #dbe5ec!important;color:#142738!important}.menu-panel button:active{transform:scale(.98);background:#eaf3ef!important}@media(min-width:620px){.menu-panel{grid-template-columns:repeat(3,minmax(0,1fr));top:98px!important}.menu-panel button{aspect-ratio:1.25/1}}'''
# append after existing styles so it wins cascade
h=h.replace('</style>',css+'</style>',1)
H.write_text(h,encoding='utf-8')
# bump version
g=G.read_text();m=re.search(r'versionCode\s+(\d+)',g);n=int(m.group(1))+1 if m else 27;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {n}',g,1));print('versionCode',n)
# checks
h=H.read_text();
for x in ["url('splash_nova_limia.jpg')",'grid-template-columns:repeat(2','position:fixed!important','aspect-ratio:1.1/1','menu-panel.hidden{display:none!important}']:
    if x not in h: raise SystemExit('Falta '+x)
print('OK FONDO FIJO + MENU CUADRICULA')
