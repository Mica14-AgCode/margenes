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
considerando costos directos, arrendamiento y características específicas de cada producción.
""")

# Inicializar variables en el estado de la sesión si no existen
if 'cultivos_data' not in st.session_state:
    # Inicializar con valores predeterminados basados en la tabla
    st.session_state.cultivos_data = {
        "Soja 1ra": {
            "superficie": 1199,
            "rendimiento": 3.2,
            "precio": 290,
            "costos": {
                "labranza": 108,
                "semilla": 56,
                "herbicidas": 59,
                "fungicidas": 12,
                "insecticidas": 12,
                "fertilizantes": 33,
                "comercializacion": 224,
                "estructura": 50,
                "cosecha": 90
            },
            "ocupacion": 1.0  # Ocupación completa
        },
        "Maíz": {
            "superficie": 1015,
            "rendimiento": 7.7,
            "precio": 168,
            "costos": {
                "labranza": 69,
                "semilla": 158,
                "herbicidas": 64,
                "fungicidas": 0,
                "insecticidas": 1,
                "fertilizantes": 165,
                "comercializacion": 488,
                "estructura": 50,
                "cosecha": 97
            },
            "ocupacion": 1.0  # Ocupación completa
        },
        "Trigo": {
            "superficie": 346,
            "rendimiento": 3.6,
            "precio": 198,
            "costos": {
                "labranza": 81,
                "semilla": 78,
                "herbicidas": 12,
                "fungicidas": 14,
                "insecticidas": 1,
                "fertilizantes": 125,
                "comercializacion": 201,
                "estructura": 25,
                "cosecha": 85
            },
            "ocupacion": 0.5  # Ocupa media temporada
        },
        "Soja 2da": {
            "superficie": 309,
            "rendimiento": 2.1,
            "precio": 290,
            "costos": {
                "labranza": 83,
                "semilla": 64,
                "herbicidas": 20,
                "fungicidas": 12,
                "insecticidas": 11,
                "fertilizantes": 16,
                "comercializacion": 148,
                "estructura": 25,
                "cosecha": 85
            },
            "ocupacion": 0.5  # Ocupa media temporada
        },
        "Maíz 2da": {
            "superficie": 37,
            "rendimiento": 6.5,
            "precio": 168,
            "costos": {
                "labranza": 83,
                "semilla": 126,
                "herbicidas": 20,
                "fungicidas": 0,
                "insecticidas": 0,
                "fertilizantes": 140,
                "comercializacion": 415,
                "estructura": 25,
                "cosecha": 85
            },
            "ocupacion": 0.5  # Ocupa media temporada
        },
        "Girasol": {
            "superficie": 101,
            "rendimiento": 2.4,
            "precio": 293,
            "costos": {
                "labranza": 77,
                "semilla": 66,
                "herbicidas": 59,
                "fungicidas": 0,
                "insecticidas": 3,
                "fertilizantes": 81,
                "comercializacion": 111,
                "estructura": 50,
                "cosecha": 85
            },
            "ocupacion": 1.0  # Ocupación completa
        }
    }

if 'hectareas_config' not in st.session_state:
    st.session_state.hectareas_config = {
        "propias": 1926,  # Estimado basado en la tabla
        "arrendadas": 1081,  # Estimado basado en la tabla
        "arrendamiento_tipo": "quintales",  # "quintales" o "dolares"
        "arrendamiento_quintales": 14,  # Valor en quintales de soja por hectárea
        "arrendamiento_dolares": 160,  # Valor en dólares por hectárea
        "precio_quintal_soja": 29  # Precio del quintal de soja (1/10 del precio por tonelada)
    }

# Crear pestañas
tab1, tab2, tab3, tab4 = st.tabs(["Análisis Comparativo", "Configuración de Cultivos", "Configuración de Hectáreas", "Flujo de Caja"])

# Pestaña 3: Configuración de Hectáreas
with tab3:
    st.header("Configuración de Hectáreas y Arrendamiento")
    st.markdown("""
    Aquí puedes configurar la cantidad de hectáreas propias y arrendadas, así como el tipo y valor del arrendamiento.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Hectáreas")
        # Hectáreas propias y arrendadas
        hectareas_propias = st.number_input(
            "Hectáreas propias totales", 
            min_value=0, 
            value=st.session_state.hectareas_config["propias"],
            step=1
        )
        
        hectareas_arrendadas = st.number_input(
            "Hectáreas arrendadas totales", 
            min_value=0, 
            value=st.session_state.hectareas_config["arrendadas"],
            step=1
        )
        
        total_hectareas = hectareas_propias + hectareas_arrendadas
        st.info(f"Total hectáreas: {total_hectareas}")
    
    with col2:
        st.subheader("Configuración de Arrendamiento")
        
        # Tipo de arrendamiento
        arrendamiento_tipo = st.radio(
            "Tipo de arrendamiento",
            ["Quintales de soja", "Dólares por hectárea"],
            index=0 if st.session_state.hectareas_config["arrendamiento_tipo"] == "quintales" else 1
        )
        
        # Configuración según tipo seleccionado
        if arrendamiento_tipo == "Quintales de soja":
            arrendamiento_quintales = st.number_input(
                "Arrendamiento (qq soja/ha)", 
                min_value=0, 
                value=st.session_state.hectareas_config["arrendamiento_quintales"],
                step=1
            )
            
            precio_quintal_soja = st.number_input(
                "Precio del quintal de soja (USD/qq)", 
                min_value=0, 
                value=st.session_state.hectareas_config["precio_quintal_soja"],
                step=1
            )
            
            # Calcular el equivalente en dólares
            arrendamiento_dolares = arrendamiento_quintales * precio_quintal_soja
            st.info(f"Equivalente en dólares: USD {arrendamiento_dolares}/ha")
            
            # Actualizar valores
            st.session_state.hectareas_config["arrendamiento_tipo"] = "quintales"
            st.session_state.hectareas_config["arrendamiento_quintales"] = arrendamiento_quintales
            st.session_state.hectareas_config["precio_quintal_soja"] = precio_quintal_soja
            st.session_state.hectareas_config["arrendamiento_dolares"] = arrendamiento_dolares
            
        else:
            arrendamiento_dolares = st.number_input(
                "Arrendamiento (USD/ha)", 
                min_value=0, 
                value=st.session_state.hectareas_config["arrendamiento_dolares"],
                step=10
            )
            
            precio_quintal_soja = st.number_input(
                "Precio del quintal de soja (USD/qq) [Para referencia]", 
                min_value=0, 
                value=st.session_state.hectareas_config["precio_quintal_soja"],
                step=1
            )
            
            # Calcular el equivalente en quintales
            if precio_quintal_soja > 0:
                arrendamiento_quintales = round(arrendamiento_dolares / precio_quintal_soja, 1)
                st.info(f"Equivalente en quintales: {arrendamiento_quintales} qq soja/ha")
            else:
                arrendamiento_quintales = 0
                st.warning("No se puede calcular el equivalente en quintales (precio del quintal es 0)")
            
            # Actualizar valores
            st.session_state.hectareas_config["arrendamiento_tipo"] = "dolares"
            st.session_state.hectareas_config["arrendamiento_dolares"] = arrendamiento_dolares
            st.session_state.hectareas_config["precio_quintal_soja"] = precio_quintal_soja
            st.session_state.hectareas_config["arrendamiento_quintales"] = arrendamiento_quintales
    
    # Actualizar hectáreas en la sesión
    st.session_state.hectareas_config["propias"] = hectareas_propias
    st.session_state.hectareas_config["arrendadas"] = hectareas_arrendadas
    
    # Botón para actualizar la distribución de hectáreas por cultivo
    if st.button("Actualizar distribución de hectáreas por cultivo"):
        # Calculamos el porcentaje que representa cada cultivo del total
        total_superficie_actual = sum(cultivo["superficie"] for cultivo in st.session_state.cultivos_data.values())
        
        if total_superficie_actual > 0:
            # Distribuir nuevas hectáreas manteniendo las proporciones actuales
            for cultivo_nombre, cultivo_data in st.session_state.cultivos_data.items():
                porcentaje = cultivo_data["superficie"] / total_superficie_actual
                nueva_superficie = round(porcentaje * total_hectareas)
                st.session_state.cultivos_data[cultivo_nombre]["superficie"] = nueva_superficie
            
            st.success("Distribución de hectáreas actualizada manteniendo las proporciones actuales")
        else:
            st.error("No hay hectáreas asignadas a cultivos para redistribuir")
    
    # Mostrar asignación actual de hectáreas por cultivo
    st.subheader("Asignación actual de hectáreas por cultivo")
    
    hectareas_data = {
        "Cultivo": [],
        "Hectáreas": [],
        "% del Total": []
    }
    
    total_superficie_actual = sum(cultivo["superficie"] for cultivo in st.session_state.cultivos_data.values())
    
    for cultivo, datos in st.session_state.cultivos_data.items():
        hectareas_data["Cultivo"].append(cultivo)
        hectareas_data["Hectáreas"].append(datos["superficie"])
        
        if total_superficie_actual > 0:
            porcentaje = (datos["superficie"] / total_superficie_actual) * 100
        else:
            porcentaje = 0
            
        hectareas_data["% del Total"].append(f"{porcentaje:.1f}%")
    
    # Añadir fila de totales
    hectareas_data["Cultivo"].append("TOTAL")
    hectareas_data["Hectáreas"].append(total_superficie_actual)
    hectareas_data["% del Total"].append("100.0%")
    
    # Convertir a dataframe y mostrar
    df_hectareas = pd.DataFrame(hectareas_data)
    st.dataframe(df_hectareas, hide_index=True, use_container_width=True)
    
    # Visualización
    chart_data = pd.DataFrame({
        "Hectáreas": hectareas_data["Hectáreas"][:-1],  # Excluir la fila TOTAL
        "Cultivo": hectareas_data["Cultivo"][:-1]  # Excluir la fila TOTAL
    })
    
    st.bar_chart(chart_data.set_index("Cultivo"))

