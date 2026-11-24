from pathlib import Path
from PIL import Image,ImageOps
import re,shutil,sys
H=Path('app/src/main/assets/index.html');M=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java');MAN=Path('app/src/main/AndroidManifest.xml');G=Path('app/build.gradle')
for p in (H,M,MAN,G):
 if not p.exists():raise SystemExit('Falta '+str(p))
h=H.read_text(encoding='utf-8');m=M.read_text(encoding='utf-8')
# Preserve current code but restore today's required features idempotently.
# SPLASH + same permanent background
shutil.copy2('splash_nova_limia.jpg','app/src/main/assets/splash_nova_limia.jpg')
if 'id="appSplash"' not in h:
 spl='''<div id="appSplash" class="app-splash"><img src="splash_nova_limia.jpg" alt=""><div class="splash-shade"></div><div class="splash-title">COMUNIDAD DE REGANTES<br>NOVA LIMIA</div></div><script>(function(){var s=document.getElementById('appSplash');setTimeout(function(){if(!s)return;s.classList.add('splash-out');setTimeout(function(){if(s&&s.parentNode)s.parentNode.removeChild(s)},350)},3000)})();</script>''';h=h.replace('<body>','<body>'+spl,1)
if '.app-splash{' not in h:
 css='''.app-splash{position:fixed;z-index:2147483647;inset:0;background:#000;overflow:hidden}.app-splash img{width:100%;height:100%;object-fit:cover;object-position:center}.splash-shade{position:absolute;inset:0;background:rgba(0,0,0,.18)}.splash-title{position:absolute;z-index:2;left:50%;top:50%;width:calc(100% - 44px);text-align:center;transform:translate(120%,-50%);opacity:0;color:#fff;font-weight:900;font-size:clamp(24px,7vw,42px);text-shadow:0 3px 14px rgba(0,0,0,.65);animation:splashTitleIn .7s ease 1s forwards}.app-splash.splash-out{animation:splashOut .32s ease forwards}@keyframes splashTitleIn{to{transform:translate(-50%,-50%);opacity:1}}@keyframes splashOut{to{opacity:0;visibility:hidden}}body:before{content:''!important;position:fixed!important;inset:0!important;z-index:-2!important;background:url('splash_nova_limia.jpg') center center/cover no-repeat!important}''';h=h.replace('</style>',css+'</style>',1)
# MENU GRID, keep existing items
if 'grid-template-columns:repeat(2,minmax(0,1fr))' not in h:
 h=h.replace('</style>','''.menu-panel{position:fixed!important;left:12px!important;right:12px!important;top:88px!important;width:auto!important;max-width:760px;margin:0 auto;padding:14px!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;background:rgba(255,255,255,.94)!important}.menu-panel.hidden{display:none!important}.menu-panel button{aspect-ratio:1.1/1;margin:0!important;border-radius:18px!important;text-align:center!important;display:flex;align-items:center;justify-content:center;font-weight:800!important}</style>''',1)
# EARTH menu
if 'id="earthMenu"' not in h:
 a='<button type="button" id="maps10Menu">🗺️ Elementos por radio</button>'
 if a in h:h=h.replace(a,a+'<button type="button" id="earthMenu">🌍 Google Earth</button>',1)
if "$('#earthMenu').onclick" not in h and "$('#maps10Menu').onclick" in h:
 needle="$('#maps10Menu').onclick=()=>{closeMenu();openSection('#maps10Card')};";h=h.replace(needle,needle+"$('#earthMenu').onclick=()=>{closeMenu();window.location.href='https://earth.google.com/web/'};",1)
# Element action sheet WhatsApp+Earth+Maps
if 'id="elementActions"' not in h:
 sheet='''<div id="elementActions" class="element-actions hidden"><div class="element-sheet"><h3 id="elementActionName">Elemento</h3><div id="elementActionMeta"></div><button id="elementActionMaps" class="go">🗺️ Abrir en Google Maps</button><button id="elementActionEarth">🌍 Ver en Google Earth</button><button id="elementActionWhatsApp">🟢 Denunciar incidencia por WhatsApp</button><button id="elementActionCancel">Cancelar</button></div></div>''';h=h.replace('</main>',sheet+'</main>',1)
if 'data-element-index' not in h:
 old="$('#mapsFoundList').innerHTML=found.slice(0,50).map(x=>`<li><b>${x.r.name}</b><small>Distancia: ${x.d<10?x.d.toFixed(1):Math.round(x.d)} m · ${x.r.type||'Sin tipo'}</small></li>`).join('')+(found.length>50?`<li><b>… y ${found.length-50} elemento(s) más</b></li>`:'');"
 new="$('#mapsFoundList').innerHTML=found.slice(0,50).map(x=>`<li><button class=\"result-action\" data-element-index=\"${x.i}\" data-element-distance=\"${x.d}\"><b>${x.r.name}</b><small>Distancia: ${x.d<10?x.d.toFixed(1):Math.round(x.d)} m · ${x.r.type||'Sin tipo'}</small></button></li>`).join('');document.querySelectorAll('[data-element-index]').forEach(b=>b.onclick=()=>openElementActions(Number(b.dataset.elementIndex),Number(b.dataset.elementDistance)));"
 if old in h:h=h.replace(old,new,1)
