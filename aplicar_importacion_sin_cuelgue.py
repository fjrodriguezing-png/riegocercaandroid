from pathlib import Path
import re,shutil,sys
base=Path('app/src/main/java/es/riegocerca/maps');H=Path('app/src/main/assets/index.html');J=base/'MainActivity.java';G=Path('app/build.gradle');src=Path('.crnl_import_files')
for p in (H,J,G,src/'ImportBridge.java',src/'NativeTabularImporter.java'):
 if not p.exists():raise SystemExit('Falta '+str(p))
# Install independent Java helper files.
shutil.copy2(src/'ImportBridge.java',base/'ImportBridge.java');shutil.copy2(src/'NativeTabularImporter.java',base/'NativeTabularImporter.java')
# Patch MainActivity minimally: bridge + callback processed on background thread so XLSX cannot freeze WebView/UI.
j=J.read_text()
if 'IMPORT=9' not in j:j=j.replace('static final int LOC=7,FILE=8;','static final int LOC=7,FILE=8,IMPORT=9;').replace('static final int LOC=7;','static final int LOC=7,IMPORT=9;')
needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");'
if '"AndroidImport"' not in j:
 if needle not in j:raise SystemExit('No AndroidMaps bridge')
 j=j.replace(needle,needle+'w.addJavascriptInterface(new ImportBridge(this,IMPORT),"AndroidImport");',1)
callback='''if(r==IMPORT&&c==RESULT_OK&&d!=null&&d.getData()!=null){Uri importUri=d.getData();new Thread(()->{try{org.json.JSONArray a=new NativeTabularImporter(this).read(importUri);String js="window.receiveImportedRows("+org.json.JSONObject.quote(a.toString())+")";w.post(()->w.evaluateJavascript(js,null));}catch(Exception ex){String msg=ex.getMessage()==null?ex.toString():ex.getMessage();w.post(()->w.evaluateJavascript("window.receiveImportError("+org.json.JSONObject.quote(msg)+")",null));}}).start();return;}'''
if 'r==IMPORT' not in j:
 if 'protected void onActivityResult' in j:
  p=j.find('{',j.find('protected void onActivityResult'))+1;j=j[:p]+callback+j[p:]
 else:
  j=j[:j.rfind('}')]+f'protected void onActivityResult(int r,int c,Intent d){{super.onActivityResult(r,c,d);{callback}}}'+j[j.rfind('}'):]
J.write_text(j)
# HTML: direct button to native importer + progress/error timeout feedback.
h=H.read_text();h=re.sub(r'<script\s+src="https://cdn\.jsdelivr\.net/npm/xlsx@[^\"]+"\s*></script>','',h)
h=re.sub(r'<input\s+id="file"[^>]*>','<button id="importBtn" type="button" class="go">📥 SELECCIONAR EXCEL / CSV</button>',h,count=1)
start=h.find("$('#file').onchange=")
if start>=0:
 end=h.find("try{rows=JSON.parse",start)
 if end>start:h=h[:start]+h[end:]
if 'window.receiveImportedRows' not in h:
 pos=h.find("try{rows=JSON.parse");
 code="""let importTimer=null;window.receiveImportedRows=function(json){if(importTimer)clearTimeout(importTimer);try{const data=JSON.parse(json);rows=data.filter(r=>r&&r.name&&Number.isFinite(+r.x)&&Number.isFinite(+r.y)).map(r=>({type:String(r.type||''),x:+r.x,y:+r.y,name:String(r.name)}));localStorage.setItem('crnl_rows',JSON.stringify(rows));$('#status').textContent=`${rows.length} elementos importados y guardados`;$('#importBtn').disabled=false;render()}catch(e){window.receiveImportError(e.message)}};window.receiveImportError=function(msg){if(importTimer)clearTimeout(importTimer);$('#status').textContent='Error de importación: '+msg;$('#importBtn').disabled=false};$('#importBtn').onclick=()=>{if(!window.AndroidImport){$('#status').textContent='Importador Android no disponible.';return}$('#status').textContent='Selecciona Excel/CSV…';window.AndroidImport.importFile();setTimeout(()=>{if($('#status').textContent.startsWith('Selecciona'))$('#status').textContent='Archivo seleccionado. Procesando…'},1000);importTimer=setTimeout(()=>{if($('#importBtn').disabled){$('#status').textContent='La importación está tardando demasiado. Prueba con CSV o un XLSX más pequeño.';$('#importBtn').disabled=false}},30000)};"""
 h=h[:pos]+code+h[pos:]
else:
 # make sure button handler exists if receive already present
 pass
H.write_text(h)
# bump
b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);code=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1))
# verify required and preservation
h=H.read_text();j=J.read_text();checks={'button':'id="importBtn"' in h,'native click':'AndroidImport.importFile' in h,'async native':'new Thread' in j,'bridge':'new ImportBridge' in j,'parser xlsx':'NativeTabularImporter' in j,'error callback':'receiveImportError' in h,'30s guard':'30000' in h,'no CDN':'cdn.jsdelivr.net/npm/xlsx' not in h,'visual preserved':'menu-panel' in h,'WA preserved':('elementActionWhatsApp' in h or 'id="aWa"' in h),'Earth preserved':'earthMenu' in h}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
print('IMPORT NO-HANG READY versionCode',code)
