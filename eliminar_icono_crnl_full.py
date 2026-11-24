from pathlib import Path
import sys
root=Path.cwd()
targets=[p for p in root.rglob('icono_crnl_full.png') if '.git' not in p.parts and 'build' not in p.parts]
if not targets:
    print('INFO: icono_crnl_full.png ya no existe en el repositorio. No hay nada que eliminar.')
else:
    for p in targets:
        print('ELIMINANDO:',p)
        p.unlink()
remaining=[p for p in root.rglob('icono_crnl_full.png') if '.git' not in p.parts and 'build' not in p.parts]
if remaining:
    print('ERROR: todavía existe:',remaining)
    sys.exit(1)
print('OK: icono_crnl_full.png no existe en el proyecto.')
