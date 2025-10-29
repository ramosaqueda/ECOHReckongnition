import streamlit as st
import boto3
import time
from PIL import Image
import hashlib
from datetime import datetime

# ==========================
# CONFIGURACIÓN GENERAL
# ==========================
st.set_page_config(page_title="AWS Rekognition Comparison", page_icon="😈", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
            color: #1e1e1e;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
        }
        h1, h2, h3 {
            color: #004388;
            font-weight: 700;
        }
        .stButton>button {
            background-color: #DC2D33;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6em 1.2em;
            transition: 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #a61f27;
            transform: scale(1.02);
        }
        .stDownloadButton>button {
            background-color: #004388;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
        .stDownloadButton>button:hover {
            background-color: #022b5c;
        }
        .stTextInput>div>div>input {
            border: 1px solid #004388;
            border-radius: 6px;
            padding: 0.4em;
        }
        .stExpander {
            border: 1px solid #004388 !important;
            border-radius: 10px !important;
        }
        .stProgress > div > div > div {
            background-color: #004388;
        }
    </style>
""", unsafe_allow_html=True)

# TÍTULO
st.title("😈 ECOH Rekognition - Comparativa Biométrica")
st.write("Compara similitud facial entre dos imágenes usando Amazon Rekognition y genera un informe con los resultados.")

# ==========================
# CREDENCIALES AWS
# ==========================
with st.expander("⚙️ Configuración AWS (obligatoria)", expanded=True):
    access_key = st.text_input("Access Key ID", placeholder="Ingresa tu AWS_ACCESS_KEY_ID")
    secret_key = st.text_input("Secret Access Key", type="password", placeholder="Ingresa tu AWS_SECRET_ACCESS_KEY")
    region = st.text_input("Región AWS", placeholder="ej: us-east-1")

# ==========================
# SECCIÓN DE IMÁGENES
# ==========================
st.markdown("---")
st.subheader("📸 Imágenes a comparar")

col1, col2 = st.columns(2)

with col1:
    image1_file = st.file_uploader("Imagen 1", type=["png", "jpg", "jpeg"], key="img1")
    if image1_file:
        image1 = Image.open(image1_file)
        # Reducir tamaño para ajustar a la vista
        max_width = 300
        ratio = max_width / image1.width
        resized = image1.resize((max_width, int(image1.height * ratio)))
        st.image(resized, caption="Imagen 1", use_container_width=False)

with col2:
    image2_file = st.file_uploader("Imagen 2", type=["png", "jpg", "jpeg"], key="img2")
    if image2_file:
        image2 = Image.open(image2_file)
        max_width = 300
        ratio = max_width / image2.width
        resized = image2.resize((max_width, int(image2.height * ratio)))
        st.image(resized, caption="Imagen 2", use_container_width=False)

# ==========================
# BOTÓN DE COMPARACIÓN
# ==========================
st.markdown("---")
if st.button("🔍 Iniciar Comparación", type="primary"):
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

            # Paso 2: Leer bytes e identificar hashes
            progress.progress(40)
            source_bytes = image1_file.getvalue()
            target_bytes = image2_file.getvalue()

            hash1 = hashlib.sha1(source_bytes).hexdigest()
            hash2 = hashlib.sha1(target_bytes).hexdigest()

            # Paso 3: Llamar al servicio Rekognition
            status.text("Comparando rostros con AWS Rekognition...")
            progress.progress(70)
            time.sleep(0.5)

            response = client.compare_faces(
                SourceImage={'Bytes': source_bytes},
                TargetImage={'Bytes': target_bytes}
            )

            progress.progress(100)
            status.text("Comparación completada ✅")

            # ==========================
            # RESULTADOS
            # ==========================
            st.markdown("---")
            st.subheader("📊 Resultados de la Comparación")

            if response.get('FaceMatches'):
                similarity = response['FaceMatches'][0]['Similarity']
                result_text = f"🎯 Coincidencia detectada con **{similarity:.2f}%** de similitud."
                st.success(result_text)
            else:
                similarity = None
                result_text = "😕 No se encontraron rostros coincidentes."
                st.warning(result_text)

            with st.expander("📄 Respuesta completa de AWS Rekognition"):
                st.json(response)

            # ==========================
            # GENERAR INFORME
            # ==========================
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_content = f"""
ECOH Rekognition - Informe de Comparativa Biométrica
====================================================

🕒 Fecha y hora: {timestamp}
🌎 Región AWS: {region}

📁 Imagen 1: {image1_file.name}
🔑 SHA1: {hash1}

📁 Imagen 2: {image2_file.name}
🔑 SHA1: {hash2}

📊 Resultado:
{result_text}

🧠 Coincidencias encontradas: {len(response.get('FaceMatches', []))}
"""

            report_bytes = report_content.encode("utf-8")
            st.download_button(
                label="📥 Descargar Informe TXT",
                data=report_bytes,
                file_name=f"reporte_rekognition_{int(time.time())}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
