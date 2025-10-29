import streamlit as st
import boto3
import time
from PIL import Image

# ==========================
# Configuración general
# ==========================
st.set_page_config(page_title="AWS Rekognition Comparison", page_icon="🧠", layout="wide")
st.title("🧠 AWS Rekognition - Face Comparison")
st.write("Compara similitud facial entre dos imágenes usando Amazon Rekognition.")

# ==========================
# Entradas de credenciales AWS
# ==========================
with st.expander("⚙️ Configuración AWS (obligatoria)", expanded=True):
    access_key = st.text_input("Access Key ID", placeholder="Ingresa tu AWS_ACCESS_KEY_ID")
    secret_key = st.text_input("Secret Access Key", type="password", placeholder="Ingresa tu AWS_SECRET_ACCESS_KEY")
    region = st.text_input("Región AWS", placeholder="ej: us-east-1")

# ==========================
# Subida de imágenes
# ==========================
col1, col2 = st.columns(2)

with col1:
    image1_file = st.file_uploader("📷 Imagen 1", type=["png", "jpg", "jpeg"], key="img1")
    if image1_file:
        image1 = Image.open(image1_file)
        st.image(image1, caption="Imagen 1", use_container_width=True)

with col2:
    image2_file = st.file_uploader("📸 Imagen 2", type=["png", "jpg", "jpeg"], key="img2")
    if image2_file:
        image2 = Image.open(image2_file)
        st.image(image2, caption="Imagen 2", use_container_width=True)

# ==========================
# Botón de comparación
# ==========================
if st.button("🔍 Comparar Rostros", type="primary"):
    if not all([access_key, secret_key, region, image1_file, image2_file]):
        st.error("⚠️ Debes ingresar las credenciales y seleccionar ambas imágenes.")
    else:
        try:
            progress = st.progress(0)
            status = st.empty()
            status.text("Inicializando cliente AWS...")

            # Paso 1: Crear cliente boto3
            progress.progress(10)
            client = boto3.client(
                'rekognition',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )

            # Paso 2: Leer bytes de las imágenes
            progress.progress(40)
            source_bytes = image1_file.getvalue()
            target_bytes = image2_file.getvalue()

            # Paso 3: Ejecutar comparación
            status.text("Comparando rostros...")
            progress.progress(70)
            time.sleep(0.5)

            response = client.compare_faces(
                SourceImage={'Bytes': source_bytes},
                TargetImage={'Bytes': target_bytes}
            )

            progress.progress(100)
            status.text("Completado ✅")

            # ==========================
            # Mostrar resultados
            # ==========================
            if response.get('FaceMatches'):
                similarity = response['FaceMatches'][0]['Similarity']
                st.success(f"🎯 Coincidencia encontrada con **{similarity:.2f}%** de similitud.")
            else:
                st.warning("😕 No se encontraron rostros coincidentes.")

            # Mostrar respuesta completa (debug)
            with st.expander("📄 Respuesta completa de AWS Rekognition"):
                st.json(response)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
