from pathlib import Path
import re,sys
H=Path('app/src/main/assets/index.html');G=Path('app/build.gradle')
if not H.exists():raise SystemExit('Falta index.html')
h=H.read_text(encoding='utf-8')
# detect ids in current project
button='mapsRadiusSearch' if 'id="mapsRadiusSearch"' in h else ('search' if 'id="search"' in h else None)
manual='mapsRadiusManual' if 'id="mapsRadiusManual"' in h else ('manual' if 'id="manual"' in h else None)
status='maps10Status' if 'id="maps10Status"' in h else ('radioStatus' if 'id="radioStatus"' in h else None)
listid='mapsFoundList' if 'id="mapsFoundList"' in h else ('found' if 'id="found"' in h else None)
title='mapsFoundTitle' if 'id="mapsFoundTitle"' in h else ('foundTitle' if 'id="foundTitle"' in h else None)
if not all([button,manual,status,listid,title]):raise SystemExit('Faltan controles de Elementos por radio')
# add visual click feedback and use already imported rows from localStorage if global rows is empty.
marker='crnlRadioDirectFixV2'
if marker not in h:
 js=f'''/*{marker}*/(function(){{const b=document.getElementById('{button}'),m=document.getElementById('{manual}'),st=document.getElementById('{status}'),ls=document.getElementById('{listid}'),tt=document.getElementById('{title}');function distance(a,b,c,d){{const R=6371000,t=x=>x*Math.PI/180,A=Math.sin(t(c-a)/2)**2+Math.cos(t(a))*Math.cos(t(c))*Math.sin(t(d-b)/2)**2;return 2*R*Math.asin(Math.sqrt(A))}}function getRows(){{if(Array.isArray(window.rows)&&window.rows.length)return window.rows;if(typeof rows!=='undefined'&&Array.isArray(rows)&&rows.length)return rows;for(const k of ['crnl_rows','regadio_baixa_limia_v102']){{try{{const x=JSON.parse(localStorage.getItem(k)||'[]');if(Array.isArray(x)&&x.length)return x}}catch(e){{}}}}return[]}}function coord(r){{try{{if(typeof gpsForRow==='function')return gpsForRow(r);if(typeof gps==='function')return gps(r);if(typeof utm==='function')return utm(Number(r.x),Number(r.y))}}catch(e){{}}return null}}function restore(){{b.disabled=false;b.textContent='🔎 BUSCAR ELEMENTOS'}}b.addEventListener('click',function(e){{e.preventDefault();e.stopPropagation();const data=getRows();if(!data.length){{st.textContent='No hay datos cargados. Importa primero el XLSX.';restore();return}}let radius=Number(m.value);if(!Number.isFinite(radius)||radius<1)radius=10;b.disabled=true;b.textContent='BUSCANDO…';st.textContent='Obteniendo ubicación GPS…';if(!navigator.geolocation){{st.textContent='GPS no disponible.';restore();return}}navigator.geolocation.getCurrentPosition(p=>{{try{{let out=[];for(let i=0;i<data.length;i++){{const r=data[i],g=coord(r);if(!g||!Number.isFinite(Number(g.lat))||!Number.isFinite(Number(g.lon)))continue;let d=distance(Number(p.coords.latitude),Number(p.coords.longitude),Number(g.lat),Number(g.lon));if(d<=radius)out.push({{r,i,g,d}})}}out.sort((x,y)=>x.d-y.d);st.textContent=out.length?`${{out.length}} elemento(s) dentro de ${{radius}} m · precisión GPS ${{Math.round(p.coords.accuracy||0)}} m`:`No hay elementos dentro de ${{radius}} m.`;tt.classList.toggle('hidden',!out.length);ls.innerHTML=out.slice(0,50).map(x=>`<li><button type="button" data-crnl-i="${{x.i}}" data-crnl-d="${{x.d}}"><b>${{x.r.name||x.r.NOMBRE||''}}</b><small>${{x.d<10?x.d.toFixed(1):Math.round(x.d)}} m · ${{x.r.type||x.r.TIPO||'Sin tipo'}}</small></button></li>`).join('');document.querySelectorAll('[data-crnl-i]').forEach(x=>x.onclick=()=>{{const i=Number(x.dataset.crnlI),d=Number(x.dataset.crnlD);if(typeof openElementActions==='function')openElementActions(i,d);else if(typeof openNameActions==='function')openNameActions(i,d)}})}}catch(err){{st.textContent='Error al buscar: '+err.message}}finally{{restore()}}}},err=>{{st.textContent=err.code===1?'Permiso GPS denegado':err.code===2?'Ubicación no disponible. Activa GPS':'El GPS ha tardado demasiado';restore()}},{{enableHighAccuracy:true,timeout:20000,maximumAge:0}})}},true);}})();'''
 pos=h.rfind('</script>');h=h[:pos]+js+h[pos:]
H.write_text(h,encoding='utf-8')
# bump
if G.exists():
 g=G.read_text();mt=re.search(r'versionCode\s+(\d+)',g);v=int(mt.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {v}',g,1));print('versionCode',v)
# checks
h=H.read_text();checks={'listener capture':'addEventListener(\'click\'' in h,'immediate feedback':"b.textContent='BUSCANDO…'" in h,'localstorage fallback':'crnl_rows' in h and 'regadio_baixa_limia_v102' in h,'gps':'getCurrentPosition' in h,'sort':'out.sort((x,y)=>x.d-y.d)' in h,'error messages':'Permiso GPS denegado' in h}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
