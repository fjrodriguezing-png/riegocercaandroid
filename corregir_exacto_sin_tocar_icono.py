from pathlib import Path
import re,hashlib,sys
H=Path('app/src/main/assets/index.html'); M=Path('app/src/main/AndroidManifest.xml'); R=Path('app/src/main/res'); G=Path('app/build.gradle')
for p in (H,M,R,G):
    if not p.exists():raise SystemExit('Falta '+str(p))
# Lock icon and manifest bytes.
locked=[M]+[p for p in R.rglob('*') if p.is_file() and ('icon' in p.name.lower() or 'launcher' in p.name.lower())]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in locked}
h=H.read_text(encoding='utf-8')
# 1) SAME PIXELS AFTER SPLASH: do not remove splash image; convert it after 3s into permanent background layer.
# Replace timer if current splash exists. This guarantees no visual jump because it is literally the same IMG element.
pattern=r"<script>\(function\(\)\{var s=document\.getElementById\('appSplash'\);.*?</script>"
replacement="""<script>(function(){var s=document.getElementById('appSplash');setTimeout(function(){if(!s)return;s.classList.add('become-background');var shade=s.querySelector('.splash-shade');var title=s.querySelector('.splash-title');if(shade)shade.remove();if(title)title.remove();},3000)})();</script>"""
h,n=re.subn(pattern,replacement,h,count=1,flags=re.S)
if n==0: raise SystemExit('No encuentro el temporizador del splash actual. No modifico nada.')
# Override CSS: after 3 sec same appSplash container/image remains fixed underneath app, exact dimensions/position preserved.
css='''.app-splash.become-background{z-index:-3!important;pointer-events:none!important;animation:none!important;opacity:1!important;visibility:visible!important}.app-splash.become-background img{width:100%!important;height:100%!important;object-fit:cover!important;object-position:center center!important}.app-splash.become-background~main{position:relative;z-index:1}'''
if '.app-splash.become-background{' not in h:h=h.replace('</style>',css+'</style>',1)
# Disable competing body background images entirely after using same splash element.
h=h.replace("background:#f3f7fa url('fondo_app.png') left center/cover fixed no-repeat;","background:#000;")
h=h.replace("background:#000 url('splash_nova_limia.jpg') center center/cover fixed no-repeat;","background:#000;")
# Remove only CSS background-image clauses that can create a shifted duplicate.
h=re.sub(r"background-image:url\('[^']+'\);?",'',h)
# 2) Remove WhatsApp MAIN MENU robustly: parse only menuPanel with its closing div immediately before </section>.
a=h.find('<div id="menuPanel"')
if a<0:raise SystemExit('No encuentro menuPanel')
section_end=h.find('</section>',a)
if section_end<0:raise SystemExit('No encuentro cierre section menu')
segment=h[a:section_end]
# Remove button if text/id/data-menu mentions WhatsApp, including nested spans/icons.
segment=re.sub(r'<button\b(?=[^>]*(?:id|data-menu)="[^"]*whats?[^"]*")[^>]*>.*?</button>','',segment,flags=re.I|re.S)
segment=re.sub(r'<button\b[^>]*>(?:(?!</button>).)*?WhatsApp(?:(?!</button>).)*?</button>','',segment,flags=re.I|re.S)
h=h[:a]+segment+h[section_end:]
H.write_text(h,encoding='utf-8')
# bump only version code
b=G.read_text();mt=re.search(r'versionCode\s+(\d+)',b);code=int(mt.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1))
# Lock check
for ps,dig in hashes.items():
 p=Path(ps)
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=dig:raise SystemExit('ICONO/MANIFEST MODIFICADO: '+ps)
# Functional hard checks
h=H.read_text();a=h.find('<div id="menuPanel"');se=h.find('</section>',a);menu=h[a:se]
checks={
'mismo splash queda de fondo':'become-background' in h and 'title.remove()' in h and 'shade.remove()' in h,
'no fondo duplicado':"background-image:url(" not in h,
'WA fuera menu':'whatsapp' not in menu.lower(),
'WA contextual sigue':'elementActionWhatsApp' in h,
'menu cuadrados sigue':'grid-template-columns:repeat(2' in h,
'icono intacto':True,
}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
print('versionCode',code)
