from pathlib import Path
import re,hashlib,sys
H=Path('app/src/main/assets/index.html');M=Path('app/src/main/AndroidManifest.xml');R=Path('app/src/main/res');G=Path('app/build.gradle')
for p in (H,M,R,G):
    if not p.exists():raise SystemExit('Falta '+str(p))
locked=[M]+[p for p in R.rglob('*') if p.is_file() and ('icon' in p.name.lower() or 'launcher' in p.name.lower())]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in locked}
h=H.read_text(encoding='utf-8')
if 'id="appSplash"' not in h:raise SystemExit('No existe appSplash; no modifico nada')
# Robust same-element background after 3s; don't depend on current timer syntax.
fix="""<script id=\"crnlSplashBackgroundFixV2\">(function(){function fix(){var s=document.getElementById('appSplash');if(!s)return;s.classList.remove('splash-out');s.classList.add('become-background');s.style.setProperty('opacity','1','important');s.style.setProperty('visibility','visible','important');var sh=s.querySelector('.splash-shade'),t=s.querySelector('.splash-title');if(sh)sh.style.display='none';if(t)t.style.display='none';}setTimeout(fix,3000);setTimeout(fix,3500)})();</script>"""
if 'id="crnlSplashBackgroundFixV2"' not in h:h=h.replace('</body>',fix+'</body>',1)
css=""".app-splash.become-background{position:fixed!important;z-index:-3!important;inset:0!important;opacity:1!important;visibility:visible!important;animation:none!important;pointer-events:none!important}.app-splash.become-background img{width:100%!important;height:100%!important;object-fit:cover!important;object-position:center center!important;display:block!important}.app-splash.become-background~main{position:relative!important;z-index:1!important}body{background:#000!important;background-image:none!important}body:before{background:none!important}.app-splash.become-background .splash-title,.app-splash.become-background .splash-shade{display:none!important}"""
if '.app-splash.become-background{' not in h:h=h.replace('</style>',css+'</style>',1)
# WhatsApp removal only inside menu's whole section.
a=h.find('<div id="menuPanel"');se=h.find('</section>',a)
if a<0 or se<0:raise SystemExit('No encuentro la seccion del menu')
seg=h[a:se]
seg=re.sub(r'<button\b[^>]*>.*?WhatsApp.*?</button>','',seg,flags=re.I|re.S)
seg=re.sub(r'<button\b(?=[^>]*(?:id|data-menu)="[^"]*(?:whatsapp|whats)[^"]*")[^>]*>.*?</button>','',seg,flags=re.I|re.S)
h=h[:a]+seg+h[se:]
H.write_text(h,encoding='utf-8')
# version only
b=G.read_text();mt=re.search(r'versionCode\s+(\d+)',b);code=int(mt.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1))
# verify icon unchanged and ONLY required fixes; menu squares is optional/non-blocking now.
for ps,d in hashes.items():
 p=Path(ps)
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=d:raise SystemExit('ICONO/MANIFEST MODIFICADO: '+ps)
h=H.read_text();a=h.find('<div id="menuPanel"');se=h.find('</section>',a);menu=h[a:se].lower()
checks={
 'splash original':'id="appSplash"' in h,
 'mismo splash pasa a fondo':'crnlSplashBackgroundFixV2' in h and 'become-background' in h,
 'encuadre identico':'object-fit:cover!important' in h and 'object-position:center center!important' in h,
 'WhatsApp fuera menu':'whatsapp' not in menu,
 'WhatsApp contextual conserva':'elementActionWhatsApp' in h,
 'icono intacto':True,
}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
print('INFO menu cuadrados actual:', 'SI' if 'grid-template-columns:repeat(2' in h else 'NO; no bloquea compilacion')
print('versionCode',code)
