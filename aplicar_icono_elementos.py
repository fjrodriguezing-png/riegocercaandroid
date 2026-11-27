from pathlib import Path
p=Path('app/src/main/assets/index.html')
img=Path('app/src/main/assets/elementos_riego.png')
if not p.exists(): raise SystemExit('No existe app/src/main/assets/index.html')
if not img.exists(): raise SystemExit('No existe app/src/main/assets/elementos_riego.png')
s=p.read_text(encoding='utf-8')
old='<button data-go="radio">🗺️ Elementos por radio</button>'
new='<button data-go="radio" class="menu-tile" aria-label="Elementos de riego" title="Elementos de riego"><img src="elementos_riego.png" alt="Elementos de riego"></button>'
if new not in s:
    if old not in s: raise SystemExit('No localizo el botón Elementos por radio actual')
    s=s.replace(old,new,1)
# Ensure menu tile images fill the grid cell, matching current design requirement.
css='.menu-tile{padding:0!important;overflow:hidden!important;background:#fff!important}.menu-tile img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important;border-radius:16px!important}'
if css not in s:s=s.replace('</style>',css+'</style>',1)
# Preserve functional target: data-go radio still present.
for token in ['data-go="radio"','id="search"','xlsx.jfif','destino.png','google earth.jfif','aWa','AndroidMaps','splash_nova_limia.jpg']:
    if token not in s: raise SystemExit('Falta elemento que debe conservarse: '+token)
p.write_text(s,encoding='utf-8')
print('OK: Elementos por radio usa elementos_riego.png y conserva data-go="radio"')
