from pathlib import Path
import re
H=Path('app/src/main/assets/index.html'); M=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java'); G=Path('app/build.gradle')
for p in (H,M,G):
    if not p.exists(): raise SystemExit('Falta '+str(p))
h=H.read_text(encoding='utf-8'); m=M.read_text(encoding='utf-8'); g=G.read_text(encoding='utf-8')
# 1 menu shortcut: after Elementos por radio, before close; generic exact insertion options
if 'id="earthMenu"' not in h:
    anchors=['<button type="button" id="maps10Menu">🗺️ Elementos por radio</button>','<button type="button" id="maps10Menu">🗺️ Maps · elementos por radio</button>']
    placed=False
    for a in anchors:
        if a in h:
            h=h.replace(a,a+'<button type="button" id="earthMenu">🌍 Google Earth</button>',1);placed=True;break
    if not placed:
        close='<button type="button" data-menu="cerrar">✕ Cerrar menú</button>'
        if close in h: h=h.replace(close,'<button type="button" id="earthMenu">🌍 Google Earth</button>'+close,1);placed=True
    if not placed: raise SystemExit('No se pudo insertar Google Earth en el menu')
# Main menu Earth handler opens app/browser landing page; Android intercept added below.
if "$('#earthMenu').onclick" not in h:
    anchor="$('#maps10Menu').onclick="
    i=h.find(anchor)
    if i<0: raise SystemExit('No se encontro handler maps10Menu')
    # append handler before q input handler to keep it in init area
    q=h.find("$('#q').oninput",i)
    h=h[:q]+"$('#earthMenu').onclick=()=>{closeMenu();window.location.href='https://earth.google.com/web/'};"+h[q:]
# 2 Selected-element action sheet Earth button
if 'id="elementActions"' in h and 'id="elementActionEarth"' not in h:
    earthbtn='<button id="elementActionEarth" type="button" class="go earth-btn">🌍 Ver este elemento en Google Earth</button>'
    mapsbtn='<button id="elementActionMaps" type="button" class="go">🗺️ Abrir en Google Maps</button>'
    if mapsbtn in h: h=h.replace(mapsbtn,mapsbtn+earthbtn,1)
    else: raise SystemExit('Existe elementActions pero no elementActionMaps')
if 'id="elementActions"' in h and "$('#elementActionEarth').onclick" not in h:
    anchor="$('#elementActionWhatsApp').onclick="
    i=h.find(anchor)
    if i<0: raise SystemExit('No se encontro WhatsApp en action sheet')
    handler="$('#elementActionEarth').onclick=()=>{if(!activeElementGps)return;const url=`https://earth.google.com/web/search/${activeElementGps.lat},${activeElementGps.lon}`;window.location.href=url};"
    h=h[:i]+handler+h[i:]
# style Earth action distinguishable
if '.earth-btn{' not in h: h=h.replace('</style>','.earth-btn{background:#e8f0fe!important;color:#174ea6!important;font-weight:800!important}</style>',1)
H.write_text(h,encoding='utf-8')
# 3 Android route Earth URLs to Google Earth package first; fallback browser.
if 'com.google.earth' not in m:
    needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");'
    # If WebViewClient was already patched for WhatsApp, inject Earth case into that existing handler.
    earthcase='if(url!=null&&url.startsWith("https://earth.google.com/")){Intent e=new Intent(Intent.ACTION_VIEW,Uri.parse(url));e.setPackage("com.google.earth");try{startActivity(e);}catch(Exception ex){e.setPackage(null);startActivity(e);}return true;}'
    if 'shouldOverrideUrlLoading(WebView' in m:
        pos=m.find('{',m.find('shouldOverrideUrlLoading(WebView'))+1
        m=m[:pos+1]+earthcase+m[pos+1:]
    elif needle in m:
        client='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");w.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView view,String url){'+earthcase+'return false;}});'
        m=m.replace(needle,client,1)
    else: raise SystemExit('No se encontro punto de integracion WebView en MainActivity')
M.write_text(m,encoding='utf-8')
# manifest package visibility
manifest=Path('app/src/main/AndroidManifest.xml');man=manifest.read_text(encoding='utf-8')
if 'com.google.earth' not in man:
    if '<queries>' in man: man=man.replace('</queries>','<package android:name="com.google.earth"/></queries>',1)
    else: man=man.replace('<application','<queries><package android:name="com.google.earth"/></queries><application',1)
manifest.write_text(man,encoding='utf-8')
# bump version
mt=re.search(r'versionCode\s+(\d+)',g); n=int(mt.group(1))+1 if mt else 27; g=re.sub(r'versionCode\s+\d+',f'versionCode {n}',g,1);G.write_text(g,encoding='utf-8')
# validate 3 things
h=H.read_text();m=M.read_text();man=manifest.read_text()
checks=['id="earthMenu"','https://earth.google.com/web/','id="elementActionEarth"','https://earth.google.com/web/search/${activeElementGps.lat},${activeElementGps.lon}']
for x in checks:
    if x not in h: raise SystemExit('Falta '+x)
if 'com.google.earth' not in m or 'com.google.earth' not in man: raise SystemExit('Falta integracion Android Earth')
print('GOOGLE EARTH: MENU + ELEMENTO + ANDROID FALLBACK OK; versionCode',n)
