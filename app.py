import streamlit as st

# IMPORTANTE: set_page_config DEBE ser el primer comando de Streamlit
st.set_page_config(
    page_title="Calculadora de Márgenes Agrícolas",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ahora podemos importar otras bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # Alternativa a Plotly si es necesario

# Mensaje de carga mientras intentamos importar Plotly
with st.spinner("Cargando componentes de visualización..."):
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        plotly_available = True
    except ImportError:
        st.warning("No se pudo importar Plotly. Se usarán visualizaciones alternativas.")
        # Creamos módulos vacíos para no romper el código
        class DummyModule:
            def __getattr__(self, name):
                return lambda *args, **kwargs: None
        px = DummyModule()
        go = DummyModule()
        plotly_available = False

# Título y descripción
st.title("📊 Calculadora de Márgenes Agrícolas")
st.markdown("""
Esta aplicación te permite calcular los márgenes de diferentes cultivos, 
teniendo en cuenta rendimientos, precios, costos directos y otros gastos.
""")

# Crear pestañas
tab1, tab2, tab3 = st.tabs(["Calculadora de Márgenes", "Comparativa de Cultivos", "Ayuda"])

# Pestaña 1: Calculadora de Márgenes
with tab1:
    st.header("Cálculo de Márgenes por Cultivo")
    
    # Organizar la entrada en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Selección de cultivo
        cultivo = st.selectbox(
            "Seleccionar cultivo",
            ["Soja 1ra", "Maíz", "Trigo", "Soja 2da", "Maíz 2da", "Girasol"]
        )
        
        # Datos básicos
        superficie = st.number_input("Superficie (Ha)", min_value=0.0, value=100.0, step=10.0)
        rendimiento = st.number_input("Rendimiento (tn/ha)", min_value=0.0, value=3.0, step=0.1)
        precio = st.number_input("Precio (USD/tn)", min_value=0.0, value=290.0, step=10.0)
    
    with col2:
        # Costos directos
        st.subheader("Costos Directos (USD/ha)")
        costo_labranza = st.number_input("Costo Labranza", min_value=0.0, value=80.0, step=5.0)
        costo_semilla = st.number_input("Costo semilla, inoc. y trat.", min_value=0.0, value=60.0, step=5.0)
        costo_herbicidas = st.number_input("Costo herbicidas", min_value=0.0, value=50.0, step=5.0)
        costo_fungicidas = st.number_input("Costo fungicidas", min_value=0.0, value=10.0, step=5.0)
        costo_insecticidas = st.number_input("Costo insecticidas", min_value=0.0, value=10.0, step=5.0)
        costo_fertilizantes = st.number_input("Costo fertilizantes", min_value=0.0, value=30.0, step=5.0)
    
    with col3:
        # Otros costos
        st.subheader("Otros Costos (USD/ha)")
        gastos_comercializacion = st.number_input("Gastos de comercialización", min_value=0.0, value=200.0, step=10.0)
        iibb = st.number_input("IIBB (%)", min_value=0.0, value=3.5, step=0.1)
        costos_estructura = st.number_input("Estructura", min_value=0.0, value=50.0, step=5.0)
        costos_cosecha = st.number_input("Cosecha", min_value=0.0, value=90.0, step=5.0)
        arrendamiento = st.number_input("Arrendamiento", min_value=0.0, value=160.0, step=10.0)
    
    # Cálculos
    # Ingresos
    ingreso_bruto_ha = rendimiento * precio
    ingreso_bruto_total = ingreso_bruto_ha * superficie
    
    # Costos directos
    total_costos_directos_ha = (
        costo_labranza + costo_semilla + costo_herbicidas + 
        costo_fungicidas + costo_insecticidas + costo_fertilizantes
    )
    total_costos_directos = total_costos_directos_ha * superficie
    
    # IIBB
    iibb_valor_ha = ingreso_bruto_ha * (iibb / 100) if iibb > 0 else 0
    iibb_valor_total = iibb_valor_ha * superficie
    
    # Ingreso neto
    ingreso_neto_ha = ingreso_bruto_ha - gastos_comercializacion - iibb_valor_ha
    ingreso_neto_total = ingreso_neto_ha * superficie
    
    # Margen bruto
    margen_bruto_ha = ingreso_neto_ha - total_costos_directos_ha - costos_estructura - costos_cosecha
    margen_bruto_total = margen_bruto_ha * superficie
    
    # Margen directo
    margen_directo_ha = margen_bruto_ha - arrendamiento
    margen_directo_total = margen_directo_ha * superficie
    
    # Mostrar resultados
    st.header("Resultados")
    
    # Crear tabla de resultados
    data = {
        "Variable": [
            "Superficie Ha", "Rendimiento tn", "USD/tn", 
            "Ingreso Bruto / ha", 
            "Costo Labranza", "Costo semilla, inoc y trat", "Costo herbicidas",
            "Costo fungicidas", "Costo insecticidas", "Costo fertilizantes",
            "Total costos directos / ha",
            "Ingreso Bruto / ha", "Gastos de comercialización", "IIBB 3.5%",
            "Ingreso Neto / ha",
            "Costos Directos", "Estructura", "Cosecha",
            "Margen Bruto / ha",
            "Arrendamiento / ha",
            "Margen Directo / ha"
        ],
        f"{cultivo} (USD/ha)": [
            superficie, rendimiento, precio,
            round(ingreso_bruto_ha, 2),
            round(costo_labranza, 2), round(costo_semilla, 2), round(costo_herbicidas, 2),
            round(costo_fungicidas, 2), round(costo_insecticidas, 2), round(costo_fertilizantes, 2),
            round(total_costos_directos_ha, 2),
            round(ingreso_bruto_ha, 2), round(gastos_comercializacion, 2), round(iibb_valor_ha, 2),
            round(ingreso_neto_ha, 2),
            round(total_costos_directos_ha, 2), round(costos_estructura, 2), round(costos_cosecha, 2),
            round(margen_bruto_ha, 2),
            round(arrendamiento, 2),
            round(margen_directo_ha, 2)
        ],
        "Total (USD)": [
            "", "", "",
            round(ingreso_bruto_total, 2),
            round(costo_labranza * superficie, 2), round(costo_semilla * superficie, 2), round(costo_herbicidas * superficie, 2),
            round(costo_fungicidas * superficie, 2), round(costo_insecticidas * superficie, 2), round(costo_fertilizantes * superficie, 2),
            round(total_costos_directos, 2),
            round(ingreso_bruto_total, 2), round(gastos_comercializacion * superficie, 2), round(iibb_valor_total, 2),
            round(ingreso_neto_total, 2),
            round(total_costos_directos, 2), round(costos_estructura * superficie, 2), round(costos_cosecha * superficie, 2),
            round(margen_bruto_total, 2),
            round(arrendamiento * superficie, 2),
            round(margen_directo_total, 2)
        ]
    }
    
    df_results = pd.DataFrame(data)
    
    # Definir grupos dentro de la tabla
    groups = {
        "Producción": list(range(0, 4)),
        "Costos directos por ha": list(range(4, 11)),
        "Margen Bruto por ha": list(range(11, 19)),
        "Margen Directo": list(range(19, 21))
    }
    
    # Mostrar tabla con estilo
    for group_name, indices in groups.items():
        st.subheader(group_name)
        st.dataframe(df_results.iloc[indices], hide_index=True, use_container_width=True)
    
    # Gráficos
    st.header("Visualización")
    
    # Verificar si Plotly está disponible para las visualizaciones
    if plotly_available:
        # Comparación de ingresos vs costos vs margen con Plotly
        labels = ['Ingreso Bruto', 'Costos Directos', 'Otros Costos', 'Margen Directo']
        otros_costos = gastos_comercializacion + iibb_valor_ha + costos_estructura + costos_cosecha + arrendamiento
        values = [ingreso_bruto_ha, total_costos_directos_ha, otros_costos, margen_directo_ha]
        colors = ['#636EFA', '#EF553B', '#FFA15A', '#00CC96']

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(title_text=f'Distribución de Ingresos y Costos para {cultivo}')
        fig.update_traces(marker=dict(colors=colors))
        st.plotly_chart(fig, use_container_width=True)
        
        # Desglose de costos directos
        costos_labels = ['Labranza', 'Semilla', 'Herbicidas', 'Fungicidas', 'Insecticidas', 'Fertilizantes']
        costos_values = [costo_labranza, costo_semilla, costo_herbicidas, costo_fungicidas, costo_insecticidas, costo_fertilizantes]
        
        fig2 = go.Figure([go.Bar(x=costos_labels, y=costos_values)])
        fig2.update_layout(title_text=f'Desglose de Costos Directos para {cultivo}')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        # Alternativa con Matplotlib si Plotly no está disponible
        st.subheader("Distribución de Ingresos y Costos")
        
        # Crear datos para el gráfico
        labels = ['Ingreso Bruto', 'Costos Directos', 'Otros Costos', 'Margen Directo']
        otros_costos = gastos_comercializacion + iibb_valor_ha + costos_estructura + costos_cosecha + arrendamiento
        values = [ingreso_bruto_ha, total_costos_directos_ha, otros_costos, margen_directo_ha]
        
        # Crear figura de matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(f'Distribución de Ingresos y Costos para {cultivo}')
        
        # Mostrar el gráfico
        st.pyplot(fig)
        
        # Desglose de costos directos con matplotlib
        st.subheader("Desglose de Costos Directos")
        
        costos_labels = ['Labranza', 'Semilla', 'Herbicidas', 'Fungicidas', 'Insecticidas', 'Fertilizantes']
        costos_values = [costo_labranza, costo_semilla, costo_herbicidas, costo_fungicidas, costo_insecticidas, costo_fertilizantes]
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.bar(costos_labels, costos_values)
        ax2.set_ylabel('USD/ha')
        ax2.set_title(f'Costos Directos para {cultivo}')
        
        st.pyplot(fig2)

# Pestaña 2: Comparativa de Cultivos
with tab2:
    st.header("Comparativa de Cultivos")
    
    # Cargar datos de ejemplo o permitir al usuario subir un archivo
    st.subheader("Datos de Comparación")
    
    option = st.radio(
        "Seleccione una opción:",
        ["Usar datos de ejemplo", "Cargar mi propio archivo CSV"]
    )
    
    if option == "Usar datos de ejemplo":
        # Datos de ejemplo basados en la tabla proporcionada
        data_example = {
            "Variable": ["Superficie Ha", "Rendimiento tn", "USD/tn", "Ingreso Bruto / ha", 
                         "Total costos directos / ha", "Margen Bruto / ha", "Margen Directo / ha"],
            "Soja 1ra": [1199, 3.2, 290, 939, 279, 296, 137],
            "Maíz": [1015, 7.7, 168, 1290, 456, 200, 40],
            "Trigo": [346, 3.6, 198, 722, 312, 98, 19],
            "Soja 2da": [309, 2.1, 290, 621, 205, 158, 78],
            "Maíz 2da": [37, 6.5, 168, 1097, 369, 203, 123],
            "Girasol": [101, 2.4, 293, 714, 286, 182, 23]
        }
        df_compare = pd.DataFrame(data_example)
    else:
        st.info("Por favor, sube un archivo CSV con los datos de comparación de cultivos.")
        uploaded_file = st.file_uploader("Elige un archivo CSV", type="csv")
        if uploaded_file is not None:
            df_compare = pd.read_csv(uploaded_file)
        else:
            st.warning("No has subido ningún archivo. Usando datos de ejemplo.")
            # Usar los mismos datos de ejemplo como fallback
            data_example = {
                "Variable": ["Superficie Ha", "Rendimiento tn", "USD/tn", "Ingreso Bruto / ha", 
                             "Total costos directos / ha", "Margen Bruto / ha", "Margen Directo / ha"],
                "Soja 1ra": [1199, 3.2, 290, 939, 279, 296, 137],
                "Maíz": [1015, 7.7, 168, 1290, 456, 200, 40],
                "Trigo": [346, 3.6, 198, 722, 312, 98, 19],
                "Soja 2da": [309, 2.1, 290, 621, 205, 158, 78],
                "Maíz 2da": [37, 6.5, 168, 1097, 369, 203, 123],
                "Girasol": [101, 2.4, 293, 714, 286, 182, 23]
            }
            df_compare = pd.DataFrame(data_example)
    
    # Mostrar la tabla de comparativa
    st.dataframe(df_compare, hide_index=True, use_container_width=True)
    
    # Visualizaciones comparativas
    st.subheader("Visualizaciones Comparativas")
    
    # Seleccionar qué visualizar
    compare_variable = st.selectbox(
        "Seleccionar variable para comparar:",
        ["Ingreso Bruto / ha", "Total costos directos / ha", "Margen Bruto / ha", "Margen Directo / ha"]
    )
    
    # Obtener los datos para la visualización
    if "Variable" in df_compare.columns:
        # Si está en formato largo (con columna de Variable)
        var_index = df_compare[df_compare["Variable"] == compare_variable].index[0]
        compare_data = df_compare.iloc[var_index, 1:].reset_index()
        compare_data.columns = ["Cultivo", "Valor"]
    else:
        # Si está en formato ancho
        compare_data = df_compare[compare_variable].reset_index()
        compare_data.columns = ["Cultivo", "Valor"]
    
    # Gráfico de barras para comparar cultivos
    if plotly_available:
        fig_compare = px.bar(compare_data, x="Cultivo", y="Valor", 
                            title=f"Comparación de {compare_variable} entre Cultivos",
                            color="Cultivo")
        st.plotly_chart(fig_compare, use_container_width=True)
        
        # Gráfico de radar para comparar todos los cultivos
        if "Variable" in df_compare.columns:
            # Preparar datos para gráfico de radar
            radar_vars = ["Rendimiento tn", "Ingreso Bruto / ha", "Total costos directos / ha", "Margen Bruto / ha", "Margen Directo / ha"]
            radar_data = {}
            
            for var in radar_vars:
                if var in df_compare["Variable"].values:
                    var_idx = df_compare[df_compare["Variable"] == var].index[0]
                    radar_data[var] = df_compare.iloc[var_idx, 1:].values
            
            if radar_data:
                radar_df = pd.DataFrame(radar_data, index=df_compare.columns[1:])
                
                # Normalizar los datos para el gráfico de radar
                radar_df_norm = radar_df.copy()
                for col in radar_df_norm.columns:
                    min_val = radar_df_norm[col].min()
                    max_val = radar_df_norm[col].max()
                    if max_val > min_val:  # Evitar división por cero
                        radar_df_norm[col] = (radar_df_norm[col] - min_val) / (max_val - min_val)
                    else:
                        radar_df_norm[col] = 0
                
                # Crear gráfico de radar
                fig_radar = go.Figure()
                
                for i, cultivo in enumerate(radar_df_norm.index):
                    fig_radar.add_trace(go.Scatterpolar(
                        r=radar_df_norm.loc[cultivo].values,
                        theta=radar_vars,
                        fill='toself',
                        name=cultivo
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )),
                    showlegend=True,
                    title="Comparación Multidimensional de Cultivos (Normalizado)"
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
    else:
        # Alternativa con Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(compare_data["Cultivo"], compare_data["Valor"])
        
        # Colorear las barras
        for i, bar in enumerate(bars):
            bar.set_color(plt.cm.tab10(i))
        
        ax.set_ylabel('Valor (USD/ha)')
        ax.set_title(f"Comparación de {compare_variable} entre Cultivos")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)

