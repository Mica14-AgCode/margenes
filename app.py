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

# Función para cargar y procesar la tabla de fletes
def cargar_tabla_fletes():
    # Definición de la tabla de fletes según la imagen proporcionada
    # NOTA: La tabla indica $/TN, los valores están en pesos argentinos por tonelada
    # El punto en estos valores es separador de miles, no decimal
    data = """KM,$/TN,KM,$/TN,KM,$/TN,KM,$/TN,KM,$/TN,KM,$/TN
5,7429,105,21465,205,32492,305,44598,405,54765,520,62717
10,7429,110,21976,210,33051,310,45100,410,55135,540,63617
15,8334,115,22487,215,33617,315,45603,415,55505,560,64494
20,9331,120,23001,220,34186,320,46108,420,55876,580,65354
25,10242,125,23523,225,34762,325,46613,425,56245,600,66192
30,11267,130,24048,230,35344,330,47120,430,56615,620,67011
35,11926,135,24576,235,35930,335,47631,435,56986,640,67811
40,12609,140,25109,240,36519,340,48143,440,57356,660,68593
45,13314,145,25649,245,37117,345,48654,445,57728,680,69358
50,14048,150,26190,250,37718,350,49167,450,58095,700,70106
55,14644,155,26742,255,38325,355,49685,455,58466,725,71509
60,15253,160,27293,260,38942,360,50201,460,58836,750,72886
65,15881,165,27853,265,39560,365,50718,465,59206,775,74241
70,16526,170,28418,270,40187,370,51240,470,59574,800,75573
75,17197,175,28988,275,40821,375,51762,475,59946,850,77598
80,17889,180,29565,280,41460,380,52283,480,60316,900,79556
85,18609,185,30147,285,42110,385,52809,485,60684,950,81444
90,19359,190,30738,290,42763,390,53337,490,61054,1000,83271
95,20141,195,31332,295,43426,395,57865,495,61426,1050,85462
100,20962,200,31935,300,44096,400,54393,500,61794,1100,87551"""
    
    # Procesamos la tabla para convertirla en un DataFrame
    # Primero construimos las listas de KM y $/TN
    filas = data.strip().split('\n')
    
    # Primero procesamos el encabezado para saber cuántas columnas hay
    encabezado = filas[0].split(',')
    num_columnas = len(encabezado) // 2
    
    # Inicializamos listas para KM y tarifas
    km_valores = []
    tarifa_valores = []
    
    # Procesamos cada fila para extraer los pares KM, $/TN
    for fila in filas[1:]:  # Saltamos la fila de encabezado
        valores = fila.split(',')
        for i in range(num_columnas):
            idx_km = i * 2
            idx_tarifa = idx_km + 1
            if idx_tarifa < len(valores):  # Verificamos que no nos pasemos del límite
                try:
                    km = float(valores[idx_km])
                    tarifa = float(valores[idx_tarifa])
                    km_valores.append(km)
                    tarifa_valores.append(tarifa)
                except (ValueError, IndexError):
                    pass  # Ignoramos valores que no podemos convertir
    
    # Creamos el DataFrame
    df_fletes = pd.DataFrame({
        'KM': km_valores,
        'Tarifa_$/TN': tarifa_valores
    })
    
    # Ordenamos por KM para asegurar que la interpolación funcione correctamente
    df_fletes = df_fletes.sort_values('KM')
    
    return df_fletes