# Pestaña 2: Configuración de Cultivos
with tab2:
    st.header("Configuración de Cultivos")
    st.markdown("""
    Aquí puedes configurar los parámetros específicos de cada cultivo: rendimiento, precio y costos asociados.
    """)
    
    # Seleccionar cultivo para configurar
    cultivo_seleccionado = st.selectbox(
        "Seleccionar cultivo para configurar",
        list(st.session_state.cultivos_data.keys())
    )
    
    # Organizar en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Datos básicos")
        
        # Superficie
        superficie = st.number_input(
            "Superficie (ha)",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["superficie"],
            step=1,
            key=f"superficie_{cultivo_seleccionado}"
        )
        
        # Factor de ocupación para cultivos de segunda
        ocupacion = st.selectbox(
            "Factor de ocupación",
            [("Temporada completa (1.0)", 1.0), ("Media temporada (0.5)", 0.5)],
            index=0 if st.session_state.cultivos_data[cultivo_seleccionado]["ocupacion"] == 1.0 else 1,
            format_func=lambda x: x[0],
            key=f"ocupacion_{cultivo_seleccionado}"
        )
        
        # Rendimiento
        rendimiento = st.number_input(
            "Rendimiento (tn/ha)",
            min_value=0.0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["rendimiento"],
            step=0.1,
            format="%.1f",
            key=f"rendimiento_{cultivo_seleccionado}"
        )
        
        # Precio
        precio = st.number_input(
            "Precio (USD/tn)",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["precio"],
            step=1,
            key=f"precio_{cultivo_seleccionado}"
        )
    
    with col2:
        st.subheader("Costos directos (USD/ha)")
        
        # Costos directos
        costo_labranza = st.number_input(
            "Costo Labranza",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["labranza"],
            step=1,
            key=f"labranza_{cultivo_seleccionado}"
        )
        
        costo_semilla = st.number_input(
            "Costo semilla, inoc. y trat.",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["semilla"],
            step=1,
            key=f"semilla_{cultivo_seleccionado}"
        )
        
        costo_herbicidas = st.number_input(
            "Costo herbicidas",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["herbicidas"],
            step=1,
            key=f"herbicidas_{cultivo_seleccionado}"
        )
        
        costo_fungicidas = st.number_input(
            "Costo fungicidas",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["fungicidas"],
            step=1,
            key=f"fungicidas_{cultivo_seleccionado}"
        )
        
        costo_insecticidas = st.number_input(
            "Costo insecticidas",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["insecticidas"],
            step=1,
            key=f"insecticidas_{cultivo_seleccionado}"
        )
        
        costo_fertilizantes = st.number_input(
            "Costo fertilizantes",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["fertilizantes"],
            step=1,
            key=f"fertilizantes_{cultivo_seleccionado}"
        )
    
    with col3:
        st.subheader("Otros costos (USD/ha)")
        
        # Otros costos
        gastos_comercializacion = st.number_input(
            "Gastos de comercialización",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["comercializacion"],
            step=1,
            key=f"comercializacion_{cultivo_seleccionado}"
        )
        
        costos_estructura = st.number_input(
            "Estructura",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["estructura"],
            step=1,
            key=f"estructura_{cultivo_seleccionado}"
        )
        
        costos_cosecha = st.number_input(
            "Cosecha",
            min_value=0,
            value=st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["cosecha"],
            step=1,
            key=f"cosecha_{cultivo_seleccionado}"
        )
    
    # Botón para guardar cambios
    if st.button("Guardar cambios para este cultivo"):
        st.session_state.cultivos_data[cultivo_seleccionado]["superficie"] = superficie
        st.session_state.cultivos_data[cultivo_seleccionado]["ocupacion"] = ocupacion[1]  # Extraer el valor numérico
        st.session_state.cultivos_data[cultivo_seleccionado]["rendimiento"] = rendimiento
        st.session_state.cultivos_data[cultivo_seleccionado]["precio"] = precio
        
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["labranza"] = costo_labranza
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["semilla"] = costo_semilla
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["herbicidas"] = costo_herbicidas
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["fungicidas"] = costo_fungicidas
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["insecticidas"] = costo_insecticidas
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["fertilizantes"] = costo_fertilizantes
        
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["comercializacion"] = gastos_comercializacion
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["estructura"] = costos_estructura
        st.session_state.cultivos_data[cultivo_seleccionado]["costos"]["cosecha"] = costos_cosecha
        
        st.success(f"Configuración guardada para {cultivo_seleccionado}")