# Pestaña 3: Ayuda
with tab3:
    st.header("Ayuda y Documentación")
    
    st.subheader("¿Cómo usar esta aplicación?")
    st.markdown("""
    Esta aplicación te permite calcular los márgenes de diferentes cultivos agrícolas. Sigue estos pasos:
    
    1. En la pestaña **Calculadora de Márgenes**:
       - Selecciona el cultivo que deseas evaluar
       - Ingresa la superficie, rendimiento y precio
       - Completa los costos directos (labranza, semillas, etc.)
       - Ingresa otros costos como comercialización, estructura y arrendamiento
       - Los resultados se actualizarán automáticamente
    
    2. En la pestaña **Comparativa de Cultivos**:
       - Puedes ver una comparación entre diferentes cultivos
       - Usar los datos de ejemplo o cargar tu propio archivo CSV
       - Seleccionar qué variable comparar entre cultivos
    """)
    
    st.subheader("Glosario de Términos")
    terms = {
        "Ingreso Bruto": "Rendimiento × Precio del cultivo",
        "Costos Directos": "Suma de costos de labranza, semillas, herbicidas, fungicidas, insecticidas y fertilizantes",
        "Gastos de Comercialización": "Costos asociados a la venta del producto (fletes, comisiones, etc.)",
        "IIBB": "Impuesto sobre los Ingresos Brutos",
        "Ingreso Neto": "Ingreso Bruto - Gastos de Comercialización - IIBB",
        "Margen Bruto": "Ingreso Neto - Costos Directos - Estructura - Cosecha",
        "Margen Directo": "Margen Bruto - Arrendamiento"
    }
    
    for term, definition in terms.items():
        st.markdown(f"**{term}**: {definition}")
    
    st.subheader("Consejos para el análisis")
    st.markdown("""
    - Compara el Margen Directo por hectárea entre diferentes cultivos para determinar cuál es más rentable
    - Presta atención a la relación entre costos directos e ingresos
    - Analiza qué costos tienen mayor impacto en cada cultivo
    - Considera la rotación de cultivos para un análisis más completo
    """)
    
    st.subheader("Contacto y Soporte")
    st.markdown("""
    Si tienes preguntas o sugerencias, por favor contacta al desarrollador o al equipo de soporte.
    """)

# Agregar información en el pie de página
st.markdown("---")
st.markdown("© 2025 Calculadora de Márgenes Agrícolas | Desarrollado con Streamlit")
