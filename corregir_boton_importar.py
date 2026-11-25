from pathlib import Path
import re,sys
H=Path('app/src/main/assets/index.html');J=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java');G=Path('app/build.gradle')
for p in (H,J,G):
 if not p.exists():raise SystemExit('Falta '+str(p))
h=H.read_text(encoding='utf-8');j=J.read_text(encoding='utf-8')
# Root fix: do NOT depend on WebView <input type=file>. Use a normal button that directly calls native Android picker.
# Accept either current input variant.
h,n=re.subn(r'<input\s+id="file"[^>]*>', '<button id="importBtn" type="button" class="go">📥 SELECCIONAR EXCEL / CSV</button>', h, count=1)
if n!=1 and 'id="importBtn"' not in h:raise SystemExit('No se encontro control de importacion')
# Remove all existing file onchange handler carefully and insert direct button handler before localStorage restore.
start=h.find("$('#file').onchange=")
if start>=0:
 end=h.find("try{rows=JSON.parse",start)
 if end<0:raise SystemExit('No se pudo delimitar handler antiguo')
 h=h[:start]+h[end:]
# Ensure receiveImportedRows and import button handler exist.
if 'window.receiveImportedRows=' not in h:
 marker="try{rows=JSON.parse"
 i=h.find(marker)
 if i<0:raise SystemExit('No se encontro punto de insercion')
 recv="""window.receiveImportedRows=function(json){try{const data=JSON.parse(json);rows=data.filter(r=>r&&r.name&&Number.isFinite(Number(r.x))&&Number.isFinite(Number(r.y))).map(r=>({type:String(r.type||''),x:Number(r.x),y:Number(r.y),name:String(r.name)}));localStorage.setItem('crnl_rows',JSON.stringify(rows));$('#status').textContent=`${rows.length} elementos importados y guardados`;render()}catch(e){$('#status').textContent='Error al procesar datos: '+e.message}};"""
 h=h[:i]+recv+h[i:]
if "$('#importBtn').onclick" not in h:
 marker="try{rows=JSON.parse"
 i=h.find(marker)
 hand="""$('#importBtn').onclick=()=>{if(window.AndroidImport&&typeof window.AndroidImport.importFile==='function'){$('#status').textContent='Selecciona un archivo Excel o CSV…';window.AndroidImport.importFile()}else $('#status').textContent='Importador Android no disponible en esta APK.';};"""
 h=h[:i]+hand+h[i:]
# No SheetJS CDN needed.
h=re.sub(r'<script\s+src="https://cdn\.jsdelivr\.net/npm/xlsx@[^\"]+"\s*></script>','',h)
H.write_text(h,encoding='utf-8')
# Java must contain native importer and activity result.
checks_java=['new ImportBridge','"AndroidImport"','r==IMPORT','NativeTabularImporter','receiveImportedRows']
missing=[x for x in checks_java if x not in j]
if missing:raise SystemExit('MainActivity no tiene importador nativo completo. Faltan: '+', '.join(missing))
# bump only code
b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);code=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1))
# final checks
h=H.read_text(); checks={'boton nativo':'id="importBtn"' in h,'click nativo':'AndroidImport.importFile' in h,'recepcion':'receiveImportedRows' in h,'sin file input':'id="file"' not in h,'sin CDN XLSX':'cdn.jsdelivr.net/npm/xlsx' not in h,'MainActivity completo':not missing}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
print('CORRECCION IMPORTACION OK versionCode',code)
