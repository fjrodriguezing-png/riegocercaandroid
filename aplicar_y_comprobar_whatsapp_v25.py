#!/usr/bin/env python3
from pathlib import Path
import re, sys, subprocess, json

ROOT=Path.cwd()
REPORT=[]
def ok(msg): REPORT.append(('OK',msg)); print('OK  ',msg)
def fail(msg): REPORT.append(('FAIL',msg)); print('FAIL',msg); raise SystemExit(msg)

def detect_file(name, preferred):
    p=ROOT/preferred
    if p.exists(): ok(f'{name}: {p}'); return p
    candidates=[x for x in ROOT.rglob(Path(preferred).name) if '.git' not in x.parts and 'build' not in x.parts]
    matches=[]
    for x in candidates:
        rel=x.relative_to(ROOT).as_posix()
        if rel.endswith(preferred): matches.append(x)
    if len(matches)==1: ok(f'{name} detectado: {matches[0]}'); return matches[0]
    fail(f'No se pudo detectar de forma unica {name}. Esperado: {preferred}. Candidatos: {[str(x) for x in matches]}')

html=detect_file('index.html','app/src/main/assets/index.html')
main=detect_file('MainActivity.java','app/src/main/java/es/riegocerca/maps/MainActivity.java')
gradle=detect_file('app/build.gradle','app/build.gradle')
manifest=detect_file('AndroidManifest.xml','app/src/main/AndroidManifest.xml')

h=html.read_text(encoding='utf-8')
m=main.read_text(encoding='utf-8')
g=gradle.read_text(encoding='utf-8')

# Structural V25 checks before patching
required_html=['mapsFoundList','function openFoundInMaps()','gpsForRow','AndroidMaps.navigate']
for token in required_html:
    if token not in h: fail(f'El proyecto no parece V25 compatible: falta {token} en index.html')
ok('Estructura V25 compatible detectada')
if 'w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");' not in m and 'startsWith("https://wa.me/")' not in m:
    fail('No se encontro AndroidMaps bridge en MainActivity.java')

# Action sheet
if 'id="elementActions"' not in h:
    if '</main>' not in h: fail('No se encontro </main> para insertar menu de acciones')
    h=h.replace('</main>','''<div id="elementActions" class="element-actions hidden"><div class="element-sheet"><div class="element-sheet-head"><div><small>Elemento seleccionado</small><h3 id="elementActionName">Elemento</h3><div id="elementActionMeta"></div></div><button id="elementActionClose" type="button" class="element-x">✕</button></div><button id="elementActionMaps" type="button" class="go">🗺️ Abrir en Google Maps</button><button id="elementActionWhatsApp" type="button" class="wa-btn">🟢 Denunciar incidencia por WhatsApp</button><button id="elementActionCancel" type="button" class="element-cancel">Cancelar</button></div></div></main>''',1)
    ok('Menu de acciones insertado')
else: ok('Menu de acciones ya existia; no duplicado')

# Robustly replace list renderer by regex around mapsFoundList assignment.
if 'data-element-index' not in h:
    pattern=r"\$\('#mapsFoundList'\)\.innerHTML=found\.slice\(0,50\)\.map\(x=>`<li><b>\$\{x\.r\.name\}</b><small>Distancia: \$\{x\.d<10\?x\.d\.toFixed\(1\):Math\.round\(x\.d\)\} m · \$\{x\.r\.type\|\|'Sin tipo'\}</small></li>`\)\.join\(''\)\+\(found\.length>50\?`<li><b>… y \$\{found\.length-50\} elemento\(s\) más</b></li>`:''\);"
    replacement="$('#mapsFoundList').innerHTML=found.slice(0,50).map(x=>`<li><button type=\"button\" class=\"result-action\" data-element-index=\"${x.i}\" data-element-distance=\"${x.d}\"><b>${x.r.name}</b><small>Distancia: ${x.d<10?x.d.toFixed(1):Math.round(x.d)} m · ${x.r.type||'Sin tipo'}</small><span>›</span></button></li>`).join('')+(found.length>50?`<li><b>… y ${found.length-50} elemento(s) más</b></li>`:'');document.querySelectorAll('[data-element-index]').forEach(btn=>btn.onclick=()=>openElementActions(Number(btn.dataset.elementIndex),Number(btn.dataset.elementDistance)));"
    h,n=re.subn(pattern,replacement,h,count=1)
    if n!=1: fail('No se pudo adaptar automaticamente el render de resultados V25')
    ok('Resultados convertidos en elementos pulsables')
else: ok('Resultados pulsables ya estaban presentes')