# Función para calcular el costo del flete basado en la distancia
def calcular_costo_flete(km, df_fletes, recargo=0):
    """
    Calcula el costo del flete por tonelada para una distancia dada.
    Interpola valores para distancias que no están exactamente en la tabla.
    
    Parámetros:
    - km: Distancia en kilómetros
    - df_fletes: DataFrame con la tabla de fletes
    - recargo: Porcentaje de recargo adicional (ej. girasol 20%)
    
    Retorna:
    - Costo del flete por tonelada en pesos argentinos
    """
    try:
        # Verificamos límites
        if km <= df_fletes['KM'].min():
            costo = df_fletes.loc[df_fletes['KM'] == df_fletes['KM'].min(), 'Tarifa_$/TN'].values[0]
        elif km >= df_fletes['KM'].max():
            costo = df_fletes.loc[df_fletes['KM'] == df_fletes['KM'].max(), 'Tarifa_$/TN'].values[0]
        else:
            # Buscar los valores cercanos en la tabla
            # Encontrar el punto de la tabla más cercano por debajo
            valor_inferior = df_fletes[df_fletes['KM'] <= km]['KM'].max()
            # Encontrar el punto de la tabla más cercano por encima
            valor_superior = df_fletes[df_fletes['KM'] >= km]['KM'].min()
            
            # Verificar que los valores no sean idénticos para evitar división por cero
            if valor_superior == valor_inferior:
                costo = df_fletes.loc[df_fletes['KM'] == valor_superior, 'Tarifa_$/TN'].values[0]
            else:
                # Obtener los costos correspondientes
                costo_inferior = df_fletes.loc[df_fletes['KM'] == valor_inferior, 'Tarifa_$/TN'].values[0]
                costo_superior = df_fletes.loc[df_fletes['KM'] == valor_superior, 'Tarifa_$/TN'].values[0]
                
                # Interpolación lineal
                # (y - y1) / (x - x1) = (y2 - y1) / (x2 - x1)
                # y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
                costo = costo_inferior + (km - valor_inferior) * (costo_superior - costo_inferior) / (valor_superior - valor_inferior)
        
        # Aplicar recargo si corresponde
        if recargo > 0:
            costo = costo * (1 + recargo/100)
        
        return costo
    except Exception as e:
        # En caso de error, devolver un valor predeterminado y mostrar advertencia
        st.warning(f"Error al calcular el costo del flete: {str(e)}. Usando valor predeterminado de 30000.")
        return 30000.0  # Valor predeterminado en caso de error

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tabla Comparativa", "Calculadora", "Rotaciones", "Análisis de Sensibilidad", "Ayuda"])

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
    
    # Nueva sección: Costos de flete
    st.markdown("---")
    st.subheader("Costos de Flete")
    
    # Cargamos la tabla de fletes
    df_fletes = cargar_tabla_fletes()
    
    # Tipo de cálculo de flete
    tipo_flete = st.radio("Método de cálculo del flete", 
                        ["Tabla FADEEAC (por km)", "Ingreso manual ($/tn)", "Ingreso manual (USD/tn)"])
    
    # Contenedor para mostrar la tabla de referencia
    with st.expander("Ver tabla de referencia de fletes"):
        st.dataframe(df_fletes, hide_index=True)
        st.caption("Fuente: FADEEAC ABRIL 2025")
        st.caption("Recargos: girasol 20%, avena 10%, caminos de tierra 20%")
    
    # Variable para almacenar el costo de flete en USD/tn
    costo_flete_usd_tn = 0
    
    if tipo_flete == "Tabla FADEEAC (por km)":
        # División en columnas para mejor organización
        col1, col2 = st.columns(2)
        
        with col1:
            # Kilómetros de flete
            km_flete = st.number_input("Distancia (km)", min_value=1, max_value=1100, value=100, step=5)
            
            # Opción para personalizar por cultivo
            personalizar_cultivo = st.checkbox("Personalizar distancia por cultivo")
            
            if personalizar_cultivo:
                # Si se activa, creamos campos para cada cultivo
                st.subheader("Distancias por cultivo (km)")
                km_soja1ra = st.number_input("Soja 1ra", min_value=1, max_value=1100, value=km_flete, step=5)
                km_maiz = st.number_input("Maíz", min_value=1, max_value=1100, value=km_flete, step=5)
                km_trigo = st.number_input("Trigo", min_value=1, max_value=1100, value=km_flete, step=5)
                km_soja2da = st.number_input("Soja 2da", min_value=1, max_value=1100, value=km_flete, step=5)
                km_maiz2da = st.number_input("Maíz 2da", min_value=1, max_value=1100, value=km_flete, step=5) 
                km_maiztardio = st.number_input("Maíz Tardío", min_value=1, max_value=1100, value=km_flete, step=5)
                km_girasol = st.number_input("Girasol", min_value=1, max_value=1100, value=km_flete, step=5)
                
                # Creamos un diccionario para almacenar estos valores
                km_por_cultivo = {
                    "Soja 1ra": km_soja1ra,
                    "Maíz": km_maiz,
                    "Trigo": km_trigo,
                    "Soja 2da": km_soja2da,
                    "Maíz 2da": km_maiz2da,
                    "Maíz Tardío": km_maiztardio,
                    "Girasol": km_girasol
                }
                # Usar el valor específico para el cultivo seleccionado
                km_actual = km_por_cultivo[cultivo]
            else:
                # Si no se personaliza, usamos el mismo valor para todos
                km_actual = km_flete
        
        with col2:
            # Aplicar recargos
            st.subheader("Recargos")
            aplicar_recargo_girasol = st.checkbox("Aplicar recargo girasol (20%)", value=True)
            aplicar_recargo_avena = st.checkbox("Aplicar recargo avena (10%)", value=False)
            aplicar_recargo_tierra = st.checkbox("Aplicar recargo caminos de tierra (20%)", value=False)
            
            # Tipo de cambio 
            tipo_cambio = st.number_input("Tipo de cambio ($/USD)", min_value=1.0, value=950.0, step=10.0)
            
            # Determinamos el recargo según el cultivo
            recargo_total = 0
            if aplicar_recargo_girasol and cultivo == "Girasol":
                recargo_total += 20
            if aplicar_recargo_avena and cultivo == "Avena":  # Por si se agrega avena en el futuro
                recargo_total += 10
            if aplicar_recargo_tierra:
                recargo_total += 20
            
            # Calculamos el costo
            costo_ars = calcular_costo_flete(km_actual, df_fletes, recargo_total)
            # Convertimos de pesos a dólares usando el tipo de cambio
            costo_flete_usd_tn = costo_ars / tipo_cambio
            
            # Mostrar resultado
            st.success(f"Costo de flete calculado: $ {int(costo_ars)}/tn (USD {costo_flete_usd_tn:.2f}/tn)")
            
            # Información adicional
            st.info(f"""
            Distancia: {km_actual} km
            {"Con recargo de " + str(recargo_total) + "%" if recargo_total > 0 else "Sin recargos"}
            Tipo de cambio: ${tipo_cambio}/USD
            """)
    
    elif tipo_flete == "Ingreso manual ($/tn)":
        col1, col2 = st.columns(2)
        
        with col1:
            flete_ars = st.number_input("Costo de flete ($/tn)", min_value=0.0, value=30000.0, step=1000.0)
            tipo_cambio = st.number_input("Tipo de cambio ($/USD)", min_value=1.0, value=950.0, step=10.0)
            # Convertimos de pesos a dólares
            costo_flete_usd_tn = flete_ars / tipo_cambio
            
            st.info(f"Equivalente a USD {costo_flete_usd_tn:.2f}/tn")
    
    else:  # Ingreso manual (USD/tn)
        costo_flete_usd_tn = st.number_input("Costo de flete (USD/tn)", min_value=0.0, value=31.5, step=0.5)
        tipo_cambio = st.number_input("Tipo de cambio ($/USD)", min_value=1.0, value=950.0, step=10.0) 
        # Convertimos de dólares a pesos
        flete_ars = costo_flete_usd_tn * tipo_cambio
        
        st.info(f"Equivalente a $ {flete_ars:.2f}/tn")
    
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
    
    # Costo de flete por hectárea y total
    # La tabla muestra valores en $/TN (pesos por tonelada)
    # Convertimos a USD/TN para usar en los cálculos
    costo_flete_ha = rendimiento * costo_flete_usd_tn
    costo_flete_total = costo_flete_ha * superficie
    
    # Margen bruto (ahora restando el flete)
    margen_bruto_ha = ingreso_bruto_ha - total_costos_directos - costos_comercializacion - costos_estructura - costos_cosecha - costo_flete_ha
    margen_bruto_total = margen_bruto_ha * superficie
    
    # Margen directo (considerando arrendamiento)
    margen_directo_ha = margen_bruto_ha - (arrendamiento_ajustado * proporcion_arrendadas)
    margen_directo_total = margen_directo_ha * superficie
    
    # Retorno sobre costos
    costos_totales_ha = total_costos_directos + costos_comercializacion + costos_estructura + costos_cosecha + costo_flete_ha + (arrendamiento_ajustado * proporcion_arrendadas)
    retorno_costos = (margen_directo_ha / costos_totales_ha) * 100 if costos_totales_ha > 0 else 0
    
    # Mostrar resultados
    st.markdown("---")
    st.header("Resultados")
    
    # Tabla de resultados simplificada, sin usar f-strings
    data = [
        ["Superficie", str(superficie) + " ha"],
        ["Rendimiento", str(rendimiento) + " tn/ha"],
        ["Precio", "USD " + str(precio) + "/tn"],
        ["Ingreso Bruto/ha", "USD " + str(round(ingreso_bruto_ha)) + "/ha"],
        ["Ingreso Bruto Total", "USD " + str(round(ingreso_bruto_total))],
        ["Costos Directos/ha", "USD " + str(round(total_costos_directos)) + "/ha"],
        ["Costos Directos Total", "USD " + str(round(costos_directos_total))],
        ["Gastos Comercialización/ha", "USD " + str(round(costos_comercializacion)) + "/ha"],
        ["Gastos Comercialización Total", "USD " + str(round(gastos_comercializacion_total))],
        ["Estructura/ha", "USD " + str(round(costos_estructura)) + "/ha"],
        ["Estructura Total", "USD " + str(round(estructura_total))],
        ["Cosecha/ha", "USD " + str(round(costos_cosecha)) + "/ha"],
        ["Cosecha Total", "USD " + str(round(cosecha_total))],
        ["Flete/ha", "USD " + str(int(costo_flete_ha)) + "/ha"],
        ["Flete Total", "USD " + str(int(costo_flete_total))],
        ["Arrendamiento/ha (ajustado)", "USD " + str(round(arrendamiento_ajustado * proporcion_arrendadas)) + "/ha"],
        ["Arrendamiento Total", "USD " + str(round(arrendamiento_total))],
        ["Margen Bruto/ha", "USD " + str(round(margen_bruto_ha)) + "/ha"],
        ["Margen Bruto Total", "USD " + str(round(margen_bruto_total))],
        ["Margen Directo/ha", "USD " + str(round(margen_directo_ha)) + "/ha"],
        ["Margen Directo Total", "USD " + str(round(margen_directo_total))],
        ["Retorno sobre costos (%)", str(round(retorno_costos, 1)) + "%"]
    ]
    
    # Crear DataFrame para la tabla
    df_resultados = pd.DataFrame(data, columns=["Concepto", "Valor"])
    
    # Mostrar la tabla
    st.dataframe(df_resultados, hide_index=True, use_container_width=True)
    
    # Visualizaciones
    st.subheader("Visualizaciones")
    
    # Gráfico de distribución de ingresos y costos usando st.bar_chart
    chart_data = pd.DataFrame({
        'USD/ha': [
            total_costos_directos, 
            costos_comercializacion, 
            costos_estructura, 
            costos_cosecha,
            costo_flete_ha,
            arrendamiento_ajustado * proporcion_arrendadas,
            margen_directo_ha
        ]
    }, index=['Costos Directos', 'Comercialización', 'Estructura', 'Cosecha', 'Flete', 'Arrendamiento', 'Margen Directo'])
    
    st.bar_chart(chart_data)

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
                "{:.1f}%".format((total_trigo/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0),
                "{:.1f}%".format((total_soja2da/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0),
                "{:.1f}%".format((total_maiz2da/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0),
                "{:.1f}%".format((total_soja1ra/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0),
                "{:.1f}%".format((total_maiz/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0),
                "{:.1f}%".format((total_maiz_tardio/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0),
                "{:.1f}%".format((total_girasol/total_superficie_efectiva*100) if total_superficie_efectiva > 0 else 0)
            ]
        }
        
        df_superficie = pd.DataFrame(superficie_cultivos)
        st.dataframe(df_superficie, hide_index=True, use_container_width=True)
        
        # Mostrar totales
        st.info("Superficie física total: " + str(total_superficie) + " ha")
        st.info("Superficie efectiva (incluyendo doble cultivo): " + str(total_superficie_efectiva) + " ha")
        intensidad_uso = (total_superficie_efectiva/total_superficie*100) if total_superficie > 0 else 0
        st.info("Intensidad de uso: {:.1f}%".format(intensidad_uso))
    
    # Gráficos de rotación usando herramientas nativas de Streamlit
    st.subheader("Visualización de Rotaciones")
    
    # Visualización por cultivo
    st.subheader("Distribución por Cultivo")
    
    # Datos para gráfico
    cultivos_labels = ["Trigo", "Soja 2da", "Maíz 2da", "Soja 1ra", "Maíz", "Maíz Tardío", "Girasol"]
    cultivos_values = [total_trigo, total_soja2da, total_maiz2da, total_soja1ra, total_maiz, total_maiz_tardio, total_girasol]
    
    # Filtrar solo valores mayores que cero
    filtered_labels = []
    filtered_values = []
    for label, value in zip(cultivos_labels, cultivos_values):
        if value > 0:
            filtered_labels.append(label)
            filtered_values.append(value)
    
    # Crear dataframe para el gráfico de barras de Streamlit
    if filtered_values:  # Solo si hay valores mayores que cero
        chart_data_cultivos = pd.DataFrame({
            'Superficie': filtered_values
        }, index=filtered_labels)
        
        st.bar_chart(chart_data_cultivos)
    else:
        st.warning("No hay cultivos con superficie para visualizar.")
    
    # Visualización por rotación
    st.subheader("Distribución por Tipo de Rotación")
    
    # Datos para gráfico
    rotaciones_labels = ["Trigo + Soja 2da", "Trigo + Maíz 2da", "Soja 1ra", "Maíz", "Maíz Tardío", "Girasol"]
    rotaciones_values = [trigo_soja2da, trigo_maiz2da, soja1ra_sola, maiz_solo, maiz_tardio, girasol_solo]
    
    # Filtrar solo valores mayores que cero
    filtered_labels = []
    filtered_values = []
    for label, value in zip(rotaciones_labels, rotaciones_values):
        if value > 0:
            filtered_labels.append(label)
            filtered_values.append(value)
    
    # Crear dataframe para el gráfico de barras de Streamlit
    if filtered_values:  # Solo si hay valores mayores que cero
        chart_data_rotaciones = pd.DataFrame({
            'Superficie': filtered_values
        }, index=filtered_labels)
        
        st.bar_chart(chart_data_rotaciones)
    else:
        st.warning("No hay rotaciones con superficie para visualizar.")
    
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
    sum_superficie = sum(df_economia_rotaciones["Superficie (ha)"])
    sum_margen_bruto_total = sum(df_economia_rotaciones["Margen Bruto Total (USD)"])
    sum_margen_directo_total = sum(df_economia_rotaciones["Margen Directo Total (USD)"])
    
    # Calcular promedios ponderados por hectárea
    prom_margen_bruto_ha = sum_margen_bruto_total / sum_superficie if sum_superficie > 0 else 0
    prom_margen_directo_ha = sum_margen_directo_total / sum_superficie if sum_superficie > 0 else 0
    
    total_row = pd.DataFrame([{
        "Rotación": "TOTAL",
        "Superficie (ha)": sum_superficie,
        "Margen Bruto (USD/ha)": prom_margen_bruto_ha,
        "Margen Directo (USD/ha)": prom_margen_directo_ha,
        "Margen Bruto Total (USD)": sum_margen_bruto_total,
        "Margen Directo Total (USD)": sum_margen_directo_total
    }])
    
    # Añadir fila de totales al dataframe
    df_economia_rotaciones = pd.concat([df_economia_rotaciones, total_row], ignore_index=True)
    
    # Mostrar tabla económica
    st.dataframe(df_economia_rotaciones, hide_index=True, use_container_width=True)
    
    # Gráfico comparativo de márgenes por rotación
    st.subheader("Comparativa de Márgenes por Rotación")
    
    # Excluir la fila de totales
    df_grafico = df_economia_rotaciones.iloc[:-1].copy()
    
    # Filtrar rotaciones con superficie > 0
    df_grafico = df_grafico[df_grafico["Superficie (ha)"] > 0]
    
    # Crear dataframe para gráfico
    if not df_grafico.empty:
        chart_data = pd.DataFrame({
            "Margen Bruto (USD/ha)": df_grafico["Margen Bruto (USD/ha)"],
            "Margen Directo (USD/ha)": df_grafico["Margen Directo (USD/ha)"]
        }, index=df_grafico["Rotación"])
        
        st.bar_chart(chart_data)
        
        # Obtener la rotación más rentable
        idx_max = df_grafico["Margen Directo (USD/ha)"].idxmax()
        mejor_rotacion = df_grafico.loc[idx_max, "Rotación"]
        margen_maximo = df_grafico.loc[idx_max, "Margen Directo (USD/ha)"]
        
        # Mostrar el mensaje de la rotación más rentable
        st.info("Conclusión: La rotación más rentable por hectárea es **" + mejor_rotacion + 
                "** con un margen directo de **USD " + str(round(margen_maximo, 2)) + "/ha**.")
    else:
        st.warning("No hay rotaciones con superficie para analizar.")
    
    # Análisis de riesgo (versión simple)
    st.subheader("Variabilidad de rendimientos por cultivo")
    st.markdown("""
    En esta sección podemos evaluar cómo diferentes variaciones en el rendimiento 
    (clima, manejo, etc.) afectan el resultado económico.
    """)
    
    # Índice para rendimiento
    idx_rendimiento = df_comparativo[df_comparativo["Variable"] == "Rendimiento tn"].index[0]
    
    # Escenarios de rendimiento
    # Para simplificar, asumimos que el rendimiento puede variar ±20%
    rendimientos = {
        "Cultivo": cultivos_labels,
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

# Pestaña 4: Análisis de Sensibilidad
with tab4:
    st.header("Análisis de Sensibilidad")
    st.markdown("""
    En esta sección puedes evaluar cómo diferentes cambios en variables clave 
    (rendimiento, precio, flete) afectan el resultado económico de los diferentes cultivos.
    """)
    
    # Selección de cultivo para el análisis
    cultivo_sensibilidad = st.selectbox("Seleccionar cultivo para análisis", cultivos, key="cultivo_sensibilidad")
    
    # Obtener índices de las variables
    idx_superficie = df_comparativo[df_comparativo["Variable"] == "Superficie Ha"].index[0]
    idx_rendimiento = df_comparativo[df_comparativo["Variable"] == "Rendimiento tn"].index[0]
    idx_precio = df_comparativo[df_comparativo["Variable"] == "USD/tn"].index[0]
    idx_costos_directos = df_comparativo[df_comparativo["Variable"] == "Total costos directos / ha"].index[0]
    
    # Valores base del cultivo seleccionado
    rendimiento_base = df_comparativo.iloc[idx_rendimiento][cultivo_sensibilidad]
    precio_base = df_comparativo.iloc[idx_precio][cultivo_sensibilidad]
    costos_directos_base = df_comparativo.iloc[idx_costos_directos][cultivo_sensibilidad]
    
    # Crear dos columnas para los parámetros de sensibilidad
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Variaciones en Rendimiento")
        
        # Rango de variación para rendimientos
        rango_rendimiento = st.slider(
            "Rango de variación para rendimiento (%)", 
            min_value=5, 
            max_value=50, 
            value=20, 
            step=5,
            help="Define el porcentaje de variación (hacia arriba y abajo) para el análisis de sensibilidad del rendimiento."
        )
        
        # Calcular los escenarios de rendimiento
        rendimiento_bajo = rendimiento_base * (1 - rango_rendimiento/100)
        rendimiento_alto = rendimiento_base * (1 + rango_rendimiento/100)
        
        # Mostrar tabla de escenarios de rendimiento
        st.write(f"**Escenarios de rendimiento para {cultivo_sensibilidad}:**")
        escenarios_rendimiento = {
            "Escenario": ["Rendimiento Bajo", "Rendimiento Base", "Rendimiento Alto"],
            "Valor (tn/ha)": [rendimiento_bajo, rendimiento_base, rendimiento_alto],
            "Variación (%)": [f"-{rango_rendimiento}%", "0%", f"+{rango_rendimiento}%"]
        }
        
        df_escenarios_rendimiento = pd.DataFrame(escenarios_rendimiento)
        st.dataframe(df_escenarios_rendimiento, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("Variaciones en Flete")
        
        # Rango de variación para flete
        rango_flete = st.slider(
            "Rango de variación para costo de flete (%)", 
            min_value=5, 
            max_value=50, 
            value=20, 
            step=5,
            help="Define el porcentaje de variación (hacia arriba y abajo) para el análisis de sensibilidad del flete."
        )
        
        # Valor base del flete (usando un valor predeterminado si no está definido)
        flete_base_usd = 30  # Valor predeterminado en USD por tonelada
        try:
            # Intentamos cargar la tabla de fletes
            df_fletes_analisis = cargar_tabla_fletes()
            # Usamos un valor promedio de la tabla como base
            flete_base_pesos = df_fletes_analisis['Tarifa_$/TN'].median()
            # Convertir a USD (asumiendo tipo de cambio de 950)
            flete_base_usd = flete_base_pesos / 950
        except:
            # Si hay algún error, mantenemos el valor predeterminado
            pass
        
        # Calcular los escenarios de flete
        flete_bajo = flete_base_usd * (1 - rango_flete/100)
        flete_alto = flete_base_usd * (1 + rango_flete/100)
        
        # Mostrar tabla de escenarios de flete
        st.write(f"**Escenarios de costo de flete:**")
        escenarios_flete = {
            "Escenario": ["Flete Bajo", "Flete Base", "Flete Alto"],
            "Valor (USD/tn)": [flete_bajo, flete_base_usd, flete_alto],
            "Variación (%)": [f"-{rango_flete}%", "0%", f"+{rango_flete}%"]
        }
        
        df_escenarios_flete = pd.DataFrame(escenarios_flete)
        st.dataframe(df_escenarios_flete, hide_index=True, use_container_width=True)
    
    # Función para calcular el margen directo en diferentes escenarios
    def calcular_margen_directo(rendimiento, precio, costos_directos, flete, otros_costos=140, arrendamiento=160*0.3):
        """
        Calcula el margen directo por hectárea para los diferentes escenarios.
        
        Parámetros:
        - rendimiento: Rendimiento en tn/ha
        - precio: Precio en USD/tn
        - costos_directos: Costos directos en USD/ha
        - flete: Costo de flete en USD/tn
        - otros_costos: Otros costos (comercialización, estructura, cosecha) en USD/ha
        - arrendamiento: Costo de arrendamiento en USD/ha (ajustado por proporción)
        
        Retorna:
        - Margen directo en USD/ha
        """
        costo_flete_ha = rendimiento * flete
        ingreso_bruto = rendimiento * precio
        margen_bruto = ingreso_bruto - costos_directos - otros_costos - costo_flete_ha
        margen_directo = margen_bruto - arrendamiento
        return margen_directo
    
    # Matriz de escenarios - combinaciones de rendimiento y flete
    st.subheader("Matriz de Escenarios: Margen Directo (USD/ha)")
    
    # Crear matriz de escenarios
    escenarios_matriz = {
        "Escenario": ["Rendimiento Bajo", "Rendimiento Base", "Rendimiento Alto"],
        "Flete Bajo": [
            calcular_margen_directo(rendimiento_bajo, precio_base, costos_directos_base, flete_bajo),
            calcular_margen_directo(rendimiento_base, precio_base, costos_directos_base, flete_bajo),
            calcular_margen_directo(rendimiento_alto, precio_base, costos_directos_base, flete_bajo)
        ],
        "Flete Base": [
            calcular_margen_directo(rendimiento_bajo, precio_base, costos_directos_base, flete_base_usd),
            calcular_margen_directo(rendimiento_base, precio_base, costos_directos_base, flete_base_usd),
            calcular_margen_directo(rendimiento_alto, precio_base, costos_directos_base, flete_base_usd)
        ],
        "Flete Alto": [
            calcular_margen_directo(rendimiento_bajo, precio_base, costos_directos_base, flete_alto),
            calcular_margen_directo(rendimiento_base, precio_base, costos_directos_base, flete_alto),
            calcular_margen_directo(rendimiento_alto, precio_base, costos_directos_base, flete_alto)
        ]
    }
    
    df_matriz = pd.DataFrame(escenarios_matriz)
    st.dataframe(df_matriz, hide_index=True, use_container_width=True)
    
    # Análisis gráfico
    st.subheader("Análisis Gráfico de Sensibilidad")
    
    # Datos para el gráfico
    base_margin = calcular_margen_directo(rendimiento_base, precio_base, costos_directos_base, flete_base_usd)
    
    # Impacto de variaciones en rendimiento (con flete base)
    rend_variations = [-30, -20, -10, 0, 10, 20, 30]
    margins_by_rend = [
        calcular_margen_directo(rendimiento_base * (1 + var/100), precio_base, costos_directos_base, flete_base_usd)
        for var in rend_variations
    ]
    
    # Impacto de variaciones en flete (con rendimiento base)
    flete_variations = [-30, -20, -10, 0, 10, 20, 30]
    margins_by_flete = [
        calcular_margen_directo(rendimiento_base, precio_base, costos_directos_base, flete_base_usd * (1 + var/100))
        for var in flete_variations
    ]
    
    # Crear DataFrame para gráfico
    df_rend_chart = pd.DataFrame({
        "Variación (%)": rend_variations,
        "Margen Directo (USD/ha)": margins_by_rend
    }).set_index("Variación (%)")
    
    df_flete_chart = pd.DataFrame({
        "Variación (%)": flete_variations,
        "Margen Directo (USD/ha)": margins_by_flete
    }).set_index("Variación (%)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Impacto del Rendimiento")
        st.line_chart(df_rend_chart)
        
        # Calcular la elasticidad (cambio porcentual en margen / cambio porcentual en rendimiento)
        rend_elasticity = ((margins_by_rend[5] - margins_by_rend[1]) / base_margin) / 0.4  # cambio de -20% a +20%
        st.info(f"Elasticidad del margen respecto al rendimiento: {rend_elasticity:.2f}")
        st.caption("Una elasticidad mayor que 1 indica alta sensibilidad del margen ante cambios en el rendimiento.")
    
    with col2:
        st.subheader("Impacto del Flete")
        st.line_chart(df_flete_chart)
        
        # Calcular la elasticidad (cambio porcentual en margen / cambio porcentual en flete)
        # Tomamos el valor absoluto porque la relación es inversa
        flete_elasticity = abs((margins_by_flete[5] - margins_by_flete[1]) / base_margin) / 0.4  # cambio de -20% a +20%
        st.info(f"Elasticidad del margen respecto al flete: {flete_elasticity:.2f}")
        st.caption("Una elasticidad cercana a 0 indica baja sensibilidad del margen ante cambios en el costo del flete.")
    
    # Tabla de análisis comparativo entre cultivos
    st.subheader("Análisis Comparativo de Sensibilidad entre Cultivos")
    
    # Calcular elasticidad para cada cultivo
    elasticidades = {
        "Cultivo": [],
        "Elasticidad Rendimiento": [],
        "Elasticidad Flete": [],
        "Relación Rendimiento/Flete": []  # Cuánto más importante es el rendimiento vs el flete
    }
    
    for cult in cultivos:
        # Obtener valores base para el cultivo
        rend = df_comparativo.iloc[idx_rendimiento][cult]
        prec = df_comparativo.iloc[idx_precio][cult]
        cost = df_comparativo.iloc[idx_costos_directos][cult]
        
        # Calcular elasticidades
        base_marg = calcular_margen_directo(rend, prec, cost, flete_base_usd)
        
        # Evitar división por cero
        if base_marg == 0:
            elast_rend = float('nan')
            elast_flete = float('nan')
            relation = float('nan')
        else:
            # Rendimiento +20%
            marg_rend_up = calcular_margen_directo(rend * 1.2, prec, cost, flete_base_usd)
            # Rendimiento -20%
            marg_rend_down = calcular_margen_directo(rend * 0.8, prec, cost, flete_base_usd)
            elast_rend = ((marg_rend_up - marg_rend_down) / base_marg) / 0.4
            
            # Flete +20%
            marg_flete_up = calcular_margen_directo(rend, prec, cost, flete_base_usd * 1.2)
            # Flete -20%
            marg_flete_down = calcular_margen_directo(rend, prec, cost, flete_base_usd * 0.8)
            elast_flete = abs((marg_flete_up - marg_flete_down) / base_marg) / 0.4
            
            # Relación entre elasticidades (cuán importante es el rendimiento vs el flete)
            relation = elast_rend / elast_flete if elast_flete != 0 else float('inf')
        
        elasticidades["Cultivo"].append(cult)
        elasticidades["Elasticidad Rendimiento"].append(elast_rend)
        elasticidades["Elasticidad Flete"].append(elast_flete)
        elasticidades["Relación Rendimiento/Flete"].append(relation)
    
    df_elasticidades = pd.DataFrame(elasticidades)
    st.dataframe(df_elasticidades, hide_index=True, use_container_width=True)
    
    # Interpretación del análisis
    st.subheader("Interpretación de Resultados")
    
    # Encontrar el cultivo más sensible al rendimiento
    if not df_elasticidades["Elasticidad Rendimiento"].isna().all():
        max_rend_idx = df_elasticidades["Elasticidad Rendimiento"].idxmax()
        cultivo_max_rend = df_elasticidades.iloc[max_rend_idx]["Cultivo"]
        elast_max_rend = df_elasticidades.iloc[max_rend_idx]["Elasticidad Rendimiento"]
        
        st.markdown(f"""
        - **Cultivo más sensible a cambios en rendimiento**: {cultivo_max_rend} (elasticidad: {elast_max_rend:.2f})
        - **Significado**: Un incremento del 10% en rendimiento de {cultivo_max_rend} aumentará su margen directo aproximadamente {elast_max_rend * 10:.1f}%
        """)
    
    # Encontrar el cultivo más sensible al flete
    if not df_elasticidades["Elasticidad Flete"].isna().all():
        max_flete_idx = df_elasticidades["Elasticidad Flete"].idxmax()
        cultivo_max_flete = df_elasticidades.iloc[max_flete_idx]["Cultivo"]
        elast_max_flete = df_elasticidades.iloc[max_flete_idx]["Elasticidad Flete"]
        
        st.markdown(f"""
        - **Cultivo más sensible a cambios en flete**: {cultivo_max_flete} (elasticidad: {elast_max_flete:.2f})
        - **Significado**: Un incremento del 10% en costo de flete de {cultivo_max_flete} reducirá su margen directo aproximadamente {elast_max_flete * 10:.1f}%
        """)
    
    # Recomendaciones basadas en el análisis
    st.subheader("Recomendaciones")
    
    st.markdown("""
    El análisis de sensibilidad permite tomar decisiones más informadas considerando el riesgo:
    
    1. **Para cultivos con alta elasticidad al rendimiento**:
       - Priorizar prácticas agronómicas que aseguren estabilidad de rendimiento
       - Considerar seguros agrícolas para proteger contra caídas de rendimiento
       - Invertir más en tecnología y manejo que maximice el potencial productivo
    
    2. **Para cultivos con alta elasticidad al flete**:
       - Negociar contratos de flete anticipados para fijar costos
       - Evaluar alternativas de comercialización más cercanas
       - Considerar almacenaje en campo para momentos de menor costo logístico
    
    3. **Para rotaciones**:
       - Buscar un balance entre cultivos de alta rentabilidad pero sensibles a variaciones
       - Incluir cultivos de mayor estabilidad para reducir el riesgo global
    """)

# Pestaña 5: Ayuda
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
       - Configura el costo del flete según distancia o monto fijo
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
        "Margen Bruto": "Ingreso Bruto - Costos Directos - Gastos Comercialización - Estructura - Cosecha - Flete",
        "Margen Directo": "Margen Bruto - Arrendamiento",
        "Factor de Ocupación": "Ajuste para cultivos de segunda (que ocupan el campo durante medio año)",
        "Retorno sobre costos": "Porcentaje que representa el Margen Directo respecto a los costos totales",
        "Cultivo de primera": "Ocupa el campo durante toda la temporada (ej. Soja 1ra, Maíz)",
        "Cultivo de segunda": "Se siembra después de la cosecha de otro cultivo (ej. Soja 2da después de Trigo)",
        "Intensidad de uso": "Relación entre la superficie efectiva (contando doble cultivo) y la superficie física total",
        "Recargos de flete": "Costos adicionales aplicados al flete según tipo de cultivo o condición de caminos"
    }
    
    for term, definition in terms.items():
        st.markdown("**" + term + "**: " + definition)
    
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
    
    # Nueva sección de ayuda para fletes
    st.subheader("Sobre los Costos de Flete")
    st.markdown("""
    El módulo de fletes te permite calcular el costo de transporte de granos de tres formas diferentes:
    
    1. **Tabla FADEEAC (por km)**: Calcula el costo basado en la distancia al centro de entrega.
       - Utiliza la tabla oficial de FADEEAC (Abril 2025)
       - Permite personalizar la distancia para cada cultivo
       - Aplica recargos específicos según tipo de cultivo (girasol 20%, avena 10%)
       - Opcional: aplica recargo por caminos de tierra (20%)
       
    2. **Ingreso manual en pesos**: Ingresas directamente el costo por tonelada en pesos argentinos.
       - Convierte automáticamente a dólares según el tipo de cambio
       
    3. **Ingreso manual en dólares**: Ingresas directamente el costo por tonelada en USD.
    
    Los costos de flete se aplican por tonelada y afectan directamente el margen, ya que se restan 
    del ingreso bruto. La calculadora multiplica automáticamente el flete por tonelada por el rendimiento 
    para obtener el costo por hectárea.
    """)

# Pie de página
st.markdown("---")
st.markdown("© 2025 Calculadora de Márgenes Agrícolas | Desarrollado para Ingenieros Agrónomos")

# Para ejecutar el programa, guarda este archivo como app.py y corre:
# streamlit run app.py
