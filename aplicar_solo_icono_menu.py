from pathlib import Path
from PIL import Image, ImageOps
import re, hashlib
H=Path('app/src/main/assets/index.html'); R=Path('app/src/main/res'); M=Path('app/src/main/AndroidManifest.xml'); G=Path('app/build.gradle')
for p in (H,R,M,G):
    if not p.exists(): raise SystemExit('Falta '+str(p))
# Snapshot all non-icon project files we must not touch.
protected=[Path('app/src/main/java/es/riegocerca/maps/MainActivity.java')]
protected_hash={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.exists()}
h=H.read_text(encoding='utf-8')
# ONLY menu visual: append override, no content, no handlers.
css='''.menu-panel{position:fixed!important;left:12px!important;right:12px!important;top:88px!important;width:auto!important;max-width:760px;margin:0 auto;padding:14px!important;background:rgba(255,255,255,.94)!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important;border-radius:22px!important;box-shadow:0 18px 48px rgba(0,0,0,.28)!important;backdrop-filter:blur(5px)}.menu-panel.hidden{display:none!important}.menu-panel button{aspect-ratio:1.08/1!important;margin:0!important;padding:12px 8px!important;border-radius:18px!important;text-align:center!important;display:flex!important;align-items:center!important;justify-content:center!important;font-weight:800!important;background:rgba(244,248,250,.98)!important;border:1px solid #dbe5ec!important;color:#142738!important}@media(min-width:620px){.menu-panel{grid-template-columns:repeat(3,minmax(0,1fr))!important}.menu-panel button{aspect-ratio:1.2/1!important}}'''
if 'grid-template-columns:repeat(2,minmax(0,1fr))!important' not in h:h=h.replace('</style>',css+'</style>',1)
H.write_text(h,encoding='utf-8')
# ONLY icon: delete all known old launcher icon families and create unique definitive family.
for p in list(R.rglob('ic_launcher*'))+list(R.rglob('ic_crnl_foto_v2*'))+list(R.rglob('ic_crnl_arqueta_v3*'))+list(R.rglob('ic_crnl_arqueta_final*')):
    if p.is_file():p.unlink()
im=Image.open('icono_crnl_arqueta.png').convert('RGB')
for d,n in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
    out=R/f'mipmap-{d}';out.mkdir(parents=True,exist_ok=True);ImageOps.fit(im,(n,n),Image.Resampling.LANCZOS).save(out/'ic_crnl_arqueta_final.png',quality=98)
manifest=M.read_text(encoding='utf-8');manifest=re.sub(r'android:icon="[^"]+"','android:icon="@mipmap/ic_crnl_arqueta_final"',manifest)
if 'android:roundIcon=' in manifest:manifest=re.sub(r'android:roundIcon="[^"]+"','android:roundIcon="@mipmap/ic_crnl_arqueta_final"',manifest)
else:manifest=manifest.replace('<application ','<application android:roundIcon="@mipmap/ic_crnl_arqueta_final" ',1)
M.write_text(manifest,encoding='utf-8')
# version only
b=G.read_text();mt=re.search(r'versionCode\s+(\d+)',b);code=int(mt.group(1))+1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1))
# Hard checks: menu grid + definitive icon + no old icon resources. Protected Java unchanged.
assert 'grid-template-columns:repeat(2,minmax(0,1fr))!important' in H.read_text()
assert '@mipmap/ic_crnl_arqueta_final' in M.read_text()
old=[str(p) for p in R.rglob('ic_launcher*')]+[str(p) for p in R.rglob('ic_crnl_foto_v2*')]+[str(p) for p in R.rglob('ic_crnl_arqueta_v3*')]
assert not old,old
for pstr,d in protected_hash.items(): assert hashlib.sha256(Path(pstr).read_bytes()).hexdigest()==d,'Se modifico '+pstr
print('OK: SOLO icono definitivo + menu en cuadrados. versionCode',code)