# Pestaña 1: Análisis Comparativo
with tab1:
    st.header("Análisis Comparativo de Cultivos")
    
    # Cálculo de métricas para todos los cultivos
    metricas_cultivos = []
    
    # Valor del arrendamiento en USD/ha
    valor_arrendamiento = st.session_state.hectareas_config["arrendamiento_dolares"]
    
    for cultivo_nombre, cultivo_data in st.session_state.cultivos_data.items():
        # Datos básicos
        superficie = cultivo_data["superficie"]
        rendimiento = cultivo_data["rendimiento"]
        precio = cultivo_data["precio"]
        ocupacion = cultivo_data["ocupacion"]
        
        # Ingresos
        ingreso_bruto_ha = rendimiento * precio
        ingreso_bruto_total = ingreso_bruto_ha * superficie
        
        # Costos directos
        costos = cultivo_data["costos"]
        total_costos_directos_ha = (
            costos["labranza"] + 
            costos["semilla"] + 
            costos["herbicidas"] + 
            costos["fungicidas"] + 
            costos["insecticidas"] + 
            costos["fertilizantes"]
        )
        total_costos_directos = total_costos_directos_ha * superficie
        
        # Gastos de comercialización
        gastos_comercializacion_ha = costos["comercializacion"]
        gastos_comercializacion = gastos_comercializacion_ha * superficie
        
        # IIBB (asumimos 0 según la tabla)
        iibb_porcentaje = 3.5
        iibb_valor_ha = ingreso_bruto_ha * (iibb_porcentaje / 100)
        iibb_valor = iibb_valor_ha * superficie
        
        # Ingreso neto
        ingreso_neto_ha = ingreso_bruto_ha - gastos_comercializacion_ha - iibb_valor_ha
        ingreso_neto = ingreso_neto_ha * superficie
        
        # Costos de estructura y cosecha
        costos_estructura_ha = costos["estructura"]
        costos_estructura = costos_estructura_ha * superficie
        
        costos_cosecha_ha = costos["cosecha"]
        costos_cosecha = costos_cosecha_ha * superficie
        
        # Margen bruto
        margen_bruto_ha = ingreso_neto_ha - total_costos_directos_ha - costos_estructura_ha - costos_cosecha_ha
        margen_bruto = margen_bruto_ha * superficie
        
        # Arrendamiento (ponderado por factor de ocupación)
        arrendamiento_ha = valor_arrendamiento * ocupacion
        # El arrendamiento total se aplica solo a las hectáreas arrendadas (proporción de hectáreas arrendadas totales)
        proporcion_arrendadas = st.session_state.hectareas_config["arrendadas"] / (st.session_state.hectareas_config["propias"] + st.session_state.hectareas_config["arrendadas"]) if (st.session_state.hectareas_config["propias"] + st.session_state.hectareas_config["arrendadas"]) > 0 else 0
        arrendamiento = arrendamiento_ha * superficie * proporcion_arrendadas
        
        # Margen directo
        margen_directo_ha = margen_bruto_ha - (arrendamiento_ha * proporcion_arrendadas)
        margen_directo = margen_directo_ha * superficie
        
        # Retorno sobre costos (ROI)
        costos_totales_ha = total_costos_directos_ha + costos_estructura_ha + costos_cosecha_ha + (arrendamiento_ha * proporcion_arrendadas)
        retorno_costos = (margen_directo_ha / costos_totales_ha) * 100 if costos_totales_ha > 0 else 0
        
        # Margen por peso invertido
        margen_por_peso = margen_directo_ha / costos_totales_ha if costos_totales_ha > 0 else 0
        
        # Agregar a la lista de métricas
        metricas_cultivos.append({
            "Cultivo": cultivo_nombre,
            "Superficie Ha": superficie,
            "Rendimiento tn": rendimiento,
            "USD/tn": precio,
            "Ingreso Bruto / ha": round(ingreso_bruto_ha),
            "Costo Labranza": costos["labranza"],
            "Costo semilla, inoc y trat": costos["semilla"],
            "Costo herbicidas": costos["herbicidas"],
            "Costo fungicidas": costos["fungicidas"],
            "Costo insecticidas": costos["insecticidas"],
            "Costo fertilizantes": costos["fertilizantes"],
            "Total costos directos / ha": round(total_costos_directos_ha),
            "Gastos de comercialización": gastos_comercializacion_ha,
            f"IIBB {iibb_porcentaje}%": round(iibb_valor_ha),
            "Ingreso Neto / ha": round(ingreso_neto_ha),
            "Estructura": costos_estructura_ha,
            "Cosecha": costos_cosecha_ha,
            "Margen Bruto / ha": round(margen_bruto_ha),
            "Arrendamiento / ha": round(arrendamiento_ha * proporcion_arrendadas),
            "Margen Directo / ha": round(margen_directo_ha),
            "Retorno sobre costos (%)": round(retorno_costos, 1),
            "Margen por peso invertido": round(margen_por_peso, 2),
            "Factor de ocupación": ocupacion
        })
    
    # Crear DataFrame para la tabla comparativa
    df_comparativo = pd.DataFrame(metricas_cultivos)
    
    # Crear tabla pivoteada para mostrar como en la imagen de referencia
    cols_to_pivot = [
        "Superficie Ha", "Rendimiento tn", "USD/tn", 
        "Ingreso Bruto / ha", 
        "Costo Labranza", "Costo semilla, inoc y trat", "Costo herbicidas",
        "Costo fungicidas", "Costo insecticidas", "Costo fertilizantes",
        "Total costos directos / ha",
        "Ingreso Bruto / ha", "Gastos de comercialización", f"IIBB 3.5%",
        "Ingreso Neto / ha",
        "Estructura", "Cosecha",
        "Margen Bruto / ha",
        "Arrendamiento / ha",
        "Margen Directo / ha"
    ]
    
    # Crear tabla pivoteada
    df_pivot = df_comparativo.set_index("Cultivo")
    
    # Calcular totales
    totales = {
        "Superficie Ha": df_pivot["Superficie Ha"].sum(),
        "Ingreso Bruto / ha": (df_pivot["Ingreso Bruto / ha"] * df_pivot["Superficie Ha"]).sum() / df_pivot["Superficie Ha"].sum() if df_pivot["Superficie Ha"].sum() > 0 else 0,
        "Total costos directos / ha": (df_pivot["Total costos directos / ha"] * df_pivot["Superficie Ha"]).sum() / df_pivot["Superficie Ha"].sum() if df_pivot["Superficie Ha"].sum() > 0 else 0,
        "Margen Bruto / ha": (df_pivot["Margen Bruto / ha"] * df_pivot["Superficie Ha"]).sum() / df_pivot["Superficie Ha"].sum() if df_pivot["Superficie Ha"].sum() > 0 else 0,
        "Margen Directo / ha": (df_pivot["Margen Directo / ha"] * df_pivot["Superficie Ha"]).sum() / df_pivot["Superficie Ha"].sum() if df_pivot["Superficie Ha"].sum() > 0 else 0,
    }
    
    # Mostrar información sobre arrendamiento
    st.subheader("Información de Arrendamiento")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"Arrendamiento: {st.session_state.hectareas_config['arrendamiento_quintales']} qq soja/ha" if st.session_state.hectareas_config['arrendamiento_tipo'] == 'quintales' else f"Arrendamiento: USD {st.session_state.hectareas_config['arrendamiento_dolares']}/ha")
    with col2:
        st.info(f"Precio de referencia del quintal de soja: USD {st.session_state.hectareas_config['precio_quintal_soja']}/qq")
    with col3:
        st.info(f"Hectáreas propias: {st.session_state.hectareas_config['propias']} ha | Hectáreas arrendadas: {st.session_state.hectareas_config['arrendadas']} ha")
    
    # Mostrar tabla de resultados
    st.subheader("Tabla Comparativa de Cultivos")
    
    # Mostrar la tabla original como en la imagen
    df_display = df_pivot[cols_to_pivot].copy()
    
    # Estilizar la tabla para darle formato similar a la imagen
    def format_table(df):
        # Formatear números
        for col in df.columns:
            if "USD" in col or "Ingreso" in col or "Costo" in col or "Margen" in col or "Gastos" in col:
                df[col] = df[col].apply(lambda x: f"${x}" if isinstance(x, (int, float)) else x)
            elif "Rendimiento" in col:
                df[col] = df[col].apply(lambda x: f"{x:.1f}" if isinstance(x, (int, float)) else x)
        
        return df
    
    df_display = format_table(df_display)
    st.dataframe(df_display, use_container_width=True)
    
    # Mostrar métricas de rendimiento
    st.subheader("Métricas de Rendimiento por Cultivo")
    
    # Crear dataframe para métricas
    metricas_df = df_comparativo[["Cultivo", "Retorno sobre costos (%)", "Margen por peso invertido"]].copy()
    st.dataframe(metricas_df, hide_index=True, use_container_width=True)
    
    # Gráfico comparativo de márgenes
    st.subheader("Comparación de Márgenes por Cultivo")
    
    # Preparar datos para el gráfico
    margin_data = pd.DataFrame({
        "Cultivo": df_comparativo["Cultivo"],
        "Margen Bruto / ha": df_comparativo["Margen Bruto / ha"],
        "Margen Directo / ha": df_comparativo["Margen Directo / ha"]
    })
    
    # Mostrar gráfico
    margin_melted = pd.melt(margin_data, id_vars=["Cultivo"], var_name="Tipo de Margen", value_name="USD/ha")
    
    # Reenfocar el dataframe para st.bar_chart
    chart_data = pd.DataFrame({
        "Margen Bruto / ha": margin_data.set_index("Cultivo")["Margen Bruto / ha"],
        "Margen Directo / ha": margin_data.set_index("Cultivo")["Margen Directo / ha"]
    })
    
    st.bar_chart(chart_data)
    
    # Gráfico de Retorno sobre costos
    st.subheader("Retorno sobre Costos por Cultivo (%)")
    
    roi_data = pd.DataFrame({
        "Retorno (%)": df_comparativo["Retorno sobre costos (%)"],
        "Cultivo": df_comparativo["Cultivo"]
    }).set_index("Cultivo")
    
    st.bar_chart(roi_data)

