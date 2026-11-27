import base64
import json
import os
import time
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

# ---------- Configuración de la página ----------
st.set_page_config(
    page_title="Ferreindustrias S.A.C.",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLOR_FONDO = "#0E1117"
AMARILLO = "#FFC800"
def bloque_html(html, alto):
    """Muestra HTML con JavaScript dentro de un marco (st.iframe en Streamlit nuevo)."""
    html = html.strip()
    if hasattr(st, "iframe"):
        st.iframe(html, height=alto)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=alto)

@st.cache_data
def a_base64(ruta, blur=0, oscuro=0.0, version=0):
    img = Image.open(ruta).convert("RGB")
    img.thumbnail((1920, 1080))
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    if oscuro:
        img = ImageEnhance.Brightness(img).enhance(1 - oscuro)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=78)
    return base64.b64encode(buf.getvalue()).decode()


# ---------- Quitar la barra superior y el botón "Deploy/Desplegar" ----------
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap');

  [data-testid="stMainBlockContainer"] h1 {
      font-family: 'Instrument Serif', 'Cormorant Garamond', Georgia, serif !important;
      font-weight: 400 !important;
      font-size: clamp(2.6rem, 3.4vw, 4.2rem) !important;
      line-height: 1.05 !important;
      letter-spacing: 0 !important;
  }
  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stToolbarActions"],
  [data-testid="stAppDeployButton"],
  [data-testid="stMainMenu"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  #MainMenu, footer { display: none !important; }

  html, body { overflow-x: hidden; }
  .block-container { padding-top: 1.2rem; }
</style>
""", unsafe_allow_html=True)


# ---------- Portada ----------
def archivo_base64(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode()


if "entrado" not in st.session_state:
    st.session_state.entrado = False

if not st.session_state.entrado:
    logo_b64 = archivo_base64("logo.png")

    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Inter:wght@400;500;600&display=swap');

          [data-testid="stApp"],
          [data-testid="stAppViewContainer"],
          [data-testid="stMain"] { background: transparent !important; }

          .video-fondo {
    position: fixed; inset: 0; width: 100vw; height: 100vh;
    object-fit: cover; z-index: -1;
    animation: velo_entrada 2.5s ease-out both;
    will-change: opacity, filter, transform;
}
          .velo {
              position: fixed; inset: 0; z-index: -1; pointer-events: none;
              background: linear-gradient(90deg, rgba(0,0,0,.9) 0%,
                          rgba(0,0,0,.10) 65%, rgba(0,0,0,0) 70%);
          }

          [data-testid="stMainBlockContainer"] {
              position: relative; z-index: 1;
              max-width: none !important;
              padding: 42vh clamp(32px, 6vw, 140px) 0 clamp(32px, 6vw, 140px) !important;
          }

          /* El grupo (logo + títulos + botón) mide lo que mide el título */
          .st-key-portada {
              width: fit-content !important;
              max-width: 100%;
              align-self: flex-start;
          }

          /* Logo plano, sin 3D */
          .logo-izq img { width: clamp(150px, 11vw, 300px); border-radius: 12px; }

          .titulo-portada {
              font-family: 'Instrument Serif', 'Cormorant Garamond', Georgia, serif;
              font-size: clamp(40px, 4.2vw, 110px);
              font-weight: 400; line-height: 1.05; color: #fff;
              margin: 20px 0 10px;
              white-space: nowrap; width: max-content;
              text-shadow: 0 2px 24px rgba(0,0,0,.35);
          }
          /* El subtítulo no estira el grupo: solo el título decide el ancho */
          .sub-portada {
              font-family: 'Inter', 'Segoe UI', sans-serif;
              font-size: clamp(14px, 1.1vw, 26px);
              color: rgba(255,255,255,.9); margin-bottom: 26px;
              width: 0; min-width: 100%;
          }

          /* Botón: ocupa todo el ancho del título, sin relleno, contorno amarillo con brillo */
          .st-key-btn_entrar,
          .st-key-btn_entrar .stButton { width: 100% !important; }
          .st-key-btn_entrar button {
              width: 100% !important;
              background: transparent !important;
              border: 2px solid #FFC800 !important;
              border-radius: 999px;
              padding: 0.7rem 2.4rem;
              font-weight: 600; letter-spacing: .15em;
              box-shadow:
                  0 0 8px rgba(255,200,0,.9),
                  0 0 22px rgba(255,200,0,.55),
                  inset 0 0 12px rgba(255,200,0,.35);
              transition: box-shadow .25s ease, transform .25s ease;
          }
          .st-key-btn_entrar button p { color: #ffffff !important; }
          .st-key-btn_entrar button:hover,
          .st-key-btn_entrar button:focus,
          .st-key-btn_entrar button:active {
              background: transparent !important;
              border-color: #FFC800 !important;
              box-shadow:
                  0 0 12px rgba(255,200,0,1),
                  0 0 34px rgba(255,200,0,.8),
                  inset 0 0 16px rgba(255,200,0,.5);
              transform: translateY(-2px);
          }

          @keyframes aparecer {
              from { opacity: 0; transform: translateY(24px); }
              to   { opacity: 1; transform: none; }
          }
          .logo-izq          { animation: aparecer 1.2s ease-out .3s both; }
          /* Efecto escritura: de izquierda a derecha, letra por letra, con borde suave tipo pincel */
@keyframes escribir {
    from { -webkit-mask-size: 0% 100%;   mask-size: 0% 100%; }
    to   { -webkit-mask-size: 120% 100%; mask-size: 120% 100%; }
}
.titulo-portada, .sub-portada {
    -webkit-mask-image: linear-gradient(90deg, #000 85%, transparent 100%);
    mask-image: linear-gradient(90deg, #000 85%, transparent 100%);
    -webkit-mask-repeat: no-repeat;   mask-repeat: no-repeat;
    -webkit-mask-position: left center; mask-position: left center;
    -webkit-mask-size: 120% 100%;     mask-size: 120% 100%;
}
.titulo-portada { padding-bottom: .12em; animation: escribir 2s   steps(20, end) .8s both; }
.sub-portada    {                        animation: escribir 2.6s steps(58, end) 2.9s both; }
          .st-key-btn_entrar { animation: aparecer 1.2s ease-out 5.5s both; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <video class="video-fondo" autoplay muted loop playsinline preload="auto">
          <source src="app/static/fondo.mp4" type="video/mp4">
        </video>
        <div class="velo"></div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="portada"):
        st.markdown(
            f"""
            <div class="logo-izq"><img src="data:image/png;base64,{logo_b64}"></div>
            <div class="titulo-portada">Aplicación Dashboard</div>
            <div class="sub-portada">Baja rotación de inventarios · Ferreindustrias Perú S.A.C.</div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Entrar", key="btn_entrar"):
            st.markdown(
                """
                <style>
                @keyframes salirPortada { to { opacity: 0; } }
                [data-testid="stMainBlockContainer"] {
                    animation: salirPortada 0.8s ease-in forwards;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            time.sleep(0.8)
            st.session_state.entrado = True
            st.session_state.recien_entrado = True
            st.rerun()

    st.stop()


# ---------- Aparición difuminada (cada vez que cambias de sección) ----------
def transicion_suave(clave):
    recien = st.session_state.pop("recien_entrado", False)
    cambio = st.session_state.get("ultima_seccion") != clave
    st.session_state.ultima_seccion = clave

    if not (recien or cambio):
        return  # al mover filtros no se repite la animación

    # Nombre distinto en cada transición: así el navegador reinicia la animación
    st.session_state.n_anim = st.session_state.get("n_anim", 0) + 1
    n = st.session_state.n_anim

    lateral = ""
    if recien:  # el lateral solo entra al venir de la portada
        lateral = f"""
        @keyframes lateral{n} {{
            from {{ opacity: 0; transform: translate3d(-24px, 0, 0); filter: blur(20px); }}
            to   {{ opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }}
        }}
        [data-testid="stSidebarContent"] {{
            animation: lateral{n} 1.2s ease-out both;
        }}
        """

    st.markdown(
        f"""
        <style>
        @keyframes pagina{n} {{
            from {{ opacity: 0; transform: translate3d(0, 40px, 0); filter: blur(12px); }}
            to   {{ opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }}
        }}
        [data-testid="stMainBlockContainer"] {{
            animation: pagina{n} 1.4s ease-out both;
        }}
        {lateral}
        </style>
        """,
        unsafe_allow_html=True,
    )
# ---------- Fin portada ----------

# =====================================================================
#  NUEVO DASHBOARD: BAJA ROTACIÓN DE INVENTARIOS (4 OBJETIVOS)
#  Todo se lee del Excel. Si cambias un número en el Excel y guardas,
#  la web se actualiza sola al recargar la página.
# =====================================================================
import openpyxl
import plotly.graph_objects as go

ARCHIVO_EXCEL = "Elaborado para Dashboard.xlsx"

# ---------- Colores ----------
PALETA = ["#FFC800", "#FF8A00", "#E5484D", "#3B82F6", "#22C55E",
          "#A855F7", "#14B8A6", "#94A3B8", "#F472B6"]
px.defaults.color_discrete_sequence = PALETA
COLOR_ESC = {"As-Is": "#E5484D", "Estándar": "#94A3B8", "To-Be": AMARILLO}
ORDEN_MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
               "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"]


# ---------- Lectura del Excel ----------
@st.cache_data
def cargar_libro(version):
    """Lee todas las hojas y guarda cada celda con valor: {'OBJ2': {'K2': ...}}."""
    wb = openpyxl.load_workbook(ARCHIVO_EXCEL, data_only=True)
    libro = {}
    for ws in wb.worksheets:
        libro[ws.title.strip()] = {
            c.coordinate: c.value for fila in ws.iter_rows() for c in fila if c.value is not None
        }
    return libro


LIBRO = cargar_libro(os.path.getmtime(ARCHIVO_EXCEL))


def celda(hoja, ref, defecto=None):
    return LIBRO.get(hoja, {}).get(ref, defecto)


def numero(hoja, ref):
    try:
        return float(str(celda(hoja, ref)).replace(",", "."))
    except (TypeError, ValueError):
        return None


def tabla(hoja, fila_ini, fila_fin, columnas):
    """Arma una tabla. columnas = {"Nombre": "Letra"}. La 1.ª columna no puede estar vacía."""
    filas = []
    for f in range(fila_ini, fila_fin + 1):
        fila = {nombre: celda(hoja, f"{letra}{f}") for nombre, letra in columnas.items()}
        if fila[next(iter(columnas))] is not None:
            filas.append(fila)
    df = pd.DataFrame(filas)
    if "Mes" in df.columns:
        df["Mes"] = df["Mes"].astype(str).str.strip().str.capitalize()
    return df


def texto(valor, unidad):
    if valor is None:
        return "—"
    return f"{valor * 100:.1f}%" if unidad == "%" else f"{valor:.1f} días"


# ---------- Resumen de los 4 objetivos (ubicación de cada dato en el Excel) ----------
P = "Planteamiento"
OBJETIVOS = [
    {
        "n": 1, "corto": "Pronóstico de la demanda", "unidad": "%", "mejor": "mayor",
        "indicador": "Exactitud del pronóstico (FA = 1 − MAPE)",
        "herramienta": celda(P, "P9"), "motivo": celda(P, "J9"), "causa": celda(P, "L9"),
        "objetivo": celda("OBJ1", "C9"),
        "as_is": numero("OBJ1", "D53"), "estandar": numero("OBJ1", "D54"), "to_be": numero("OBJ1", "D55"),
        "conclusion": celda("OBJ1", "C72"), "recomendacion": celda("OBJ1", "C73"),
    },
    {
        "n": 2, "corto": "Duración del inventario", "unidad": "días", "mejor": "menor",
        "indicador": "Duración del inventario (días)",
        "herramienta": celda(P, "P13"), "motivo": celda(P, "J13"), "causa": celda(P, "L13"),
        "objetivo": celda("OBJ2", "K2"),
        "as_is": numero("OBJ2", "L84"), "estandar": numero("OBJ2", "F28"), "to_be": numero("OBJ2", "P84"),
        "conclusion": celda(P, "AF13"), "recomendacion": celda(P, "AI13"),
    },
    {
        "n": 3, "corto": "Exactitud de inventarios", "unidad": "%", "mejor": "mayor",
        "indicador": "Confiabilidad del inventario (1 − % error)",
        "herramienta": celda(P, "P17"), "motivo": celda(P, "J17"), "causa": celda(P, "L17"),
        "objetivo": celda(P, "R17"),
        "as_is": numero("OBJ3", "P52"), "estandar": numero("OBJ3", "M76"), "to_be": numero("OBJ3", "P223"),
        "conclusion": celda(P, "AF17"), "recomendacion": celda(P, "AI17"),
    },
    {
        "n": 4, "corto": "Cumplimiento de pedidos", "unidad": "%", "mejor": "mayor",
        "indicador": "Cumplimiento de pedidos (%)",
        "herramienta": "Programación de despachos (regla EDD)",
        "motivo": celda("OBJ4", "C2"), "causa": celda("OBJ4", "C3"),
        "objetivo": celda("OBJ4", "G1"),
        "as_is": numero("OBJ4", "D90"), "estandar": numero("OBJ4", "L67"), "to_be": numero("OBJ4", "F90"),
        "conclusion": celda("OBJ4", "B92"), "recomendacion": celda("OBJ4", "B56"),
    },
]

for o in OBJETIVOS:
    a, s, t = o["as_is"], o["estandar"], o["to_be"]
    o["cumple"] = (t >= s) if o["mejor"] == "mayor" else (t <= s)
    o["cierre"] = (t - a) / (s - a) * 100 if s != a else 100.0  # % de la brecha que se cerró


# ---------- Gráficos reutilizables ----------
def escala(valores, unidad):
    return [v * 100 for v in valores] if unidad == "%" else list(valores)


def grafico_tres_barras(o, alto=300):
    esc = ["As-Is", "Estándar", "To-Be"]
    vals = escala([o["as_is"], o["estandar"], o["to_be"]], o["unidad"])
    sufijo = "%" if o["unidad"] == "%" else " d"
    fig = go.Figure(go.Bar(
        x=esc, y=vals, marker_color=[COLOR_ESC[e] for e in esc],
        text=[f"{v:.1f}{sufijo}" for v in vals], textposition="outside",
    ))
    fig.update_layout(height=alto, margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                      yaxis=dict(range=[0, max(vals) * 1.25], title=o["unidad"]))
    return fig


def grafico_medidor(o):
    a, s, t = escala([o["as_is"], o["estandar"], o["to_be"]], o["unidad"])
    tope = 100 if o["unidad"] == "%" else max(a, s, t) * 1.3
    sube_bien = o["mejor"] == "mayor"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=t,
        number={"suffix": "%" if o["unidad"] == "%" else " días", "valueformat": ".1f"},
        delta={"reference": a, "valueformat": ".1f",
               "increasing": {"color": "#22C55E" if sube_bien else "#E5484D"},
               "decreasing": {"color": "#E5484D" if sube_bien else "#22C55E"}},
        gauge={"axis": {"range": [0, tope]}, "bar": {"color": AMARILLO},
               "steps": [{"range": [0, a], "color": "#3A1F24"}],
               "threshold": {"line": {"color": "#FFFFFF", "width": 4}, "value": s}},
        title={"text": "To-Be vs. As-Is (línea blanca = estándar)", "font": {"size": 14}},
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=10))
    return fig


def linea_estandar(fig, valor, texto_linea="Estándar"):
    fig.add_hline(y=valor, line_dash="dash", line_color=COLOR_ESC["Estándar"],
                  annotation_text=texto_linea, annotation_position="top left")
    return fig


def filtrar_meses(df, meses):
    d = df[df["Mes"].isin(meses)].copy()
    d["Mes"] = pd.Categorical(d["Mes"], categories=ORDEN_MESES, ordered=True)
    return d.sort_values("Mes")


# ---------- Estilos de las tarjetas ----------
st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: #1A1D24;
        border-left: 5px solid #FFC800;
        padding: 12px 16px;
        border-radius: 8px;
    }
    [data-testid="stMetricValue"] { font-size: 1.5rem; }
    .ficha {
        background-color: #1A1D24; border-radius: 8px; padding: 12px 14px;
        height: 100%; border-top: 3px solid #FFC800;
    }
    .ficha small { color: #9AA0A6; text-transform: uppercase; letter-spacing: 1px; font-size: 0.7rem; }
    .ficha p { margin: 4px 0 0 0; font-size: 0.95rem; }
    .etiqueta { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }
    .ok  { background: #14532D; color: #86EFAC; }
    .no  { background: #4C1D1D; color: #FCA5A5; }
    </style>
    """,
    unsafe_allow_html=True,
)


def ficha(titulo, contenido):
    st.markdown(f'<div class="ficha"><small>{titulo}</small><p>{contenido}</p></div>',
                unsafe_allow_html=True)


def etiqueta_cumple(o):
    if o["cumple"]:
        return '<span class="etiqueta ok">Cumple el estándar</span>'
    return '<span class="etiqueta no">Aún no llega al estándar</span>'

st.markdown("""
<style>
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0B0E14 0%, #10141C 100%) !important;
  border-right: 1px solid rgba(255,200,0,.22);
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
  color: #FFC800 !important; letter-spacing: .32em; text-transform: uppercase;
  font-size: .72rem !important; font-weight: 700;
}
[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; counter-reset: idx; }
[data-testid="stSidebar"] [role="radiogroup"] > label {
  counter-increment: idx;
  display: flex; align-items: center; gap: 12px;
  padding: 9px 16px; margin: 0; cursor: pointer;
  background: rgba(255,255,255,.03);
  clip-path: polygon(14px 0, 100% 0, 100% calc(100% - 14px), calc(100% - 14px) 100%, 0 100%, 0 14px);
  transition: background .3s ease, transform .3s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child { display: none !important; }
[data-testid="stSidebar"] [role="radiogroup"] > label::before {
  content: "0" counter(idx); color: #FFC800; font-size: .72rem;
  letter-spacing: .12em; font-weight: 700;
}
[data-testid="stSidebar"] [role="radiogroup"] > label p {
  color: #D9D5CB !important; margin: 0; letter-spacing: .02em; transition: color .3s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
  background: linear-gradient(90deg, rgba(255,200,0,.16), rgba(255,200,0,.04));
  transform: translateX(4px);
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {
  background: linear-gradient(120deg, #FFE98A 0%, #FFC800 45%, #D99A00 100%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.55);
  transform: translateX(6px);
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked)::before { color: #0E1117; }
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) p { color: #0E1117 !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)
# ---------- Barra lateral: logo e índice ----------
st.sidebar.image("logo.png")
st.sidebar.title("Ferreindustrias S.A.C.")
seccion = st.sidebar.radio(
    "Índice",
    ["Carátula", "Planteamiento", "Dashboard general",
     "Objetivo 1", "Objetivo 2", "Objetivo 3", "Objetivo 4"],
)
transicion_suave(seccion)

# Filtro de meses (solo para los objetivos 2, 3 y 4)
meses_elegidos = ORDEN_MESES
if seccion in ("Objetivo 2", "Objetivo 3", "Objetivo 4"):
    with st.sidebar:
        st.divider()
        st.subheader("Filtros")
        desde, hasta = st.select_slider("Meses", options=ORDEN_MESES,
                                        value=(ORDEN_MESES[0], ORDEN_MESES[-1]))
        meses_elegidos = ORDEN_MESES[ORDEN_MESES.index(desde): ORDEN_MESES.index(hasta) + 1]


# ---------- Cabecera común de cada objetivo ----------
def cabecera_objetivo(o):
    st.title(f"Objetivo {o['n']}: {o['corto']}")
    st.markdown(etiqueta_cumple(o), unsafe_allow_html=True)
    st.caption(o["objetivo"])

    c1, c2, c3, c4 = st.columns(4)
    with c1: ficha("Motivo", o["motivo"])
    with c2: ficha("Causa raíz", o["causa"])
    with c3: ficha("Herramienta", o["herramienta"])
    with c4: ficha("Indicador", o["indicador"])
    st.write("")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("As-Is (actual)", texto(o["as_is"], o["unidad"]))
    m2.metric("Estándar (meta)", texto(o["estandar"], o["unidad"]))
    dif = o["to_be"] - o["as_is"]
    dif_txt = f"{dif * 100:+.1f} pp" if o["unidad"] == "%" else f"{dif:+.1f} días"
    m3.metric("To-Be (con la mejora)", texto(o["to_be"], o["unidad"]), dif_txt,
              delta_color="normal" if o["mejor"] == "mayor" else "inverse")
    m4.metric("Brecha cerrada", f"{min(o['cierre'], 100):.0f}%")

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("As-Is vs. Estándar vs. To-Be")
        st.plotly_chart(grafico_tres_barras(o), width="stretch", key=f"barras{o['n']}")
    with g2:
        st.subheader("Avance del indicador")
        st.plotly_chart(grafico_medidor(o), width="stretch", key=f"medidor{o['n']}")


def pie_objetivo(o):
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Conclusión")
        st.success(o["conclusion"] or "—")
    with c2:
        st.subheader("Recomendación" if o["n"] != 4 else "Propuesta")
        st.info(o["recomendacion"] or "—")


def ver_tabla(df, nombre):
    with st.expander("Ver los datos de esta tabla"):
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("Descargar (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"{nombre}.csv", mime="text/csv", key=f"dl_{nombre}")


# ---------- Contenido según la opción elegida ----------
if seccion == "Carátula":
        # ----- Edita estos datos con los de tu equipo -----
    INSTITUCION = "Universidad Privada del Norte"
    FACULTAD = "Facultad de Ingeniería Industrial"
    CURSO = "Gestión Estratégica de Operaciones"
    TITULO_1 = "Dashboard:"
    TITULO_2 = "Baja rotación de inventarios"
    INTEGRANTES = [
        "DIANA MARIBEL GARCIA SALAZAR",
        "YASSER ARAFAT LUQUE GARCIA",
        "ERIG JOHAN DIAZ PERALTA",
        "JOSUE EDUARDO RAVELLO YASAKA",
    ]
    DOCENTE = "ALDO GUILLERMO RIVADENEYRA CUYA"
    FECHA = "30 Noviembre del 2026"
    # --------------------------------------------------

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;0,700;0,800;1,400&display=swap');

[data-testid="stMainBlockContainer"] { padding-top: 0.3rem !important; padding-bottom: 0.3rem !important; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: 0 !important; }
.caratula {
  position: relative; overflow: hidden;
  height: calc(100vh - 1.2rem); min-height: 520px;
  border-radius: 16px; border: 1px solid rgba(255,255,255,.08);
  background: radial-gradient(ellipse at center, #1b2130 0%, #0E1117 75%);
  display: flex; flex-direction: column; align-items: center;
  justify-content: space-between; text-align: center;
  padding: 4vh 9%; box-sizing: border-box; color: #fff;
  font-family: 'Source Serif 4', Georgia, serif;
}
.caratula > div:not(.hoja):not(.arcos):not(.puntos) { position: relative; z-index: 2; }
/* --- Textos --- */
.univ  { font-size: min(3.4vh, 2.2vw); font-weight: 800; color: #FFC800; letter-spacing: .06em; text-transform: uppercase; }
.fac   { font-size: min(2.6vh, 1.7vw); font-weight: 600; margin-top: .6vh; }
.curso { font-size: min(2.3vh, 1.5vw); font-style: italic; color: #C9CED6; margin-top: .4vh; }
.linea { width: min(55%, 520px); height: 2px; margin: 2vh auto; background: rgba(255,200,0,.65); }
.t1 { font-size: min(8.5vh, 5.2vw); font-weight: 800; color: #FFC800; text-transform: uppercase; line-height: 1.05; }
.t2 { font-size: min(5.6vh, 3.6vw); font-weight: 400; color: #E6E8EB; text-transform: uppercase; line-height: 1.1; }
.rotulo { font-size: min(2.2vh, 1.4vw); font-weight: 700; color: #FFC800; letter-spacing: .18em; text-transform: uppercase; margin-bottom: 1vh; }
.nombres { display: grid; grid-template-columns: 1fr 1fr; gap: .8vh 4vw; }
.nombre { font-size: min(2.2vh, 1.4vw); font-weight: 600; }
.docente { font-size: min(2.4vh, 1.5vw); font-weight: 600; }
.fecha { font-size: min(2.1vh, 1.4vw); font-style: italic; color: #C9CED6; margin-top: .5vh; }

/* --- Hojas amarillas (esquinas: arriba-izquierda y abajo-derecha) --- */
.hoja { position: absolute; width: 70px; z-index: 1; }
.hoja i { display: block; width: 70px; height: 70px; background: #FFC800; }
.hoja i:first-child { border-radius: 0 100% 0 100%; }
.hoja i:last-child  { border-radius: 100% 0 100% 0; }
.h-izq { left: -26px; top: 14%; }
.h-der { right: -26px; bottom: 14%; transform: rotate(180deg); }

/* --- Rayitas blancas (esquinas: arriba-derecha y abajo-izquierda) --- */
.arcos { position: absolute; width: 0; height: 0; z-index: 1; }
.arcos span { position: absolute; border: 2px solid rgba(255,255,255,.8); border-radius: 50%; }
.a-der { right: 0; top: 0; }
.a-der span { right: 0; top: 0; transform: translate(50%, -50%); }
.a-izq { left: 0; bottom: 0; }
.a-izq span { left: 0; bottom: 0; transform: translate(-50%, 50%); }
.arcos span:nth-child(1) { width: 90px;  height: 90px; }
.arcos span:nth-child(2) { width: 140px; height: 140px; }
.arcos span:nth-child(3) { width: 190px; height: 190px; }
.arcos span:nth-child(4) { width: 240px; height: 240px; }

/* --- Puntos amarillos --- */
.puntos { position: absolute; width: 110px; height: 70px; z-index: 1;
  background-image: radial-gradient(#FFC800 2px, transparent 2.5px); background-size: 16px 16px; }
.p-der { top: 5%; right: 12%; }
.p-izq { bottom: 5%; left: 12%; }
</style>
""", unsafe_allow_html=True)

    nombres_html = "".join(f'<div class="nombre">{n}</div>' for n in INTEGRANTES)
    st.markdown(
        '<div class="caratula">'
        '<div class="hoja h-izq"><i></i><i></i></div>'
        '<div class="hoja h-der"><i></i><i></i></div>'
        '<div class="arcos a-der"><span></span><span></span><span></span><span></span></div>'
        '<div class="arcos a-izq"><span></span><span></span><span></span><span></span></div>'
        '<div class="puntos p-der"></div><div class="puntos p-izq"></div>'
        f'<div><div class="univ">{INSTITUCION}</div>'
        f'<div class="fac">{FACULTAD}</div>'
        f'<div class="curso">{CURSO}</div></div>'
        f'<div><div class="linea"></div><div class="t1">{TITULO_1}</div>'
        f'<div class="t2">{TITULO_2}</div><div class="linea"></div>'
        f'<div class="rotulo">Integrantes</div><div class="nombres">{nombres_html}</div></div>'
        f'<div><div class="rotulo">Docente</div><div class="docente">{DOCENTE}</div>'
        f'<div class="fecha">{FECHA}</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

elif seccion == "Planteamiento":
    st.title("Planteamiento del problema")
    problema = str(celda(P, "F8", "BAJA ROTACIÓN DE INVENTARIOS")).capitalize().replace("rotacion", "rotación")
    st.markdown(
        '<div style="margin:.2rem 0 .6rem">'
        '<div style="color:#FFC800;letter-spacing:.3em;text-transform:uppercase;font-size:.72rem;font-weight:700">Problema general</div>'
        f'<div style="font-size:1.5rem;font-weight:600;line-height:1.25;color:#F2EDE3;margin-top:.15rem">{problema}</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption(celda(P, "F3", ""))
    st.info(f"**Objetivo general:** {celda(P, 'R4', '')}")

    k1, k2, k3 = st.columns(3)
    rot_actual = numero(P, "H7")
    rot_ref = numero(P, "H13")
    k1.metric("Rotación actual", f"{rot_actual:.2f} veces/año" if rot_actual else "—")
    k2.metric("Rotación de referencia", f"{rot_ref:.0f} veces/año" if rot_ref else "—")
    k3.metric("Impacto económico", f"S/ {numero(P, 'H15'):,.0f}" if numero(P, "H15") else "—")

    st.subheader("Del problema a la solución")
    st.caption("Haz clic en cada objetivo del anillo para ver su detalle.")

    def limpia(v):
        v = "—" if v is None else str(v)
        return v.capitalize() if v.isupper() else v

    datos = [{
        "n": o["n"], "corto": o["corto"],
        "motivo": limpia(o["motivo"]), "causa": limpia(o["causa"]),
        "herramienta": str(o["herramienta"] or "—"), "indicador": str(o["indicador"] or "—"),
        "as_is": texto(o["as_is"], o["unidad"]), "to_be": texto(o["to_be"], o["unidad"]),
        "estandar": texto(o["estandar"], o["unidad"]), "cumple": bool(o["cumple"]),
    } for o in OBJETIVOS]
    centro = {"actual": f"{rot_actual:.2f}" if rot_actual else "—",
              "ref": f"{rot_ref:.0f}" if rot_ref else "—"}

    with open("rueda.html", encoding="utf-8") as f:
        html_rueda = f.read()
    html_rueda = (html_rueda
                  .replace("__DATOS__", json.dumps(datos, ensure_ascii=False).replace("</", "<\\/"))
                  .replace("__CENTRO__", json.dumps(centro, ensure_ascii=False)))
    bloque_html(html_rueda, 640)

    # ---------- Impacto económico ----------
    st.subheader("Impacto económico: de dónde sale el ahorro")

    imp2_antes, imp2_desp = numero("OBJ2", "H125") or 0, numero("OBJ2", "K125") or 0
    imp3_antes = sum(numero("OBJ3", f"L{r}") or 0 for r in range(40, 52))
    imp3_desp = sum(numero("OBJ3", f"L{r}") or 0 for r in range(211, 223))
    imp4_antes, imp4_desp = numero("OBJ4", "J82") or 0, numero("OBJ4", "K82") or 0
    inversion = numero("OBJ3", "P114") or 0

    ahorros = [imp2_antes - imp2_desp, imp3_antes - imp3_desp, imp4_antes - imp4_desp]
    total_antes = imp2_antes + imp3_antes + imp4_antes
    total_desp = imp2_desp + imp3_desp + imp4_desp
    ahorro_total = sum(ahorros)

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Costo actual del problema", f"S/ {total_antes:,.0f}")
    e2.metric("Costo con la mejora", f"S/ {total_desp:,.0f}")
    e3.metric("Ahorro estimado", f"S/ {ahorro_total:,.0f}",
              f"-{ahorro_total / total_antes * 100:.0f}%" if total_antes else None,
              delta_color="inverse")
    e4.metric("Inversión en RFID", f"S/ {inversion:,.0f}")

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Costo actual (As-Is)", "Obj. 2 · EOQ", "Obj. 3 · RFID",
           "Obj. 4 · Despachos EDD", "Costo con la mejora (To-Be)"],
        y=[total_antes, -ahorros[0], -ahorros[1], -ahorros[2], 0],
        text=[f"S/ {total_antes:,.0f}", f"-S/ {ahorros[0]:,.0f}", f"-S/ {ahorros[1]:,.0f}",
              f"-S/ {ahorros[2]:,.0f}", f"S/ {total_desp:,.0f}"],
        textposition="outside",
        connector={"line": {"color": "rgba(255,255,255,.35)", "dash": "dot"}},
        decreasing={"marker": {"color": "#22C55E"}},
        totals={"marker": {"color": AMARILLO}},
    ))
    fig.update_layout(height=440, showlegend=False, margin=dict(l=10, r=10, t=30, b=10),
                      yaxis=dict(title="Soles (S/)", range=[0, total_antes * 1.15]))
    st.plotly_chart(fig, width="stretch", key="cascada_ahorro")
    st.caption("Suma de los objetivos con impacto en soles en tu Excel (2, 3 y 4). "
               "Obj. 2: valor del exceso de inventario. Obj. 3: diferencia valorizada entre inventario "
               "físico y de sistema. Obj. 4: costo de pedidos retrasados. El Objetivo 1 no tiene valor "
               "económico en el Excel.")
