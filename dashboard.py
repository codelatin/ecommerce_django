import streamlit as st
import requests
import pandas as pd

# Configuración general
st.set_page_config(page_title="Dashboard Ecommerce", layout="wide")
API_URL = "http://localhost:8000/api/productos/"

# Función para obtener los datos desde la API
@st.cache_data(ttl=60)  # Cachear por 60 segundos (opcional)
def obtener_productos():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Error al cargar los datos desde Django.")
        return pd.DataFrame()

# Título del dashboard
st.title("📊 Dashboard de Productos - Ecommerce")
st.markdown("Este dashboard consume datos desde la API de Django REST.")

# Botón para limpiar el caché y recargar los datos
if st.button("🔄 Recargar datos"):
    st.cache_data.clear()  # Limpia todo el caché de funciones @st.cache_data
    st.rerun()  # Vuelve a ejecutar el script

# Cargar datos
df_productos = obtener_productos()

if not df_productos.empty:
    
    # Mostrar estadísticas generales
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Productos", len(df_productos))
    col2.metric("Precio Promedio", f"$ {df_productos['precio'].mean():,.2f}")
    col3.metric("Stock Total", df_productos['stock'].sum())

    # Filtro interactivo por categoría
    categorias = df_productos['categoria'].unique()
    categoria_seleccionada = st.selectbox("Filtrar por categoría", options=categorias)

    df_filtrado = df_productos[df_productos['categoria'] == categoria_seleccionada]

    # Mostrar tabla filtrada
    st.subheader(f"Productos en la categoría: {categoria_seleccionada}")
    st.dataframe(df_filtrado[['nombre_producto', 'precio', 'stock', 'esta_disponible']])

    # Gráfico de barras: Precios de productos
    st.subheader("📈 Precios de Productos")
    st.bar_chart(df_filtrado.set_index('nombre_producto')['precio'])

    # Opcional: Mostrar imagen de un producto
    with st.expander("Ver detalles de un producto"):
        producto_seleccionado = st.selectbox("Selecciona un producto", df_filtrado['nombre_producto'])
        prod = df_filtrado[df_filtrado['nombre_producto'] == producto_seleccionado].iloc[0]
        st.write(f"**Descripción:** {prod['descripcion']}")
        st.write(f"**Precio:** $ {prod['precio']}")
        st.write(f"**Stock:** {prod['stock']}")
        st.write(f"**Disponible:** {'✅ Sí' if prod['esta_disponible'] else '❌ No'}")

else:
    st.warning("No se encontraron datos para mostrar.")