from pathlib import Path
import re, shutil, sys
H=Path('app/src/main/assets/index.html'); M=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java'); G=Path('app/build.gradle')
for p in (H,M,G):
    if not p.exists(): raise SystemExit('Falta '+str(p))
h=H.read_text(encoding='utf-8'); m=M.read_text(encoding='utf-8'); g=G.read_text(encoding='utf-8')
# ---------- SPLASH ----------
src=Path('splash_nova_limia.jpg'); dst=Path('app/src/main/assets/splash_nova_limia.jpg')
if not src.exists(): raise SystemExit('Falta splash_nova_limia.jpg')
shutil.copy2(src,dst)
if 'id="appSplash"' not in h:
    markup='''<div id="appSplash" class="app-splash"><img src="splash_nova_limia.jpg" alt=""><div class="splash-shade"></div><div class="splash-title">COMUNIDAD DE REGANTES<br>NOVA LIMIA</div></div><script>(function(){var s=document.getElementById('appSplash');setTimeout(function(){if(!s)return;s.classList.add('splash-out');setTimeout(function(){if(s&&s.parentNode)s.parentNode.removeChild(s)},350)},3000)})();</script>'''
    h=h.replace('<body>','<body>'+markup,1)
if '.app-splash{' not in h:
    css='''.app-splash{position:fixed;z-index:9999;inset:0;background:#000;overflow:hidden}.app-splash img{width:100%;height:100%;object-fit:cover;object-position:center}.splash-shade{position:absolute;inset:0;background:rgba(0,0,0,.18)}.splash-title{position:absolute;z-index:2;left:50%;top:50%;width:calc(100% - 44px);text-align:center;transform:translate(120%,-50%);opacity:0;color:#fff;font-weight:900;font-size:clamp(24px,7vw,42px);line-height:1.04;text-shadow:0 3px 14px rgba(0,0,0,.65);animation:splashTitleIn .70s cubic-bezier(.22,.61,.36,1) 1s forwards}.app-splash.splash-out{animation:splashOut .32s ease forwards}@keyframes splashTitleIn{from{transform:translate(120%,-50%);opacity:0}to{transform:translate(-50%,-50%);opacity:1}}@keyframes splashOut{to{opacity:0;visibility:hidden}}@media(orientation:landscape){.splash-title{left:50%;top:50%;width:calc(100% - 56px);text-align:center;font-size:clamp(23px,5vw,38px)}}'''
    h=h.replace('</style>',css+'</style>',1)
# ---------- WHATSAPP ----------
if 'id="elementActions"' not in h:
    sheet='''<div id="elementActions" class="element-actions hidden"><div class="element-sheet"><div class="element-sheet-head"><div><small>Elemento seleccionado</small><h3 id="elementActionName">Elemento</h3><div id="elementActionMeta"></div></div><button id="elementActionClose" type="button">✕</button></div><button id="elementActionMaps" type="button" class="go">🗺️ Abrir en Google Maps</button><button id="elementActionWhatsApp" type="button" class="wa-btn">🟢 Denunciar incidencia por WhatsApp</button><button id="elementActionCancel" type="button">Cancelar</button></div></div>'''
    h=h.replace('</main>',sheet+'</main>',1)
# adapt result rendering by broad replacement of the V25 map line, if still plain
if 'data-element-index' not in h:
    pat=r"\$\('#mapsFoundList'\)\.innerHTML=found\.slice\(0,50\)\.map\(x=>`<li><b>\$\{x\.r\.name\}</b><small>Distancia:.*?</li>`\)\.join\(''\)\+\(found\.length>50\?.*?:''\);"
    rep="$('#mapsFoundList').innerHTML=found.slice(0,50).map(x=>`<li><button type=\"button\" class=\"result-action\" data-element-index=\"${x.i}\" data-element-distance=\"${x.d}\"><b>${x.r.name}</b><small>Distancia: ${x.d<10?x.d.toFixed(1):Math.round(x.d)} m · ${x.r.type||'Sin tipo'}</small><span>›</span></button></li>`).join('')+(found.length>50?`<li><b>… y ${found.length-50} elemento(s) más</b></li>`:'');document.querySelectorAll('[data-element-index]').forEach(b=>b.onclick=()=>openElementActions(Number(b.dataset.elementIndex),Number(b.dataset.elementDistance)));"
    h,n=re.subn(pat,rep,h,count=1,flags=re.S)
    if n!=1: raise SystemExit('No pude localizar la lista V25 de Elementos por radio para hacerla pulsable')