elif seccion == "Dashboard general":
    st.title("Dashboard")
    st.caption("Resumen de los 4 objetivos para incrementar la rotación de inventarios.")

    k1, k2, k3, k4 = st.columns(4)
    cumplen = sum(o["cumple"] for o in OBJETIVOS)
    k1.metric("Rotación actual", f"{numero(P, 'H7'):.2f}")
    k2.metric("Rotación de referencia", f"{numero(P, 'H13'):.0f}")
    k3.metric("Impacto económico", f"S/ {numero(P, 'H15'):,.0f}")
    k4.metric("Objetivos que cumplen el estándar", f"{cumplen} de {len(OBJETIVOS)}")

    st.subheader("As-Is, Estándar y To-Be de cada objetivo")
    for fila in (OBJETIVOS[:2], OBJETIVOS[2:]):
        cols = st.columns(2)
        for col, o in zip(cols, fila):
            with col:
                st.markdown(f"**Objetivo {o['n']} · {o['corto']}** &nbsp; {etiqueta_cumple(o)}",
                            unsafe_allow_html=True)
                st.caption(f"{o['herramienta']} — {o['indicador']}")
                st.plotly_chart(grafico_tres_barras(o, alto=260), width="stretch",
                                key=f"resumen{o['n']}")

    st.subheader("¿Cuánto de la brecha se cerró?")
    st.caption("100% = el To-Be llega al estándar. Más de 100% = lo supera.")
    cierre = pd.DataFrame([{"Objetivo": f"Obj. {o['n']} · {o['corto']}",
                            "Brecha cerrada (%)": round(o["cierre"], 1)} for o in OBJETIVOS])
    fig = px.bar(cierre, x="Brecha cerrada (%)", y="Objetivo", orientation="h",
                 text="Brecha cerrada (%)", color_discrete_sequence=[AMARILLO])
    fig.add_vline(x=100, line_dash="dash", line_color="#FFFFFF")
    fig.update_layout(height=300, yaxis={"categoryorder": "array",
                                          "categoryarray": list(cierre["Objetivo"])[::-1]})
    st.plotly_chart(fig, width="stretch")

    tabla_resumen = pd.DataFrame([{
        "Objetivo": f"Objetivo {o['n']}", "Indicador": o["indicador"],
        "As-Is": texto(o["as_is"], o["unidad"]), "Estándar": texto(o["estandar"], o["unidad"]),
        "To-Be": texto(o["to_be"], o["unidad"]), "¿Cumple?": "Sí" if o["cumple"] else "No",
    } for o in OBJETIVOS])
    st.dataframe(tabla_resumen, width="stretch", hide_index=True)

