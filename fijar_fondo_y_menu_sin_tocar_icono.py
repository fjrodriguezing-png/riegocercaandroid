from pathlib import Path
import re,hashlib,sys
H=Path('app/src/main/assets/index.html');M=Path('app/src/main/AndroidManifest.xml');R=Path('app/src/main/res');G=Path('app/build.gradle')
for p in (H,M,R,G):
    if not p.exists():raise SystemExit('Falta '+str(p))
# Lock icon + manifest. This patch cannot change them.
locked=[M]+[p for p in R.rglob('*') if p.is_file() and ('icon' in p.name.lower() or 'launcher' in p.name.lower())]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in locked}
h=H.read_text(encoding='utf-8')
# Permanent background: create exact fixed IMG if absent; use same file as splash.
if 'id="crnlPermanentBg"' not in h:
    h=h.replace('<body>','<body><img id="crnlPermanentBg" src="splash_nova_limia.jpg" alt="">',1)
# Explicitly keep app content above the fixed bg, and ensure same cover+center as splash.
css='''#crnlPermanentBg{position:fixed!important;z-index:-10!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;object-fit:cover!important;object-position:center center!important;display:block!important;pointer-events:none!important}body{background:#000!important;background-image:none!important}body:before{background:rgba(244,247,250,.18)!important;z-index:-9!important}main{position:relative!important;z-index:1!important}.menu-panel{position:fixed!important;z-index:500!important;left:12px!important;right:12px!important;top:88px!important;width:auto!important;max-width:760px!important;margin:0 auto!important;padding:14px!important;background:rgba(255,255,255,.95)!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important;border-radius:22px!important;box-shadow:0 18px 48px rgba(0,0,0,.30)!important;backdrop-filter:blur(5px)!important}.menu-panel.hidden{display:none!important}.menu-panel button{aspect-ratio:1/1!important;margin:0!important;padding:10px!important;border-radius:18px!important;display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;font-weight:800!important;background:#f4f8fa!important;border:1px solid #dbe5ec!important;color:#142738!important}@media(min-width:620px){.menu-panel{grid-template-columns:repeat(3,minmax(0,1fr))!important}.menu-panel button{aspect-ratio:1.15/1!important}}'''
# Append always, with unique marker, making it last CSS and therefore winning cascade.
if 'id="crnlVisualFixStyles"' not in h:
    h=h.replace('</head>','<style id="crnlVisualFixStyles">'+css+'</style></head>',1)
# Remove WhatsApp only from main menu so it cannot occupy a grid tile.
a=h.find('<div id="menuPanel"');se=h.find('</section>',a)
if a<0 or se<0:raise SystemExit('No encuentro seccion menuPanel')
seg=h[a:se]
seg=re.sub(r'<button\b[^>]*>.*?WhatsApp.*?</button>','',seg,flags=re.I|re.S)
seg=re.sub(r'<button\b(?=[^>]*(?:id|data-menu)="[^"]*(?:whatsapp|whats)[^"]*")[^>]*>.*?</button>','',seg,flags=re.I|re.S)
h=h[:a]+seg+h[se:]
H.write_text(h,encoding='utf-8')
# bump only version code
b=G.read_text();mt=re.search(r'versionCode\s+(\d+)',b);code=int(mt.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1))
# Verify locked icon unchanged.
for ps,d in hashes.items():
    p=Path(ps)
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=d:raise SystemExit('ICONO/MANIFEST CAMBIADO: '+ps)
# Hard visual checks from final text; no brittle old CSS test.
h=H.read_text();a=h.find('<div id="menuPanel"');se=h.find('</section>',a);menu=h[a:se].lower()
checks={
 'fondo fijo real':'id="crnlPermanentBg"' in h,
 'mismo archivo splash':'src="splash_nova_limia.jpg"' in h,
 'cover center':'object-fit:cover!important' in h and 'object-position:center center!important' in h,
 'menu grid css al final':'id="crnlVisualFixStyles"' in h and 'display:grid!important' in h,
 '2 columnas movil':'grid-template-columns:repeat(2,minmax(0,1fr))!important' in h,
 'WhatsApp no menu':'whatsapp' not in menu,
 'WhatsApp contextual':'elementActionWhatsApp' in h,
 'icono intacto':True,
}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
print('FIX VISUAL EXACTO OK; versionCode',code)
