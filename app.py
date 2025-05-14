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
    "Maíz Tardío": [120, 6.0, 168, 1008, 369, 180, 100],  # Agregamos Maíz Tardío
    "Girasol": [101, 2.4, 293, 714, 286, 182, 23]
}

# Crear DataFrame
df_comparativo = pd.DataFrame(datos_cultivos)

# Inicializar estado para rotaciones si no existe
if 'rotaciones' not in st.session_state:
    st.session_state.rotaciones = {
        'trigo_soja2da': 280,       # Trigo seguido de Soja 2da
        'trigo_maiz2da': 66,        # Trigo seguido de Maíz 2da
        'soja1ra_sola': 1199,       # Soja 1ra como único cultivo en el año
        'maiz_solo': 1015,          # Maíz como único cultivo en el año
        'maiz_tardio': 120,         # Maíz tardío
        'girasol_solo': 101         # Girasol como único cultivo en el año
    }

# Crear pestañas
tab1, tab2, tab3, tab4 = st.tabs(["Tabla Comparativa", "Calculadora", "Rotaciones", "Ayuda"])

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

# Pestaña 3: Rotaciones
with tab3:
    st.header("Análisis de Rotaciones")
    st.markdown("""
    En esta sección puedes analizar tus rotaciones de cultivos y su impacto económico.
    Recuerda que algunos cultivos como el trigo se complementan con cultivos de segunda
    ocupación como la soja 2da o el maíz 2da.
    """)
    
    # Crear columnas para editar rotaciones
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuración de Rotaciones")
        st.markdown("Define la cantidad de hectáreas para cada rotación:")
        
        # Trigo seguido de Soja 2da
        trigo_soja2da = st.number_input(
            "Trigo + Soja 2da (ha)",
            min_value=0,
            value=st.session_state.rotaciones['trigo_soja2da'],
            step=10
        )
        
        # Trigo seguido de Maíz 2da
        trigo_maiz2da = st.number_input(
            "Trigo + Maíz 2da (ha)",
            min_value=0,
            value=st.session_state.rotaciones['trigo_maiz2da'],
            step=10
        )
        
        # Soja 1ra como único cultivo
        soja1ra_sola = st.number_input(
            "Soja 1ra (ha)",
            min_value=0,
            value=st.session_state.rotaciones['soja1ra_sola'],
            step=10
        )
        
        # Maíz como único cultivo
        maiz_solo = st.number_input(
            "Maíz (ha)",
            min_value=0,
            value=st.session_state.rotaciones['maiz_solo'],
            step=10
        )
        
        # Maíz tardío
        maiz_tardio = st.number_input(
            "Maíz Tardío (ha)",
            min_value=0,
            value=st.session_state.rotaciones['maiz_tardio'],
            step=10
        )
        
        # Girasol como único cultivo
        girasol_solo = st.number_input(
            "Girasol (ha)",
            min_value=0,
            value=st.session_state.rotaciones['girasol_solo'],
            step=10
        )
        
        # Guardar valores en session_state
        if st.button("Actualizar Rotaciones"):
            st.session_state.rotaciones['trigo_soja2da'] = trigo_soja2da
            st.session_state.rotaciones['trigo_maiz2da'] = trigo_maiz2da
            st.session_state.rotaciones['soja1ra_sola'] = soja1ra_sola
            st.session_state.rotaciones['maiz_solo'] = maiz_solo
            st.session_state.rotaciones['maiz_tardio'] = maiz_tardio
            st.session_state.rotaciones['girasol_solo'] = girasol_solo
            st.success("Rotaciones actualizadas correctamente")
    
    # Calcular totales por cultivo
    total_trigo = trigo_soja2da + trigo_maiz2da
    total_soja2da = trigo_soja2da
    total_maiz2da = trigo_maiz2da
    total_soja1ra = soja1ra_sola
    total_maiz = maiz_solo
    total_maiz_tardio = maiz_tardio
    total_girasol = girasol_solo
    
    # Superficie total
    total_superficie = (
        total_trigo +     # Trigo (ya incluye la superficie que luego se usa para 2da)
        total_soja1ra +   # Soja 1ra
        total_maiz +      # Maíz
        total_maiz_tardio + # Maíz tardío
        total_girasol     # Girasol
    )
    
    # Superficie efectiva (contando doble ocupación)
    total_superficie_efectiva = (
        total_trigo +     # Trigo 
        total_soja2da +   # Soja 2da
        total_maiz2da +   # Maíz 2da
        total_soja1ra +   # Soja 1ra
        total_maiz +      # Maíz
        total_maiz_tardio + # Maíz tardío
        total_girasol     # Girasol
    )
    
    with col2:
        st.subheader("Resumen de Superficie por Cultivo")
        
        # Crear DataFrame de superficie por cultivo
        superficie_cultivos = {
            "Cultivo": ["Trigo", "Soja 2da", "Maíz 2da", "Soja 1ra", "Maíz", "Maíz Tardío", "Girasol"],
            "Superficie (ha)": [total_trigo, total_soja2da, total_maiz2da, total_soja1ra, total_maiz, total_maiz_tardio, total_girasol],
            "% del Total": [
                f"{(total_trigo/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0:.1f}%",
                f"{(total_soja2da/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0:.1f}%",
                f"{(total_maiz2da/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0:.1f}%",
                f"{(total_soja1ra/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0:.1f}%",
                f"{(total_maiz/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0:.1f}%",
                f"{(total_maiz_tardio/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0:.1f}%",
                f"{(total_girasol/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0:.1f}%"
            ]
        }
        
        df_superficie = pd.DataFrame(superficie_cultivos)
        st.dataframe(df_superficie, hide_index=True, use_container_width=True)
        
        # Mostrar totales
        st.info(f"Superficie física total: {total_superficie} ha")
        st.info(f"Superficie efectiva (incluyendo doble cultivo): {total_superficie_efectiva} ha")
        st.info(f"Intensidad de uso: {(total_superficie_efectiva/total_superficie*100) if total_superficie > 0 else 0:.1f}%")
    
    # Gráficos de rotación
    st.subheader("Visualización de Rotaciones")
    
    # Gráfico de torta de distribución de cultivos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución por Cultivo")
        
        # Datos para gráfico
        cultivos_labels = ["Trigo", "Soja 2da", "Maíz 2da", "Soja 1ra", "Maíz", "Maíz Tardío", "Girasol"]
        cultivos_values = [total_trigo, total_soja2da, total_maiz2da, total_soja1ra, total_maiz, total_maiz_tardio, total_girasol]
        
        # Filtrar solo valores mayores que cero
        filtered_labels = [label for label, value in zip(cultivos_labels, cultivos_values) if value > 0]
        filtered_values = [value for value in cultivos_values if value > 0]
        
        # Crear dataframe para pie chart
        chart_data = pd.DataFrame({
            'Cultivo': filtered_labels,
            'Superficie': filtered_values
        })
        
        # Streamlit no tiene gráfico de torta nativo, usamos matplotlib a través de st.pyplot
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(chart_data['Superficie'], labels=chart_data['Cultivo'], autopct='%1.1f%%')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Distribución de Superficie por Cultivo')
        
        st.pyplot(fig)
    
    with col2:
        st.subheader("Distribución por Tipo de Rotación")
        
        # Datos para gráfico
        rotaciones_labels = ["Trigo + Soja 2da", "Trigo + Maíz 2da", "Soja 1ra", "Maíz", "Maíz Tardío", "Girasol"]
        rotaciones_values = [trigo_soja2da, trigo_maiz2da, soja1ra_sola, maiz_solo, maiz_tardio, girasol_solo]
        
        # Filtrar solo valores mayores que cero
        filtered_labels = [label for label, value in zip(rotaciones_labels, rotaciones_values) if value > 0]
        filtered_values = [value for value in rotaciones_values if value > 0]
        
        # Crear dataframe para pie chart
        chart_data = pd.DataFrame({
            'Rotación': filtered_labels,
            'Superficie': filtered_values
        })
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(chart_data['Superficie'], labels=chart_data['Rotación'], autopct='%1.1f%%')
        ax.axis('equal')
        plt.title('Distribución por Tipo de Rotación')
        
        st.pyplot(fig)
    
    # Análisis económico de las rotaciones
    st.subheader("Análisis Económico de Rotaciones")
    
    # Índices para obtener márgenes
    idx_margen_bruto = df_comparativo[df_comparativo["Variable"] == "Margen Bruto / ha"].index[0]
    idx_margen_directo = df_comparativo[df_comparativo["Variable"] == "Margen Directo / ha"].index[0]
    
    # Obtener márgenes por cultivo
    margen_bruto_trigo = df_comparativo.iloc[idx_margen_bruto]["Trigo"]
    margen_bruto_soja2da = df_comparativo.iloc[idx_margen_bruto]["Soja 2da"]
    margen_bruto_maiz2da = df_comparativo.iloc[idx_margen_bruto]["Maíz 2da"]
    margen_bruto_soja1ra = df_comparativo.iloc[idx_margen_bruto]["Soja 1ra"]
    margen_bruto_maiz = df_comparativo.iloc[idx_margen_bruto]["Maíz"]
    margen_bruto_maiztardio = df_comparativo.iloc[idx_margen_bruto]["Maíz Tardío"]
    margen_bruto_girasol = df_comparativo.iloc[idx_margen_bruto]["Girasol"]
    
    margen_directo_trigo = df_comparativo.iloc[idx_margen_directo]["Trigo"]
    margen_directo_soja2da = df_comparativo.iloc[idx_margen_directo]["Soja 2da"]
    margen_directo_maiz2da = df_comparativo.iloc[idx_margen_directo]["Maíz 2da"]
    margen_directo_soja1ra = df_comparativo.iloc[idx_margen_directo]["Soja 1ra"]
    margen_directo_maiz = df_comparativo.iloc[idx_margen_directo]["Maíz"]
    margen_directo_maiztardio = df_comparativo.iloc[idx_margen_directo]["Maíz Tardío"]
    margen_directo_girasol = df_comparativo.iloc[idx_margen_directo]["Girasol"]
    
    # Calcular márgenes por rotación
    margen_bruto_trigosoja2da = margen_bruto_trigo + margen_bruto_soja2da
    margen_bruto_trigomaiz2da = margen_bruto_trigo + margen_bruto_maiz2da
    
    margen_directo_trigosoja2da = margen_directo_trigo + margen_directo_soja2da
    margen_directo_trigomaiz2da = margen_directo_trigo + margen_directo_maiz2da
    
    # Crear tabla de resultados económicos por rotación
    rotaciones_economico = {
        "Rotación": [
            "Trigo + Soja 2da", 
            "Trigo + Maíz 2da", 
            "Soja 1ra", 
            "Maíz", 
            "Maíz Tardío", 
            "Girasol"
        ],
        "Superficie (ha)": [
            trigo_soja2da,
            trigo_maiz2da,
            soja1ra_sola,
            maiz_solo,
            maiz_tardio,
            girasol_solo
        ],
        "Margen Bruto (USD/ha)": [
            margen_bruto_trigosoja2da,
            margen_bruto_trigomaiz2da,
            margen_bruto_soja1ra,
            margen_bruto_maiz,
            margen_bruto_maiztardio,
            margen_bruto_girasol
        ],
        "Margen Directo (USD/ha)": [
            margen_directo_trigosoja2da,
            margen_directo_trigomaiz2da,
            margen_directo_soja1ra,
            margen_directo_maiz,
            margen_directo_maiztardio,
            margen_directo_girasol
        ],
        "Margen Bruto Total (USD)": [
            margen_bruto_trigosoja2da * trigo_soja2da,
            margen_bruto_trigomaiz2da * trigo_maiz2da,
            margen_bruto_soja1ra * soja1ra_sola,
            margen_bruto_maiz * maiz_solo,
            margen_bruto_maiztardio * maiz_tardio,
            margen_bruto_girasol * girasol_solo
        ],
        "Margen Directo Total (USD)": [
            margen_directo_trigosoja2da * trigo_soja2da,
            margen_directo_trigomaiz2da * trigo_maiz2da,
            margen_directo_soja1ra * soja1ra_sola,
            margen_directo_maiz * maiz_solo,
            margen_directo_maiztardio * maiz_tardio,
            margen_directo_girasol * girasol_solo
        ]
    }
    
    df_economia_rotaciones = pd.DataFrame(rotaciones_economico)
    
    # Agregar fila de totales
    total_row = {
        "Rotación": "TOTAL",
        "Superficie (ha)": sum(df_economia_rotaciones["Superficie (ha)"]),
        "Margen Bruto (USD/ha)": sum(df_economia_rotaciones["Margen Bruto Total (USD)"]) / sum(df_economia_rotaciones["Superficie (ha)"]) if sum(df_economia_rotaciones["Superficie (ha)"]) > 0 else 0,
        "Margen Directo (USD/ha)": sum(df_economia_rotaciones["Margen Directo Total (USD)"]) / sum(df_economia_rotaciones["Superficie (ha)"]) if sum(df_economia_rotaciones["Superficie (ha)"]) > 0 else 0,
        "Margen Bruto Total (USD)": sum(df_economia_rotaciones["Margen Bruto Total (USD)"]),
        "Margen Directo Total (USD)": sum(df_economia_rotaciones["Margen Directo Total (USD)"])
    }
    
    # Añadir fila de totales al dataframe
    df_economia_rotaciones = pd.concat([df_economia_rotaciones, pd.DataFrame([total_row])], ignore_index=True)
    
    # Mostrar tabla económica
    st.dataframe(df_economia_rotaciones, hide_index=True, use_container_width=True)
    
    # Gráfico comparativo de márgenes por rotación
    st.subheader("Comparativa de Márgenes por Rotación")
    
    # Excluir la fila de totales
    df_grafico = df_economia_rotaciones[:-1].copy()
    
    # Filtrar rotaciones con superficie > 0
    df_grafico = df_grafico[df_grafico["Superficie (ha)"] > 0]
    
    # Crear dataframe para gráfico
    chart_data = pd.DataFrame({
        "Margen Bruto (USD/ha)": df_grafico["Margen Bruto (USD/ha)"],
        "Margen Directo (USD/ha)": df_grafico["Margen Directo (USD/ha)"]
    }, index=df_grafico["Rotación"])
    
    st.bar_chart(chart_data)
    
    # Análisis de riesgo (versión simple)
    st.subheader("Variabilidad de rendimientos por cultivo")
    st.markdown("""
    En esta sección podemos evaluar cómo diferentes variaciones en el rendimiento 
    (clima, manejo, etc.) afectan el resultado económico.
    """)
    
    # Escenarios de rendimiento
    # Para simplificar, asumimos que el rendimiento puede variar ±20%
    rendimientos = {
        "Cultivo": ["Trigo", "Soja 2da", "Maíz 2da", "Soja 1ra", "Maíz", "Maíz Tardío", "Girasol"],
        "Rendimiento Base (tn/ha)": [
            df_comparativo.iloc[idx_rendimiento]["Trigo"],
            df_comparativo.iloc[idx_rendimiento]["Soja 2da"],
            df_comparativo.iloc[idx_rendimiento]["Maíz 2da"],
            df_comparativo.iloc[idx_rendimiento]["Soja 1ra"],
            df_comparativo.iloc[idx_rendimiento]["Maíz"],
            df_comparativo.iloc[idx_rendimiento]["Maíz Tardío"],
            df_comparativo.iloc[idx_rendimiento]["Girasol"]
        ],
        "Rinde Bajo (-20%)": [
            df_comparativo.iloc[idx_rendimiento]["Trigo"] * 0.8,
            df_comparativo.iloc[idx_rendimiento]["Soja 2da"] * 0.8,
            df_comparativo.iloc[idx_rendimiento]["Maíz 2da"] * 0.8,
            df_comparativo.iloc[idx_rendimiento]["Soja 1ra"] * 0.8,
            df_comparativo.iloc[idx_rendimiento]["Maíz"] * 0.8,
            df_comparativo.iloc[idx_rendimiento]["Maíz Tardío"] * 0.8,
            df_comparativo.iloc[idx_rendimiento]["Girasol"] * 0.8
        ],
        "Rinde Alto (+20%)": [
            df_comparativo.iloc[idx_rendimiento]["Trigo"] * 1.2,
            df_comparativo.iloc[idx_rendimiento]["Soja 2da"] * 1.2,
            df_comparativo.iloc[idx_rendimiento]["Maíz 2da"] * 1.2,
            df_comparativo.iloc[idx_rendimiento]["Soja 1ra"] * 1.2,
            df_comparativo.iloc[idx_rendimiento]["Maíz"] * 1.2,
            df_comparativo.iloc[idx_rendimiento]["Maíz Tardío"] * 1.2,
            df_comparativo.iloc[idx_rendimiento]["Girasol"] * 1.2
        ]
    }
    
    df_rendimientos = pd.DataFrame(rendimientos)
    st.dataframe(df_rendimientos, hide_index=True, use_container_width=True)
    
    # Mostrar un mensaje final
    st.info(f"""
    Conclusión: La rotación más rentable por hectárea es 
    **{df_grafico.loc[df_grafico['Margen Directo (USD/ha)'].idxmax(), 'Rotación']}** 
    con un margen directo de 
    **USD {df_grafico['Margen Directo (USD/ha)'].max():.2f}/ha**.
    """)