elif seccion == "Objetivo 1":
    o = OBJETIVOS[0]
    cabecera_objetivo(o)

    st.subheader("Exactitud por producto")
    fa = tabla("OBJ1", 64, 67, {"Producto": "B", "As-Is": "C", "Estándar": "D", "To-Be": "E"})
    fa_largo = fa.melt(id_vars="Producto", var_name="Escenario", value_name="FA")
    fa_largo["FA (%)"] = (fa_largo["FA"].astype(float) * 100).round(1)
    fig = px.bar(fa_largo, x="Producto", y="FA (%)", color="Escenario", barmode="group",
                 text="FA (%)", color_discrete_map=COLOR_ESC)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Error (MAPE) de cada modelo de pronóstico")
    mape = tabla("OBJ1", 38, 40, {"Producto": "B", "PMS (n=3)": "C", "PMP": "D", "SES": "E",
                                  "Regresión lineal": "F", "Estacional (m=2)": "G",
                                  "Modelo elegido": "H"})
    mape_largo = mape.drop(columns="Modelo elegido").melt(id_vars="Producto", var_name="Modelo",
                                                          value_name="MAPE")
    mape_largo["MAPE (%)"] = (mape_largo["MAPE"].astype(float) * 100).round(1)
    fig = px.bar(mape_largo, x="Producto", y="MAPE (%)", color="Modelo", barmode="group",
                 text="MAPE (%)")
    st.plotly_chart(fig, width="stretch")
    st.caption("Modelo elegido (menor MAPE): " +
               ", ".join(f"{r['Producto']} → {r['Modelo elegido']}" for _, r in mape.iterrows()))

    st.subheader("Demanda real vs. pronóstico")
    bloques = {"Pintura": 10, "Cintillo": 30, "Llave": 50}  # fila donde empieza cada producto
    producto = st.selectbox("Producto", list(bloques))
    ini = bloques[producto]
    pron = tabla("OBJ 1 PRONOSTCS", ini, ini + 11,
                 {"Mes": "A", "Demanda real": "C", "PMS (n=3)": "D", "PMP": "E", "SES": "F",
                  "Regresión lineal": "G", "Estacional (m=2)": "H"})
    elegido = mape.set_index("Producto").get("Modelo elegido", pd.Series()).get(producto)
    modelos = st.multiselect("Modelos a comparar",
                             ["PMS (n=3)", "PMP", "SES", "Regresión lineal", "Estacional (m=2)"],
                             default=[m for m in ["PMS (n=3)", elegido] if m] if elegido else ["PMS (n=3)"])
    fig = px.line(pron, x="Mes", y=["Demanda real"] + modelos, markers=True,
                  labels={"value": "Unidades", "variable": "Serie"})
    st.plotly_chart(fig, width="stretch")
    ver_tabla(pron, f"pronostico_{producto.lower()}")
    pie_objetivo(o)

