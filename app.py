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
considerando costos directos y características específicas de cada producción.
""")

# Datos de ejemplo basados en la tabla proporcionada
datos_cultivos = {
    "Variable": ["Superficie Ha", "Rendimiento tn", "USD/tn", "Ingreso Bruto / ha", 
                "Total costos directos / ha", "Margen Bruto / ha", "Margen Directo / ha"],
    "Soja 1ra": [1199, 3.2, 290, 939, 279, 296, 137],
    "Maíz": [1015, 7.7, 168, 1290, 456, 200, 40],
    "Trigo": [346, 3.6, 198, 722, 312, 98, 19],
    "Soja 2da": [309, 2.1, 290, 621, 205, 158, 78],
    "Maíz 2da": [37, 6.5, 168, 1097, 369, 203, 123],
    "Girasol": [101, 2.4, 293, 714, 286, 182, 23]
}

# Crear DataFrame
df_comparativo = pd.DataFrame(datos_cultivos)

# Crear pestañas
tab1, tab2, tab3 = st.tabs(["Tabla Comparativa", "Calculadora", "Ayuda"])

# Pestaña 1: Tabla Comparativa
with tab1:
    st.header("Tabla Comparativa de Cultivos")
    st.dataframe(df_comparativo, hide_index=True, use_container_width=True)
    
    # Extraer datos para gráficos
    cultivos = list(df_comparativo.columns)[1:]  # Excluir la columna "Variable"
    
    # Buscar índices de las variables que nos interesan
    idx_margen_bruto = df_comparativo[df_comparativo["Variable"] == "Margen Bruto / ha"].index[0]
    idx_margen_directo = df_comparativo[df_comparativo["Variable"] == "Margen Directo / ha"].index[0]
    
    # Crear datos para gráficos
    margen_bruto = [df_comparativo.iloc[idx_margen_bruto][cultivo] for cultivo in cultivos]
    margen_directo = [df_comparativo.iloc[idx_margen_directo][cultivo] for cultivo in cultivos]
    
    # Gráfico de Margen Bruto
    st.subheader("Margen Bruto por Cultivo (USD/ha)")
    chart_data_bruto = pd.DataFrame({"Margen Bruto": margen_bruto}, index=cultivos)
    st.bar_chart(chart_data_bruto)
    
    # Gráfico de Margen Directo
    st.subheader("Margen Directo por Cultivo (USD/ha)")
    chart_data_directo = pd.DataFrame({"Margen Directo": margen_directo}, index=cultivos)
    st.bar_chart(chart_data_directo)

# Pestaña 2: Calculadora
with tab2:
    st.header("Calculadora de Márgenes")
    
    # Selección de cultivo
    cultivo = st.selectbox("Seleccionar cultivo", cultivos)
    
    # Crear columnas para la entrada de datos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Datos básicos")
        # Obtener índices de las variables
        idx_superficie = df_comparativo[df_comparativo["Variable"] == "Superficie Ha"].index[0]
        idx_rendimiento = df_comparativo[df_comparativo["Variable"] == "Rendimiento tn"].index[0]
        idx_precio = df_comparativo[df_comparativo["Variable"] == "USD/tn"].index[0]
        
        # Valores por defecto del cultivo seleccionado
        superficie_default = df_comparativo.iloc[idx_superficie][cultivo]
        rendimiento_default = df_comparativo.iloc[idx_rendimiento][cultivo]
        precio_default = df_comparativo.iloc[idx_precio][cultivo]
        
        # Campos de entrada
        superficie = st.number_input("Superficie (Ha)", min_value=0, value=int(superficie_default), step=1)
        rendimiento = st.number_input("Rendimiento (tn/ha)", min_value=0.0, value=float(rendimiento_default), step=0.1, format="%.1f")
        precio = st.number_input("Precio (USD/tn)", min_value=0, value=int(precio_default), step=1)
    
    with col2:
        st.subheader("Costos")
        # Cálculo del costo directo total (simplificado para esta versión)
        idx_costos_directos = df_comparativo[df_comparativo["Variable"] == "Total costos directos / ha"].index[0]
        costos_default = df_comparativo.iloc[idx_costos_directos][cultivo]
        
        # Desglose de costos (valores de ejemplo para esta versión simplificada)
        costo_labranza = st.number_input("Costo Labranza (USD/ha)", min_value=0, value=int(costos_default * 0.2), step=1)
        costo_semilla = st.number_input("Costo Semilla (USD/ha)", min_value=0, value=int(costos_default * 0.3), step=1)
        costo_agroquimicos = st.number_input("Costo Agroquímicos (USD/ha)", min_value=0, value=int(costos_default * 0.3), step=1)
        costo_fertilizantes = st.number_input("Costo Fertilizantes (USD/ha)", min_value=0, value=int(costos_default * 0.2), step=1)
        
        # Sumar todos los costos
        total_costos_directos = costo_labranza + costo_semilla + costo_agroquimicos + costo_fertilizantes
    
    with col3:
        st.subheader("Otros gastos")
        # Cálculo de otros gastos (valores de ejemplo)
        costos_comercializacion = st.number_input("Gastos Comercialización (USD/ha)", min_value=0, value=int(precio_default * rendimiento_default * 0.1), step=1)
        costos_estructura = st.number_input("Estructura (USD/ha)", min_value=0, value=50, step=1)
        costos_cosecha = st.number_input("Cosecha (USD/ha)", min_value=0, value=90, step=1)
        
        # Arrendamiento (simplificado)
        tipo_arrendamiento = st.radio("Tipo de Arrendamiento", ["Dólares por hectárea", "Quintales de soja"])
        
        if tipo_arrendamiento == "Dólares por hectárea":
            valor_arrendamiento = st.number_input("Arrendamiento (USD/ha)", min_value=0, value=160, step=10)
            arrendamiento = valor_arrendamiento
        else:
            qq_arrendamiento = st.number_input("Arrendamiento (qq soja/ha)", min_value=0, value=15, step=1)
            precio_qq_soja = st.number_input("Precio quintal soja (USD/qq)", min_value=0, value=29, step=1)
            arrendamiento = qq_arrendamiento * precio_qq_soja
            st.info(f"Arrendamiento equivalente: USD {arrendamiento}/ha")
    
    # Cálculos
    # Ingresos
    ingreso_bruto_ha = rendimiento * precio
    ingreso_bruto_total = ingreso_bruto_ha * superficie
    
    # Costos
    costos_directos_total = total_costos_directos * superficie
    gastos_comercializacion_total = costos_comercializacion * superficie
    estructura_total = costos_estructura * superficie
    cosecha_total = costos_cosecha * superficie
    
    # Factor de ocupación (simplificado)
    factor_ocupacion = 0.5 if "2da" in cultivo else 1.0
    arrendamiento_ajustado = arrendamiento * factor_ocupacion
    
    # Calcular proporción de hectáreas arrendadas (simplificado para esta versión)
    proporcion_arrendadas = 0.3  # Asumimos 30% de hectáreas arrendadas
    arrendamiento_total = arrendamiento_ajustado * superficie * proporcion_arrendadas
    
    # Margen bruto
    margen_bruto_ha = ingreso_bruto_ha - total_costos_directos - costos_comercializacion - costos_estructura - costos_cosecha
    margen_bruto_total = margen_bruto_ha * superficie
    
    # Margen directo (considerando arrendamiento)
    margen_directo_ha = margen_bruto_ha - (arrendamiento_ajustado * proporcion_arrendadas)
    margen_directo_total = margen_directo_ha * superficie
    
    # Retorno sobre costos
    costos_totales_ha = total_costos_directos + costos_comercializacion + costos_estructura + costos_cosecha + (arrendamiento_ajustado * proporcion_arrendadas)
    retorno_costos = (margen_directo_ha / costos_totales_ha) * 100 if costos_totales_ha > 0 else 0
    
    # Mostrar resultados
    st.header("Resultados")
    
    # Mostrar tabla de resultados
    results_data = {
        "Concepto": [
            "Superficie", "Rendimiento", "Precio", 
            "Ingreso Bruto/ha", "Ingreso Bruto Total",
            "Costos Directos/ha", "Costos Directos Total",
            "Gastos Comercialización/ha", "Gastos Comercialización Total",
            "Estructura/ha", "Estructura Total",
            "Cosecha/ha", "Cosecha Total",
            "Arrendamiento/ha (ajustado)", "Arrendamiento Total",
            "Margen Bruto/ha", "Margen Bruto Total",
            "Margen Directo/ha", "Margen Directo Total",
            "Retorno sobre costos (%)"
        ],
        "Valor": [
            f"{superficie} ha", f"{rendimiento} tn/ha", f"USD {precio}/tn",
            f"USD {round(ingreso_bruto_ha)}/ha", f"USD {round(ingreso_bruto_total)}",
            f"USD {round(total_costos_directos)}/ha", f"USD {round(costos_directos_total)}",
            f"USD {round(costos_comercializacion)}/ha", f"USD {round(gastos_comercializacion_total)}",
            f"USD {round(costos_estructura)}/ha", f"USD {round(estructura_total)}",
            f"USD {round(costos_cosecha)}/ha", f"USD {round(cosecha_total)}",
            f"USD {round(arrendamiento_ajustado * proporcion_arrendadas)}/ha", f"USD {round(arrendamiento_total)}",
            f"USD {round(margen_bruto_ha)}/ha", f"USD {round(margen_bruto_total)}",
            f"USD {round(margen_directo_ha)}/ha", f"USD {round(margen_directo_total)}",
            f"{round(retorno_costos, 1)}%"
        ]
    }
    
    results_df = pd.DataFrame(results_data)
    st.dataframe(results_df, hide_index=True, use_container_width=True)
    
    # Visualizaciones
    st.subheader("Visualizaciones")
    
    # Gráfico de distribución de ingresos y costos
    labels = ['Costos Directos', 'Comercialización', 'Estructura', 'Cosecha', 'Arrendamiento', 'Margen Directo']
    values = [
        total_costos_directos, 
        costos_comercializacion, 
        costos_estructura, 
        costos_cosecha, 
        arrendamiento_ajustado * proporcion_arrendadas,
        margen_directo_ha
    ]
    
    # Crear dataframe para el gráfico
    chart_data = pd.DataFrame({
        'Categoría': labels,
        'USD/ha': values
    })
    
    st.bar_chart(chart_data.set_index('Categoría'))

# Pestaña 3: Ayuda
with tab3:
    st.header("Ayuda y Documentación")
    
    st.subheader("¿Cómo usar esta aplicación?")
    st.markdown("""
    Esta aplicación te permite comparar los márgenes de diferentes cultivos. Sigue estos pasos:
    
    1. En la pestaña **Tabla Comparativa**:
       - Observa los datos comparativos de todos los cultivos
       - Analiza gráficamente los márgenes brutos y directos
    
    2. En la pestaña **Calculadora**:
       - Selecciona el cultivo que deseas evaluar
       - Ajusta los valores de superficie, rendimiento y precio
       - Modifica los costos directos, gastos de comercialización, estructura y cosecha
       - Configura el tipo de arrendamiento (por hectárea o en quintales de soja)
       - Observa los resultados y las visualizaciones
    """)
    
    st.subheader("Glosario de Términos")
    terms = {
        "Margen Bruto": "Ingreso Bruto - Costos Directos - Gastos Comercialización - Estructura - Cosecha",
        "Margen Directo": "Margen Bruto - Arrendamiento",
        "Factor de Ocupación": "Ajuste para cultivos de segunda (que ocupan el campo durante medio año)",
        "Retorno sobre costos": "Porcentaje que representa el Margen Directo respecto a los costos totales"
    }
    
    for term, definition in terms.items():
        st.markdown(f"**{term}**: {definition}")
    
    st.subheader("Próximas funcionalidades")
    st.markdown("""
    En próximas versiones, planeamos añadir:
    
    - Configuración detallada de hectáreas propias y arrendadas
    - Flujo de caja mensual
    - Análisis de riesgo y sensibilidad
    - Comparativa de escenarios
    """)

# Pie de página
st.markdown("---")
st.markdown("© 2025 Calculadora de Márgenes Agrícolas | Desarrollado para Ingenieros Agrónomos")