# Pestaña 4: Flujo de Caja
with tab4:
    st.header("Flujo de Caja Proyectado")
    st.markdown("""
    Esta sección muestra un flujo de caja proyectado basado en los cultivos configurados, 
    considerando los momentos de siembra, tratamientos y cosecha.
    """)
    
    # Definir meses
    meses = ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May", "Jun"]
    
    # Crear un diccionario para almacenar flujos por mes
    flujo_mensual = {mes: {"ingresos": 0, "egresos": 0, "neto": 0} for mes in meses}
    
    # Definir la distribución estacional de costos e ingresos por cultivo
    # Esto es una simplificación, en un modelo real deberías tener datos más precisos
    estacionalidad = {
        "Soja 1ra": {
            # Mes: [% costos directos, % gastos comercialización, % ingresos]
            "Oct": [0.3, 0, 0],  # Siembra y parte de insumos
            "Nov": [0.2, 0, 0],  # Fertilización y control inicial
            "Dic": [0.1, 0, 0],  # Controles
            "Ene": [0.1, 0, 0],  # Controles
            "Feb": [0.1, 0, 0],  # Controles finales
            "Mar": [0.1, 0, 0],  # Preparación cosecha
            "Abr": [0.1, 0.5, 0.5],  # Cosecha y venta parcial
            "May": [0, 0.5, 0.5],  # Venta final
        },
        "Maíz": {
            # Mes: [% costos directos, % gastos comercialización, % ingresos]
            "Sep": [0.4, 0, 0],  # Siembra y mayor parte de insumos
            "Oct": [0.2, 0, 0],  # Fertilización
            "Nov": [0.1, 0, 0],  # Controles
            "Dic": [0.1, 0, 0],  # Controles
            "Ene": [0.1, 0, 0],  # Controles
            "Feb": [0.1, 0, 0],  # Preparación cosecha
            "Mar": [0, 0.3, 0.3],  # Cosecha y venta parcial
            "Abr": [0, 0.4, 0.4],  # Venta parcial
            "May": [0, 0.3, 0.3],  # Venta final
        },
        "Trigo": {
            # Mes: [% costos directos, % gastos comercialización, % ingresos]
            "Jun": [0.3, 0, 0],  # Siembra y parte de insumos
            "Jul": [0.3, 0, 0],  # Fertilización y control inicial
            "Ago": [0.2, 0, 0],  # Controles
            "Sep": [0.1, 0, 0],  # Controles
            "Oct": [0.1, 0, 0],  # Controles finales
            "Nov": [0, 0, 0],  # Preparación cosecha
            "Dic": [0, 0.7, 0.7],  # Cosecha y venta principal
            "Ene": [0, 0.3, 0.3],  # Venta final
        },
        "Soja 2da": {
            # Mes: [% costos directos, % gastos comercialización, % ingresos]
            "Dic": [0.4, 0, 0],  # Siembra y parte de insumos (después de trigo)
            "Ene": [0.2, 0, 0],  # Fertilización y control inicial
            "Feb": [0.2, 0, 0],  # Controles
            "Mar": [0.1, 0, 0],  # Controles
            "Abr": [0.1, 0, 0],  # Preparación cosecha
            "May": [0, 0.7, 0.7],  # Cosecha y venta principal
            "Jun": [0, 0.3, 0.3],  # Venta final
        },
        "Maíz 2da": {
            # Mes: [% costos directos, % gastos comercialización, % ingresos]
            "Dic": [0.4, 0, 0],  # Siembra y mayor parte de insumos (después de trigo)
            "Ene": [0.2, 0, 0],  # Fertilización
            "Feb": [0.2, 0, 0],  # Controles
            "Mar": [0.1, 0, 0],  # Controles
            "Abr": [0.1, 0, 0],  # Preparación cosecha
            "May": [0, 0.4, 0.4],  # Cosecha y venta parcial
            "Jun": [0, 0.6, 0.6],  # Venta final
        },
        "Girasol": {
            # Mes: [% costos directos, % gastos comercialización, % ingresos]
            "Sep": [0.4, 0, 0],  # Siembra y parte de insumos
            "Oct": [0.2, 0, 0],  # Fertilización y control inicial
            "Nov": [0.2, 0, 0],  # Controles
            "Dic": [0.1, 0, 0],  # Controles
            "Ene": [0.1, 0, 0],  # Controles finales
            "Feb": [0, 0.4, 0.4],  # Cosecha y venta parcial
            "Mar": [0, 0.6, 0.6],  # Venta final
        }
    }
    
    # Calcular flujos mensuales
    for cultivo_nombre, cultivo_data in st.session_state.cultivos_data.items():
        # Datos básicos
        superficie = cultivo_data["superficie"]
        rendimiento = cultivo_data["rendimiento"]
        precio = cultivo_data["precio"]
        
        # Calcular totales
        ingreso_total = rendimiento * precio * superficie
        
        # Costos directos
        costos = cultivo_data["costos"]
        costos_directos_total = (
            costos["labranza"] + 
            costos["semilla"] + 
            costos["herbicidas"] + 
            costos["fungicidas"] + 
            costos["insecticidas"] + 
            costos["fertilizantes"]
        ) * superficie
        
        # Gastos de comercialización
        comercializacion_total = costos["comercializacion"] * superficie
        
        # Estructura y cosecha (distribuimos uniformemente durante el año)
        estructura_mensual = (costos["estructura"] * superficie) / 12
        cosecha_total = costos["cosecha"] * superficie
        
        # Arrendamiento (se paga según el contrato, suponemos semestral)
        arrendamiento_ha = st.session_state.hectareas_config["arrendamiento_dolares"] * cultivo_data["ocupacion"]
        proporcion_arrendadas = st.session_state.hectareas_config["arrendadas"] / (st.session_state.hectareas_config["propias"] + st.session_state.hectareas_config["arrendadas"]) if (st.session_state.hectareas_config["propias"] + st.session_state.hectareas_config["arrendadas"]) > 0 else 0
        arrendamiento_total = arrendamiento_ha * superficie * proporcion_arrendadas
        
        # Distribuir según estacionalidad
        for mes, porcentajes in estacionalidad.get(cultivo_nombre, {}).items():
            # Costos directos
            flujo_mensual[mes]["egresos"] += costos_directos_total * porcentajes[0]
            
            # Gastos de comercialización
            flujo_mensual[mes]["egresos"] += comercializacion_total * porcentajes[1]
            
            # Ingresos
            flujo_mensual[mes]["ingresos"] += ingreso_total * porcentajes[2]
        
        # Distribuir cosecha según el mes de cosecha (simplificación)
        meses_cosecha = {
            "Soja 1ra": "Abr",
            "Maíz": "Mar",
            "Trigo": "Dic",
            "Soja 2da": "May",
            "Maíz 2da": "May",
            "Girasol": "Feb"
        }
        
        if cultivo_nombre in meses_cosecha:
            flujo_mensual[meses_cosecha[cultivo_nombre]]["egresos"] += cosecha_total
        
        # Distribuir estructura uniformemente
        for mes in meses:
            flujo_mensual[mes]["egresos"] += estructura_mensual
        
        # Arrendamiento (suponemos pagos semestrales en Julio y Enero)
        flujo_mensual["Jul"]["egresos"] += arrendamiento_total / 2
        flujo_mensual["Ene"]["egresos"] += arrendamiento_total / 2
    
    # Calcular flujo neto para cada mes
    for mes in meses:
        flujo_mensual[mes]["neto"] = flujo_mensual[mes]["ingresos"] - flujo_mensual[mes]["egresos"]
    
    # Crear dataframe para visualización
    flujo_df = pd.DataFrame({
        "Mes": meses,
        "Ingresos (USD)": [round(flujo_mensual[mes]["ingresos"]) for mes in meses],
        "Egresos (USD)": [round(flujo_mensual[mes]["egresos"]) for mes in meses],
        "Flujo Neto (USD)": [round(flujo_mensual[mes]["neto"]) for mes in meses]
    })
    
    # Mostrar tabla de flujo de caja
    st.dataframe(flujo_df, hide_index=True, use_container_width=True)
    
    # Gráfico de flujo de caja
    st.subheader("Flujo de Caja Mensual")
    
    # Reenfocar el dataframe para st.bar_chart
    chart_data = pd.DataFrame({
        "Ingresos": flujo_df.set_index("Mes")["Ingresos (USD)"],
        "Egresos": flujo_df.set_index("Mes")["Egresos (USD)"] * -1,  # Multiplicar por -1 para mostrar como negativo
        "Flujo Neto": flujo_df.set_index("Mes")["Flujo Neto (USD)"]
    })
    
    st.bar_chart(chart_data)
    
    # Resumen anual
    total_ingresos = sum(flujo_mensual[mes]["ingresos"] for mes in meses)
    total_egresos = sum(flujo_mensual[mes]["egresos"] for mes in meses)
    saldo_final = total_ingresos - total_egresos
    
    # Mostrar resumen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Ingresos Anuales", f"USD {round(total_ingresos):,}")
    with col2:
        st.metric("Total Egresos Anuales", f"USD {round(total_egresos):,}")
    with col3:
        st.metric("Resultado Anual", f"USD {round(saldo_final):,}", delta=f"{round(saldo_final/total_egresos*100, 1)}%" if total_egresos > 0 else "N/A")

# Agregar información en el pie de página
st.markdown("---")
st.markdown("© 2025 Calculadora de Márgenes Agrícolas | Desarrollado por un Ingeniero Agrónomo")
