from pathlib import Path
p=Path('app/src/main/assets/index.html')
if not p.exists(): raise SystemExit('No existe app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')
variants=[
 '<button data-go="radio">🗺️ Elementos por radio</button>',
 '<button data-go="radio" class="menu-tile" aria-label="Elementos de riego" title="Elementos de riego"><img src="elementos_riego.png" alt="Elementos de riego"></button>'
]
new='<button data-go="radio" class="menu-tile" aria-label="Elementos de riego" title="Elementos de riego"><img src="elementos_riego.png" alt="Elementos de riego"></button>'
if new not in s:
    done=False
    for old in variants:
        if old in s:
            s=s.replace(old,new,1);done=True;break
    if not done: raise SystemExit('No localizo el botón de radio para restaurar su icono')
css='.menu-tile{padding:0!important;overflow:hidden!important;background:#fff!important}.menu-tile img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important;border-radius:16px!important}'
if css not in s:s=s.replace('</style>',css+'</style>',1)
for t in ['data-go="radio"','elementos_riego.png','id="closeMenu"','cerrar_menu.png','earthMenu','AndroidMaps','aWa']:
    if t not in s: raise SystemExit('Falta elemento que debe conservarse: '+t)
p.write_text(s,encoding='utf-8')
print('OK: icono Elementos de Riego restaurado sin quitar puerta verde ni funciones')
