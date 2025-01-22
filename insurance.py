import streamlit as st
import pandas as pd
import plotly.express as px

# Colores BBVA
BBVA_COLORS = {
    'blue': '#004481',
    'aqua': '#2dcccd',
    'navy': '#072146',
    'coral': '#ff7e67',
    'sky': '#5bbeff',
    'white': '#ffffff'
}

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Accidentes Automovilísticos",
    page_icon="🚗",
    layout="wide"
)

# Funciones de utilidad
def limpiar_nombre_columna(nombre):
    return nombre.replace(" (Absoluto)", "")

def cargar_datos():
    # Cargar los archivos Excel
    causas_df = pd.read_excel('accidentes_causa_inegi.xlsx')
    clases_df = pd.read_excel('accidentes_clase_inegi.xlsx')
    tipos_df = pd.read_excel('accidentes_tipo.xlsx')
    victimas_df = pd.read_excel('victimas_inegi.xlsx')
    vmrc_df = pd.read_excel('vmrc.xlsx')

    # Limpiar nombres de columnas
    for df in [causas_df, clases_df, tipos_df, victimas_df]:
        df.columns = [limpiar_nombre_columna(col) for col in df.columns]

    return causas_df, clases_df, tipos_df, victimas_df, vmrc_df

try:
    # Cargar datos
    causas_df, clases_df, tipos_df, victimas_df, vmrc_df = cargar_datos()

    # Título principal
    st.title("📊 Dashboard de Análisis de Accidentes Automovilísticos")

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_eventos = causas_df[(causas_df['Entidad'] == 'Nacional') & 
                                (causas_df['Variable'] == 'Total de eventos (Absoluto)')]['2023'].iloc[0]
        st.metric("Total de Eventos (2023)", f"{total_eventos:,.0f}")

    with col2:
        total_fallecidos = victimas_df[(victimas_df['Entidad'] == 'Nacional') & 
                                     (victimas_df['Variable'] == 'Total de víctimas muertas (Absoluto)')]['2023'].iloc[0]
        st.metric("Total de Víctimas Fatales (2023)", f"{total_fallecidos:,.0f}")

    with col3:
        total_heridos = victimas_df[(victimas_df['Entidad'] == 'Nacional') & 
                                  (victimas_df['Variable'] == 'Total de víctimas heridas (Absoluto)')]['2023'].iloc[0]
        st.metric("Total de Heridos (2023)", f"{total_heridos:,.0f}")

    with col4:
        eventos_fatales = clases_df[(clases_df['Entidad'] == 'Nacional') & 
                                  (clases_df['Variable'] == 'Fatal (Absoluto)')]['2023'].iloc[0]
        st.metric("Accidentes Fatales (2023)", f"{eventos_fatales:,.0f}")

    # Tabs para diferentes análisis
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Tendencias", "🗺️ Análisis por Estado", "📊 Causas y Tipos", "💡 Frases Tractoras", "📘 Glosario"])

    with tab1:
        # Análisis de tendencia
        años_disponibles = [col for col in causas_df.columns if col.isdigit()]

        años_seleccionados = st.multiselect(
            "Selecciona los años para la tendencia:",
            options=años_disponibles,
            default=años_disponibles
        )

        if años_seleccionados:
            datos_tendencia = pd.DataFrame({
                'Año': años_seleccionados,
                'Accidentes': causas_df[
                    (causas_df['Entidad'] == 'Nacional') & 
                    (causas_df['Variable'] == 'Total de eventos (Absoluto)')
                ][años_seleccionados].values.flatten()
            })

            fig_trend = px.line(
                datos_tendencia,
                x='Año',
                y='Accidentes',
                title='Tendencia Nacional de Accidentes',
                markers=True,
                color_discrete_sequence=[BBVA_COLORS['blue']]
            )

            fig_trend.update_traces(
                line_width=3,
                marker=dict(size=8)
            )
            fig_trend.update_layout(
                plot_bgcolor='white',
                height=400,
                showlegend=False,
                yaxis=dict(
                    title='Número de Accidentes',
                    showgrid=True,
                    gridcolor='lightgray',
                    tickformat=','
                ),
                xaxis=dict(
                    title='Año',
                    showgrid=True,
                    gridcolor='lightgray',
                    tickmode='array',
                    ticktext=años_seleccionados,
                    tickvals=años_seleccionados,
                    tickangle=0
                )
            )

            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("Por favor, selecciona al menos un año para visualizar la tendencia.")

        # Análisis de cruce para 2023
        st.markdown("---")
        st.markdown("### 🚗 Propensión a accidentes por entidad 2023")

        # Filtrar datos de 2023 para otras bases
        accidentes_2023 = causas_df[(causas_df['Entidad'] != 'Nacional') & (causas_df['Variable'] == 'Total de eventos (Absoluto)')][['Entidad', '2023']]
        accidentes_2023.rename(columns={'2023': 'Total Accidentes'}, inplace=True)

        # Ajustar encabezados de vmrc y realizar el cruce
        vmrc_df.rename(columns={'ENTIDAD FEDERATIVA': 'Entidad', 'TOTAL': 'Total Vehículos'}, inplace=True)

        # Seleccionar columnas relevantes para el análisis
        columnas_vmrc = ['Entidad', 'AUTOMÓVILES SUMA', 'CAMIONES PARA PASAJEROS SUMA', 
                         'CAMIONES Y CAMIONETAS PARA CARGA SUMA', 'MOTOCICLETAS SUMA']
        vmrc_df = vmrc_df[columnas_vmrc]

        # Realizar el cruce
        vmrc_cruce = vmrc_df.merge(accidentes_2023, on='Entidad', how='inner')

        # Transformar vmrc_cruce para análisis por tipo de vehículo
        tipos_vehiculos = [
            'AUTOMÓVILES SUMA',
            'CAMIONES PARA PASAJEROS SUMA',
            'CAMIONES Y CAMIONETAS PARA CARGA SUMA',
            'MOTOCICLETAS SUMA'
        ]
        vmrc_cruce_melted = vmrc_cruce.melt(
            id_vars=['Entidad', 'Total Accidentes'],
            value_vars=tipos_vehiculos,
            var_name='Tipo de Vehículo',
            value_name='Total Vehículos'
        )

        if not vmrc_cruce_melted.empty:
            fig_cruce = px.bar(
                vmrc_cruce_melted,
                x='Entidad',
                y='Total Vehículos',
                color='Tipo de Vehículo',
                title='Accidentes por Tipo de Vehículo y Entidad (2023)',
                barmode='group',
                color_discrete_sequence=px.colors.sequential.Plasma
            )

            fig_cruce.update_layout(
                plot_bgcolor='white',
                height=500,
                xaxis=dict(title='Entidad', showgrid=False),
                yaxis=dict(title='Total Vehículos', showgrid=True, gridcolor='lightgray')
            )

            st.plotly_chart(fig_cruce, use_container_width=True)
        else:
            st.warning("No se encontraron datos coincidentes para el análisis de 2023.")

    with tab2:
        st.markdown("### 🗺️ Análisis por Estado")

        # Selector de año
        años_disponibles = [col for col in causas_df.columns if col.isdigit()]
        year = st.selectbox('Selecciona el año:', años_disponibles)

        # Filtrar datos por año seleccionado y mostrar el top 10 de estados
        datos_estados = causas_df[
            (causas_df['Entidad'] != 'Nacional') & 
            (causas_df['Variable'] == 'Total de eventos (Absoluto)')
        ][['Entidad', year]].nlargest(10, year)

        # Selector de estado del top 10
        estado_seleccionado = st.selectbox(
            "Selecciona un estado del top 10 para analizar:",
            options=datos_estados['Entidad']
        )

        # Análisis de clases de accidente para el estado seleccionado
        datos_clase_estado = clases_df[
            (clases_df['Entidad'] == estado_seleccionado) & 
            (clases_df['Variable'] != 'Total de eventos (Absoluto)')
        ][['Variable', year]].copy()
        datos_clase_estado['Variable'] = datos_clase_estado['Variable'].str.replace(' \(Absoluto\)', '', regex=True)

        # Gráfico de pastel
        fig_clases = px.pie(
            datos_clase_estado,
            names='Variable',
            values=year,
            title=f'Distribución de Clases de Accidentes en {estado_seleccionado} ({year})',
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig_clases.update_traces(
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        )

        # Análisis de tipos de accidente para el estado seleccionado
        datos_tipo_estado = tipos_df[
            (tipos_df['Entidad'] == estado_seleccionado) & 
            (tipos_df['Variable'] != 'Total de eventos (Absoluto)')
        ][['Variable', year]].copy()
        datos_tipo_estado['Variable'] = datos_tipo_estado['Variable'].str.replace(' \(Absoluto\)', '', regex=True)

        fig_tipos = px.bar(
            datos_tipo_estado,
            x='Variable',
            y=year,
            title=f'Distribución de Tipos de Accidentes en {estado_seleccionado} ({year})',
            color_discrete_sequence=px.colors.sequential.Sunset,
            text=year
        )
        fig_tipos.update_layout(
            plot_bgcolor='white',
            height=400,
            xaxis=dict(title='Tipo de Accidente', showgrid=False),
            yaxis=dict(title='Número de Accidentes', showgrid=True, gridcolor='lightgray')
        )
        fig_tipos.update_traces(texttemplate='%{text:.0f}', textposition='outside', cliponaxis=False)

        # Mostrar gráficos en dos columnas
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_clases, use_container_width=True)
        with col2:
            st.plotly_chart(fig_tipos, use_container_width=True)



    with tab3:
        # Obtener años disponibles
        años_disponibles = [col for col in causas_df.columns if col.isdigit()]
        
        # Selector de año
        año_seleccionado = st.selectbox(
            "Selecciona el año para analizar las causas:",
            options=años_disponibles,
            index=len(años_disponibles) - 1  # Por defecto, el año más reciente
        )

        # Filtrar datos para el año seleccionado y limpiar nombres
        datos_causas = causas_df[
            (causas_df['Entidad'] == 'Nacional') & 
            (causas_df['Variable'] != 'Total de eventos (Absoluto)')
        ][['Variable', año_seleccionado]].copy()
        
        datos_causas['Variable'] = datos_causas['Variable'].str.replace(' \(Absoluto\)', '', regex=True)
        datos_causas['Porcentaje'] = datos_causas[año_seleccionado] / datos_causas[año_seleccionado].sum() * 100
        datos_causas = datos_causas.sort_values(año_seleccionado, ascending=True)

        # Gráfica de barras horizontales con porcentajes
        fig_causas = px.bar(
            datos_causas,
            y='Variable',
            x=año_seleccionado,
            orientation='h',
            title=f'Distribución de Causas de Accidentes ({año_seleccionado})',
            color_discrete_sequence=[BBVA_COLORS['blue']],
            text='Porcentaje'
        )
        
        # Configuración de la gráfica
        fig_causas.update_layout(
            plot_bgcolor='white',
            height=400,
            showlegend=False,
            xaxis=dict(
                title='Número de Accidentes',
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='Causa',
                showgrid=False
            )
        )
        fig_causas.update_traces(texttemplate='%{text:.1f}%', textposition='auto')
        
        # Mostrar gráfica
        st.plotly_chart(fig_causas, use_container_width=True)

        # Insights adicionales: Total y porcentajes
        st.markdown("### 🧐 Ojo")
        total_accidentes = datos_causas[año_seleccionado].sum()
        causa_principal = datos_causas.iloc[-1]
        
        st.markdown(f"- **Total de accidentes en {año_seleccionado}:** {total_accidentes:,.0f}")
        st.markdown(
            f"- **Causa principal:** {causa_principal['Variable']} "
            f"({causa_principal[año_seleccionado]:,.0f} accidentes, {causa_principal['Porcentaje']:.2f}%)."
        )
        
        # Análisis adicional: Variación porcentual entre años
        st.markdown("### 🔄 Variación Porcentual entre Años")
        causas_variacion = causas_df[
            (causas_df['Entidad'] == 'Nacional') & 
            (causas_df['Variable'] != 'Total de eventos (Absoluto)')
        ].copy()
        causas_variacion['Variable'] = causas_variacion['Variable'].str.replace(' \(Absoluto\)', '', regex=True)
        
        # Calcular variaciones porcentuales año contra año
        for i in range(1, len(años_disponibles)):
            causas_variacion[f'Variación {años_disponibles[i]} vs {años_disponibles[i-1]}'] = (
                (causas_variacion[años_disponibles[i]] - causas_variacion[años_disponibles[i-1]]) /
                causas_variacion[años_disponibles[i-1]] * 100
            )
        
        variacion_long = causas_variacion.melt(
            id_vars=['Variable'], 
            value_vars=[col for col in causas_variacion.columns if 'Variación' in col],
            var_name='Periodo',
            value_name='Variación (%)'
        )
        
        # Gráfica de variaciones
        fig_variacion = px.line(
            variacion_long,
            x='Periodo',
            y='Variación (%)',
            color='Variable',
            title="Variación Porcentual de Causas de Accidentes por Año",
            markers=True,
            color_discrete_sequence=[BBVA_COLORS['blue'], BBVA_COLORS['aqua'], BBVA_COLORS['coral'], BBVA_COLORS['navy']]
        )
        fig_variacion.update_layout(
            plot_bgcolor='white',
            height=400,
            xaxis=dict(
                title='Periodo',
                showgrid=True,
                gridcolor='lightgray',
                tickmode='array',
                type='category'
            ),
            yaxis=dict(
                title='Variación (%)',
                showgrid=True,
                gridcolor='lightgray'
            )
        )
        fig_variacion.update_traces(line_width=3)
        
        # Mostrar gráfica de variaciones
        st.plotly_chart(fig_variacion, use_container_width=True)

    with tab4:
        st.markdown("### 💡 Frases Tractoras para Venta de Seguros")

        # Diccionario de plantillas de frases
        plantillas = {
            'MOTOCICLETAS SUMA': "En {Entidad}, las motocicletas representan un alto porcentaje de accidentes. Asegura tu motocicleta con nuestras mejores coberturas.",
            'AUTOMÓVILES SUMA': "En {Entidad}, los automóviles están involucrados en numerosos accidentes. Protégete adquiriendo un seguro de auto.",
            'CAMIONES PARA PASAJEROS SUMA': "En {Entidad}, los camiones de pasajeros son protagonistas en accidentes. Garantiza la seguridad con nuestro seguro especializado.",
            'CAMIONES Y CAMIONETAS PARA CARGA SUMA': "En {Entidad}, los camiones de carga tienen alta incidencia en accidentes. Protege tu inversión con nuestra cobertura para vehículos de carga."
        }

        # Generar frases tractoras dinámicamente
        if not vmrc_cruce.empty:
            frases = []
            for _, row in vmrc_cruce.iterrows():
                for tipo, plantilla in plantillas.items():
                    if row[tipo] > 0:
                        frases.append(plantilla.format(Entidad=row['Entidad']))

            for frase in frases:
                st.write(f"- {frase}")
        else:
            st.warning("No hay datos suficientes para generar frases tractoras.")


    with tab5:
        st.markdown("### 📘 Glosario")
        st.markdown("""
        **Accidentes de tránsito terrestre:**  
        Se refiere a los accidentes en zonas urbanas y suburbanas.  
        No se consideran los eventos viales ocurridos en carreteras de jurisdicción federal.

        **Clasificación de accidentes:**  
        - **Fatal:** Se refiere a todo accidente de tránsito en el cual una o más personas fallecen en el lugar del evento.  
        - **No fatal:** Se refiere a todo accidente de tránsito en el cual una o más personas resultaron heridas, independientemente de la gravedad de sus lesiones.  
        - **Solo daños:** Se refiere a todo accidente en el que se ocasionaron daños materiales a vehículos automotores, propiedad del estado, inmueble particular y otros.  
        """)

except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.info("Por favor, asegúrate de que los archivos Excel estén en el directorio correcto y tengan el formato esperado.")
