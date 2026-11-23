from pathlib import Path

H = Path("app/src/main/assets/index.html")

if not H.exists():
    raise SystemExit("Falta app/src/main/assets/index.html")

h = H.read_text(encoding="utf-8")

marker = "/* FONDO PRINCIPAL NOVA LIMIA V2 */"

css = r"""
/* FONDO PRINCIPAL NOVA LIMIA V2 */

html,
body {
    min-height: 100%;
}

/* Fotografia del aspersor como fondo permanente */
body::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -2;

    background:
        url("splash_nova_limia.jpg")
        center center / cover
        no-repeat;
}

/* Capa clara para poder leer textos y botones */
body::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -1;

    background: rgba(255, 255, 255, 0.58);
    pointer-events: none;
}

/*
La pantalla inicial debe permanecer por encima
del fondo de la pantalla principal.
*/
#appSplash {
    z-index: 2147483647 !important;
}
"""

# ------------------------------------------------------------
# ELIMINAR EL PARCHE DE FONDO ANTERIOR, SI TODAVIA EXISTE
# ------------------------------------------------------------

old_marker = "/* FONDO PRINCIPAL NOVA LIMIA */"

if old_marker in h:
    start = h.find(old_marker)
    end = h.find("</style>", start)

    if end != -1:
        h = h[:start] + h[end:]


# ------------------------------------------------------------
# INSERTAR EL NUEVO FONDO
# ------------------------------------------------------------

if marker not in h:

    if "</style>" in h:

        h = h.replace(
            "</style>",
            css + "\n</style>",
            1
        )

    elif "</head>" in h:

        h = h.replace(
            "</head>",
            "<style>\n" + css + "\n</style>\n</head>",
            1
        )

    else:

        h = (
            "<style>\n"
            + css
            + "\n</style>\n"
            + h
        )


# ------------------------------------------------------------
# GUARDAR
# ------------------------------------------------------------

H.write_text(
    h,
    encoding="utf-8"
)


# ------------------------------------------------------------
# COMPROBACIONES DE SEGURIDAD
# ------------------------------------------------------------

check = H.read_text(encoding="utf-8")


# El nuevo fondo debe haberse instalado

if marker not in check:
    raise SystemExit(
        "ERROR: no se pudo aplicar el fondo principal"
    )


# La pantalla inicial NO puede haber desaparecido

if 'id="appSplash"' not in check:
    raise SystemExit(
        "ERROR: no existe appSplash despues de aplicar el fondo"
    )


# La fotografia debe seguir presente

if "splash_nova_limia.jpg" not in check:
    raise SystemExit(
        "ERROR: falta splash_nova_limia.jpg en index.html"
    )


print(
    "OK: fondo principal aplicado sin eliminar appSplash"
)
