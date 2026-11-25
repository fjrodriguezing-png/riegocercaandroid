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
# strip obsolete import handlers first
for token in ["$('#file').onchange=","$('#importBtn').onclick=","$('#xlsxBtn').onclick="]:
 s=h.find(token)
 if s>=0:
  e=h.find("try{rows=JSON.parse",s)
  if e>s:h=h[:s]+h[e:]
pos=h.find("try{rows=JSON.parse")
if pos<0:raise SystemExit('No rows restore marker')
code="""window.receiveXlsxRows=function(json){try{const data=JSON.parse(json);rows=data.map(r=>({type:String(r.type||''),x:Number(r.x),y:Number(r.y),name:String(r.name||'')})).filter(r=>r.name&&Number.isFinite(r.x)&&Number.isFinite(r.y));localStorage.setItem('crnl_rows',JSON.stringify(rows));$('#status').textContent=`${rows.length} elementos XLSX importados y guardados`;$('#xlsxBtn').disabled=false;render()}catch(e){window.receiveXlsxError(e.message)}};window.receiveXlsxError=function(msg){$('#status').textContent='Error XLSX: '+msg;$('#xlsxBtn').disabled=false};$('#xlsxBtn').onclick=()=>{if(!window.AndroidImport){$('#status').textContent='Importador XLSX Android no disponible.';return}$('#status').textContent='Selecciona el archivo XLSX…';$('#xlsxBtn').disabled=true;window.AndroidImport.importXlsx();setTimeout(()=>{if($('#xlsxBtn').disabled)$('#status').textContent='Procesando XLSX…'},1200)};"""
h=h[:pos]+code+h[pos:]
# radio listener
button='mapsRadiusSearch' if 'id="mapsRadiusSearch"' in h else 'search';manual='mapsRadiusManual' if 'id="mapsRadiusManual"' in h else 'manual';status='maps10Status' if 'id="maps10Status"' in h else 'radioStatus';lst='mapsFoundList' if 'id="mapsFoundList"' in h else 'found';title='mapsFoundTitle' if 'id="mapsFoundTitle"' in h else 'foundTitle'
for x in [button,manual,status,lst,title]:
 if f'id="{x}"' not in h:raise SystemExit('Falta control radio '+x)
radio=f'''/*crnlXlsxRadioUnifiedV1*/(function(){{const b=document.getElementById('{button}'),m=document.getElementById('{manual}'),st=document.getElementById('{status}'),ls=document.getElementById('{lst}'),tt=document.getElementById('{title}');function D(a,b,c,d){{const R=6371000,t=x=>x*Math.PI/180,A=Math.sin(t(c-a)/2)**2+Math.cos(t(a))*Math.cos(t(c))*Math.sin(t(d-b)/2)**2;return 2*R*Math.asin(Math.sqrt(A))}}function GR(r){{if(typeof gpsForRow==='function')return gpsForRow(r);if(typeof gps==='function')return gps(r);if(typeof utm==='function')return utm(Number(r.x),Number(r.y));return null}}function rowsNow(){{if(typeof rows!=='undefined'&&Array.isArray(rows)&&rows.length)return rows;try{{return JSON.parse(localStorage.getItem('crnl_rows')||'[]')}}catch(e){{return[]}}}}b.addEventListener('click',e=>{{e.preventDefault();e.stopPropagation();let rr=rowsNow();if(!rr.length){{st.textContent='No hay datos XLSX cargados.';return}}let rad=Number(m.value)||10;b.textContent='BUSCANDO…';b.disabled=true;st.textContent='Obteniendo ubicación GPS…';navigator.geolocation.getCurrentPosition(p=>{{let out=[];rr.forEach((r,i)=>{{let g=GR(r);if(!g)return;let d=D(p.coords.latitude,p.coords.longitude,Number(g.lat),Number(g.lon));if(Number.isFinite(d)&&d<=rad)out.push({{r,i,d}})}});out.sort((a,b)=>a.d-b.d);st.textContent=out.length?`${{out.length}} elemento(s) dentro de ${{rad}} m`:`No hay elementos dentro de ${{rad}} m`;tt.classList.toggle('hidden',!out.length);ls.innerHTML=out.slice(0,50).map(x=>`<li><button type="button"><b>${{x.r.name}}</b><small>${{x.d<10?x.d.toFixed(1):Math.round(x.d)}} m · ${{x.r.type||'Sin tipo'}}</small></button></li>`).join('');b.disabled=false;b.textContent='🔎 BUSCAR ELEMENTOS'}},err=>{{st.textContent=err.code===1?'Permiso GPS denegado':err.code===2?'Activa el GPS':'GPS tardó demasiado';b.disabled=false;b.textContent='🔎 BUSCAR ELEMENTOS'}},{{enableHighAccuracy:true,timeout:20000,maximumAge:0}})}},true);}})();'''
q=h.rfind('</script>');h=h[:q]+radio+h[q:];H.write_text(h)
b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);v=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {v}',b,1))
checks={'stream fix':'ByteArrayInputStream(so.toByteArray())' in (B/'XlsxStreamingImporter.java').read_text(),'xlsx button':'id="xlsxBtn"' in h,'xlsx callback':'receiveXlsxRows' in h,'native bridge':'"AndroidImport"' in j,'radio unified':'crnlXlsxRadioUnifiedV1' in h,'radio reads same storage':"localStorage.getItem('crnl_rows')" in h}
for k,z in checks.items():print(('OK   ' if z else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
print('UNIFIED XLSX+RADIO OK',v)
