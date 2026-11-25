from pathlib import Path
import re,shutil,sys
H=Path('app/src/main/assets/index.html');J=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java');G=Path('app/build.gradle');B=J.parent;S=Path('.crnl_import_files')
for p in (H,J,G,S/'ImportBridge.java',S/'XlsxStreamingImporter.java'):
 if not p.exists():raise SystemExit('Falta '+str(p))
shutil.copy2(S/'ImportBridge.java',B/'ImportBridge.java');shutil.copy2(S/'XlsxStreamingImporter.java',B/'XlsxStreamingImporter.java')
j=J.read_text();needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");'
if 'IMPORT_XLSX=91' not in j:
 p=j.find('{',j.find('class MainActivity'))+1;j=j[:p]+'static final int IMPORT_XLSX=91;'+j[p:]
if '"AndroidImport"' not in j:
 if needle not in j:raise SystemExit('No AndroidMaps bridge')
 j=j.replace(needle,needle+'w.addJavascriptInterface(new ImportBridge(this,IMPORT_XLSX),"AndroidImport");',1)
cb='''if(r==IMPORT_XLSX&&c==RESULT_OK&&d!=null&&d.getData()!=null){Uri xlsxUri=d.getData();new Thread(()->{try{org.json.JSONArray a=new XlsxStreamingImporter(this).read(xlsxUri);String js="window.receiveXlsxRows("+org.json.JSONObject.quote(a.toString())+")";w.post(()->w.evaluateJavascript(js,null));}catch(Exception ex){String msg=ex.getMessage()==null?ex.toString():ex.getMessage();w.post(()->w.evaluateJavascript("window.receiveXlsxError("+org.json.JSONObject.quote(msg)+")",null));}}).start();return;}'''
if 'r==IMPORT_XLSX' not in j:
 if 'protected void onActivityResult' in j:
  p=j.find('{',j.find('protected void onActivityResult'))+1;j=j[:p]+cb+j[p:]
 else:j=j[:j.rfind('}')]+f'protected void onActivityResult(int r,int c,Intent d){{super.onActivityResult(r,c,d);{cb}}}'+j[j.rfind('}'):]
J.write_text(j)
h=H.read_text();h=re.sub(r'<script\s+src="https://cdn\.jsdelivr\.net/npm/xlsx@[^\"]+"\s*></script>','',h)
h=re.sub(r'<input\s+id="file"[^>]*>','<button id="xlsxBtn" type="button" class="go">📥 SELECCIONAR XLSX</button>',h,count=1)
h=re.sub(r'<button\s+id="(?:importBtn|xlsxBtn)"[^>]*>.*?</button>','<button id="xlsxBtn" type="button" class="go">📥 SELECCIONAR XLSX</button>',h,count=1,flags=re.S)
# Remove obsolete handlers
for tok in ["$('#file').onchange=","$('#importBtn').onclick=","$('#xlsxBtn').onclick="]:
 s=h.find(tok)
 if s>=0:
  e=h.find("try{rows=JSON.parse",s)
  if e>s:h=h[:s]+h[e:]
pos=h.find("try{rows=JSON.parse")
if pos<0:raise SystemExit('No rows restore marker')
# import callback with automatic return-to-open-menu
if 'window.receiveXlsxRows=' not in h:
 imp="""function crnlReturnOpenMenu(){document.querySelectorAll('.menu-section,.screen').forEach(x=>{x.classList.add('hidden');x.classList.remove('active-view')});document.body.classList.remove('menu-mode');const mp=document.getElementById('menuPanel')||document.getElementById('menu');if(mp)mp.classList.remove('hidden');const mb=document.getElementById('menuBtn');if(mb)mb.setAttribute('aria-expanded','true');window.scrollTo({top:0,behavior:'smooth'})}window.receiveXlsxRows=function(json){try{const data=JSON.parse(json);rows=data.map(r=>({type:String(r.type||''),x:Number(r.x),y:Number(r.y),name:String(r.name||'')})).filter(r=>r.name&&Number.isFinite(r.x)&&Number.isFinite(r.y));localStorage.setItem('crnl_rows',JSON.stringify(rows));$('#status').textContent=`${rows.length} elementos XLSX importados y guardados`;$('#xlsxBtn').disabled=false;render();crnlReturnOpenMenu()}catch(e){window.receiveXlsxError(e.message)}};window.receiveXlsxError=function(msg){$('#status').textContent='Error XLSX: '+msg;$('#xlsxBtn').disabled=false};$('#xlsxBtn').onclick=()=>{if(!window.AndroidImport){$('#status').textContent='Importador XLSX Android no disponible.';return}$('#status').textContent='Selecciona el archivo XLSX…';$('#xlsxBtn').disabled=true;window.AndroidImport.importXlsx();setTimeout(()=>{if($('#xlsxBtn').disabled)$('#status').textContent='Procesando XLSX…'},1200)};"""
 h=h[:pos]+imp+h[pos:]
