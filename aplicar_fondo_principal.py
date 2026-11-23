from pathlib import Path

H = Path("app/src/main/assets/index.html")
IMG = "splash_nova_limia.jpg"

if not H.exists():
    raise SystemExit("Falta app/src/main/assets/index.html")

h = H.read_text(encoding="utf-8")
marker = "/* FONDO PRINCIPAL NOVA LIMIA */"

css = r'''
/* FONDO PRINCIPAL NOVA LIMIA */
html, body {
    min-height: 100%;
}
body {
    background:
      linear-gradient(rgba(255,255,255,.66), rgba(255,255,255,.66)),
      url("splash_nova_limia.jpg") center center / cover fixed no-repeat !important;
}
main {
    background: transparent !important;
}
'''

if marker not in h:
    if "</style>" in h:
        h = h.replace("</style>", css + "\n</style>", 1)
    elif "</head>" in h:
        h = h.replace("</head>", "<style>" + css + "</style>\n</head>", 1)
    else:
        h = "<style>" + css + "</style>\n" + h

H.write_text(h, encoding="utf-8")

check = H.read_text(encoding="utf-8")
if marker not in check or IMG not in check:
    raise SystemExit("No se pudo aplicar el fondo principal")

print("OK: splash_nova_limia.jpg aplicado como fondo de la pantalla principal")
