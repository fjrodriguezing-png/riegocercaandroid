from pathlib import Path
from PIL import Image, ImageOps
import re,sys
H=Path('app/src/main/assets/index.html'); G=Path('app/build.gradle'); MAN=Path('app/src/main/AndroidManifest.xml')
for p in (H,G,MAN):
    if not p.exists(): raise SystemExit('Falta '+str(p))
# ICON: center crop biased downward so the concrete irrigation box + blue valve dominate launcher icon.
im=Image.open('icono_crnl.jpg').convert('RGB')
w,h=im.size; side=min(w,h); left=(w-side)//2; top=max(0,min(h-side,int((h-side)*0.72))); crop=im.crop((left,top,left+side,top+side))
# zoom another 1.38x around crop center to make installation fill icon
cw,ch=crop.size; z=int(cw/1.38); x=(cw-z)//2; y=(ch-z)//2; crop=crop.crop((x,y,x+z,y+z))
for d,n in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
 out=Path(f'app/src/main/res/mipmap-{d}');out.mkdir(parents=True,exist_ok=True); ImageOps.fit(crop,(n,n),Image.Resampling.LANCZOS).save(out/'ic_launcher.png',quality=96)
ImageOps.fit(crop,(1024,1024),Image.Resampling.LANCZOS).save('app/src/main/assets/icono_crnl_1024.jpg',quality=96)
ms=MAN.read_text();ms=re.sub(r'android:icon="[^"]+"','android:icon="@mipmap/ic_launcher"',ms);ms=re.sub(r'android:roundIcon="[^"]+"','android:roundIcon="@mipmap/ic_launcher"',ms) if 'android:roundIcon=' in ms else ms.replace('<application ','<application android:roundIcon="@mipmap/ic_launcher" ',1);MAN.write_text(ms)
# MENU: remove any WhatsApp entry from hamburger/menu panel only. Preserve action sheet inside Elements by radius.
h=H.read_text(encoding='utf-8')
start=h.find('<div id="menuPanel"'); end=h.find('</div>',start) if start>=0 else -1
if start>=0 and end>start:
    menu=h[start:end]
    menu=re.sub(r'<button[^>]*(?:id="[^"]*whatsapp[^"]*"|data-menu="whatsapp")[^>]*>.*?</button>','',menu,flags=re.I|re.S)
    menu=re.sub(r'<button[^>]*>[^<]*WhatsApp[^<]*</button>','',menu,flags=re.I|re.S)
    h=h[:start]+menu+h[end:]
# Remove stale primary-menu WhatsApp handlers only, not elementActionWhatsApp.
h=re.sub(r"\$\('#(?:whatsappMenu|menuWhatsApp|whatsAppMenu)'\)\.onclick=.*?;(?=\$|function|let|const)",'',h,flags=re.I|re.S)
H.write_text(h,encoding='utf-8')
# bump version
b=G.read_text();m=re.search(r'versionCode\s+(\d+)',b);n=int(m.group(1))+1;b=re.sub(r'versionCode\s+\d+',f'versionCode {n}',b,1);G.write_text(b)
# checks
h=H.read_text(); start=h.find('<div id="menuPanel"');end=h.find('</div>',start);menu=h[start:end] if start>=0 else ''
if 'WhatsApp' in menu: raise SystemExit('WhatsApp sigue en menu principal')
# If action WhatsApp already exists, guarantee it remains. If project does not yet have it, do not invent unrelated patch here.
if 'elementActionWhatsApp' in h: print('OK WhatsApp permanece solo en acciones de elemento')
print('OK icono foto aplicado; WhatsApp eliminado del menu principal; versionCode',n)
