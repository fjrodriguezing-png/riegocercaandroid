from pathlib import Path
import re

p = Path("app/src/main/assets/index.html")

if not p.exists():
    raise SystemExit("No existe app/src/main/assets/index.html")

h = p.read_text(encoding="utf-8")

pattern = r'(<button\b[^>]*id=["\']menuBtn["\'][^>]*>)(.*?)(</button>)'

m = re.search(pattern, h, re.S | re.I)

if not m:
    raise SystemExit("No se encontró el botón menuBtn")

open_tag = m.group(1)

if "aria-label=" in open_tag:
    open_tag = re.sub(
        r'aria-label=["\'][^"\']*["\']',
        'aria-label="Abrir menú"',
        open_tag
    )

new_button = (
    open_tag
    + '<span id="crnlMenuDrop" aria-hidden="true">💧</span>'
    + "</button>"
)

h = h[:m.start()] + new_button + h[m.end():]

style = """
<style id="crnlMenuDropStyle">

#menuBtn {
    width: 54px !important;
    height: 54px !important;
    min-width: 54px !important;
    padding: 0 !important;
    margin: 0 !important;

    border-radius: 50% !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    background: rgba(255,255,255,.18) !important;

    border:
        1px solid rgba(255,255,255,.38) !important;

    box-shadow:
        0 5px 16px rgba(0,0,0,.22) !important;
}

#menuBtn span:not(#crnlMenuDrop) {
    display: none !important;
}

#crnlMenuDrop {
    display: block !important;

    width: auto !important;
    height: auto !important;

    background: transparent !important;

    margin: 0 !important;
    padding: 0 !important;

    font-size: 36px !important;
    line-height: 1 !important;

    opacity: 1 !important;
    visibility: visible !important;

    transform: none !important;
}

@media(max-width:390px) {

    #menuBtn {
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
    }

    #crnlMenuDrop {
        font-size: 33px !important;
    }
}

</style>
"""

h = re.sub(
    r'<style id="crnlMenuDropStyle">.*?</style>',
    "",
    h,
    flags=re.S
)

h = h.replace("</head>", style + "</head>")

p.write_text(h, encoding="utf-8")

print("OK: botón del menú sustituido por 💧")

