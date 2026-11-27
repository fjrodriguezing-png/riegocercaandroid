from pathlib import Path
import re
p=Path('app/src/main/assets/index.html')
if not p.exists(): raise SystemExit('No existe app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')
# restore both menu icons
radio='<button data-go="radio" class="menu-tile" aria-label="Elementos de riego" title="Elementos de riego"><img src="elementos_riego.png" alt="Elementos de riego"></button>'
if radio not in s:
 s,n=re.subn(r'<button[^>]*data-go="radio"[^>]*>.*?</button>',radio,s,count=1,flags=re.S)
 if not n: raise SystemExit('No localizo Elementos por radio')
close='<button id="closeMenu" class="menu-tile" aria-label="Cerrar menú" title="Cerrar menú"><img src="cerrar_menu.png" alt="Cerrar menú"></button>'
if close not in s:
 s,n=re.subn(r'<button[^>]*id="closeMenu"[^>]*>.*?</button>',close,s,count=1,flags=re.S)
 if not n: raise SystemExit('No localizo Cerrar menú')
# styles
css='.menu-tile{padding:0!important;overflow:hidden!important;background:#fff!important}.menu-tile img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important;border-radius:16px!important}.back-menu{background:#187bcd;color:#fff;font-weight:800;margin-top:14px}'
if '.back-menu{' not in s:s=s.replace('</style>',css+'</style>',1)
# add back button independently to every internal screen: datos, destino, radio
btn='<button type="button" class="back-menu">💧 Volver al menú</button>'
for screen_id in ['datos','destino','radio']:
 pattern=r'(<section id="'+screen_id+r'" class="screen hidden">.*?)(</section>)'
 m=re.search(pattern,s,re.S)
 if not m: raise SystemExit('No localizo pantalla '+screen_id)
 if 'class="back-menu"' not in m.group(1):
  repl=m.group(1)+btn+m.group(2)
  s=s[:m.start()]+repl+s[m.end():]
# handler, robustly add once
if "document.querySelectorAll('.back-menu').forEach" not in s:
 anchor="$('#closeMenu').onclick=()=>menu.classList.add('hidden');"
 if anchor not in s: raise SystemExit('No localizo controlador closeMenu')
 handler=anchor+"document.querySelectorAll('.back-menu').forEach(b=>b.onclick=()=>{document.querySelectorAll('.screen').forEach(x=>x.classList.add('hidden'));menu.classList.remove('hidden')});"
 s=s.replace(anchor,handler,1)
# hard gates
for t in ['elementos_riego.png','cerrar_menu.png','data-go="radio"','id="closeMenu"','earthMenu','AndroidMaps','aWa']:
 if t not in s: raise SystemExit('Falta '+t)
if s.count('class="back-menu"') < 3: raise SystemExit('Faltan botones Volver al menú')
p.write_text(s,encoding='utf-8')
print('OK: iconos + 3 botones Volver al menú')
