from pathlib import Path
import re,sys
H=Path('app/src/main/assets/index.html');G=Path('app/build.gradle')
if not H.exists():raise SystemExit('Falta '+str(H))
h=H.read_text(encoding='utf-8')
# FIX 1: Make background use an actual fixed IMG layer with exact same object-fit/object-position as splash.
# CSS body backgrounds can crop differently because viewport/scrolling changes. A fixed image layer avoids that.
if 'id="mainBackgroundImage"' not in h:
    h=h.replace('<body>','<body><img id="mainBackgroundImage" src="splash_nova_limia.jpg" alt="">',1)
css='''#mainBackgroundImage{position:fixed;z-index:-3;inset:0;width:100%;height:100%;object-fit:cover;object-position:center center;pointer-events:none}body{background:#000!important;background-image:none!important}body:before{z-index:-2!important}'''
if '#mainBackgroundImage{' not in h:h=h.replace('</style>',css+'</style>',1)
# Remove all mobile/per-breakpoint rules that reposition or resize body background.
h=re.sub(r'body\{background-position:[^}]*\}', 'body{background:#000!important;background-image:none!important}', h)
# FIX 2: Remove every WhatsApp menu button only inside menuPanel using DOM fragment bounds.
start=h.find('<div id="menuPanel"');end=h.find('</div>',start)
if start<0 or end<0:raise SystemExit('No encuentro menuPanel')
menu=h[start:end]
# remove any button whose text or id references WhatsApp, case-insensitive
menu=re.sub(r'<button\b[^>]*>[^<]*WhatsApp[^<]*</button>','',menu,flags=re.I|re.S)
menu=re.sub(r'<button\b[^>]*(?:id|data-menu)="[^"]*whats?[^"]*"[^>]*>.*?</button>','',menu,flags=re.I|re.S)
h=h[:start]+menu+h[end:]
# Remove menu-specific Whatsapp handlers, never elementActionWhatsApp.
h=re.sub(r"\$\('#(?!(?:elementActionWhatsApp))[^']*whats?[^']*'\)\.onclick\s*=.*?;(?=\$\(|function|let|const|$)",'',h,flags=re.I|re.S)
H.write_text(h,encoding='utf-8')
# version bump
if G.exists():
 g=G.read_text();m=re.search(r'versionCode\s+(\d+)',g);n=int(m.group(1))+1 if m else 1;G.write_text(re.sub(r'versionCode\s+\d+',f'versionCode {n}',g,1));print('versionCode',n)
# HARD verification
h=H.read_text();start=h.find('<div id="menuPanel"');end=h.find('</div>',start);menu=h[start:end]
checks={
'exact background IMG':'id="mainBackgroundImage"' in h and 'object-fit:cover' in h and 'object-position:center center' in h,
'no body positioning overrides':'background-position:left center' not in h and 'background-size:auto 100%' not in h,
'no WhatsApp in main menu':'WhatsApp' not in menu and 'whatsapp' not in menu.lower(),
'context WhatsApp preserved':'id="elementActionWhatsApp"' in h,
'splash preserved':'id="appSplash"' in h,
'earth preserved':'id="earthMenu"' in h,
}
for k,v in checks.items():print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()):sys.exit(1)
