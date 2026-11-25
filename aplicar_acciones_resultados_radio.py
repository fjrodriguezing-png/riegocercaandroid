from pathlib import Path
import re,sys
H=Path('app/src/main/assets/index.html');G=Path('app/build.gradle')
if not H.exists():raise SystemExit('Falta index.html')
h=H.read_text(encoding='utf-8')
# Detect current list/status control IDs and require the existing action sheet or create it.
listid='mapsFoundList' if 'id="mapsFoundList"' in h else ('found' if 'id="found"' in h else None)
if not listid:raise SystemExit('No se encontro la lista de resultados por radio')
# Ensure a self-contained contextual action sheet exists.
if 'id="crnlResultActions"' not in h:
 sheet='''<div id="crnlResultActions" class="crnl-result-actions hidden"><div class="crnl-result-sheet"><h3 id="crnlResultName">Elemento</h3><div id="crnlResultMeta"></div><button id="crnlResultMaps" type="button" class="go">🗺️ Abrir en Google Maps</button><button id="crnlResultEarth" type="button">🌍 Ver en Google Earth</button><button id="crnlResultWhatsApp" type="button" class="crnl-wa">🟢 Denunciar incidencia por WhatsApp</button><button id="crnlResultCancel" type="button">Cancelar</button></div></div>'''
 h=h.replace('</main>',sheet+'</main>',1)
 css='''.crnl-result-actions{position:fixed;z-index:2000;inset:0;background:rgba(0,0,0,.50);display:flex;align-items:flex-end;justify-content:center;padding:12px}.crnl-result-actions.hidden{display:none}.crnl-result-sheet{width:min(100%,520px);background:#fff;border-radius:22px;padding:16px;box-shadow:0 18px 50px #0005}.crnl-result-sheet button{margin-top:9px}.crnl-wa{background:#25D366!important;color:#073b1c!important;font-weight:900!important}'''
 h=h.replace('</style>',css+'</style>',1)
# Add delegated click listener on the actual found list. This works with current radio result renderer even when its buttons have no onclick.
if 'crnlResultActionsFixV1' not in h:
 js=f'''/*crnlResultActionsFixV1*/(function(){{const list=document.getElementById('{listid}'),box=document.getElementById('crnlResultActions'),name=document.getElementById('crnlResultName'),meta=document.getElementById('crnlResultMeta');let current=null,currentGps=null;function close(){{box.classList.add('hidden');current=null;currentGps=null}}function allRows(){{if(typeof rows!=='undefined'&&Array.isArray(rows)&&rows.length)return rows;try{{return JSON.parse(localStorage.getItem('crnl_rows')||'[]')}}catch(e){{return[]}}}}function gp(r){{if(typeof gpsForRow==='function')return gpsForRow(r);if(typeof gps==='function')return gps(r);if(typeof utm==='function')return utm(Number(r.x),Number(r.y));return null}}list.addEventListener('click',e=>{{const btn=e.target.closest('button');if(!btn)return;e.preventDefault();e.stopPropagation();let idx=btn.dataset.crnlI??btn.dataset.radioIndex??btn.dataset.elementIndex;if(idx==null){{const buttons=[...list.querySelectorAll('button')];idx=buttons.indexOf(btn)}}idx=Number(idx);const rr=allRows();if(!Number.isInteger(idx)||idx<0||idx>=rr.length)return;current=rr[idx];currentGps=gp(current);if(!currentGps)return;let d=Number(btn.dataset.crnlD??btn.dataset.radioDistance??btn.dataset.elementDistance);name.textContent=current.name||current.NOMBRE||'Elemento';meta.textContent=`${{current.type||current.TIPO||'Sin tipo'}}${{Number.isFinite(d)?' · '+(d<10?d.toFixed(1):Math.round(d))+' m':''}}`;box.classList.remove('hidden')}},true);document.getElementById('crnlResultCancel').onclick=close;box.onclick=e=>{{if(e.target===box)close()}};document.getElementById('crnlResultMaps').onclick=()=>{{if(currentGps&&window.AndroidMaps)window.AndroidMaps.navigate(Number(currentGps.lat),Number(currentGps.lon))}};document.getElementById('crnlResultEarth').onclick=()=>{{if(!currentGps)return;location.href=`https://earth.google.com/web/search/${{currentGps.lat}},${{currentGps.lon}}`}};document.getElementById('crnlResultWhatsApp').onclick=()=>{{if(!current||!currentGps)return;const nm=current.name||current.NOMBRE||'Elemento',tp=current.type||current.TIPO||'Sin tipo',map=`https://www.google.com/maps/search/?api=1&query=${{currentGps.lat}},${{currentGps.lon}}`,text=`INCIDENCIA - ${{nm}}\nTipo: ${{tp}}\nSe ha detectado una incidencia en este elemento. Gracias.\n\nUbicación Google Maps:\n${{map}}`;location.href=`https://wa.me/34615179537?text=${{encodeURIComponent(text)}}`}};}})();'''
 q=h.rfind('</script>');h=h[:q]+js+h[q:]
H.write_text(h)
# bump
if G.exists():
 g=G.read_text();m=re.search(r'versionCode\s+(\d+)',g);v=int(m.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {v}',g,1));print('versionCode',v)
# checks
h=H.read_text();checks={'sheet':'id="crnlResultActions"' in h,'delegated listener':'crnlResultActionsFixV1' in h and "list.addEventListener('click'" in h,'Maps':'crnlResultMaps' in h and 'AndroidMaps.navigate' in h,'Earth':'crnlResultEarth' in h and 'earth.google.com/web/search' in h,'WhatsApp':'crnlResultWhatsApp' in h and 'wa.me/34615179537' in h,'data fallback':'crnl_rows' in h}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
