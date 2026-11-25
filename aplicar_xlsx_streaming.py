from pathlib import Path
import re,shutil,sys
base=Path('app/src/main/java/es/riegocerca/maps');H=Path('app/src/main/assets/index.html');J=base/'MainActivity.java';G=Path('app/build.gradle');src=Path('.crnl_import_files')
for p in (H,J,G,src/'ImportBridge.java',src/'XlsxStreamingImporter.java'):
 if not p.exists():raise SystemExit('Falta '+str(p))
base.mkdir(parents=True,exist_ok=True);shutil.copy2(src/'ImportBridge.java',base/'ImportBridge.java');shutil.copy2(src/'XlsxStreamingImporter.java',base/'XlsxStreamingImporter.java')
j=J.read_text();needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");'
if 'IMPORT_XLSX=91' not in j:
 # add constant directly after class open to avoid old constant variants
 p=j.find('{',j.find('class MainActivity'))+1;j=j[:p]+'static final int IMPORT_XLSX=91;'+j[p:]
if '"AndroidImport"' not in j:
 if needle not in j:raise SystemExit('No se encontro AndroidMaps bridge')
 j=j.replace(needle,needle+'w.addJavascriptInterface(new ImportBridge(this,IMPORT_XLSX),"AndroidImport");',1)
cb='''if(r==IMPORT_XLSX&&c==RESULT_OK&&d!=null&&d.getData()!=null){Uri xlsxUri=d.getData();new Thread(()->{try{org.json.JSONArray a=new XlsxStreamingImporter(this).read(xlsxUri);String js="window.receiveXlsxRows("+org.json.JSONObject.quote(a.toString())+")";w.post(()->w.evaluateJavascript(js,null));}catch(Exception ex){String msg=ex.getMessage()==null?ex.toString():ex.getMessage();w.post(()->w.evaluateJavascript("window.receiveXlsxError("+org.json.JSONObject.quote(msg)+")",null));}}).start();return;}'''
if 'r==IMPORT_XLSX' not in j:
 if 'protected void onActivityResult' in j:
  p=j.find('{',j.find('protected void onActivityResult'))+1;j=j[:p]+cb+j[p:]
 else:j=j[:j.rfind('}')]+f'protected void onActivityResult(int r,int c,Intent d){{super.onActivityResult(r,c,d);{cb}}}'+j[j.rfind('}'):]
J.write_text(j)
h=H.read_text();h=re.sub(r'<script\s+src="https://cdn\.jsdelivr\.net/npm/xlsx@[^\"]+"\s*></script>','',h)
# replace current file/import control with a deterministic native XLSX button
h=re.sub(r'<input\s+id="file"[^>]*>','<button id="xlsxBtn" type="button" class="go">📥 SELECCIONAR XLSX</button>',h,count=1)
h=re.sub(r'<button\s+id="importBtn"[^>]*>.*?</button>','<button id="xlsxBtn" type="button" class="go">📥 SELECCIONAR XLSX</button>',h,count=1,flags=re.S)
# remove old file onchange handler conservatively
start=h.find("$('#file').onchange=")
if start>=0:
 end=h.find("try{rows=JSON.parse",start)
 if end>start:h=h[:start]+h[end:]
# insert bridge callbacks just before rows restore
pos=h.find("try{rows=JSON.parse")
if pos<0:raise SystemExit('No restore marker')
code="""window.receiveXlsxRows=function(json){try{const data=JSON.parse(json);rows=data.map(r=>({type:String(r.type||''),x:Number(r.x),y:Number(r.y),name:String(r.name||'')})).filter(r=>r.name&&Number.isFinite(r.x)&&Number.isFinite(r.y));localStorage.setItem('crnl_rows',JSON.stringify(rows));$('#status').textContent=`${rows.length} elementos XLSX importados y guardados`;$('#xlsxBtn').disabled=false;render()}catch(e){window.receiveXlsxError(e.message)}};window.receiveXlsxError=function(msg){$('#status').textContent='Error XLSX: '+msg;$('#xlsxBtn').disabled=false};$('#xlsxBtn').onclick=()=>{if(!window.AndroidImport){$('#status').textContent='Importador XLSX Android no disponible.';return}$('#status').textContent='Selecciona el archivo XLSX…';$('#xlsxBtn').disabled=true;window.AndroidImport.importXlsx();setTimeout(()=>{if($('#xlsxBtn').disabled)$('#status').textContent='Procesando XLSX…'},1200)};"""
if 'receiveXlsxRows' not in h:h=h[:pos]+code+h[pos:]
H.write_text(h)
# bump
b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);ver=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {ver}',b,1))
# checks
h=H.read_text();j=J.read_text();checks={'button':'xlsxBtn' in h,'bridge':'importXlsx' in h and 'AndroidImport' in j,'stream parser':'XlsxStreamingImporter' in j,'background':'new Thread' in j,'receive':'receiveXlsxRows' in h,'no SheetJS CDN':'cdn.jsdelivr.net/npm/xlsx' not in h,'radio preserved':('mapsRadiusSearch' in h or 'id="search"' in h),'WA preserved':('elementActionWhatsApp' in h or 'id="aWa"' in h),'Earth preserved':'earthMenu' in h}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
print('XLSX STREAMING READY versionCode',ver)
