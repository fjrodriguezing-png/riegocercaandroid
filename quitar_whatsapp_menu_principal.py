from pathlib import Path
import re,sys
H=Path('app/src/main/assets/index.html');G=Path('app/build.gradle')
if not H.exists():raise SystemExit('Falta '+str(H))
h=H.read_text(encoding='utf-8')
start=h.find('<div id="menuPanel"');end=h.find('</div>',start)
if start<0 or end<0:raise SystemExit('No se encontro menuPanel')
menu=h[start:end]
# Remove WhatsApp buttons only from main menu, irrespective of id/data-menu/text.
menu=re.sub(r'<button\b[^>]*>.*?WhatsApp.*?</button>','',menu,flags=re.I|re.S)
menu=re.sub(r'<button\b[^>]*(?:id|data-menu)="[^"]*whats?[^"]*"[^>]*>.*?</button>','',menu,flags=re.I|re.S)
h=h[:start]+menu+h[end:]
# Remove only stale main-menu handler identifiers; contextual elementActionWhatsApp is protected.
for ident in ['whatsappMenu','WhatsAppMenu','menuWhatsApp','menuWhatsapp','whatsAppMenu']:
    h=re.sub(r"\$\('#"+re.escape(ident)+r"'\)\.onclick\s*=.*?;(?=\$\(|function|let|const|$)",'',h,flags=re.S)
H.write_text(h,encoding='utf-8')
# bump
if G.exists():
 g=G.read_text();m=re.search(r'versionCode\s+(\d+)',g);code=int(m.group(1))+1 if m else 1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {code}',g,1));print('versionCode',code)
# hard checks
h=H.read_text();a=h.find('<div id="menuPanel"');b=h.find('</div>',a);menu=h[a:b].lower()
if 'whatsapp' in menu:raise SystemExit('WhatsApp sigue en el menu principal')
if 'elementActionWhatsApp' not in h:raise SystemExit('Se ha perdido WhatsApp de Elementos por radio')
print('OK: WhatsApp eliminado del menu principal y conservado en accion de elemento')
