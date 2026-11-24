from pathlib import Path
from PIL import Image, ImageOps
import re, shutil
SRC=Path('icono_crnl_arqueta.png');RES=Path('app/src/main/res');MAN=Path('app/src/main/AndroidManifest.xml');G=Path('app/build.gradle')
for p in (SRC,RES,MAN,G):
    if not p.exists():raise SystemExit('Falta '+str(p))
# Remove ALL prior launcher resources so there is only one possible launcher icon family.
for p in list(RES.rglob('ic_launcher*'))+list(RES.rglob('ic_crnl_foto_v2*'))+list(RES.rglob('ic_crnl_arqueta_v3*')):
    if p.is_file():p.unlink()
# Use generated drawing full-bleed. Its background already reaches edges; crop to square without margins.
im=Image.open(SRC).convert('RGB')
for d,n in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
    out=RES/f'mipmap-{d}';out.mkdir(parents=True,exist_ok=True);ImageOps.fit(im,(n,n),Image.Resampling.LANCZOS,centering=(0.5,0.5)).save(out/'ic_crnl_arqueta_v3.png',quality=98)
assets=Path('app/src/main/assets');assets.mkdir(parents=True,exist_ok=True);ImageOps.fit(im,(1024,1024),Image.Resampling.LANCZOS).save(assets/'icono_crnl_arqueta_v3.jpg',quality=98)
# Force manifest to the unique resource.
m=MAN.read_text();m=re.sub(r'android:icon="[^"]+"','android:icon="@mipmap/ic_crnl_arqueta_v3"',m)
if 'android:roundIcon=' in m:m=re.sub(r'android:roundIcon="[^"]+"','android:roundIcon="@mipmap/ic_crnl_arqueta_v3"',m)
else:m=m.replace('<application ','<application android:roundIcon="@mipmap/ic_crnl_arqueta_v3" ',1)
MAN.write_text(m)
# version bump
g=G.read_text();mt=re.search(r'versionCode\s+(\d+)',g);code=int(mt.group(1))+1 if mt else 28;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',g,1))
# Verification: old resources forbidden.
old=[str(p) for p in RES.rglob('ic_launcher*')]+[str(p) for p in RES.rglob('ic_crnl_foto_v2*')]
if old:raise SystemExit('Quedan iconos antiguos: '+str(old))
if '@mipmap/ic_crnl_arqueta_v3' not in MAN.read_text():raise SystemExit('Manifest no apunta al icono definitivo')
print('OK icono definitivo: arqueta con hierba, tapa verde e hidrante azul. versionCode',code)
