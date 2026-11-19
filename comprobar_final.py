from pathlib import Path
import re,sys
h=Path('app/src/main/assets/index.html').read_text(encoding='utf-8')
m=Path('app/src/main/java/es/riegocerca/maps/MainActivity.java').read_text(encoding='utf-8')
man=Path('app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
checks={
 'splash visible':'id="appSplash"' in h,
 'splash image':'splash_nova_limia.jpg' in h,
 'splash title':'COMUNIDAD DE REGANTES<br>NOVA LIMIA' in h,
 'splash 3 sec':'},3000)' in h or '},3000);' in h,
 'splash removed':'removeChild(s)' in h or 'removeChild(splash)' in h,
 'whatsapp action':'elementActionWhatsApp' in h,
 'whatsapp number':'https://wa.me/34615179537' in h,
 'whatsapp message':'Se ha detectado una incidencia en este elemento. Gracias.' in h,
 'whatsapp type':'Tipo: ${activeElement.type' in h,
 'whatsapp map link':'https://www.google.com/maps/search/?api=1&query=' in h,
 'android whatsapp routing':'https://wa.me/' in m,
 'icon manifest':'@mipmap/ic_launcher' in man,
}
for k,v in checks.items(): print(('OK   ' if v else 'FAIL ')+k)
if not all(checks.values()): sys.exit(1)
print('COMPROBACION FINAL SPLASH + WHATSAPP + ICONO: OK')