# Detect radio controls and add self-contained radio+actions
ids={'b':'mapsRadiusSearch' if 'id="mapsRadiusSearch"' in h else 'search','m':'mapsRadiusManual' if 'id="mapsRadiusManual"' in h else 'manual','s':'maps10Status' if 'id="maps10Status"' in h else 'radioStatus','l':'mapsFoundList' if 'id="mapsFoundList"' in h else 'found','t':'mapsFoundTitle' if 'id="mapsFoundTitle"' in h else 'foundTitle'}
for x in ids.values():
 if f'id="{x}"' not in h:raise SystemExit('Falta control radio '+x)
if 'id="crnlFinalActions"' not in h:
 sheet='''<div id="crnlFinalActions" class="crnl-f-actions hidden"><div class="crnl-f-sheet"><h3 id="crnlFName">Elemento</h3><div id="crnlFMeta"></div><button id="crnlFMaps" type="button" class="go">🗺️ Abrir en Google Maps</button><button id="crnlFEarth" type="button">🌍 Ver en Google Earth</button><button id="crnlFWa" type="button" class="crnl-f-wa">🟢 Denunciar incidencia por WhatsApp</button><button id="crnlFCancel" type="button">Cancelar</button></div></div>'''
 h=h.replace('</main>',sheet+'</main>',1)
 h=h.replace('</style>','.crnl-f-actions{position:fixed;z-index:2200;inset:0;background:#0007;display:flex;align-items:flex-end;justify-content:center;padding:12px}.crnl-f-actions.hidden{display:none}.crnl-f-sheet{width:min(100%,520px);background:#fff;border-radius:22px;padding:16px}.crnl-f-sheet button{margin-top:9px}.crnl-f-wa{background:#25D366!important;color:#073b1c!important;font-weight:900!important}</style>',1)
