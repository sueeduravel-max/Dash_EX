import pandas as pd
import plotly.express as px
import streamlit as st

# ---------- Configuración de la página ----------
st.set_page_config(
    page_title="Ferreindustrias S.A.C.",
    page_icon="logo.png",
    layout="wide",
)

ARCHIVO_EXCEL = "Libro2_JR1_1.xlsx"
HOJA = "BD FERREIN"
TIPO_CAMBIO = 3.70  # soles por cada dólar
# ---------- Colores de la marca ----------
PALETA = ["#FFC800", "#FF8A00", "#E5484D", "#3B82F6", "#22C55E",
          "#A855F7", "#14B8A6", "#94A3B8", "#F472B6"]
px.defaults.color_discrete_sequence = PALETA
# ---------- Reglas para clasificar cada producto en una categoría ----------
# El código busca estas palabras dentro del nombre del producto.
# Si un producto no coincide con ninguna, queda en "Otros".
REGLAS = {
    "Pinturas y solventes": ["PINTURA", "THINER", "THINNER", "ESMALTE", "BROCHA", "RODILLO", "BARNIZ",
                             "LACA", "SELLADOR", "IMPRIMANTE", "SPRAY", "SOLVENTE", "DISOLVENTE"],
    "Tuberías y válvulas": ["VALVULA", "TUBERIA", "TUBO", "ACOPLE", "NIPLE", "CODO", "UNION", " TEE ",
                            "REDUCCION", "MANGUERA", "ABRAZADERA", "BRIDA", "GRIFO", "CAÑO", "ADAPTADOR",
                            "TAPON", "CPVC", "PVC", "SIFON", "FLEXIBLE", "MEZCLADORA", "CONECTOR", "BUJE"],
    "Herramientas": ["LLAVE", "ALICATE", "MARTILLO", "DESARMADOR", "DESTORNILLADOR", "FLEXOMETRO",
                     "CINCEL", "SIERRA", "SERRUCHO", "TALADRO", "AMOLADORA", "CIZALLA", " PALA", " PICO",
                     "COMBA", "BARRETA", "ESCUADRA", "NIVEL", "PRENSA", " DADO ", "CARRETILLA", "CARBON",
                     "EXTENSION", "ESPATULA", "CUCHILLA", "TIJERA", "PISTOLA", "MULTIMETRO", "ESCALERA",
                     "BROCA", "DISCO", "LIJA", "ESMERIL", "TORQUIMETRO", "ENZUNCHADORA", "CEPILLO",
                     "ESCOBA", "RECOGEDOR", "SOLDAR", "SOLDADURA", "MAQUINA", "FRESA", "GATA",
                     "TERRAJA", "REFRENTADOR"],
    "Seguridad y señalización": ["CANDADO", " CONO", "CASCO", "GUANTE", " LENTE", " BOTA", "ARNES",
                                 "EXTINTOR", "SEÑAL", "CHALECO", "MASCARILLA", "RESPIRADOR", "LOCKER",
                                 "LOCK OUT", "LOCKOUT", "BARRERA", "BOTIQUIN", "OREJERA", "PROTECTOR",
                                 "TRAJE", "UNIFORME", "CORTAVIENTO", " POLO", "PANTALON", "CAMISACA",
                                 "ANTIDERRAME", "RETRACTIL"],
    "Fijaciones y ferretería": ["CINTILLO", "PERNO", "TORNILLO", "CLAVO", "TUERCA", "ARANDELA", "ALAMBRE",
                                "GRAPA", "REMACHE", "TARUGO", "BISAGRA", "CADENA", "PASADOR", "CERRADURA",
                                "PICAPORTE", "GRILLETE", "ESPARRAGO", "SOGA", "CUERDA", "CABLE DE ACERO",
                                "PEGAMENTO", "SILICONA", "ADHESIVO", "CINTA", "CABO"],
    "Eléctrico": ["INTERRUPTOR", "TOMACORRIENTE", "CABLE", "FOCO", "LAMPARA", "REFLECTOR", "TABLERO",
                  "TERMOMAGNETICO", "CONTACTOR", " RELE ", "FUSIBLE", "ENCHUFE", " PILA", "BATERIA",
                  "SENSOR", " LED ", "TRANSFORMADOR", "CONDUCTOR", "CAPACITOR", "MOTOR", "TIMER",
                  "LUMINARIA"],
    "Construcción y materiales": ["CEMENTO", "SIKA", "LISTON", "MADERA", "TRIPLAY", "PLANCHA", "FIERRO",
                                  "ACERO", "ANGULO", "PERFIL", "LADRILLO", "ARENA", "YESO", "MALLA",
                                  "COBERTOR", "CALAMINA", "DRYWALL", "CONCRETO", "GROUT", "BANDEJA",
                                  "RIEL", "VIGA", "MATRIZ", "CERAMICA", "ENCHAPE", "PISO", "TEJA",
                                  "MAYOLICA", "GRATING", "CANAL STRUT", "BENTONITA", "TACO"],
    "Limpieza, oficina y varios": ["BOLSA", "PAÑO", "PAPEL", "DETERGENTE", "JABON", "LEJIA", "TRAPEADOR",
                                   "ESCOBILLA", "BALDE", "TACHO", "BIDON", "TOALLA", "CORTINA", "FRAZADA",
                                   "LAPICERO", "PLUMON", "ARCHIVADOR", "FOLDER", "TINTA", "TONER",
                                   "CUADERNO", " SILLA", " MESA ", "ESTANTE", "ALCOHOL", "DESINFECTANTE",
                                   "ESPONJA", "RECIPIENTE", "CAJA", "TRAPO", "SACO", "BEBIDA", "AGUA",
                                   "GALLETA", "TAPER", "FOSFOROS", "COLCHON", "CUBRECAMA", "EDREDON"],
}


