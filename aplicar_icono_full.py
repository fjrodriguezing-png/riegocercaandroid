from pathlib import Path
from PIL import Image, ImageOps
import re
src=Path('icono_crnl_full.png')
if not src.exists(): raise SystemExit('Falta icono_crnl_full.png')
res=Path('app/src/main/res'); manifest=Path('app/src/main/AndroidManifest.xml'); gradle=Path('app/build.gradle')
for p in (res,manifest,gradle):
    if not p.exists(): raise SystemExit('Falta '+str(p))
im=Image.open(src).convert('RGB')
# Crop-to-fill, never letterbox: artwork fills every pixel of legacy launcher bitmap.
for d,n in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
    out=res/f'mipmap-{d}'; out.mkdir(parents=True,exist_ok=True)
    ImageOps.fit(im,(n,n),method=Image.Resampling.LANCZOS,centering=(0.5,0.5)).save(out/'ic_launcher.png',quality=96)
# high-res full-bleed source
assets=Path('app/src/main/assets');assets.mkdir(parents=True,exist_ok=True)
ImageOps.fit(im,(1024,1024),method=Image.Resampling.LANCZOS,centering=(0.5,0.5)).save(assets/'icono_crnl_full.png',quality=96)
# Force legacy bitmap icon references (no vector with inner margins).
m=manifest.read_text(encoding='utf-8')
m=re.sub(r'android:icon="[^"]+"','android:icon="@mipmap/ic_launcher"',m)
if 'android:roundIcon=' in m:m=re.sub(r'android:roundIcon="[^"]+"','android:roundIcon="@mipmap/ic_launcher"',m)
else:m=m.replace('<application ','<application android:roundIcon="@mipmap/ic_launcher" ',1)
manifest.write_text(m,encoding='utf-8')
# bump version
b=gradle.read_text(); match=re.search(r'versionCode\s+(\d+)',b); code=int(match.group(1))+1 if match else 27;b=re.sub(r'versionCode\s+\d+',f'versionCode {code}',b,1);gradle.write_text(b)
print('Icono full-bleed aplicado. versionCode',code)
