from pathlib import Path
import re, shutil
root=Path.cwd(); html=root/'app/src/main/assets/index.html'; gradle=root/'app/build.gradle'
if not html.exists(): raise SystemExit('Falta app/src/main/assets/index.html')
if not gradle.exists(): raise SystemExit('Falta app/build.gradle')
source=root/'splash_nova_limia.jpg'
if not source.exists(): raise SystemExit('Falta splash_nova_limia.jpg en la raiz')
asset=root/'app/src/main/assets/splash_nova_limia.jpg'; shutil.copy2(source,asset)
s=html.read_text(encoding='utf-8')
# Insert splash immediately after body. Timeline: image immediate; title starts at 1.0s sliding from right; complete splash ends at 3.0s.
if 'id="appSplash"' not in s:
    s=s.replace('<body>','''<body><div id="appSplash" class="app-splash" aria-label="Comunidad de Regantes Nova Limia"><img src="splash_nova_limia.jpg" alt=""><div class="splash-shade"></div><div class="splash-title">COMUNIDAD DE REGANTES<br>NOVA LIMIA</div></div><script>(function(){var splash=document.getElementById('appSplash');window.setTimeout(function(){if(!splash)return;splash.classList.add('splash-out');window.setTimeout(function(){if(splash&&splash.parentNode)splash.parentNode.removeChild(splash);},350);},3000);})();</script>''',1)
css='''.app-splash{position:fixed;z-index:9999;inset:0;background:#000;overflow:hidden;display:block}.app-splash img{width:100%;height:100%;object-fit:cover;object-position:center;display:block}.splash-shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.08),rgba(0,0,0,.28))}.splash-title{position:absolute;z-index:2;left:50%;top:50%;width:calc(100% - 44px);text-align:center;transform:translate(120%,-50%);opacity:0;color:#fff;font-weight:900;font-size:clamp(24px,7vw,42px);line-height:1.04;letter-spacing:.6px;text-shadow:0 3px 14px rgba(0,0,0,.60);animation:splashTitleIn .70s cubic-bezier(.22,.61,.36,1) 1s forwards}.app-splash.splash-out{animation:splashOut .32s ease forwards}@keyframes splashTitleIn{from{transform:translate(120%,-50%);opacity:0}to{transform:translate(-50%,-50%);opacity:1}}@keyframes splashOut{to{opacity:0;visibility:hidden}}@media(orientation:landscape){.splash-title{left:50%;top:50%;width:calc(100% - 56px);text-align:center;transform:translate(120%,-50%);font-size:clamp(23px,5vw,38px)}}'''
if '.app-splash{' not in s:s=s.replace('</style>',css+'</style>',1)
# Make main interface inert/hidden during the full 3 sec splash, then remove splash from DOM.
# El temporizador independiente ya se inserta inmediatamente despues del splash.

html.write_text(s,encoding='utf-8')
# bump version
b=gradle.read_text();m=re.search(r'versionCode\s+(\d+)',b);n=int(m.group(1))+1 if m else 26;b=re.sub(r'versionCode\s+\d+',f'versionCode {n}',b,1);gradle.write_text(b);print('Splash aplicado; versionCode',n)
# checks
s=html.read_text(); checks=['id="appSplash"','splash_nova_limia.jpg','animation:splashTitleIn',' 1s forwards','},3000);','removeChild(splash)','COMUNIDAD DE REGANTES<br>NOVA LIMIA']
for x in checks:
    if x not in s: raise SystemExit('Comprobacion splash fallida: '+x)
print('COMPROBACION SPLASH OK')