# Pestaña 4: Ayuda
with tab4:
    st.header("Ayuda y Documentación")
    
    st.subheader("¿Cómo usar esta aplicación?")
    st.markdown("""
    Esta aplicación te permite comparar los márgenes de diferentes cultivos y planificar rotaciones. Sigue estos pasos:
    
    1. En la pestaña **Tabla Comparativa**:
       - Observa los datos comparativos de todos los cultivos
       - Analiza gráficamente los márgenes brutos y directos
    
    2. En la pestaña **Calculadora**:
       - Selecciona el cultivo que deseas evaluar
       - Ajusta los valores de superficie, rendimiento y precio
       - Modifica los costos directos, gastos de comercialización, estructura y cosecha
       - Configura el tipo de arrendamiento (por hectárea o en quintales de soja)
       - Observa los resultados y las visualizaciones
       
    3. En la pestaña **Rotaciones**:
       - Configura la cantidad de hectáreas para cada rotación
       - Observa la distribución de superficie por cultivo
       - Analiza los márgenes económicos por rotación
       - Compara la rentabilidad de diferentes esquemas de rotación
    """)
    
    st.subheader("Glosario de Términos")
    terms = {
        "Margen Bruto": "Ingreso Bruto - Costos Directos - Gastos Comercialización - Estructura - Cosecha",
        "Margen Directo": "Margen Bruto - Arrendamiento",
        "Factor de Ocupación": "Ajuste para cultivos de segunda (que ocupan el campo durante medio año)",
        "Retorno sobre costos": "Porcentaje que representa el Margen Directo respecto a los costos totales",
        "Cultivo de primera": "Ocupa el campo durante toda la temporada (ej. Soja 1ra, Maíz)",
        "Cultivo de segunda": "Se siembra después de la cosecha de otro cultivo (ej. Soja 2da después de Trigo)",
        "Intensidad de uso": "Relación entre la superficie efectiva (contando doble cultivo) y la superficie física total"
    }
    
    for term, definition in terms.items():
        st.markdown(f"**{term}**: {definition}")
    
    st.subheader("Sobre las Rotaciones")
    st.markdown("""
    Las rotaciones de cultivos son fundamentales para la sustentabilidad del sistema agrícola:
    
    - **Beneficios agronómicos**: Mejora la fertilidad del suelo, reduce problemas de malezas, plagas y enfermedades.
    - **Beneficios económicos**: Diversifica riesgos, optimiza el uso de la tierra, reduce costos de insumos.
    - **Esquemas comunes**: 
      - Trigo seguido de Soja 2da
      - Trigo seguido de Maíz 2da
      - Maíz - Soja 1ra (alternancia anual)
    
    La elección de la rotación depende de diversos factores como el tipo de suelo, régimen de lluvias, 
    capacidad operativa, disponibilidad de maquinaria y consideraciones económicas.
    """)

# Pie de página
st.markdown("---")
st.markdown("© 2025 Calculadora de Márgenes Agrícolas | Desarrollado para Ingenieros Agrónomos")
