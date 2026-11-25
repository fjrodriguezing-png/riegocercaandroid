from pathlib import Path
import re
H=Path('app/src/main/assets/index.html'); J=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java'); G=Path('app/build.gradle')
for p in (H,J,G):
    if not p.exists(): raise SystemExit('Falta '+str(p))
# Preserve all visual/UI files except exact import handler in index.html and MainActivity import capability.
h=H.read_text(encoding='utf-8')
h=re.sub(r'<script\s+src="https://cdn\.jsdelivr\.net/npm/xlsx@[^\"]+"\s*></script>','',h)
start=h.find("$('#file').onchange=")
if start<0: raise SystemExit('No se encontro #file onchange en index.html')
# identify end robustly using persisted rows restore; current projects use crnl_rows or regadio key
candidates=[h.find("try{rows=JSON.parse",start),h.find("render();</script>",start)]
ends=[x for x in candidates if x>start]
if not ends: raise SystemExit('No se pudo delimitar el handler de importacion')
end=min(ends)
handler="""window.receiveImportedRows=function(json){try{const data=JSON.parse(json);rows=data.filter(r=>r&&r.name&&Number.isFinite(Number(r.x))&&Number.isFinite(Number(r.y))).map(r=>({type:String(r.type||''),x:Number(r.x),y:Number(r.y),name:String(r.name)}));localStorage.setItem('crnl_rows',JSON.stringify(rows));$('#status').textContent=`${rows.length} elementos importados y guardados`;render()}catch(e){$('#status').textContent='Error al procesar los datos: '+e.message}};$('#file').onchange=e=>{const f=e.target.files&&e.target.files[0];if(!f){$('#status').textContent='No se seleccionó archivo.';return}$('#status').textContent='Importando '+f.name+'…';if(window.AndroidImport&&typeof window.AndroidImport.importFile==='function')window.AndroidImport.importFile();else $('#status').textContent='Importador Android no disponible.';};"""
h=h[:start]+handler+h[end:]
H.write_text(h,encoding='utf-8')
# Patch current MainActivity rather than replace all app logic: imports + bridge + result handling + parser methods.
j=J.read_text(encoding='utf-8')
# Required Java imports are added after package declaration safely.
imports='''import android.provider.OpenableColumns;import android.database.Cursor;import java.io.*;import java.util.*;import java.util.zip.*;import java.text.Normalizer;import org.json.*;import org.w3c.dom.*;import javax.xml.parsers.*;'''
if 'android.provider.OpenableColumns' not in j:
    pos=j.find(';',j.find('package '))+1;j=j[:pos]+imports+j[pos:]
# request code
j=j.replace('static final int LOC=7,FILE=8;','static final int LOC=7,FILE=8,IMPORT=9;') if 'static final int LOC=7,FILE=8;' in j else j
# bridge
needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");'
if 'new ImportBridge()' not in j:
    if needle not in j: raise SystemExit('No se encontro AndroidMaps bridge en MainActivity')
    j=j.replace(needle,needle+'w.addJavascriptInterface(new ImportBridge(),"AndroidImport");',1)
