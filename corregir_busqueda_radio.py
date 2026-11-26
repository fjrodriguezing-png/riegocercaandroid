from pathlib import Path
p=Path('app/src/main/assets/index.html')
if not p.exists(): raise SystemExit('No existe app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')
old=")},{enableHighAccuracy:true,timeout:20000,maximumAge:0})};function openActions"
new=")},err=>{let m='No se pudo obtener la ubicación.';if(err&&err.code===1)m='Permiso de ubicación denegado. Activa la ubicación para buscar elementos por radio.';else if(err&&err.code===2)m='Ubicación no disponible. Activa el GPS y vuelve a intentarlo.';else if(err&&err.code===3)m='Tiempo de espera agotado al obtener la ubicación. Vuelve a intentarlo.';$('#radioStatus').textContent=m;$('#foundTitle').classList.add('hidden');$('#found').innerHTML='';$('#openAll').classList.add('hidden')},{enableHighAccuracy:true,timeout:20000,maximumAge:0})};function openActions"
if old not in s:
    raise SystemExit('No localizo la llamada getCurrentPosition esperada; no modifico el proyecto.')
s=s.replace(old,new,1)
# Verify core features remain.
for token in ['xlsx.jfif','destino.png','google earth.jfif','splash_nova_limia.jpg','wa.me/34615179537','AndroidMaps','getCurrentPosition(p=>']:
    if token not in s: raise SystemExit('Falta elemento que debe conservarse: '+token)
p.write_text(s,encoding='utf-8')
print('OK: getCurrentPosition ahora usa success, error y options en el orden correcto')
print('OK: mensajes de GPS/permisos visibles en radioStatus')
print('OK: menu, iconos, importacion, Maps, Earth y WhatsApp conservados')
