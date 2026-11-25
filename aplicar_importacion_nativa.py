from pathlib import Path
import re
H=Path('app/src/main/assets/index.html')
J=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java')
G=Path('app/build.gradle')
for p in (H,J,G):
    if not p.exists(): raise SystemExit('Falta '+str(p))
h=H.read_text(encoding='utf-8')
# Remove remote SheetJS dependency if present.
h=re.sub(r'<script\s+src="https://cdn\.jsdelivr\.net/npm/xlsx@[^\"]+"\s*></script>','',h)
start=h.find("$('#file').onchange=")
if start<0: raise SystemExit('No se encontro #file onchange')
end=h.find("try{rows=JSON.parse",start)
if end<0: raise SystemExit('No se encontro restauracion localStorage')
new="""window.receiveImportedRows=function(json){try{const data=JSON.parse(json);rows=data.filter(r=>r&&r.name&&Number.isFinite(Number(r.x))&&Number.isFinite(Number(r.y))).map(r=>({type:String(r.type||''),x:Number(r.x),y:Number(r.y),name:String(r.name)}));localStorage.setItem('crnl_rows',JSON.stringify(rows));$('#status').textContent=`${rows.length} elementos importados y guardados`;render()}catch(e){$('#status').textContent='Error al procesar los datos importados: '+e.message}};$('#file').onchange=e=>{const f=e.target.files&&e.target.files[0];if(!f){$('#status').textContent='No se seleccionó archivo.';return}$('#status').textContent='Importando '+f.name+'…';if(window.AndroidImport&&typeof window.AndroidImport.importFile==='function')window.AndroidImport.importFile();else $('#status').textContent='Importador Android no disponible.';};"""
h=h[:start]+new+h[end:]
H.write_text(h,encoding='utf-8')
# This patch intentionally checks for the native bridge implementation in MainActivity.
j=J.read_text(encoding='utf-8')
if 'class ImportBridge' not in j or 'parseXlsx' not in j or 'parseCsv' not in j:
    raise SystemExit('MainActivity todavía no contiene el importador nativo completo. Usa primero el ZIP completo corregido o sustituye MainActivity con la versión nativa.')
# bump
b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);code=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1))
print('Importacion nativa enlazada; versionCode',code)
