from pathlib import Path
import re,shutil,sys
H=Path('app/src/main/assets/index.html');base=Path('app/src/main/java/es/riegocerca/maps');src=Path('import_files')
if not H.exists():raise SystemExit('Falta index.html')
# java files are expected beside script under import_files after workflow copies package; script handles project root package use
pkg=Path('.crnl_import_files')
if not pkg.exists():raise SystemExit('Falta .crnl_import_files con los Java')
base.mkdir(parents=True,exist_ok=True)
for n in ['MainActivity.java','ImportBridge.java','NativeTabularImporter.java']:shutil.copy2(pkg/n,base/n)
h=H.read_text();h=re.sub(r'<script\s+src="https://cdn\.jsdelivr\.net/npm/xlsx@[^\"]+"\s*></script>','',h)
start=h.find("$('#file').onchange=");end=h.find("try{rows=JSON.parse",start)
if start<0 or end<0:raise SystemExit('No se pudo localizar handler importacion')
new="""window.receiveImportedRows=function(json){try{const data=JSON.parse(json);rows=data.filter(r=>r&&r.name&&Number.isFinite(Number(r.x))&&Number.isFinite(Number(r.y))).map(r=>({type:String(r.type||''),x:Number(r.x),y:Number(r.y),name:String(r.name)}));localStorage.setItem('crnl_rows',JSON.stringify(rows));$('#status').textContent=`${rows.length} elementos importados y guardados`;render()}catch(e){$('#status').textContent='Error al procesar los datos: '+e.message}};$('#file').onchange=e=>{const f=e.target.files&&e.target.files[0];if(!f)return;$('#status').textContent='Importando '+f.name+'…';if(window.AndroidImport)window.AndroidImport.importFile();else $('#status').textContent='Importador Android no disponible.';};"""
h=h[:start]+new+h[end:];H.write_text(h)
# verify
j=(base/'MainActivity.java').read_text();checks=['AndroidImport','ImportBridge','NativeTabularImporter'];
for x in checks:
 if x not in j:raise SystemExit('Falta '+x)
if 'receiveImportedRows' not in H.read_text():raise SystemExit('Falta receiveImportedRows')
print('PAQUETE UNICO IMPORTACION INSTALADO Y VERIFICADO')