if 'let activeElement=' not in h:
    js=r'''let activeElement=null,activeElementGps=null,activeElementDistance=0;function closeElementActions(){$('#elementActions').classList.add('hidden')}function openElementActions(i,d){const r=rows[i],g=r?gpsForRow(r):null;if(!r||!g)return;activeElement=r;activeElementGps=g;activeElementDistance=Number(d)||0;$('#elementActionName').textContent=r.name;$('#elementActionMeta').textContent=`${r.type||'Sin tipo'} · ${activeElementDistance<10?activeElementDistance.toFixed(1):Math.round(activeElementDistance)} m`;$('#elementActions').classList.remove('hidden')}$('#elementActionClose').onclick=closeElementActions;$('#elementActionCancel').onclick=closeElementActions;$('#elementActions').onclick=e=>{if(e.target===$('#elementActions'))closeElementActions()};$('#elementActionMaps').onclick=()=>{if(activeElementGps&&window.AndroidMaps)window.AndroidMaps.navigate(activeElementGps.lat,activeElementGps.lon)};$('#elementActionWhatsApp').onclick=()=>{if(!activeElement||!activeElementGps)return;const map=`https://www.google.com/maps/search/?api=1&query=${activeElementGps.lat},${activeElementGps.lon}`;const text=`INCIDENCIA - ${activeElement.name}\nTipo: ${activeElement.type||'Sin tipo'}\nSe ha detectado una incidencia en este elemento. Gracias.\n\nUbicación Google Maps:\n${map}`;window.location.href=`https://wa.me/34615179537?text=${encodeURIComponent(text)}`};'''
    if 'function openFoundInMaps()' not in h: raise SystemExit('No encuentro openFoundInMaps()')
    h=h.replace('function openFoundInMaps()',js+'function openFoundInMaps()',1)
if '.element-actions{' not in h:
    css2='''.result-action{width:100%;text-align:left;padding:12px;background:#f7fafc;border:0}.element-actions{position:fixed;z-index:120;inset:0;background:rgba(0,0,0,.44);display:flex;align-items:flex-end;justify-content:center;padding:12px}.element-actions.hidden{display:none}.element-sheet{width:min(100%,520px);background:#fff;border-radius:22px;padding:16px}.element-sheet-head{display:flex;justify-content:space-between}.wa-btn{background:#25D366!important;color:#073b1c!important;font-weight:900!important}'''
    h=h.replace('</style>',css2+'</style>',1)
H.write_text(h,encoding='utf-8')
# Android: WhatsApp opens outside WebView
if 'startsWith("https://wa.me/")' not in m:
    needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");'
    if needle not in m: raise SystemExit('No encuentro AndroidMaps bridge')
    client='''w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");w.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView v,String u){if(u!=null&&u.startsWith("https://wa.me/")){try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(u)));}catch(Exception e){android.widget.Toast.makeText(MainActivity.this,"No se pudo abrir WhatsApp",android.widget.Toast.LENGTH_LONG).show();}return true;}return false;}});'''
    m=m.replace(needle,client,1)
M.write_text(m,encoding='utf-8')
# version 26
g=re.sub(r'versionCode\s+\d+','versionCode 26',g,1);G.write_text(g,encoding='utf-8')
# final verification
h=H.read_text(encoding='utf-8');m=M.read_text(encoding='utf-8')
checks=['id="appSplash"','removeChild(s)','COMUNIDAD DE REGANTES<br>NOVA LIMIA','id="elementActionWhatsApp"','https://wa.me/34615179537','Se ha detectado una incidencia en este elemento. Gracias.','Tipo: ${activeElement.type','https://www.google.com/maps/search/?api=1&query=','data-element-index']
for x in checks:
    if x not in h: raise SystemExit('Fallo de comprobacion: '+x)
if 'startsWith("https://wa.me/")' not in m: raise SystemExit('Fallo handler WhatsApp Android')
print('OK: SPLASH + WHATSAPP integrados en el mismo proyecto')
