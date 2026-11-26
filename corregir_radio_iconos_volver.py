from pathlib import Path
import re
p=Path('app/src/main/assets/index.html')
if not p.exists(): raise SystemExit('No existe app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')

# 1) Iconos llenan por completo las baldosas.
css='.menu-tile{padding:0!important;overflow:hidden!important;background:#fff!important}.menu-tile img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important;border-radius:16px!important}.back-menu{background:#187bcd;color:#fff;font-weight:800;margin-top:14px}'
if css not in s:s=s.replace('</style>',css+'</style>',1)

# 2) Restaurar/asegurar Volver al menú en Datos, Destino y Radio, sin duplicarlo.
def inject_once(anchor, button):
    global s
    if button in s:return
    if anchor not in s:raise SystemExit('No localizo '+anchor)
    s=s.replace(anchor,anchor.replace('</section>',button+'</section>'),1)

inject_once('<div id="status">Importa Excel con TIPO, X, Y y NOMBRE.</div></section>','<button type="button" class="back-menu">💧 Volver al menú</button>')
inject_once('<div id="detail"></div></section>','<button type="button" class="back-menu">💧 Volver al menú</button>')
inject_once('<button id="openAll" class="go hidden">🗺️ ABRIR EN GOOGLE MAPS</button></section>','<button type="button" class="back-menu">💧 Volver al menú</button>')
needle="$('#closeMenu').onclick=()=>menu.classList.add('hidden');"
handler="$('#closeMenu').onclick=()=>menu.classList.add('hidden');document.querySelectorAll('.back-menu').forEach(b=>b.onclick=()=>{document.querySelectorAll('.screen').forEach(x=>x.classList.add('hidden'));menu.classList.remove('hidden')});"
if "document.querySelectorAll('.back-menu')" not in s:
    if needle not in s:raise SystemExit('No localizo closeMenu')
    s=s.replace(needle,handler,1)

# 3) Reescribir búsqueda por radio robusta.
start=s.find("$('#search').onclick=()=>")
end=s.find(';function openActions',start)
if start<0 or end<0:raise SystemExit('No localizo BUSCAR ELEMENTOS')
new=r'''$('#search').onclick=()=>{
if(!rows.length){$('#radioStatus').textContent='No hay datos cargados. Importa primero el Excel.';return}
if(!navigator.geolocation){$('#radioStatus').textContent='Ubicación GPS no disponible en este dispositivo.';return}
$('#radioStatus').textContent='Obteniendo ubicación GPS…';
const ok=p=>{let r=Math.max(1,Math.min(100000,+$('#manual').value||10)),f=rows.map((x,i)=>{let g=gps(x);return{x,i,g,d:hav(p.coords.latitude,p.coords.longitude,g.lat,g.lon)}}).filter(x=>Number.isFinite(x.d)&&x.d<=r).sort((a,b)=>a.d-b.d);$('#radioStatus').textContent=`${f.length} elemento(s) dentro de ${r} m · Precisión GPS ±${Math.round(p.coords.accuracy||0)} m`;$('#foundTitle').classList.toggle('hidden',!f.length);$('#found').innerHTML=f.slice(0,50).map(x=>`<li><button data-i="${x.i}" data-d="${x.d}"><b>${x.x.name}</b><br><small>${x.d<10?x.d.toFixed(1):Math.round(x.d)} m · ${x.x.type}</small></button></li>`).join('');document.querySelectorAll('[data-i]').forEach(b=>b.onclick=()=>openActions(+b.dataset.i,+b.dataset.d));$('#openAll').classList.toggle('hidden',!f.length)};
const fail=e=>{let m='No se pudo obtener la ubicación GPS.';if(e&&e.code===1)m='Permiso de ubicación denegado. Activa Ubicación para C.R.N.L. en Ajustes.';else if(e&&e.code===2)m='GPS no disponible. Activa la ubicación del teléfono.';else if(e&&e.code===3)m='El GPS tardó demasiado. Vuelve a intentarlo.';$('#radioStatus').textContent=m;$('#foundTitle').classList.add('hidden');$('#found').innerHTML='';$('#openAll').classList.add('hidden')};
navigator.geolocation.getCurrentPosition(ok,fail,{enableHighAccuracy:true,timeout:30000,maximumAge:0})
}'''
s=s[:start]+new+s[end:]

# Gates, including back-menu count.
required=['xlsx.jfif','destino.png','google earth.jfif','splash_nova_limia.jpg','earthMenu','AndroidMaps','aWa','id="search"','id="file"']
for x in required:
    if x not in s:raise SystemExit('Falta '+x)
if s.count('class="back-menu"') < 3:raise SystemExit('Faltan botones Volver al menú')
p.write_text(s,encoding='utf-8')
print('OK: 3 botones Volver al menú presentes')
print('OK: Buscar elementos corregido')
print('OK: iconos al 100% de las baldosas')
