from pathlib import Path
p=Path('app/src/main/assets/index.html')
if not p.exists(): raise SystemExit('No existe app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')
# Radio: accept text or existing image version.
radio_new='<button data-go="radio" class="menu-tile" aria-label="Elementos de riego" title="Elementos de riego"><img src="elementos_riego.png" alt="Elementos de riego"></button>'
if radio_new not in s:
    import re
    ns,n=re.subn(r'<button[^>]*data-go="radio"[^>]*>.*?</button>',radio_new,s,count=1,flags=re.S)
    if not n: raise SystemExit('No localizo el botón Elementos por radio')
    s=ns
# Close: accept text or image version.
close_new='<button id="closeMenu" class="menu-tile" aria-label="Cerrar menú" title="Cerrar menú"><img src="cerrar_menu.png" alt="Cerrar menú"></button>'
if close_new not in s:
    import re
    ns,n=re.subn(r'<button[^>]*id="closeMenu"[^>]*>.*?</button>',close_new,s,count=1,flags=re.S)
    if not n: raise SystemExit('No localizo el botón Cerrar menú')
    s=ns
# Visual fill.
css='.menu-tile{padding:0!important;overflow:hidden!important;background:#fff!important}.menu-tile img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important;border-radius:16px!important}'
if css not in s:s=s.replace('</style>',css+'</style>',1)
# Do NOT require image names before repository copy; both PNG files ship in this ZIP.
for token in ['data-go="radio"','id="closeMenu"','earthMenu','AndroidMaps','aWa']:
    if token not in s: raise SystemExit('Falta elemento funcional: '+token)
p.write_text(s,encoding='utf-8')
print('OK: Elementos de Riego y Cerrar menú restaurados')
