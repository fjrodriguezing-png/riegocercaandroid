from pathlib import Path
import re, hashlib, sys
H=Path('app/src/main/assets/index.html'); M=Path('app/src/main/AndroidManifest.xml'); R=Path('app/src/main/res'); G=Path('app/build.gradle')
for p in (H,M,R,G):
    if not p.exists(): raise SystemExit('Falta '+str(p))
# Bloquear icono y manifest byte a byte.
locked=[M]+[p for p in R.rglob('*') if p.is_file() and ('icon' in p.name.lower() or 'launcher' in p.name.lower())]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in locked}
h=H.read_text(encoding='utf-8')
# Localizar splash por DOM, sin depender de un texto exacto del temporizador.
if 'id="appSplash"' not in h: raise SystemExit('No existe appSplash en este proyecto')
# Insertar un temporizador robusto justo antes de </body>. Cancela/neutraliza el efecto visual de timers antiguos
# convirtiendo el MISMO splash en fondo tras 3s y forzando sus estilos con !important.
robust="""<script id=\"crnlSplashBackgroundFix\">(function(){function keepSameImage(){var s=document.getElementById('appSplash');if(!s)return;s.classList.remove('splash-out');s.classList.add('become-background');s.style.setProperty('opacity','1','important');s.style.setProperty('visibility','visible','important');var sh=s.querySelector('.splash-shade');var t=s.querySelector('.splash-title');if(sh)sh.style.display='none';if(t)t.style.display='none';}window.setTimeout(keepSameImage,3000);window.setTimeout(keepSameImage,3400);})();</script>"""
if 'id="crnlSplashBackgroundFix"' not in h:h=h.replace('</body>',robust+'</body>',1)
css=""".app-splash.become-background{position:fixed!important;z-index:-3!important;inset:0!important;opacity:1!important;visibility:visible!important;animation:none!important;pointer-events:none!important}.app-splash.become-background img{width:100%!important;height:100%!important;object-fit:cover!important;object-position:center center!important;display:block!important}.app-splash.become-background~main{position:relative!important;z-index:1!important}body{background:#000!important;background-image:none!important}body:before{background:none!important}.app-splash.become-background .splash-title,.app-splash.become-background .splash-shade{display:none!important}"""
if '.app-splash.become-background{' not in h:h=h.replace('</style>',css+'</style>',1)
# Quitar reglas de fondo movil que generan otro encuadre.
h=re.sub(r'body\{background-position:[^}]*\}', 'body{background:#000!important;background-image:none!important}', h)
h=re.sub(r"background-image\s*:\s*url\([^;]+;?",'background-image:none!important;',h)
# WhatsApp: localizar el panel de menu de manera estructural hasta </section>, no hasta el primer div.
a=h.find('<div id="menuPanel"')
if a<0: raise SystemExit('No existe menuPanel')
sec_end=h.find('</section>',a)
if sec_end<0: raise SystemExit('No se encontro cierre del section del menu')
seg=h[a:sec_end]
# Eliminar botones que tengan WhatsApp en texto o atributo, permitiendo emojis/spans.
seg=re.sub(r'<button\b[^>]*>.*?WhatsApp.*?</button>','',seg,flags=re.I|re.S)
seg=re.sub(r'<button\b(?=[^>]*(?:id|data-menu)="[^"]*(?:whatsapp|whats)[^"]*")[^>]*>.*?</button>','',seg,flags=re.I|re.S)
h=h[:a]+seg+h[sec_end:]
H.write_text(h,encoding='utf-8')
# VersionCode solamente.
g=G.read_text(); mt=re.search(r'versionCode\s+(\d+)',g); code=int(mt.group(1))+1 if mt else 1; G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',g,1))
# Verificaciones duras.
for ps,d in hashes.items():
    p=Path(ps)
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=d: raise SystemExit('ERROR: se modifico icono/manifest: '+ps)
h=H.read_text(); a=h.find('<div id="menuPanel"'); z=h.find('</section>',a); menu=h[a:z].lower()
checks={
 'splash original': 'id="appSplash"' in h,
 'mismo splash como fondo': 'id="crnlSplashBackgroundFix"' in h and 'become-background' in h,
 'mismo encuadre': 'object-position:center center!important' in h,
 'WhatsApp fuera menu': 'whatsapp' not in menu,
 'WhatsApp contextual conserva': 'elementActionWhatsApp' in h,
 'menu cuadrados conserva': 'grid-template-columns:repeat(2' in h,
 'icono intacto': True,
}
for k,v in checks.items(): print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()): sys.exit(1)
print('CORRECCION ROBUSTA OK versionCode',code)
