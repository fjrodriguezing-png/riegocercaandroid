from pathlib import Path
p=Path('app/src/main/assets/index.html')
if not p.exists(): raise SystemExit('No existe app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')
# Add common style once.
style='.back-menu{background:#187bcd;color:#fff;font-weight:800;margin-top:14px}'
if '.back-menu{' not in s:
    s=s.replace('</style>',style+'</style>',1)
# Three internal screens: Datos, Destino, Radio. Earth is external; menu remains available through droplet after return to app.
repls={
'<div id="status">Importa Excel con TIPO, X, Y y NOMBRE.</div></section>':'<div id="status">Importa Excel con TIPO, X, Y y NOMBRE.</div><button type="button" class="back-menu">💧 Volver al menú</button></section>',
'<div id="detail"></div></section>':'<div id="detail"></div><button type="button" class="back-menu">💧 Volver al menú</button></section>',
'<button id="openAll" class="go hidden">🗺️ ABRIR EN GOOGLE MAPS</button></section>':'<button id="openAll" class="go hidden">🗺️ ABRIR EN GOOGLE MAPS</button><button type="button" class="back-menu">💧 Volver al menú</button></section>'
}
for old,new in repls.items():
    if old not in s and 'Volver al menú' not in s: raise SystemExit('No localizo una de las pantallas esperadas')
    s=s.replace(old,new,1)
# Handler: close all screens then open menu panel.
needle="$('#closeMenu').onclick=()=>menu.classList.add('hidden');"
handler="$('#closeMenu').onclick=()=>menu.classList.add('hidden');document.querySelectorAll('.back-menu').forEach(b=>b.onclick=()=>{document.querySelectorAll('.screen').forEach(x=>x.classList.add('hidden'));menu.classList.remove('hidden')});"
if "document.querySelectorAll('.back-menu')" not in s:
    if needle not in s: raise SystemExit('No localizo closeMenu')
    s=s.replace(needle,handler,1)
# Hard gates: preserve current app features.
for t in ['xlsx.jfif','destino.png','google earth.jfif','splash_nova_limia.jpg','earthMenu','AndroidMaps','aWa','search','file']:
    if t not in s: raise SystemExit('Falta elemento que debe conservarse: '+t)
p.write_text(s,encoding='utf-8')
print('OK: Volver al menú añadido a Datos, Destino y Elementos por radio')
print('OK: menu, iconos, importacion, GPS, Maps, Earth y WhatsApp conservados')
