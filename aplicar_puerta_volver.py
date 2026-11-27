from pathlib import Path
p=Path('app/src/main/assets/index.html')
if not p.exists(): raise SystemExit('No existe index.html')
s=p.read_text(encoding='utf-8')
old='<button id="closeMenu">✕ Cerrar menú</button>'
new='<button id="closeMenu" class="menu-tile" aria-label="Cerrar menú"><img src="cerrar_menu.png" alt="Cerrar menú"></button>'
if new not in s:
 if old not in s: raise SystemExit('No localizo Cerrar menú')
 s=s.replace(old,new,1)
css='.menu-tile{padding:0!important;overflow:hidden!important;background:#fff!important}.menu-tile img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important;border-radius:16px!important}.back-menu{background:#187bcd;color:#fff;font-weight:800;margin-top:14px}'
if '.back-menu{' not in s:s=s.replace('</style>',css+'</style>',1)
btn='<button type="button" class="back-menu">💧 Volver al menú</button>'
for a in ['<div id="status">Importa Excel con TIPO, X, Y y NOMBRE.</div></section>','<div id="detail"></div></section>','<button id="openAll" class="go hidden">🗺️ ABRIR EN GOOGLE MAPS</button></section>']:
 target=a[:-10]+btn+'</section>'
 if target not in s:
  if a not in s: raise SystemExit('No localizo una pantalla interna')
  s=s.replace(a,target,1)
needle="$('#closeMenu').onclick=()=>menu.classList.add('hidden');"
handler="$('#closeMenu').onclick=()=>menu.classList.add('hidden');document.querySelectorAll('.back-menu').forEach(b=>b.onclick=()=>{document.querySelectorAll('.screen').forEach(x=>x.classList.add('hidden'));menu.classList.remove('hidden')});"
if "document.querySelectorAll('.back-menu')" not in s:
 if needle not in s: raise SystemExit('No localizo controlador closeMenu')
 s=s.replace(needle,handler,1)
if s.count('class="back-menu"')<3:raise SystemExit('Faltan botones volver al menú')
for t in ['cerrar_menu.png','earthMenu','data-go="radio"','AndroidMaps','aWa']:
 if t not in s:raise SystemExit('Falta '+t)
p.write_text(s,encoding='utf-8')
print('OK: puerta verde y Volver al menú aplicados')
