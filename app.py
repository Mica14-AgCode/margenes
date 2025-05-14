import streamlit as st
import pandas as pd
import numpy as np

# IMPORTANTE: set_page_config DEBE ser el primer comando de Streamlit
st.set_page_config(
    page_title="Calculadora de Márgenes Agrícolas",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("📊 Calculadora de Márgenes Agrícolas")
st.markdown("""
Esta aplicación te permite calcular los márgenes de diferentes cultivos, 
teniendo en cuenta rendimientos, precios, costos directos y otros gastos.
""")

# Crear pestañas
tab1, tab2, tab3 = st.tabs(["Calculadora de Márgenes", "Configuración de Hectáreas", "Ayuda"])

# Inicializar variables en el estado de la sesión si no existen
if 'hectareas_cultivos' not in st.session_state:
    # Inicializar con valores predeterminados
    st.session_state.hectareas_cultivos = {
        "Soja 1ra": {"propias": 800, "arrendadas": 399, "total": 1199},
        "Maíz": {"propias": 600, "arrendadas": 415, "total": 1015},
        "Trigo": {"propias": 246, "arrendadas": 100, "total": 346},
        "Soja 2da": {"propias": 209, "arrendadas": 100, "total": 309},
        "Maíz 2da": {"propias": 20, "arrendadas": 17, "total": 37},
        "Girasol": {"propias": 51, "arrendadas": 50, "total": 101}
    }

# Pestaña 2: Configuración de Hectáreas
with tab2:
    st.header("Configuración de Hectáreas por Cultivo")
    st.markdown("""
    Aquí puedes configurar cuántas hectáreas destinas a cada cultivo, diferenciando entre hectáreas propias y arrendadas.
    """)
    
    # Crear columnas para los cultivos
    col1, col2 = st.columns(2)
    
    # Contador para alternar entre columnas
    counter = 0
    
    # Crear un diccionario temporal para almacenar los nuevos valores
    new_hectareas = {}
    
    # Para cada cultivo, mostrar campos para hectáreas propias y arrendadas
    for cultivo in st.session_state.hectareas_cultivos:
        # Alternar entre columnas
        current_col = col1 if counter % 2 == 0 else col2
        counter += 1
        
        with current_col:
            st.subheader(cultivo)
            # Hectáreas propias (solo números enteros)
            hectareas_propias = st.number_input(
                f"Hectáreas propias - {cultivo}", 
                min_value=0, 
                value=st.session_state.hectareas_cultivos[cultivo]["propias"],
                step=1,
                key=f"propias_{cultivo}"
            )
            
            # Hectáreas arrendadas (solo números enteros)
            hectareas_arrendadas = st.number_input(
                f"Hectáreas arrendadas - {cultivo}", 
                min_value=0, 
                value=st.session_state.hectareas_cultivos[cultivo]["arrendadas"],
                step=1,
                key=f"arrendadas_{cultivo}"
            )
            
            # Calcular total
            total_hectareas = hectareas_propias + hectareas_arrendadas
            st.info(f"Total hectáreas {cultivo}: {total_hectareas}")
            
            # Guardar en el diccionario temporal
            new_hectareas[cultivo] = {
                "propias": hectareas_propias,
                "arrendadas": hectareas_arrendadas,
                "total": total_hectareas
            }
    
    # Botón para actualizar todas las hectáreas
    if st.button("Actualizar Hectáreas"):
        st.session_state.hectareas_cultivos = new_hectareas
        st.success("Hectáreas actualizadas correctamente")
    
    # Mostrar resumen
    st.header("Resumen de Hectáreas")
    
    # Crear dataframe para mostrar el resumen
    hectareas_data = {
        "Cultivo": [],
        "Hectáreas Propias": [],
        "Hectáreas Arrendadas": [],
        "Total Hectáreas": []
    }
    
    for cultivo, datos in st.session_state.hectareas_cultivos.items():
        hectareas_data["Cultivo"].append(cultivo)
        hectareas_data["Hectáreas Propias"].append(datos["propias"])
        hectareas_data["Hectáreas Arrendadas"].append(datos["arrendadas"])
        hectareas_data["Total Hectáreas"].append(datos["total"])
    
    hectareas_df = pd.DataFrame(hectareas_data)
    
    # Añadir fila de totales
    totales = {
        "Cultivo": "TOTAL",
        "Hectáreas Propias": sum(hectareas_data["Hectáreas Propias"]),
        "Hectáreas Arrendadas": sum(hectareas_data["Hectáreas Arrendadas"]),
        "Total Hectáreas": sum(hectareas_data["Total Hectáreas"])
    }
    
    # Convertir a dataframe y concatenar
    totales_df = pd.DataFrame([totales])
    hectareas_df = pd.concat([hectareas_df, totales_df], ignore_index=True)
    
    # Mostrar tabla
    st.dataframe(hectareas_df, hide_index=True, use_container_width=True)
    
    # Visualización
    st.subheader("Distribución de Hectáreas por Cultivo")
    
    # Preparar datos para gráfico
    chart_data = pd.DataFrame({
        "Hectáreas": hectareas_data["Total Hectáreas"],
        "Cultivo": hectareas_data["Cultivo"]
    })
    
    # Mostrar gráfico
    st.bar_chart(chart_data.set_index("Cultivo"))

# Pestaña 1: Calculadora de Márgenes
with tab1:
    st.header("Cálculo de Márgenes por Cultivo")
    
    # Organizar la entrada en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Selección de cultivo
        cultivo = st.selectbox(
            "Seleccionar cultivo",
            list(st.session_state.hectareas_cultivos.keys())
        )
        
        # Obtener hectáreas del cultivo seleccionado
        hectareas_propias = st.session_state.hectareas_cultivos[cultivo]["propias"]
        hectareas_arrendadas = st.session_state.hectareas_cultivos[cultivo]["arrendadas"]
        superficie = st.session_state.hectareas_cultivos[cultivo]["total"]
        
        # Mostrar información de hectáreas
        st.info(f"Hectáreas propias: {hectareas_propias}")
        st.info(f"Hectáreas arrendadas: {hectareas_arrendadas}")
        st.info(f"Total hectáreas: {superficie}")
        
        # Datos básicos
        rendimiento = st.number_input("Rendimiento (tn/ha)", min_value=0.0, value=3.0, step=0.1, format="%.1f")
        precio = st.number_input("Precio (USD/tn)", min_value=0, value=290, step=10)
    
    with col2:
        # Costos directos
        st.subheader("Costos Directos (USD/ha)")
        costo_labranza = st.number_input("Costo Labranza", min_value=0, value=80, step=5)
        costo_semilla = st.number_input("Costo semilla, inoc. y trat.", min_value=0, value=60, step=5)
        costo_herbicidas = st.number_input("Costo herbicidas", min_value=0, value=50, step=5)
        costo_fungicidas = st.number_input("Costo fungicidas", min_value=0, value=10, step=5)
        costo_insecticidas = st.number_input("Costo insecticidas", min_value=0, value=10, step=5)
        costo_fertilizantes = st.number_input("Costo fertilizantes", min_value=0, value=30, step=5)
    
    with col3:
        # Otros costos
        st.subheader("Otros Costos (USD/ha)")
        gastos_comercializacion = st.number_input("Gastos de comercialización", min_value=0, value=200, step=10)
        iibb = st.number_input("IIBB (%)", min_value=0.0, value=3.5, step=0.5, format="%.1f")
        costos_estructura = st.number_input("Estructura", min_value=0, value=50, step=5)
        costos_cosecha = st.number_input("Cosecha", min_value=0, value=90, step=5)
        arrendamiento = st.number_input("Arrendamiento (USD/ha, solo para hectáreas arrendadas)", min_value=0, value=160, step=10)
    
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
    
    # Costos de arrendamiento (solo para hectáreas arrendadas)
    costo_arrendamiento_total = arrendamiento * hectareas_arrendadas
    
    # Calcular el costo de arrendamiento por hectárea distribuido sobre todas las hectáreas
    arrendamiento_promedio_ha = costo_arrendamiento_total / superficie if superficie > 0 else 0
    
    # Margen bruto
    margen_bruto_ha = ingreso_neto_ha - total_costos_directos_ha - costos_estructura - costos_cosecha
    margen_bruto_total = margen_bruto_ha * superficie
    
    # Margen directo (considerando arrendamiento real)
    margen_directo_ha = margen_bruto_ha - arrendamiento_promedio_ha
    margen_directo_total = margen_directo_ha * superficie
    
    # Mostrar resultados
    st.header("Resultados")
    
    # Crear tabla de resultados
    data = {
        "Variable": [
            "Superficie Total Ha", "Hectáreas Propias", "Hectáreas Arrendadas", 
            "Rendimiento tn", "USD/tn", 
            "Ingreso Bruto / ha", 
            "Costo Labranza", "Costo semilla, inoc y trat", "Costo herbicidas",
            "Costo fungicidas", "Costo insecticidas", "Costo fertilizantes",
            "Total costos directos / ha",
            "Ingreso Bruto / ha", "Gastos de comercialización", f"IIBB {iibb}%",
            "Ingreso Neto / ha",
            "Costos Directos", "Estructura", "Cosecha",
            "Margen Bruto / ha",
            "Arrendamiento promedio / ha",
            "Margen Directo / ha"
        ],
        f"{cultivo} (USD/ha)": [
            superficie, hectareas_propias, hectareas_arrendadas,
            rendimiento, precio,
            round(ingreso_bruto_ha, 2),
            round(costo_labranza, 2), round(costo_semilla, 2), round(costo_herbicidas, 2),
            round(costo_fungicidas, 2), round(costo_insecticidas, 2), round(costo_fertilizantes, 2),
            round(total_costos_directos_ha, 2),
            round(ingreso_bruto_ha, 2), round(gastos_comercializacion, 2), round(iibb_valor_ha, 2),
            round(ingreso_neto_ha, 2),
            round(total_costos_directos_ha, 2), round(costos_estructura, 2), round(costos_cosecha, 2),
            round(margen_bruto_ha, 2),
            round(arrendamiento_promedio_ha, 2),
            round(margen_directo_ha, 2)
        ],
        "Total (USD)": [
            "", "", "",
            "", "",
            round(ingreso_bruto_total, 2),
            round(costo_labranza * superficie, 2), round(costo_semilla * superficie, 2), round(costo_herbicidas * superficie, 2),
            round(costo_fungicidas * superficie, 2), round(costo_insecticidas * superficie, 2), round(costo_fertilizantes * superficie, 2),
            round(total_costos_directos, 2),
            round(ingreso_bruto_total, 2), round(gastos_comercializacion * superficie, 2), round(iibb_valor_total, 2),
            round(ingreso_neto_total, 2),
            round(total_costos_directos, 2), round(costos_estructura * superficie, 2), round(costos_cosecha * superficie, 2),
            round(margen_bruto_total, 2),
            round(costo_arrendamiento_total, 2),
            round(margen_directo_total, 2)
        ]
    }
    
    df_results = pd.DataFrame(data)
    
    # Definir grupos dentro de la tabla
    groups = {
        "Producción": list(range(0, 6)),
        "Costos directos por ha": list(range(6, 13)),
        "Margen Bruto por ha": list(range(13, 21)),
        "Margen Directo": list(range(21, 23))
    }
    
    # Mostrar tabla con estilo
    for group_name, indices in groups.items():
        st.subheader(group_name)
        st.dataframe(df_results.iloc[indices], hide_index=True, use_container_width=True)
    
    # Visualizaciones simplificadas usando las utilidades nativas de Streamlit
    st.header("Visualización")
    
    # Datos para gráficos
    labels = ['Ingreso Bruto', 'Costos Directos', 'Otros Costos', 'Arrendamiento', 'Margen Directo']
    otros_costos = gastos_comercializacion + iibb_valor_ha + costos_estructura + costos_cosecha
    values = [ingreso_bruto_ha, total_costos_directos_ha, otros_costos, arrendamiento_promedio_ha, margen_directo_ha]
    
    # Gráfico de barras simple usando Streamlit
    st.subheader(f'Distribución de Ingresos y Costos para {cultivo}')
    st.bar_chart(pd.DataFrame({
        'Categoría': labels,
        'USD/ha': values
    }).set_index('Categoría'))
    
    # Desglose de costos directos
    st.subheader(f'Desglose de Costos Directos para {cultivo}')
    costos_labels = ['Labranza', 'Semilla', 'Herbicidas', 'Fungicidas', 'Insecticidas', 'Fertilizantes']
    costos_values = [costo_labranza, costo_semilla, costo_herbicidas, costo_fungicidas, costo_insecticidas, costo_fertilizantes]
    
    st.bar_chart(pd.DataFrame({
        'Tipo de Costo': costos_labels,
        'USD/ha': costos_values
    }).set_index('Tipo de Costo'))
    
    # Comparativa de resultados entre hectáreas propias y arrendadas
    if hectareas_propias > 0 and hectareas_arrendadas > 0:
        st.subheader(f'Comparativa entre hectáreas propias y arrendadas para {cultivo}')
        
        # Cálculos específicos para hectáreas propias
        margen_bruto_propias = margen_bruto_ha * hectareas_propias
        margen_directo_propias = margen_bruto_ha * hectareas_propias
        
        # Cálculos específicos para hectáreas arrendadas
        margen_bruto_arrendadas = margen_bruto_ha * hectareas_arrendadas
        margen_directo_arrendadas = (margen_bruto_ha - arrendamiento) * hectareas_arrendadas
        
        # Preparar datos para el gráfico
        comp_labels = ['Hectáreas Propias', 'Hectáreas Arrendadas']
        margen_bruto_values = [margen_bruto_propias/hectareas_propias, margen_bruto_arrendadas/hectareas_arrendadas]
        margen_directo_values = [margen_directo_propias/hectareas_propias, margen_directo_arrendadas/hectareas_arrendadas]
        
        # Crear dataframe para el gráfico
        comp_data = pd.DataFrame({
            'Tipo': comp_labels,
            'Margen Bruto (USD/ha)': margen_bruto_values,
            'Margen Directo (USD/ha)': margen_directo_values
        })
        
        # Mostrar tabla
        st.dataframe(comp_data, hide_index=True, use_container_width=True)
        
        # Visualizar
        st.subheader("Margen Bruto (USD/ha)")
        st.bar_chart(pd.DataFrame({
            'Tipo': comp_labels,
            'USD/ha': margen_bruto_values
        }).set_index('Tipo'))
        
        st.subheader("Margen Directo (USD/ha)")
        st.bar_chart(pd.DataFrame({
            'Tipo': comp_labels,
            'USD/ha': margen_directo_values
        }).set_index('Tipo'))

# Pestaña 3: Ayuda
with tab3:
    st.header("Ayuda y Documentación")
    
    st.subheader("¿Cómo usar esta aplicación?")
    st.markdown("""
    Esta aplicación te permite calcular los márgenes de diferentes cultivos agrícolas. Sigue estos pasos:
    
    1. En la pestaña **Configuración de Hectáreas**:
       - Establece cuántas hectáreas propias y arrendadas tienes para cada cultivo
       - Haz clic en "Actualizar Hectáreas" para guardar los cambios
    
    2. En la pestaña **Calculadora de Márgenes**:
       - Selecciona el cultivo que deseas evaluar
       - Ingresa el rendimiento y precio
       - Completa los costos directos (labranza, semillas, etc.)
       - Ingresa otros costos como comercialización, estructura y arrendamiento
       - Los resultados se actualizarán automáticamente
    """)
    
    st.subheader("Glosario de Términos")
    terms = {
        "Hectáreas Propias": "Terrenos de tu propiedad donde realizas cultivos",
        "Hectáreas Arrendadas": "Terrenos que alquilas a terceros para realizar cultivos",
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
    - Considera la diferencia entre hectáreas propias y arrendadas para maximizar tu rentabilidad
    - Evalúa estrategias de rotación de cultivos para un análisis más completo
    """)
    
    st.subheader("Contacto y Soporte")
    st.markdown("""
    Si tienes preguntas o sugerencias, por favor contacta al desarrollador o al equipo de soporte.
    """)

# Agregar información en el pie de página
st.markdown("---")
st.markdown("© 2025 Calculadora de Márgenes Agrícolas | Desarrollado con Streamlit")