elif seccion == "Objetivo 2":
    o = OBJETIVOS[1]
    cabecera_objetivo(o)

    st.subheader("Duración del inventario por mes")
    dur = tabla("OBJ2", 72, 83, {"Mes": "F", "Duración actual (días)": "L",
                                 "Duración con EOQ (días)": "P", "Mejora (días)": "R"})
    dur = filtrar_meses(dur, meses_elegidos)
    fig = px.line(dur, x="Mes", y=["Duración actual (días)", "Duración con EOQ (días)"],
                  markers=True, labels={"value": "Días", "variable": "Escenario"},
                  color_discrete_sequence=[COLOR_ESC["As-Is"], COLOR_ESC["To-Be"]])
    linea_estandar(fig, o["estandar"], f"Estándar {o['estandar']:.0f} días")
    st.plotly_chart(fig, width="stretch")
    ver_tabla(dur, "duracion_inventario")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Lote actual vs. lote óptimo (EOQ)")
        lotes = pd.DataFrame({
            "Producto": ["Pintura", "Cintillo", "Llave"],
            "Lote actual": [numero("OBJ2", "G64"), numero("OBJ2", "K64"), numero("OBJ2", "O64")],
            "EOQ óptimo": [numero("OBJ2", "G65"), numero("OBJ2", "K65"), numero("OBJ2", "O65")],
        })
        fig = px.bar(lotes, x="Producto", y=["Lote actual", "EOQ óptimo"], barmode="group",
                     text_auto=True, labels={"value": "Unidades", "variable": ""},
                     color_discrete_sequence=[COLOR_ESC["As-Is"], COLOR_ESC["To-Be"]])
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.subheader("Clasificación ABC")
        abc = tabla("OBJ2", 46, 48, {"Producto": "F", "Demanda": "I", "Costo (S/)": "L",
                                     "Valor anual (S/)": "O", "Clase": "R"})
        fig = px.pie(abc, names="Producto", values="Valor anual (S/)", hole=0.5)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Impacto económico mensual: antes vs. después del EOQ")
    imp = tabla("OBJ2", 113, 124, {"Mes": "F", "Antes (S/)": "H", "Después (S/)": "K"})
    imp = filtrar_meses(imp, meses_elegidos)
    fig = px.bar(imp, x="Mes", y=["Antes (S/)", "Después (S/)"], barmode="group",
                 labels={"value": "Soles", "variable": ""},
                 color_discrete_sequence=[COLOR_ESC["As-Is"], COLOR_ESC["To-Be"]])
    st.plotly_chart(fig, width="stretch")
    pie_objetivo(o)