def clasificar(texto):
    t = " " + str(texto).upper() + " "
    for categoria, palabras in REGLAS.items():
        if any(p in t for p in palabras):
            return categoria
    return "Otros"

@st.cache_data
def cargar_datos():
    df = pd.read_excel(ARCHIVO_EXCEL, sheet_name=HOJA)

    # Quita filas sin fecha (por ejemplo, una fila de totales)
    df = df.dropna(subset=["Fecha documento"])

    # Nombres de columnas más cortos
    df = df.rename(columns={
        "Fecha documento": "Fecha",
        "Texto breve": "Producto",
        "Cantidad de pedido": "Cantidad",
        "Precio neto": "Precio",
        "Unidad medida pedido": "Unidad",
        "Proveedor/Centro suministrador": "Proveedor",
    })

    # Convierte a soles los precios que están en dólares
    df["Precio_PEN"] = df["Precio"].where(df["Moneda"] != "USD", df["Precio"] * TIPO_CAMBIO)

    # Monto de cada compra y columnas útiles para los gráficos
    df["Monto_PEN"] = df["Cantidad"] * df["Precio_PEN"]
    df["Mes"] = df["Fecha"].dt.to_period("M").dt.to_timestamp()
    df["Categoria"] = df["Producto"].map(clasificar)
    return df


df = cargar_datos()
st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: #1A1D24;
        border-left: 5px solid #FFC800;
        padding: 12px 16px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Barra lateral: logo e índice ----------
st.sidebar.image("logo.png")
st.sidebar.title("Ferreindustrias S.A.C.")
seccion = st.sidebar.radio(
    "Índice",
    ["Carátula", "Base de datos", "Dashboard"],
)

