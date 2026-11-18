# Riego Cerca Android
Proyecto listo para compilar en GitHub Actions.

## Pasos
1. Cree un repositorio vacío en GitHub.
2. Descomprima el ZIP y suba el contenido de `RiegoCercaAndroid` a la raíz. Deben verse `app`, `.github`, `build.gradle` y `settings.gradle`.
3. Abra **Actions > Compilar APK Riego Cerca > Run workflow**.
4. Al terminar, descargue **Artifacts > RiegoCerca-APK**.
5. Descomprima el artefacto e instale `RiegoCerca-debug.apk`.

La primera vez, use **Datos** para importar `ELEMENTOS DE RIEGO PARA APP.xlsx`. El listado queda guardado al cerrar la app. Coordenadas esperadas: ETRS89 / UTM 29N.