# Insert class/methods before final class closing brace. Avoid relying on existing onActivityResult.
if 'class ImportBridge' not in j:
    block=r'''
 class ImportBridge{@JavascriptInterface public void importFile(){runOnUiThread(()->{Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("*/*");i.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","text/csv","text/comma-separated-values","application/csv"});startActivityForResult(i,IMPORT);});}}
 void handleImport(Intent d){if(d==null||d.getData()==null)return;Uri u=d.getData();try{String name=fileName(u).toLowerCase(Locale.ROOT);JSONArray arr=name.endsWith(".csv")?parseCsv(u):parseXlsx(u);String js="window.receiveImportedRows("+JSONObject.quote(arr.toString())+")";w.post(()->w.evaluateJavascript(js,null));}catch(Exception e){String msg=e.getMessage()==null?e.toString():e.getMessage();w.post(()->w.evaluateJavascript("document.querySelector('#status').textContent="+JSONObject.quote("Error al importar: "+msg),null));}}
 String fileName(Uri u){String n="";try(Cursor c=getContentResolver().query(u,null,null,null,null)){if(c!=null&&c.moveToFirst()){int i=c.getColumnIndex(OpenableColumns.DISPLAY_NAME);if(i>=0)n=c.getString(i);}}return n;}
 JSONArray parseCsv(Uri u)throws Exception{BufferedReader br=new BufferedReader(new InputStreamReader(getContentResolver().openInputStream(u),"UTF-8"));String head=br.readLine();if(head==null)throw new Exception("CSV vacío");char sep=head.contains(";")?';':',';String[] cols=head.split(java.util.regex.Pattern.quote(String.valueOf(sep)),-1);JSONArray a=new JSONArray();String line;while((line=br.readLine())!=null){JSONObject o=row(cols,line.split(java.util.regex.Pattern.quote(String.valueOf(sep)),-1));if(o!=null)a.put(o);}return a;}
 JSONObject row(String[] c,String[] v)throws Exception{String tipo="",nombre="",xs="",ys="";for(int i=0;i<c.length&&i<v.length;i++){String k=norm(c[i]),x=v[i].trim();if(k.equals("TIPO"))tipo=x;else if(k.equals("NOMBRE"))nombre=x;else if(k.equals("X")||k.equals("COORDENADAX"))xs=x;else if(k.equals("Y")||k.equals("COORDENADAY"))ys=x;}if(nombre.isEmpty()||xs.isEmpty()||ys.isEmpty())return null;return new JSONObject().put("type",tipo).put("name",nombre).put("x",Double.parseDouble(xs.replace(',','.'))).put("y",Double.parseDouble(ys.replace(',','.')));}
 String norm(String s){return Normalizer.normalize(s==null?"":s,Normalizer.Form.NFD).replaceAll("\\p{M}","").replaceAll("[^A-Za-z0-9]","").toUpperCase(Locale.ROOT);}
 JSONArray parseXlsx(Uri u)throws Exception{File t=File.createTempFile("crnl_",".xlsx",getCacheDir());try(InputStream in=getContentResolver().openInputStream(u);OutputStream out=new FileOutputStream(t)){byte[] b=new byte[8192];int n;while((n=in.read(b))>0)out.write(b,0,n);}Map<String,byte[]> z=new HashMap<>();try(ZipInputStream in=new ZipInputStream(new FileInputStream(t))){ZipEntry e;while((e=in.getNextEntry())!=null){String n=e.getName();if(n.equals("xl/sharedStrings.xml")||n.equals("xl/worksheets/sheet1.xml")){ByteArrayOutputStream o=new ByteArrayOutputStream();byte[] b=new byte[4096];int q;while((q=in.read(b))>0)o.write(b,0,q);z.put(n,o.toByteArray());}}}List<String> ss=shared(z.get("xl/sharedStrings.xml"));byte[] sheet=z.get("xl/worksheets/sheet1.xml");if(sheet==null)throw new Exception("No se encontró la primera hoja");Document doc=DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(new ByteArrayInputStream(sheet));NodeList rs=doc.getElementsByTagName("row");List<List<String>> rr=new ArrayList<>();for(int ri=0;ri<rs.getLength();ri++){NodeList cs=((Element)rs.item(ri)).getElementsByTagName("c");Map<Integer,String> map=new HashMap<>();int mx=-1;for(int ci=0;ci<cs.getLength();ci++){Element ce=(Element)cs.item(ci);int idx=col(ce.getAttribute("r"));String val="";NodeList vn=ce.getElementsByTagName("v");if(vn.getLength()>0)val=vn.item(0).getTextContent();if("s".equals(ce.getAttribute("t"))&&!val.isEmpty())val=ss.get(Integer.parseInt(val));map.put(idx,val);mx=Math.max(mx,idx);}List<String> line=new ArrayList<>();for(int k=0;k<=mx;k++)line.add(map.getOrDefault(k,""));rr.add(line);}if(rr.isEmpty())throw new Exception("Excel sin filas");String[] cols=rr.get(0).toArray(new String[0]);JSONArray a=new JSONArray();for(int i=1;i<rr.size();i++){JSONObject o=row(cols,rr.get(i).toArray(new String[0]));if(o!=null)a.put(o);}t.delete();return a;}
 List<String> shared(byte[] b)throws Exception{List<String> o=new ArrayList<>();if(b==null)return o;Document d=DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(new ByteArrayInputStream(b));NodeList n=d.getElementsByTagName("si");for(int i=0;i<n.getLength();i++)o.add(n.item(i).getTextContent());return o;}
 int col(String r){int n=0;for(int i=0;i<r.length()&&Character.isLetter(r.charAt(i));i++)n=n*26+(Character.toUpperCase(r.charAt(i))-'A'+1);return n-1;}
'''
    # Insert before last }
    j=j[:j.rfind('}')]+block+j[j.rfind('}'):]
# Hook onActivityResult: if existing, add IMPORT branch after super line; otherwise create.
if 'protected void onActivityResult' in j:
    sig=j.find('protected void onActivityResult')
    body=j.find('{',sig)+1
    if 'r==IMPORT' not in j[sig:j.find('}',body)+1]: j=j[:body]+'if(r==IMPORT&&c==RESULT_OK){handleImport(d);return;}'+j[body:]
else:
    insertion='protected void onActivityResult(int r,int c,Intent d){super.onActivityResult(r,c,d);if(r==IMPORT&&c==RESULT_OK)handleImport(d);}'
    j=j[:j.rfind('}')]+insertion+j[j.rfind('}'):]
J.write_text(j,encoding='utf-8')
# bump version
b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);code=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1))
# validate exact features and preserve others
h=H.read_text();j=J.read_text();checks={'JS bridge call':'AndroidImport.importFile' in h,'JS receive':'receiveImportedRows' in h,'No remote XLSX':'cdn.jsdelivr.net/npm/xlsx' not in h,'ImportBridge':'class ImportBridge' in j,'parseXlsx':'parseXlsx' in j,'parseCsv':'parseCsv' in j,'onActivityResult':'r==IMPORT' in j,'columns':all(x in j for x in ['TIPO','NOMBRE','COORDENADAX','COORDENADAY']),'Maps preserved':'MapsBridge' in j,'splash preserved':'appSplash' in h or 'id="splash"' in h,'menu preserved':'menu-panel' in h,'WhatsApp preserved':'elementActionWhatsApp' in h or 'id="aWa"' in h,'Earth preserved':'earthMenu' in h}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):raise SystemExit('Falló la comprobación del parche completo')
print('PATCH COMPLETE OK versionCode',code)
