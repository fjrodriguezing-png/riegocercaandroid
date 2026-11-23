from pathlib import Path
import re, shutil, html as htmlmod, sys
H=Path('app/src/main/assets/index.html'); M=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java'); G=Path('app/build.gradle')
for p in (H,M,G):
    if not p.exists(): raise SystemExit('Falta '+str(p))
h=H.read_text(encoding='utf-8')
# 1. Repair the two concrete corruptions visible in the pasted current source.
h=re.sub(r'<script src="<a href="https://cdn\.jsdelivr\.net/npm/xlsx@0\.18\.5/dist/xlsx\.full\.min\.js".*?</a>">.*?</script>', '<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>', h, flags=re.S)
h=re.sub(r'let url=`<a href="https://www\.google\.com/maps/dir/\?api=1&destination=\$\{dest\}&travelmode=driving`.*?</a>}', "let url=`https://www.google.com/maps/dir/?api=1&destination=${dest}&travelmode=driving`;if(wp)url+=`&waypoints=${wp}`;window.location.href=url}", h, flags=re.S)
# If source was saved escaped, decode once only when doctype itself is escaped.
if h.lstrip().startswith('&lt;!doctype html&gt;'):
    h=htmlmod.unescape(h)
# Remove accidental chat HTML fragments if any remain.
h=re.sub(r'<br aria-hidden="true">','',h)
# 2. Splash: independent timer, centered all orientations.
asset=Path('app/src/main/assets/splash_nova_limia.jpg'); shutil.copy2('splash_nova_limia.jpg',asset)
if 'id="appSplash"' not in h:
    splash='''<div id="appSplash" class="app-splash"><img src="splash_nova_limia.jpg" alt=""><div class="splash-shade"></div><div class="splash-title">COMUNIDAD DE REGANTES<br>NOVA LIMIA</div></div><script>(function(){var s=document.getElementById('appSplash');setTimeout(function(){if(!s)return;s.classList.add('splash-out');setTimeout(function(){if(s&&s.parentNode)s.parentNode.removeChild(s)},350)},3000)})();</script>'''
    h=h.replace('<body>','<body>'+splash,1)
if '.app-splash{' not in h:
    css='''.app-splash{position:fixed;z-index:9999;inset:0;background:#000;overflow:hidden}.app-splash img{width:100%;height:100%;object-fit:cover;object-position:center}.splash-shade{position:absolute;inset:0;background:rgba(0,0,0,.18)}.splash-title{position:absolute;z-index:2;left:50%;top:50%;width:calc(100% - 44px);text-align:center;transform:translate(120%,-50%);opacity:0;color:#fff;font-weight:900;font-size:clamp(24px,7vw,42px);line-height:1.04;text-shadow:0 3px 14px rgba(0,0,0,.65);animation:splashTitleIn .70s cubic-bezier(.22,.61,.36,1) 1s forwards}.app-splash.splash-out{animation:splashOut .32s ease forwards}@keyframes splashTitleIn{from{transform:translate(120%,-50%);opacity:0}to{transform:translate(-50%,-50%);opacity:1}}@keyframes splashOut{to{opacity:0;visibility:hidden}}@media(orientation:landscape){.splash-title{left:50%;top:50%;text-align:center;font-size:clamp(23px,5vw,38px)}}'''
    h=h.replace('</style>',css+'</style>',1)
# 3. Google Earth menu.
if 'id="earthMenu"' not in h:
    a='<button type="button" id="maps10Menu">🗺️ Elementos por radio</button>'
    if a not in h: raise SystemExit('No encuentro Elementos por radio en el menu')
    h=h.replace(a,a+'<button type="button" id="earthMenu">🌍 Google Earth</button>',1)
if "$('#earthMenu').onclick" not in h:
    h=h.replace("$('#maps10Menu').onclick=()=>{closeMenu();openSection('#maps10Card')};", "$('#maps10Menu').onclick=()=>{closeMenu();openSection('#maps10Card')};$('#earthMenu').onclick=()=>{closeMenu();window.location.href='https://earth.google.com/web/'};",1)
# 4. Result action sheet Maps + Earth + WhatsApp.
if 'id="elementActions"' not in h:
    sheet='''<div id="elementActions" class="element-actions hidden"><div class="element-sheet"><div class="element-sheet-head"><div><small>Elemento seleccionado</small><h3 id="elementActionName">Elemento</h3><div id="elementActionMeta"></div></div><button id="elementActionClose" type="button">✕</button></div><button id="elementActionMaps" type="button" class="go">🗺️ Abrir en Google Maps</button><button id="elementActionEarth" type="button" class="earth-btn">🌍 Ver en Google Earth</button><button id="elementActionWhatsApp" type="button" class="wa-btn">🟢 Denunciar incidencia por WhatsApp</button><button id="elementActionCancel" type="button">Cancelar</button></div></div>'''
    h=h.replace('</main>',sheet+'</main>',1)