elif seccion == "Objetivo 3":
    o = OBJETIVOS[2]
    cabecera_objetivo(o)

    asis = tabla("OBJ3", 40, 51, {"Mes": "G", "Diferencia (S/)": "L", "Error": "N", "Confiabilidad": "P"})
    tobe = tabla("OBJ3", 211, 222, {"Mes": "G", "Diferencia (S/)": "L", "Error": "N", "Confiabilidad": "P"})
    asis["Escenario"], tobe["Escenario"] = "As-Is", "To-Be"
    ambos = filtrar_meses(pd.concat([asis, tobe]), meses_elegidos)
    ambos["Confiabilidad (%)"] = (ambos["Confiabilidad"].astype(float) * 100).round(1)
    ambos["Error (%)"] = (ambos["Error"].astype(float) * 100).round(1)

    st.subheader("Confiabilidad del inventario por mes")
    fig = px.line(ambos, x="Mes", y="Confiabilidad (%)", color="Escenario", markers=True,
                  color_discrete_map=COLOR_ESC)
    linea_estandar(fig, o["estandar"] * 100, f"Estándar {o['estandar'] * 100:.0f}%")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Diferencia entre físico y sistema (S/)")
        fig = px.bar(ambos, x="Mes", y="Diferencia (S/)", color="Escenario", barmode="group",
                     color_discrete_map=COLOR_ESC)
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.subheader("Costo de implementación RFID")
        costos = tabla("OBJ3", 109, 113, {"Componente": "F", "Cantidad": "N",
                                          "Costo unitario (S/)": "O", "Costo total (S/)": "P"})
        fig = px.pie(costos, names="Componente", values="Costo total (S/)", hole=0.5)
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Inversión total estimada: S/ {numero('OBJ3', 'P114'):,.0f}")
    ver_tabla(ambos.drop(columns=["Error", "Confiabilidad"]), "exactitud_inventarios")
    pie_objetivo(o)

