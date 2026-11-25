from pathlib import Path
import re,sys
H=Path('app/src/main/assets/index.html');G=Path('app/build.gradle')
if not H.exists():raise SystemExit('Falta index.html')
h=H.read_text(encoding='utf-8')
# Detect current IDs: old V25 mapsRadiusSearch/mapsRadiusManual/maps10Status/mapsFoundList or consolidated search/manual/radioStatus/found.
old='mapsRadiusSearch' in h
ids={
 'button':'mapsRadiusSearch' if old else 'search',
 'manual':'mapsRadiusManual' if old else 'manual',
 'status':'maps10Status' if old else 'radioStatus',
 'list':'mapsFoundList' if old else 'found',
 'title':'mapsFoundTitle' if old else 'foundTitle'
}
for x in ids.values():
 if f'id="{x}"' not in h:raise SystemExit('Falta control '+x)
# Append robust override at end of main inline script, independent of previous broken handler.
marker='crnlRadioSearchFixV1'
if marker not in h:
 code=f'''/*{marker}*/(function(){{const btn=document.getElementById('{ids['button']}'),manual=document.getElementById('{ids['manual']}'),status=document.getElementById('{ids['status']}'),list=document.getElementById('{ids['list']}'),title=document.getElementById('{ids['title']}');function dist(a,b,c,d){{const R=6371000,t=x=>x*Math.PI/180,A=Math.sin(t(c-a)/2)**2+Math.cos(t(a))*Math.cos(t(c))*Math.sin(t(d-b)/2)**2;return 2*R*Math.asin(Math.sqrt(A))}}function rowGps(r){{if(typeof gpsForRow==='function')return gpsForRow(r);if(typeof gps==='function')return gps(r);if(typeof utm==='function')return utm(Number(r.x),Number(r.y));return null}}async function runRadio(){{try{{if(!Array.isArray(rows)||!rows.length){{status.textContent='No hay datos cargados. Importa primero el Excel/CSV.';return}}let radius=Number(manual.value);if(!Number.isFinite(radius)||radius<1)radius=10;btn.disabled=true;btn.textContent='BUSCANDO…';status.textContent='Solicitando ubicación GPS…';if(!navigator.geolocation)throw new Error('GPS no disponible en este dispositivo');navigator.geolocation.getCurrentPosition(p=>{{try{{const lat=Number(p.coords.latitude),lon=Number(p.coords.longitude);let found=rows.map((r,i)=>{{const g=rowGps(r);if(!g||!Number.isFinite(g.lat)||!Number.isFinite(g.lon))return null;return{{r,i,g,d:dist(lat,lon,g.lat,g.lon)}}}}).filter(Boolean).filter(x=>x.d<=radius).sort((a,b)=>a.d-b.d);status.textContent=found.length?`${{found.length}} elemento(s) dentro de ${{radius}} m · precisión GPS aprox. ${{Math.round(p.coords.accuracy||0)}} m`:`No hay elementos dentro de ${{radius}} m.`;title.classList.toggle('hidden',!found.length);list.innerHTML=found.slice(0,50).map(x=>`<li><button type="button" class="result-action" data-radio-index="${{x.i}}" data-radio-distance="${{x.d}}"><b>${{x.r.name}}</b><small>Distancia: ${{x.d<10?x.d.toFixed(1):Math.round(x.d)}} m · ${{x.r.type||'Sin tipo'}}</small></button></li>`).join('');document.querySelectorAll('[data-radio-index]').forEach(b=>b.onclick=()=>{{const i=Number(b.dataset.radioIndex),d=Number(b.dataset.radioDistance);if(typeof openElementActions==='function')openElementActions(i,d);else if(typeof openNameActions==='function')openNameActions(i,d)}});}}catch(e){{status.textContent='Error al calcular radio: '+e.message}}finally{{btn.disabled=false;btn.textContent='🔎 BUSCAR ELEMENTOS'}}}},e=>{{let msg='No se pudo obtener ubicación';if(e.code===1)msg='Permiso de ubicación denegado';if(e.code===2)msg='Ubicación no disponible. Activa GPS';if(e.code===3)msg='El GPS tardó demasiado';status.textContent=msg;btn.disabled=false;btn.textContent='🔎 BUSCAR ELEMENTOS'}},{{enableHighAccuracy:true,timeout:20000,maximumAge:0}})}}catch(e){{status.textContent='Error: '+e.message;btn.disabled=false;btn.textContent='🔎 BUSCAR ELEMENTOS'}}}}btn.onclick=runRadio;}})();'''
 # insert before last </script> to run after existing handlers
 pos=h.rfind('</script>');h=h[:pos]+code+h[pos:]
H.write_text(h,encoding='utf-8')
# bump
if G.exists():
 b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);code=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1));print('versionCode',code)
# verify
h=H.read_text();checks={'fix present':marker in h,'button bind':'btn.onclick=runRadio' in h,'gps':'navigator.geolocation.getCurrentPosition' in h,'sort':'.sort((a,b)=>a.d-b.d)' in h,'radius':f"getElementById('{ids['manual']}')" in h,'rows check':'No hay datos cargados' in h,'errors':'Permiso de ubicación denegado' in h}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