if 'data-element-index' not in h:
    old="$('#mapsFoundList').innerHTML=found.slice(0,50).map(x=>`<li><b>${x.r.name}</b><small>Distancia: ${x.d<10?x.d.toFixed(1):Math.round(x.d)} m · ${x.r.type||'Sin tipo'}</small></li>`).join('')+(found.length>50?`<li><b>… y ${found.length-50} elemento(s) más</b></li>`:'');"
    new="$('#mapsFoundList').innerHTML=found.slice(0,50).map(x=>`<li><button type=\"button\" class=\"result-action\" data-element-index=\"${x.i}\" data-element-distance=\"${x.d}\"><b>${x.r.name}</b><small>Distancia: ${x.d<10?x.d.toFixed(1):Math.round(x.d)} m · ${x.r.type||'Sin tipo'}</small><span>›</span></button></li>`).join('')+(found.length>50?`<li><b>… y ${found.length-50} elemento(s) más</b></li>`:'');document.querySelectorAll('[data-element-index]').forEach(b=>b.onclick=()=>openElementActions(Number(b.dataset.elementIndex),Number(b.dataset.elementDistance)));"
    if old not in h: raise SystemExit('No encuentro el render exacto de la lista actual')
    h=h.replace(old,new,1)
if 'let activeElement=' not in h:
    logic=r'''let activeElement=null,activeElementGps=null,activeElementDistance=0;function closeElementActions(){$('#elementActions').classList.add('hidden')}function openElementActions(i,d){const r=rows[i],g=r?gpsForRow(r):null;if(!r||!g)return;activeElement=r;activeElementGps=g;activeElementDistance=Number(d)||0;$('#elementActionName').textContent=r.name;$('#elementActionMeta').textContent=`${r.type||'Sin tipo'} · ${activeElementDistance<10?activeElementDistance.toFixed(1):Math.round(activeElementDistance)} m`;$('#elementActions').classList.remove('hidden')}$('#elementActionClose').onclick=closeElementActions;$('#elementActionCancel').onclick=closeElementActions;$('#elementActions').onclick=e=>{if(e.target===$('#elementActions'))closeElementActions()};$('#elementActionMaps').onclick=()=>{if(activeElementGps&&window.AndroidMaps)window.AndroidMaps.navigate(activeElementGps.lat,activeElementGps.lon)};$('#elementActionEarth').onclick=()=>{if(!activeElementGps)return;window.location.href=`https://earth.google.com/web/search/${activeElementGps.lat},${activeElementGps.lon}`};$('#elementActionWhatsApp').onclick=()=>{if(!activeElement||!activeElementGps)return;const map=`https://www.google.com/maps/search/?api=1&query=${activeElementGps.lat},${activeElementGps.lon}`;const text=`INCIDENCIA - ${activeElement.name}\nTipo: ${activeElement.type||'Sin tipo'}\nSe ha detectado una incidencia en este elemento. Gracias.\n\nUbicación Google Maps:\n${map}`;window.location.href=`https://wa.me/34615179537?text=${encodeURIComponent(text)}`};'''
    h=h.replace('function openFoundInMaps()',logic+'function openFoundInMaps()',1)
if '.element-actions{' not in h:
    h=h.replace('</style>','''.result-action{width:100%;text-align:left;padding:12px;background:#f7fafc;border:0}.element-actions{position:fixed;z-index:120;inset:0;background:rgba(0,0,0,.44);display:flex;align-items:flex-end;justify-content:center;padding:12px}.element-actions.hidden{display:none}.element-sheet{width:min(100%,520px);background:#fff;border-radius:22px;padding:16px}.element-sheet-head{display:flex;justify-content:space-between}.wa-btn{background:#25D366!important;color:#073b1c!important;font-weight:900!important}.earth-btn{background:#e8f0fe!important;color:#174ea6!important;font-weight:800!important}</style>''',1)
H.write_text(h,encoding='utf-8')
# Android routes for WA and Earth, preserving bridge.
m=M.read_text(encoding='utf-8')
needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");'
if 'shouldOverrideUrlLoading(WebView' not in m:
    client='''w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");w.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView v,String u){if(u!=null&&u.startsWith("https://wa.me/")){startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(u)));return true;}if(u!=null&&u.startsWith("https://earth.google.com/")){Intent e=new Intent(Intent.ACTION_VIEW,Uri.parse(u));e.setPackage("com.google.earth");try{startActivity(e);}catch(Exception ex){e.setPackage(null);startActivity(e);}return true;}return false;}});'''
    if needle not in m: raise SystemExit('No encuentro AndroidMaps bridge')
    m=m.replace(needle,client,1)
M.write_text(m,encoding='utf-8')
# Manifest Earth visibility.
man=Path('app/src/main/AndroidManifest.xml');ms=man.read_text(encoding='utf-8')
if 'com.google.earth' not in ms:
    if '<queries>' in ms: ms=ms.replace('</queries>','<package android:name="com.google.earth"/></queries>',1)
    else: ms=ms.replace('<application','<queries><package android:name="com.google.earth"/></queries><application',1)
man.write_text(ms,encoding='utf-8')
# Version bump.
g=G.read_text();mt=re.search(r'versionCode\s+(\d+)',g);n=int(mt.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {n}',g,1))
# Exact checks.
h=H.read_text();m=M.read_text();
checks=['id="appSplash"','removeChild(s)','COMUNIDAD DE REGANTES<br>NOVA LIMIA','id="earthMenu"','id="elementActionEarth"','id="elementActionWhatsApp"','https://wa.me/34615179537','Se ha detectado una incidencia en este elemento. Gracias.','Tipo: ${activeElement.type','https://www.google.com/maps/search/?api=1&query=']
for x in checks:
    if x not in h: raise SystemExit('Falta tras corregir: '+x)
print('CODIGO ACTUAL CORREGIDO E INTEGRADO. versionCode',n)
