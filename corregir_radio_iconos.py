from pathlib import Path
p=Path('app/src/main/assets/index.html')
if not p.exists(): raise SystemExit('No existe app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')

# ICONOS: ocupar completamente cada baldosa, sin padding ni margen visual.
extra='.menu-tile{padding:0!important;overflow:hidden!important;background:#fff!important}.menu-tile img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important;border-radius:16px!important}'
if extra not in s:
    s=s.replace('</style>',extra+'</style>',1)

# RADIO: replace the complete search handler with a robust implementation.
start=s.find("$('#search').onclick=()=>")
end=s.find(';function openActions',start)
if start<0 or end<0: raise SystemExit('No localizo el manejador actual de BUSCAR ELEMENTOS')
new=r'''$('#search').onclick=()=>{
  if(!rows.length){$('#radioStatus').textContent='No hay datos cargados. Importa primero el Excel.';return}
  if(!navigator.geolocation){$('#radioStatus').textContent='Este dispositivo no permite obtener la ubicación.';return}
  $('#radioStatus').textContent='Obteniendo ubicación GPS…';
  const ok=p=>{
    let r=Math.max(1,Math.min(100000,+$('#manual').value||10));
    let f=rows.map((x,i)=>{let g=gps(x);return{x,i,g,d:hav(p.coords.latitude,p.coords.longitude,g.lat,g.lon)}}).filter(x=>Number.isFinite(x.d)&&x.d<=r).sort((a,b)=>a.d-b.d);
    $('#radioStatus').textContent=`${f.length} elemento(s) dentro de ${r} m · Precisión GPS ±${Math.round(p.coords.accuracy||0)} m`;
    $('#foundTitle').classList.toggle('hidden',!f.length);
    $('#found').innerHTML=f.slice(0,50).map(x=>`<li><button data-i="${x.i}" data-d="${x.d}"><b>${x.x.name}</b><br><small>${x.d<10?x.d.toFixed(1):Math.round(x.d)} m · ${x.x.type}</small></button></li>`).join('');
    document.querySelectorAll('[data-i]').forEach(b=>b.onclick=()=>openActions(+b.dataset.i,+b.dataset.d));
    $('#openAll').classList.toggle('hidden',!f.length);
  };
  const fail=e=>{
    let m='No se pudo obtener la ubicación GPS.';
    if(e&&e.code===1)m='Permiso de ubicación denegado. Activa Ubicación para C.R.N.L. en Ajustes.';
    else if(e&&e.code===2)m='GPS no disponible. Activa la ubicación del teléfono.';
    else if(e&&e.code===3)m='El GPS tardó demasiado. Sal al exterior o vuelve a intentarlo.';
    $('#radioStatus').textContent=m;
    $('#foundTitle').classList.add('hidden');$('#found').innerHTML='';$('#openAll').classList.add('hidden');
  };
  navigator.geolocation.getCurrentPosition(ok,fail,{enableHighAccuracy:true,timeout:30000,maximumAge:0});
}'''
s=s[:start]+new+s[end:]

# Gates: preserve buttons, import/menu/icons, bridges and WhatsApp.
for t in ['id="search"','id="radioStatus"','xlsx.jfif','destino.png','google earth.jfif','earthMenu','AndroidMaps','aWa','splash_nova_limia.jpg']:
    if t not in s: raise SystemExit('Falta elemento obligatorio: '+t)
p.write_text(s,encoding='utf-8')
print('OK: BUSCAR ELEMENTOS reparado con success/error/options y feedback visible')
print('OK: iconos al 100% de las baldosas del menu')