logic=r'''let activeElement=null,activeElementGps=null,activeElementDistance=0;function closeElementActions(){$('#elementActions').classList.add('hidden');activeElement=null;activeElementGps=null}function openElementActions(index,distance){const r=rows[index],g=r?gpsForRow(r):null;if(!r||!g)return;activeElement=r;activeElementGps=g;activeElementDistance=Number(distance)||0;$('#elementActionName').textContent=r.name;$('#elementActionMeta').textContent=`${r.type||'Sin tipo'} · ${activeElementDistance<10?activeElementDistance.toFixed(1):Math.round(activeElementDistance)} m`;$('#elementActions').classList.remove('hidden')}$('#elementActionClose').onclick=closeElementActions;$('#elementActionCancel').onclick=closeElementActions;$('#elementActions').onclick=e=>{if(e.target===$('#elementActions'))closeElementActions()};$('#elementActionMaps').onclick=()=>{if(!activeElementGps)return;if(window.AndroidMaps&&typeof window.AndroidMaps.navigate==='function')window.AndroidMaps.navigate(activeElementGps.lat,activeElementGps.lon);else window.location.href=`https://www.google.com/maps/dir/?api=1&destination=${activeElementGps.lat},${activeElementGps.lon}&travelmode=driving`};$('#elementActionWhatsApp').onclick=()=>{if(!activeElement||!activeElementGps)return;const mapsUrl=`https://www.google.com/maps/search/?api=1&query=${activeElementGps.lat},${activeElementGps.lon}`;const message=`INCIDENCIA - ${activeElement.name}\nTipo: ${activeElement.type||'Sin tipo'}\nSe ha detectado una incidencia en este elemento. Gracias.\n\nUbicación Google Maps:\n${mapsUrl}`;window.location.href=`https://wa.me/34615179537?text=${encodeURIComponent(message)}`};'''
if 'let activeElement=' not in h:
    h=h.replace('function openFoundInMaps()',logic+'function openFoundInMaps()',1); ok('Logica Maps/WhatsApp insertada')
else: ok('Logica Maps/WhatsApp ya existia')

css='''.maps-found-list li{padding:0!important;overflow:hidden}.result-action{position:relative;width:100%;margin:0!important;padding:12px 34px 12px 12px!important;text-align:left;background:#f7fafc!important;color:#142738!important;border:0!important}.result-action b,.result-action small{display:block}.result-action small{color:#68798a;margin-top:3px}.result-action span{position:absolute;right:13px;top:50%;transform:translateY(-50%);font-size:25px;color:#087f5b}.element-actions{position:fixed;z-index:120;inset:0;background:rgba(0,0,0,.44);display:flex;align-items:flex-end;justify-content:center;padding:12px}.element-actions.hidden{display:none}.element-sheet{width:min(100%,520px);background:#fff;border-radius:22px;padding:16px;box-shadow:0 20px 60px rgba(0,0,0,.3)}.element-sheet-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}.element-sheet-head h3{margin:3px 0}.element-sheet-head small,#elementActionMeta{color:#68798a}.element-x{width:42px!important;min-width:42px;height:42px;padding:0!important;margin:0!important;background:#eef3f6!important;color:#234!important}.wa-btn{background:#25D366!important;color:#073b1c!important;font-weight:900!important;border-color:#1cb956!important}.element-cancel{background:#eef3f6!important;color:#234!important;font-weight:700!important}@media(min-width:650px){.element-actions{align-items:center}}'''
if '.element-actions{' not in h: h=h.replace('</style>',css+'</style>',1); ok('Estilos insertados')
html.write_text(h,encoding='utf-8')

# WebView WhatsApp routing, idempotent
if 'startsWith("https://wa.me/")' not in m:
    needle='w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");'
    client='''w.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");w.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView view,String url){if(url!=null&&(url.startsWith("https://wa.me/")||url.startsWith("whatsapp:"))){try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)));}catch(Exception e){android.widget.Toast.makeText(MainActivity.this,"No se pudo abrir WhatsApp",android.widget.Toast.LENGTH_LONG).show();}return true;}return false;}});'''
    m=m.replace(needle,client,1); ok('Apertura externa WhatsApp insertada')
else: ok('Apertura externa WhatsApp ya existia')
main.write_text(m,encoding='utf-8')
# Version
g=re.sub(r'versionCode\s+\d+','versionCode 26',g,1);gradle.write_text(g,encoding='utf-8');ok('versionCode fijado a 26')

# Post checks
h=html.read_text(encoding='utf-8');m=main.read_text(encoding='utf-8');g=gradle.read_text(encoding='utf-8')
checks={
'numero WhatsApp':'https://wa.me/34615179537' in h,
'mensaje':'Se ha detectado una incidencia en este elemento. Gracias.' in h,
'tipo':'Tipo: ${activeElement.type' in h,
'ubicacion':'https://www.google.com/maps/search/?api=1&query=' in h,
'click resultados':'data-element-index' in h,
'menu acciones':'id="elementActions"' in h,
'Maps':'AndroidMaps.navigate' in h,
'WhatsApp externo':'startsWith("https://wa.me/")' in m,
'versionCode 26':'versionCode 26' in g,
}
for name,value in checks.items():
    if not value: fail(f'Comprobacion final fallida: {name}')
    ok(f'Comprobacion final: {name}')
Path('whatsapp_patch_report.txt').write_text('\n'.join(f'{a}: {b}' for a,b in REPORT),encoding='utf-8')
print('PARCHE Y COMPROBACIONES COMPLETADOS')
