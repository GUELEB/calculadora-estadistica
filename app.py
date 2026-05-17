import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px

st.set_page_config(page_title="Software Estadístico Avanzado", layout="wide")

# Inicializar memoria para guardar las interpretaciones de los casilleros
if 'interpretaciones_guardadas' not in st.session_state:
    st.session_state['interpretaciones_guardadas'] = []

st.title("📊 Calculadora de Estadística Descriptiva Completa")

# --- 1. CLASIFICADOR DE VARIABLES Y CONTEXTO ---
st.header("1. Planteamiento del Problema")
problema = st.text_area("Escribe el problema aquí:")

tipo_sugerido = "Cuantitativa Discreta"
recomendacion_datos = "(datos simples o sueltos)"

if problema:
    p_lower = problema.lower()
    if any(word in p_lower for word in ["color", "marca", "nombre", "género", "profesión"]):
        tipo_sugerido = "Cualitativa Nominal"
        recomendacion_datos = "(datos simples o sueltos)"
    elif any(word in p_lower for word in ["nivel", "calidad", "rango", "grado"]):
        tipo_sugerido = "Cualitativa Ordinal"
        recomendacion_datos = "(datos simples o sueltos)"
    elif any(word in p_lower for word in ["peso", "estatura", "tiempo", "salario", "distancia"]):
        tipo_sugerido = "Cuantitativa Continua (Intervalos)"
        recomendacion_datos = "(Intervalos)"
    elif any(word in p_lower for word in ["cantidad", "cuántos", "hermanos", "hijos", "autos", "edad"]):
        tipo_sugerido = "Cuantitativa Discreta (Datos)"
        recomendacion_datos = "(datos simples o sueltos)"

st.info(f"**Análisis de IA:** Según tu texto, la variable parece ser **{tipo_sugerido}**. Por lo tanto, te sugerimos seleccionar la opción de carga por **{recomendacion_datos}** aquí abajo.")

col_ctx1, col_ctx2 = st.columns(2)
with col_ctx1:
    sujeto = st.text_input("¿De qué estamos hablando? (Sujeto)", value="las observaciones", help="Ej: los libros, las familias, los estudiantes")
with col_ctx2:
    unidad = st.text_input("Unidad de medida", value="unidades", help="Ej: kg, años, computadoras")

# --- 2. CONFIGURACIÓN Y CARGA DE DATOS ---
st.header("2. Carga de Datos")
tipo_datos = st.radio("¿Cómo deseas ingresar los datos?", 
                      ["Datos Sueltos (Discreta / Cualitativa)", "Intervalos (Continua)"], horizontal=True)

if tipo_datos == "Datos Sueltos (Discreta / Cualitativa)":
    df_input = pd.DataFrame({"Xi (Dato)": [0, 1, 2, 3], "fi (Frec. Absoluta)": [0, 0, 0, 0]})
else:
    df_input = pd.DataFrame({"Li (Lim. Inf)": [0, 10, 20], "Ls (Lim. Sup)": [10, 20, 30], "fi (Frec. Absoluta)": [0, 0, 0]})

st.write("Edita la tabla a continuación:")
datos_editados = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# --- 3. CONFIGURACIÓN DE CUANTILES ---
st.header("3. Configuración de Cuantiles")
col1, col2 = st.columns(2)
with col1:
    deciles_req = st.multiselect("¿Qué Deciles (D) deseas calcular?", [1, 2, 3, 4, 5, 6, 7, 8, 9])
with col2:
    percentiles_req = st.text_input("¿Qué Percentiles (P) deseas calcular? (Separa con comas, ej: 15, 82)")

if 'calculado' not in st.session_state:
    st.session_state['calculado'] = False

if st.button("🚀 Calcular Todo y Generar Reporte", type="primary"):
    st.session_state['calculado'] = True