# ---------- Contenido según la opción elegida ----------
if seccion == "Carátula":
    # ----- Edita estos datos con los de tu equipo -----
    INSTITUCION = "Universidad Privada del Norte"
    CURSO = "Gestión Estratégica de Operaciones"
    TITULO = "Elaboración del Dashbord a partir de la base de datos"
    INTEGRANTES = [
        "DIANA MARIBEL GARCIA SALAZAR",
        "YASSER ARAFAT LUQUE GARCIA",
        "ERIG JOHAN DIAZ PERALTA",
        "JOSUE EDUARDO RAVELLO YASAKA",
    ]
    DOCENTE = "Aldo Guillermo Rivadeneyra Cuya"
    FECHA = "16 Noviembre del 2026"
    # --------------------------------------------------

    izq, centro, der = st.columns([1, 3, 1])
    with centro:
        st.image("logo.png", width=320)
        st.markdown(f"<h3 style='text-align:center'>{INSTITUCION}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{CURSO}</p>", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<h1 style='text-align:center'>{TITULO}</h1>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<h4 style='text-align:center'>Integrantes</h4>", unsafe_allow_html=True)
        for nombre in INTEGRANTES:
            st.markdown(f"<p style='text-align:center'>{nombre}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'><b>Docente:</b> {DOCENTE}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{FECHA}</p>", unsafe_allow_html=True)

elif seccion == "Base de datos":
    st.title("Base de datos")
    st.caption("Datos tomados directamente del archivo Excel (hoja BD FERREIN).")

    columnas_originales = ["Fecha", "Material", "Producto", "Cantidad",
                           "Precio", "Moneda", "Unidad", "Proveedor"]
    columnas_calculadas = ["Precio_PEN", "Monto_PEN", "Mes", "Categoria"]

    # ----- Indicadores -----
    c1, c2, c3 = st.columns(3)
    c1.metric("Compras (filas)", f"{len(df):,}")
    c2.metric("Columnas", len(columnas_originales))
    c3.metric("Productos distintos", f"{df['Producto'].nunique():,}")
    st.caption(f"Periodo: {df['Fecha'].min():%d/%m/%Y} a {df['Fecha'].max():%d/%m/%Y}")

    # ----- Buscador y filtros -----
    f1, f2 = st.columns([2, 1])
    texto = f1.text_input("Buscar producto", placeholder="Ejemplo: pintura, disco, válvula...")
    moneda = f2.selectbox("Moneda", ["Todas", "PEN", "USD"])
    ver_calculadas = st.checkbox(
        "Mostrar también las columnas calculadas (precio en soles, monto, mes y categoría)"
    )

    # ----- Aplicar filtros -----
    vista = df.copy()
    if texto:
        vista = vista[vista["Producto"].str.contains(texto, case=False, na=False, regex=False)]
    if moneda != "Todas":
        vista = vista[vista["Moneda"] == moneda]

    columnas = columnas_originales + (columnas_calculadas if ver_calculadas else [])
    vista = vista[columnas].copy()

    # ----- Dar buen formato a la tabla -----
    vista["Fecha"] = vista["Fecha"].dt.date
    vista["Material"] = vista["Material"].astype("Int64").astype(str).replace("<NA>", "")
    if "Mes" in vista.columns:
        vista["Mes"] = vista["Mes"].dt.strftime("%Y-%m")

    st.write(f"Mostrando **{len(vista):,}** de **{len(df):,}** filas")
    st.dataframe(vista, width="stretch", hide_index=True, height=500)

    st.download_button(
        "Descargar esta tabla (CSV)",
        vista.to_csv(index=False).encode("utf-8-sig"),
        file_name="base_de_datos.csv",
        mime="text/csv",
    )

else:
    st.title("Panel de control")

    # ----- Filtros en la barra lateral -----
    with st.sidebar:
        st.divider()
        st.subheader("Filtros")
        f_min = df["Fecha"].min().date()
        f_max = df["Fecha"].max().date()
        rango = st.date_input("Periodo", value=(f_min, f_max), min_value=f_min, max_value=f_max)
        opciones = sorted(df["Categoria"].unique())
        elegidas = st.multiselect("Categoría", opciones, default=opciones)
        moneda = st.selectbox("Moneda original de la compra", ["Todas", "PEN", "USD"])

    if len(rango) != 2:
        st.info("Elige la fecha inicial y la fecha final del periodo.")
        st.stop()

    # ----- Aplicar filtros -----
    d = df[
        (df["Fecha"].dt.date >= rango[0])
        & (df["Fecha"].dt.date <= rango[1])
        & (df["Categoria"].isin(elegidas))
    ]
    if moneda != "Todas":
        d = d[d["Moneda"] == moneda]
    if d.empty:
        st.warning("No hay compras con esos filtros. Prueba ampliando el periodo o las categorías.")
        st.stop()

    # ----- Indicadores -----
    total = d["Monto_PEN"].sum()
    lineas = len(d)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Monto comprado", f"S/ {total:,.0f}")
    k2.metric("Líneas de compra", f"{lineas:,}")
    k3.metric("Promedio por línea", f"S/ {total / lineas:,.0f}")
    k4.metric("Productos distintos", f"{d['Producto'].nunique():,}")
    k5.metric("Categoría principal", d.groupby("Categoria")["Monto_PEN"].sum().idxmax())

    st.caption(f"Todos los montos están en soles. Las compras en USD se convirtieron a S/ {TIPO_CAMBIO:.2f} por dólar.")

    # ----- Gráficos -----
    g1, g2 = st.columns([3, 2])

    with g1:
        st.subheader("Evolución mensual de compras")
        mensual = d.groupby("Mes")["Monto_PEN"].sum()
        meses = pd.date_range(mensual.index.min(), mensual.index.max(), freq="MS")
        mensual = mensual.reindex(meses, fill_value=0).rename_axis("Mes").reset_index()
        fig_linea = px.line(mensual, x="Mes", y="Monto_PEN", markers=True,
                            labels={"Monto_PEN": "Compras (S/)", "Mes": "Mes"})
        st.plotly_chart(fig_linea, width="stretch")

    with g2:
        st.subheader("Compras por categoría")
        por_cat = d.groupby("Categoria", as_index=False)["Monto_PEN"].sum()
        fig_dona = px.pie(por_cat, names="Categoria", values="Monto_PEN", hole=0.5)
        fig_dona.update_traces(textinfo="percent")
        st.plotly_chart(fig_dona, width="stretch")

    st.subheader("Los 10 productos con mayor monto comprado")
    top = d.groupby("Producto", as_index=False)["Monto_PEN"].sum().nlargest(10, "Monto_PEN")
    fig_top = px.bar(top, x="Monto_PEN", y="Producto", orientation="h",
                     labels={"Monto_PEN": "Compras (S/)", "Producto": ""})
    fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_top, width="stretch")