elif seccion == "Objetivo 4":
    o = OBJETIVOS[3]
    cabecera_objetivo(o)

    cum = tabla("OBJ4", 70, 81, {"Mes": "B", "Programados": "C", "Retrasados As-Is": "D",
                                 "Cumplimiento As-Is": "E", "Retrasados To-Be": "F",
                                 "Cumplimiento To-Be": "H", "Impacto As-Is (S/)": "J",
                                 "Impacto To-Be (S/)": "K", "Ahorro (S/)": "L"})
    cum = filtrar_meses(cum, meses_elegidos)
    graf = cum.assign(**{"As-Is": cum["Cumplimiento As-Is"].astype(float) * 100,
                         "To-Be": cum["Cumplimiento To-Be"].astype(float) * 100})

    st.subheader("Cumplimiento de pedidos por mes")
    fig = px.line(graf, x="Mes", y=["As-Is", "To-Be"], markers=True,
                  labels={"value": "Cumplimiento (%)", "variable": "Escenario"},
                  color_discrete_map=COLOR_ESC)
    linea_estandar(fig, o["estandar"] * 100, f"Meta {o['estandar'] * 100:.0f}%")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Impacto económico por retrasos")
        fig = px.bar(cum, x="Mes", y=["Impacto As-Is (S/)", "Impacto To-Be (S/)"], barmode="group",
                     labels={"value": "Soles", "variable": ""},
                     color_discrete_sequence=[COLOR_ESC["As-Is"], COLOR_ESC["To-Be"]])
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Ahorro en los meses elegidos: S/ {cum['Ahorro (S/)'].astype(float).sum():,.0f}")
    with c2:
        st.subheader("Gráfico de control de retrasos (p)")
        ctrl = tabla("OBJ4", 30, 41, {"Mes": "B", "Proporción de retraso": "G",
                                      "LCS": "I", "LC": "K", "LCI": "M"})
        ctrl = filtrar_meses(ctrl, meses_elegidos)
        fig = px.line(ctrl, x="Mes", y=["Proporción de retraso", "LCS", "LC", "LCI"], markers=True,
                      labels={"value": "Proporción", "variable": ""},
                      color_discrete_sequence=[AMARILLO, "#E5484D", "#94A3B8", "#E5484D"])
        st.plotly_chart(fig, width="stretch")

    st.subheader("Plan de programación de despachos")
    plan = tabla("OBJ4", 60, 64, {"Actividad": "B", "Descripción": "E",
                                  "Responsable": "I", "Frecuencia": "K"})
    st.dataframe(plan, width="stretch", hide_index=True)
    ver_tabla(cum, "cumplimiento_pedidos")
    pie_objetivo(o)