if 'crnlFinalRuntimeV1' not in h:
 r=f'''/*crnlFinalRuntimeV1*/(function(){{const b=document.getElementById('{ids['b']}'),m=document.getElementById('{ids['m']}'),st=document.getElementById('{ids['s']}'),ls=document.getElementById('{ids['l']}'),tt=document.getElementById('{ids['t']}'),box=document.getElementById('crnlFinalActions');let cur=null,cg=null;function all(){{if(typeof rows!=='undefined'&&Array.isArray(rows)&&rows.length)return rows;try{{return JSON.parse(localStorage.getItem('crnl_rows')||'[]')}}catch(e){{return[]}}}}function gp(x){{if(typeof gpsForRow==='function')return gpsForRow(x);if(typeof gps==='function')return gps(x);if(typeof utm==='function')return utm(Number(x.x),Number(x.y));return null}}function D(a,b,c,d){{const R=6371000,t=x=>x*Math.PI/180,A=Math.sin(t(c-a)/2)**2+Math.cos(t(a))*Math.cos(t(c))*Math.sin(t(d-b)/2)**2;return 2*R*Math.asin(Math.sqrt(A))}}function done(){{b.disabled=false;b.textContent='🔎 BUSCAR ELEMENTOS'}}b.addEventListener('click',e=>{{e.preventDefault();e.stopPropagation();let rr=all();if(!rr.length){{st.textContent='No hay datos XLSX cargados.';return}}let rad=Number(m.value)||10;b.disabled=true;b.textContent='BUSCANDO…';st.textContent='Obteniendo ubicación GPS…';navigator.geolocation.getCurrentPosition(p=>{{let out=[];rr.forEach((x,i)=>{{let g=gp(x);if(!g)return;let d=D(p.coords.latitude,p.coords.longitude,Number(g.lat),Number(g.lon));if(Number.isFinite(d)&&d<=rad)out.push({{x,i,g,d}})}});out.sort((a,b)=>a.d-b.d);st.textContent=out.length?`${{out.length}} elemento(s) dentro de ${{rad}} m`:`No hay elementos dentro de ${{rad}} m`;tt.classList.toggle('hidden',!out.length);ls.innerHTML=out.slice(0,50).map(y=>`<li><button type="button" data-f-i="${{y.i}}" data-f-d="${{y.d}}"><b>${{y.x.name}}</b><small>${{y.d<10?y.d.toFixed(1):Math.round(y.d)}} m · ${{y.x.type||'Sin tipo'}}</small></button></li>`).join('');done()}},err=>{{st.textContent=err.code===1?'Permiso GPS denegado':err.code===2?'Activa el GPS':'GPS tardó demasiado';done()}},{{enableHighAccuracy:true,timeout:20000,maximumAge:0}})}},true);ls.addEventListener('click',e=>{{let bt=e.target.closest('button[data-f-i]');if(!bt)return;e.preventDefault();e.stopPropagation();let rr=all(),i=Number(bt.dataset.fI),d=Number(bt.dataset.fD);if(i<0||i>=rr.length)return;cur=rr[i];cg=gp(cur);if(!cg)return;document.getElementById('crnlFName').textContent=cur.name;document.getElementById('crnlFMeta').textContent=`${{cur.type||'Sin tipo'}} · ${{d<10?d.toFixed(1):Math.round(d)}} m`;box.classList.remove('hidden')}},true);function close(){{box.classList.add('hidden')}}document.getElementById('crnlFCancel').onclick=close;box.onclick=e=>{{if(e.target===box)close()}};document.getElementById('crnlFMaps').onclick=()=>{{if(cg&&window.AndroidMaps)window.AndroidMaps.navigate(cg.lat,cg.lon)}};document.getElementById('crnlFEarth').onclick=()=>{{if(cg)location.href=`https://earth.google.com/web/search/${{cg.lat}},${{cg.lon}}`}};document.getElementById('crnlFWa').onclick=()=>{{if(!cur||!cg)return;const map=`https://www.google.com/maps/search/?api=1&query=${{cg.lat}},${{cg.lon}}`,text=`INCIDENCIA - ${{cur.name}}\nTipo: ${{cur.type||'Sin tipo'}}\nSe ha detectado una incidencia en este elemento. Gracias.\n\nUbicación Google Maps:\n${{map}}`;location.href=`https://wa.me/34615179537?text=${{encodeURIComponent(text)}}`}};}})();'''
 q=h.rfind('</script>');h=h[:q]+r+h[q:]
H.write_text(h)
b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);v=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {v}',b,1))
h=H.read_text();j=J.read_text();checks={'stream fix':'ByteArrayInputStream(so.toByteArray())' in (B/'XlsxStreamingImporter.java').read_text(),'xlsx callback':'receiveXlsxRows' in h,'return menu':'crnlReturnOpenMenu' in h,'radio':'crnlFinalRuntimeV1' in h,'actions':'id="crnlFinalActions"' in h,'maps':'crnlFMaps' in h,'earth':'crnlFEarth' in h,'whatsapp':'crnlFWa' in h and 'wa.me/34615179537' in h,'storage':"localStorage.getItem('crnl_rows')" in h,'bridge':'"AndroidImport"' in j}
for k,x in checks.items():print(('OK   ' if x else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
print('FINAL INTEGRATION OK',v)