if st.session_state['calculado']:
    df = datos_editados.copy().reset_index(drop=True)
    
    if df['fi (Frec. Absoluta)'].sum() == 0:
        st.error("Por favor, ingresa valores mayores a 0 en la columna 'fi'.")
        st.stop()

    # --- CÁLCULOS MATEMÁTICOS ---
    N = df['fi (Frec. Absoluta)'].sum()
    
    if tipo_datos == "Intervalos (Continua)":
        df['Xi* (Marca de Clase)'] = (df['Li (Lim. Inf)'] + df['Ls (Lim. Sup)']) / 2
        Xi_col = 'Xi* (Marca de Clase)'
    else:
        df['Xi* (Marca de Clase)'] = df['Xi (Dato)']
        Xi_col = 'Xi (Dato)'

    df['Fi (Frec. Abs Acum)'] = df['fi (Frec. Absoluta)'].cumsum()
    df['fr (Frec. Relativa)'] = df['fi (Frec. Absoluta)'] / N
    df['Fr (Frec. Rel Acum)'] = df['fr (Frec. Relativa)'].cumsum()
    df['f% (Porcentaje)'] = df['fr (Frec. Relativa)'] * 100
    df['F% (Porc. Acum)'] = df['Fr (Frec. Rel Acum)'] * 100
    
    df['Xi * fi'] = df['Xi* (Marca de Clase)'] * df['fi (Frec. Absoluta)']
    suma_xi_fi = df['Xi * fi'].sum()
    promedio = suma_xi_fi / N
    
    df['Xi - X'] = df['Xi* (Marca de Clase)'] - promedio
    df['(Xi - X)²'] = df['Xi - X'] ** 2
    df['(Xi - X)².fi'] = df['(Xi - X)²'] * df['fi (Frec. Absoluta)']
    
    suma_var = df['(Xi - X)².fi'].sum()
    varianza = suma_var / N
    desviacion = np.sqrt(varianza)
    cv = (desviacion / promedio) * 100 if promedio != 0 else 0

    idx_moda = df['fi (Frec. Absoluta)'].idxmax()
    fi_mo = df.loc[idx_moda, 'fi (Frec. Absoluta)']
    
    if tipo_datos == "Intervalos (Continua)":
        Li_mo = df.loc[idx_moda, 'Li (Lim. Inf)']
        Ls_mo = df.loc[idx_moda, 'Ls (Lim. Sup)']
        f_ant = df.loc[idx_moda - 1, 'fi (Frec. Absoluta)'] if idx_moda > 0 else 0
        f_post = df.loc[idx_moda + 1, 'fi (Frec. Absoluta)'] if idx_moda < len(df) - 1 else 0
        a = Ls_mo - Li_mo
        delta1 = fi_mo - f_ant
        delta2 = fi_mo - f_post
        moda = Li_mo + (delta1 / (delta1 + delta2)) * a if (delta1 + delta2) != 0 else Li_mo
        
        detalle_moda = f"Mo = Li + [Δ1 / (Δ1 + Δ2)] * a = {Li_mo:.2f} + [{delta1:.2f} / ({delta1:.2f} + {delta2:.2f})] * {a:.2f} = {moda:.2f} {unidad}"
    else:
        moda = df.loc[idx_moda, 'Xi* (Marca de Clase)']
        detalle_moda = f"Mo = Valor con mayor frecuencia absoluta (fi = {fi_mo}) = {moda:.2f} {unidad}"

    detalle_promedio = f"X̄ = Σ(Xi*fi) / N = {suma_xi_fi:.2f} / {N} = {promedio:.2f} {unidad}"
    detalle_var = f"S² = Σ[(Xi - X̄)².fi] / N = {suma_var:.2f} / {N} = {varianza:.2f}"
    detalle_desv = f"S = √S² = √{varianza:.2f} = {desviacion:.2f} {unidad}"
    detalle_cv = f"CV = (S / X̄) * 100 = ({desviacion:.2f} / {promedio:.2f}) * 100 = {cv:.2f}%"

    # --- PREPARAR DATAFRAME DE VISUALIZACIÓN ---
    df_formateado = df.copy()
    columnas_numericas = df_formateado.select_dtypes(include=[np.number]).columns
    df_formateado[columnas_numericas] = df_formateado[columnas_numericas].round(2)
    
    totales = {}
    for col in df_formateado.columns:
        if col == df_formateado.columns[0]:
            totales[col] = "TOTAL"
        elif col in ['fi (Frec. Absoluta)', 'fr (Frec. Relativa)', 'f% (Porcentaje)', 'Xi * fi', '(Xi - X)².fi']:
            totales[col] = round(df[col].sum(), 2) 
        else:
            totales[col] = np.nan
            
    df_display = pd.concat([df_formateado, pd.DataFrame([totales])], ignore_index=True)
    df_display = df_display.fillna("")

    reporte_txt = []
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Tabla Frecuencias", "📈 Interpretaciones", "📊 Gráficos", "💾 Exportar a Excel"])
    
    with tab1:
        st.dataframe(df_display, use_container_width=True)
        
        # --- SECCIÓN INTEGRADA: INTERPRETACIÓN DE CASILLEROS SOMBREADOS ---
        st.divider()
        st.subheader("🖍️ Selección e Interpretación de Casilleros")
        st.write("Observa la tabla superior y usa estos selectores para elegir la fila y columna del casillero que quieres interpretar y añadir al reporte.")
        
        if tipo_datos == "Intervalos (Continua)":
            etiquetas_fila = [f"[{row['Li (Lim. Inf)']}-{row['Ls (Lim. Sup)']})" for _, row in df.iterrows()]
        else:
            etiquetas_fila = df['Xi (Dato)'].astype(str).tolist()

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fila_sel = st.selectbox("1. Elige la Fila (Valor de la variable):", etiquetas_fila)
        with col_s2:
            opciones_col = {
                "f_i (Frecuencia Absoluta)": "fi (Frec. Absoluta)",
                "F_i (Frec. Absoluta Acumulada)": "Fi (Frec. Abs Acum)",
                "f_r (Frecuencia Relativa)": "fr (Frec. Relativa)",
                "F_r (Frec. Rel. Acumulada)": "Fr (Frec. Rel Acum)",
                "f% (Porcentaje)": "f% (Porcentaje)",
                "F% (Porcentaje Acumulado)": "F% (Porc. Acum)"
            }
            col_sel_label = st.selectbox("2. Elige la Columna (Frecuencia):", list(opciones_col.keys()))
            col_sel = opciones_col[col_sel_label]

        idx_fila = etiquetas_fila.index(fila_sel)
        valor_celda = df.loc[idx_fila, col_sel]

        if "Porcentaje" in col_sel: val_display = f"{valor_celda:.2f}%"
        elif "Relativa" in col_sel: val_display = f"{valor_celda:.4f}"
        else: val_display = f"{valor_celda}"

        if tipo_datos == "Intervalos (Continua)":
            lim_inf = df.loc[idx_fila, 'Li (Lim. Inf)']
            lim_sup = df.loc[idx_fila, 'Ls (Lim. Sup)']
            txt_exacto = f"entre {lim_inf} y {lim_sup} {unidad}"
            txt_acum = f"{lim_sup} {unidad} o menos"
        else:
            xi_val = df.loc[idx_fila, 'Xi (Dato)']
            txt_exacto = f"exactamente {xi_val} {unidad}"
            txt_acum = f"{xi_val} {unidad} o menos"

        if col_sel == "fi (Frec. Absoluta)":
            interp_casillero = f"Hay exactamente **{valor_celda}** {sujeto} que tienen o registran {txt_exacto}."
        elif col_sel == "Fi (Frec. Abs Acum)":
            interp_casillero = f"Hay un total de **{valor_celda}** {sujeto} que tienen o registran {txt_acum}."
        elif col_sel == "fr (Frec. Relativa)":
            interp_casillero = f"La proporción de {sujeto} que tienen o registran {txt_exacto} es de **{valor_celda:.4f}** respecto al total."
        elif col_sel == "Fr (Frec. Rel Acum)":
            interp_casillero = f"La proporción acumulada de {sujeto} con {txt_acum} es de **{valor_celda:.4f}** respecto al total."
        elif col_sel == "f% (Porcentaje)":
            interp_casillero = f"El **{valor_celda:.2f}%** de {sujeto} tienen o registran {txt_exacto}."
        elif col_sel == "F% (Porc. Acum)":
            interp_casillero = f"El **{valor_celda:.2f}%** de {sujeto} tienen o registran {txt_acum}."

        st.info(f"**Valor del Casillero:** {val_display}\n\n👉 **Interpretación:** {interp_casillero}")

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("💾 Agregar al Reporte"):
                texto_guardar = f"Fila [{fila_sel}] | Columna [{col_sel_label}] -> {interp_casillero.replace('**', '')}"
                st.session_state['interpretaciones_guardadas'].append(texto_guardar)
                st.rerun()

        if st.session_state['interpretaciones_guardadas']:
            st.success(f"✅ Tienes {len(st.session_state['interpretaciones_guardadas'])} casillero(s) guardado(s) para el informe.")
            if st.button("🗑️ Borrar lista de casilleros"):
                st.session_state['interpretaciones_guardadas'] = []
                st.rerun()

    with tab2:
        st.subheader("Medidas de Tendencia Central")
        st.markdown(f"**Promedio ($\overline{{X}}$):**")
        st.code(detalle_promedio, language="text")
        st.write(f"👉 *Interpretación:* El promedio de {sujeto} es de **{promedio:.2f} {unidad}**.")
        
        st.markdown(f"**Moda (Mo):**")
        st.code(detalle_moda, language="text")
        st.write(f"👉 *Interpretación:* El valor más frecuente para {sujeto} es de **{moda:.2f} {unidad}**.")

        st.divider()
        st.subheader("📉 Medidas de Dispersión")
        st.markdown(f"**Varianza ($S^2$):**")
        st.code(detalle_var, language="text")
        
        st.markdown(f"**Desvío Estándar ($S$):**")
        st.code(detalle_desv, language="text")
        
        st.markdown(f"**Coeficiente de Variación ($CV$):**")
        st.code(detalle_cv, language="text")
        
        if cv <= 15: eval_cv = "altamente homogénea"
        elif cv <= 25: eval_cv = "moderadamente homogénea"
        else: eval_cv = "heterogénea (alta dispersión)"
        st.write(f"👉 *Interpretación:* La muestra es **{eval_cv}** con una variabilidad del {cv:.2f}%.")

        st.divider()
        st.subheader("Medidas de Posición (Fórmulas Exactas)")
        
        def calcular_cuantil(porcentaje, nombre):
            posicion = (porcentaje * N) / 100
            detalle_posicion = f"Posición = ({porcentaje} * {N}) / 100 = {posicion:.2f}"
            
            if tipo_datos == "Intervalos (Continua)":
                idx = df[df['Fi (Frec. Abs Acum)'] >= posicion].index[0]
                fila = df.loc[idx]
                Li = fila['Li (Lim. Inf)']
                Ls = fila['Ls (Lim. Sup)']
                fi = fila['fi (Frec. Absoluta)']
                a = Ls - Li
                Fant = df.loc[idx - 1, 'Fi (Frec. Abs Acum)'] if idx > 0 else 0
                valor = Li + ((posicion - Fant) / fi) * a
                detalle_calculo = f"Cálculo = Li + [(Pos - Fant) / fi] * a = {Li:.2f} + [({posicion:.2f} - {Fant:.2f}) / {fi:.2f}] * {a:.2f} = {valor:.2f} {unidad}"
            else:
                fila = df[df['Fi (Frec. Abs Acum)'] >= posicion].iloc[0]
                valor = fila['Xi* (Marca de Clase)']
                detalle_calculo = f"Cálculo = El primer valor de Xi* cuya Fi es >= {posicion:.2f} es {valor:.2f} {unidad}"
            
            interpretacion = f"Deducimos que el {porcentaje}% de {sujeto} tiene un valor igual o menor a {valor:.2f} {unidad}."
            
            st.markdown(f"**{nombre}:**")
            st.code(detalle_posicion, language="text")
            st.code(detalle_calculo, language="text")
            st.write(f"👉 *Interpretación:* {interpretacion}")
            
            reporte_txt.append(f"--- {nombre} ---")
            reporte_txt.append(f"  • {detalle_posicion}")
            reporte_txt.append(f"  • {detalle_calculo}")
            reporte_txt.append(f"  • Interpretación: {interpretacion}")
            reporte_txt.append("") 

        calcular_cuantil(25, "Cuartil 1 (Q1)")
        calcular_cuantil(50, "Cuartil 2 / Mediana (Me)")
        calcular_cuantil(75, "Cuartil 3 (Q3)")

        if deciles_req:
            st.divider()
            for d in deciles_req:
                calcular_cuantil(d * 10, f"Decil {d} (D{d})")
                
        if percentiles_req:
            st.divider()
            try:
                percs = [int(p.strip()) for p in percentiles_req.split(",")]
                for p in percs:
                    if 0 < p < 100: calcular_cuantil(p, f"Percentil {p} (P{p})")
            except:
                st.warning("Formato de percentiles incorrecto.")
                
        # --- Mostrar Casilleros Guardados en el Reporte Visual ---
        st.divider()
        st.subheader("🖍️ Interpretación de Casilleros Específicos")
        if st.session_state['interpretaciones_guardadas']:
            for item in st.session_state['interpretaciones_guardadas']:
                st.write(f"👉 {item}")
        else:
            st.write("Aún no has guardado ninguna interpretación de casillero desde la pestaña 'Tabla Frecuencias'.")

    with tab3:
        st.subheader("Selecciona el tipo de gráfico")
        tipo_graf = st.selectbox("Opciones:", ["Gráfico de Barras", "Histograma (Solo para intervalos)", "Gráfico Circular (Pastel)", "Ojiva (Frecuencia Acumulada)"])
        
        etiquetas_ejes = {
            Xi_col: f"{Xi_col} ({unidad})",
            'fi (Frec. Absoluta)': f"Cantidad de {sujeto} (fi)",
            'F% (Porc. Acum)': f"Porcentaje Acumulado de {sujeto} (F%)"
        }
        
        if tipo_graf == "Gráfico de Barras":
            fig = px.bar(df, x=Xi_col, y='fi (Frec. Absoluta)', text='fi (Frec. Absoluta)', 
                         labels=etiquetas_ejes, title=f"Gráfico de Barras: Distribución de frecuencias de {sujeto}")
        elif tipo_graf == "Gráfico Circular (Pastel)":
            fig = px.pie(df, names=Xi_col, values='fi (Frec. Absoluta)', 
                         labels=etiquetas_ejes, title=f"Gráfico Circular: Proporción según {sujeto}")
        elif tipo_graf == "Ojiva (Frecuencia Acumulada)":
            fig = px.line(df, x=Xi_col, y='F% (Porc. Acum)', markers=True, 
                          labels=etiquetas_ejes, title=f"Ojiva: Frecuencia Porcentual Acumulada de {sujeto}")
        else:
            fig = px.bar(df, x=Xi_col, y='fi (Frec. Absoluta)', 
                         labels=etiquetas_ejes, title=f"Histograma: Distribución agrupada de {sujeto}")
            fig.update_layout(bargap=0)
            
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Descargar Reporte a 2 Decimales")
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            
            df_export = df_display.copy()
            df_export.to_excel(writer, sheet_name='Tabla Frecuencias', index=False)
            
            workbook = writer.book
            ws_tabla = writer.sheets['Tabla Frecuencias']
            
            formato_datos = workbook.add_format({'bg_color': '#D9EAD3', 'border': 1, 'num_format': '0.00'}) 
            formato_calculo = workbook.add_format({'bg_color': '#C9DAF8', 'border': 1, 'num_format': '0.00'}) 
            
            for col_num, col_name in enumerate(df_export.columns):
                if col_name in ["Xi (Dato)", "Li (Lim. Inf)", "Ls (Lim. Sup)", "fi (Frec. Absoluta)"]:
                    ws_tabla.set_column(col_num, col_num, 15, formato_datos)
                else:
                    ws_tabla.set_column(col_num, col_num, 18, formato_calculo)

            ws_reporte = workbook.add_worksheet('Reporte de Resultados')
            ws_reporte.set_column(0, 0, 150) 
            
            formato_titulo = workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#4a86e8', 'font_color': 'white'})
            formato_sub = workbook.add_format({'bold': True, 'font_size': 12, 'bottom': 1})
            formato_formula = workbook.add_format({'italic': True, 'font_color': '#333333'})
            
            fila = 0
            ws_reporte.write(fila, 0, "REPORTE ESTADÍSTICO COMPLETO", formato_titulo)
            fila += 2
            
            ws_reporte.write(fila, 0, "1. MEDIDAS DE TENDENCIA CENTRAL", formato_sub)
            fila += 1
            ws_reporte.write(fila, 0, f"Promedio ({promedio:.2f} {unidad})")
            fila += 1
            ws_reporte.write(fila, 0, f"  • {detalle_promedio}", formato_formula)
            fila += 1
            ws_reporte.write(fila, 0, f"  • Interpretación: El promedio de {sujeto} es de {promedio:.2f} {unidad}.")
            fila += 2
            ws_reporte.write(fila, 0, f"Moda ({moda:.2f} {unidad})")
            fila += 1
            ws_reporte.write(fila, 0, f"  • {detalle_moda}", formato_formula)
            fila += 1
            ws_reporte.write(fila, 0, f"  • Interpretación: El valor más frecuente para {sujeto} es {moda:.2f} {unidad}.")
            fila += 2
            
            ws_reporte.write(fila, 0, "2. MEDIDAS DE DISPERSIÓN", formato_sub)
            fila += 1
            ws_reporte.write(fila, 0, "Varianza (S²)")
            fila += 1
            ws_reporte.write(fila, 0, f"  • {detalle_var}", formato_formula)
            fila += 1
            ws_reporte.write(fila, 0, "Desvío Estándar (S)")
            fila += 1
            ws_reporte.write(fila, 0, f"  • {detalle_desv}", formato_formula)
            fila += 1
            ws_reporte.write(fila, 0, "Coeficiente de Variación (CV)")
            fila += 1
            ws_reporte.write(fila, 0, f"  • {detalle_cv}", formato_formula)
            fila += 1
            ws_reporte.write(fila, 0, f"  • Interpretación: Muestra {eval_cv}.")
            fila += 2
            
            ws_reporte.write(fila, 0, "3. MEDIDAS DE POSICIÓN", formato_sub)
            fila += 1
            for linea in reporte_txt:
                if linea.startswith("  • Cálculo") or linea.startswith("  • Posición"):
                    ws_reporte.write(fila, 0, linea, formato_formula)
                else:
                    ws_reporte.write(fila, 0, linea)
                fila += 1
            
            fila += 1
            ws_reporte.write(fila, 0, "4. FORMULARIO MATEMÁTICO APLICADO", formato_sub)
            fila += 1
            
            formulas_utilizadas = [
                "• Tamaño de muestra (N) = Σ fi",
                "• Marca de Clase (Xi*) = (Límite Inferior + Límite Superior) / 2",
                "• Frecuencia Relativa (fr) = fi / N",
                "• Frecuencia Porcentual (f%) = fr * 100",
                "• Promedio (X̄) = Σ (Xi* * fi) / N",
                "• Varianza (S²) = Σ [ (Xi* - X̄)² * fi ] / N",
                "• Desvío Estándar (S) = √S²",
                "• Coeficiente de Variación (CV) = (S / X̄) * 100"
            ]
            
            for formula in formulas_utilizadas:
                ws_reporte.write(fila, 0, formula)
                fila += 1
                
            fila += 2
            ws_reporte.write(fila, 0, "5. INTERPRETACIÓN DE CASILLEROS ESPECÍFICOS (Sombreados)", formato_sub)
            fila += 1
            if st.session_state['interpretaciones_guardadas']:
                for interp in st.session_state['interpretaciones_guardadas']:
                    ws_reporte.write(fila, 0, f"• {interp}")
                    fila += 1
            else:
                ws_reporte.write(fila, 0, "No se guardaron interpretaciones de casilleros.")
                fila += 1

        st.download_button(
            label="📥 Descargar Reporte en Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="Reporte_Estadistica_Avanzada_Detallado.xlsx",
            mime="application/vnd.ms-excel"
        )