if 'let activeElement=' not in h:
 logic=r'''let activeElement=null,activeElementGps=null;function openElementActions(i,d){const r=rows[i],g=r?gpsForRow(r):null;if(!r||!g)return;activeElement=r;activeElementGps=g;$('#elementActionName').textContent=r.name;$('#elementActionMeta').textContent=`${r.type||'Sin tipo'} · ${Math.round(d)} m`;$('#elementActions').classList.remove('hidden')}$('#elementActionCancel').onclick=()=>$('#elementActions').classList.add('hidden');$('#elementActionMaps').onclick=()=>activeElementGps&&window.AndroidMaps&&window.AndroidMaps.navigate(activeElementGps.lat,activeElementGps.lon);$('#elementActionEarth').onclick=()=>{if(activeElementGps)window.location.href=`https://earth.google.com/web/search/${activeElementGps.lat},${activeElementGps.lon}`};$('#elementActionWhatsApp').onclick=()=>{if(!activeElement||!activeElementGps)return;const map=`https://www.google.com/maps/search/?api=1&query=${activeElementGps.lat},${activeElementGps.lon}`;const text=`INCIDENCIA - ${activeElement.name}\nTipo: ${activeElement.type||'Sin tipo'}\nSe ha detectado una incidencia en este elemento. Gracias.\n\nUbicación Google Maps:\n${map}`;window.location.href=`https://wa.me/34615179537?text=${encodeURIComponent(text)}`};''';h=h.replace('function openFoundInMaps()',logic+'function openFoundInMaps()',1)
if '.element-actions{' not in h:h=h.replace('</style>','.element-actions{position:fixed;z-index:120;inset:0;background:#0007;display:flex;align-items:flex-end;justify-content:center}.element-actions.hidden{display:none}.element-sheet{background:#fff;border-radius:22px;padding:16px;width:min(94%,520px);margin:12px}.result-action{width:100%;text-align:left}.element-sheet button{margin-top:9px}</style>',1)
H.write_text(h,encoding='utf-8')
# Android WA/Earth routing if missing
if 'shouldOverrideUrlLoading(WebView' not in m:
 needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");';client='''w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");w.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView v,String u){if(u!=null&&u.startsWith("https://wa.me/")){startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(u)));return true;}if(u!=null&&u.startsWith("https://earth.google.com/")){Intent e=new Intent(Intent.ACTION_VIEW,Uri.parse(u));e.setPackage("com.google.earth");try{startActivity(e);}catch(Exception x){e.setPackage(null);startActivity(e);}return true;}return false;}});''';m=m.replace(needle,client,1)
M.write_text(m,encoding='utf-8')
# Definitive illustrated icon only
im=Image.open('icono_crnl_arqueta.png').convert('RGB');RES=Path('app/src/main/res')
for p in list(RES.rglob('ic_launcher*'))+list(RES.rglob('ic_crnl_foto_v2*'))+list(RES.rglob('ic_crnl_arqueta_v3*')):
 if p.is_file():p.unlink()
for d,n in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
 out=RES/f'mipmap-{d}';out.mkdir(parents=True,exist_ok=True);ImageOps.fit(im,(n,n),Image.Resampling.LANCZOS).save(out/'ic_crnl_arqueta_v3.png')
ms=MAN.read_text();ms=re.sub(r'android:icon="[^"]+"','android:icon="@mipmap/ic_crnl_arqueta_v3"',ms);ms=re.sub(r'android:roundIcon="[^"]+"','android:roundIcon="@mipmap/ic_crnl_arqueta_v3"',ms) if 'android:roundIcon=' in ms else ms.replace('<application ','<application android:roundIcon="@mipmap/ic_crnl_arqueta_v3" ',1);MAN.write_text(ms)
# Earth package query
ms=MAN.read_text();
if 'com.google.earth' not in ms:ms=ms.replace('<application','<queries><package android:name="com.google.earth"/></queries><application',1);MAN.write_text(ms)
# bump and verify
g=G.read_text();mt=re.search(r'versionCode\s+(\d+)',g);code=int(mt.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',g,1))
h=H.read_text();checks=['id="appSplash"','splash_nova_limia.jpg','grid-template-columns:repeat(2','id="earthMenu"','id="elementActionWhatsApp"','https://wa.me/34615179537','id="elementActionEarth"'];
for x in checks:
 if x not in h:raise SystemExit('Falta '+x)
print('RESTauracion integral OK, icono definitivo v3, versionCode',code)
