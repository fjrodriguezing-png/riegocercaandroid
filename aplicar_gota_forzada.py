name: CRNL GOTA MENU FORZADA

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Descargar proyecto
        uses: actions/checkout@v6

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Localizar y aplicar gota de agua
        run: |
          echo "Directorio actual:"
          pwd

          echo "Buscando aplicar_gota_forzada.py..."
          SCRIPT="$(find . -type f -name 'aplicar_gota_forzada.py' -print -quit)"

          if [ -z "$SCRIPT" ]; then
            echo "ERROR: no encuentro aplicar_gota_forzada.py"
            echo "Archivos disponibles:"
            find . -maxdepth 5 -type f | sort
            exit 1
          fi

          echo "Encontrado en: $SCRIPT"
          python "$SCRIPT"

      - name: Verificar gota ANTES de Gradle
        run: |
          test -f app/src/main/assets/index.html

          grep -q 'id="menuBtn"' app/src/main/assets/index.html
          grep -q 'id="crnlMenuDrop"' app/src/main/assets/index.html
          grep -q '💧' app/src/main/assets/index.html
          grep -q 'id="crnlMenuDropStyle"' app/src/main/assets/index.html

          echo "OK: gota de agua instalada en menuBtn"

      - name: Configurar Java 17
        uses: actions/setup-java@v5
        with:
          distribution: temurin
          java-version: '17'

      - name: Configurar Gradle 8.9
        uses: gradle/actions/setup-gradle@v6
        with:
          gradle-version: '8.9'

      - name: Compilar APK
        run: gradle --no-daemon clean assembleDebug

      - name: Preparar APK
        run: |
          cp app/build/outputs/apk/debug/app-debug.apk CRNL-GOTA-FORZADA-debug.apk

      - name: Publicar APK
        uses: actions/upload-artifact@v4
        with:
          name: CRNL-GOTA-FORZADA-APK
          path: CRNL-GOTA-FORZADA-debug.apk
          if-no-files-found: error
