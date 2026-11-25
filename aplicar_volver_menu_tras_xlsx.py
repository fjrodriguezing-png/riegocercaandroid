from pathlib import Path
import re,sys
H=Path('app/src/main/assets/index.html');G=Path('app/build.gradle')
if not H.exists():raise SystemExit('Falta index.html')
h=H.read_text(encoding='utf-8')
# Require current XLSX callback and menu panel before editing.
if 'receiveXlsxRows' not in h:raise SystemExit('No existe receiveXlsxRows; aplica este cambio sobre la version XLSX actual')
# Add helper that returns to main app view and leaves the hamburger menu OPEN.
helper="""function crnlReturnToOpenMenuAfterImport(){try{document.querySelectorAll('.menu-section,.screen').forEach(x=>{x.classList.add('hidden');x.classList.remove('active-view')});document.body.classList.remove('menu-mode');const mp=document.getElementById('menuPanel')||document.getElementById('menu');if(mp)mp.classList.remove('hidden');const mb=document.getElementById('menuBtn');if(mb)mb.setAttribute('aria-expanded','true');window.scrollTo({top:0,behavior:'smooth'})}catch(e){console.log(e)}}"""
if 'function crnlReturnToOpenMenuAfterImport()' not in h:
    # place immediately before receive callback
    pos=h.find('window.receiveXlsxRows=')
    h=h[:pos]+helper+h[pos:]
# Inject menu reopening after render, only inside receive XLSX callback.
# Current callbacks use render()}catch ; replace first occurrence after receiveXlsxRows.
pos=h.find('window.receiveXlsxRows=')
end=h.find('window.receiveXlsxError=',pos)
seg=h[pos:end]
if 'crnlReturnToOpenMenuAfterImport();' not in seg:
    # handle render()} variants
    if 'render()' not in seg:raise SystemExit('receiveXlsxRows no contiene render()')
    seg=seg.replace('render()','render();crnlReturnToOpenMenuAfterImport();',1)
    h=h[:pos]+seg+h[end:]
H.write_text(h,encoding='utf-8')
if G.exists():
 b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);v=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {v}',b,1));print('versionCode',v)
# Checks
hh=H.read_text();a=hh.find('window.receiveXlsxRows=');b=hh.find('window.receiveXlsxError=',a);seg=hh[a:b]
checks={'helper':'function crnlReturnToOpenMenuAfterImport()' in hh,'after successful import':'crnlReturnToOpenMenuAfterImport();' in seg,'opens menu':'classList.remove(\'hidden\')' in hh,'aria expanded':'aria-expanded\',\'true\'' in hh,'XLSX retained':'receiveXlsxRows' in hh and 'receiveXlsxError' in hh,'radio retained':('crnlUnifiedRuntimeV1' in hh or 'crnlXlsxRadioUnifiedV1' in hh or 'mapsRadiusSearch' in hh or 'id="search"' in hh)}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
