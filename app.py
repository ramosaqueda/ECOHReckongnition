import streamlit as st
import boto3
import time
from PIL import Image
import hashlib
from datetime import datetime
import os

# ==========================
# CONFIGURACIÓN GENERAL
# ==========================
st.set_page_config(page_title="ECOH Rekognition", page_icon="😈", layout="wide")

# Mostrar logo SVG centrado (con manejo de error)
import base64

svg_path = "logo_ecoh1.svg"

# Verificar si el archivo existe antes de abrirlo
if os.path.exists(svg_path):
    try:
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_data = f.read()
        svg_base64 = base64.b64encode(svg_data.encode("utf-8")).decode("utf-8")
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; align-items:center; margin-top:-20px; margin-bottom:10px;">
                <img src="data:image/svg+xml;base64,{svg_base64}" alt="ECOH Logo" width="180"/>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"⚠️ No se pudo cargar el logo: {e}")
else:
    st.info("ℹ️ Logo no encontrado. Asegúrate de que 'logo_ecoh1.svg' esté en el repositorio.")
    # Opcional: mostrar un placeholder o título alternativo
    st.markdown("<h2 style='text-align:center; color:#004388;'>ECOH Rekognition</h2>", unsafe_allow_html=True)


# Estilos personalizados
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
            color: #1e1e1e;
        }
        .main {
            background-color: #ffffff;
            padding: 1rem 2rem;
        }
        h1 {
            color: #004388;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0.5em;
        }
        h3 {
            color: #004388;
            font-weight: 700;
            margin-top: 1em;
        }
        .section-card {
            background-color: #f9f9f9;
            border: 1px solid #e6e6e6;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .stButton>button {
            background-color: #DC2D33;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6em 1.4em;
            transition: 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #a61f27;
            transform: scale(1.03);
        }
        .stDownloadButton>button {
            background-color: #004388;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1.2em;
        }
        .stDownloadButton>button:hover {
            background-color: #022b5c;
        }
        .stTextInput>div>div>input {
            border: 1px solid #004388;
            border-radius: 6px;
            padding: 0.4em;
        }
        .stProgress > div > div > div {
            background-color: #004388;
        }
    </style>
""", unsafe_allow_html=True)

# Título principal (solo si no se mostró el logo)
if os.path.exists(svg_path):
    st.title(" ECOH Rekognition - Comparativa Biométrica")
else:
    st.title(" Comparativa Biométrica")
    
st.markdown("<p style='text-align:center; color:#444;'>Compara similitud facial entre dos imágenes usando Amazon Rekognition y genera un informe con los resultados.</p>", unsafe_allow_html=True)

# ==========================
# DISTRIBUCIÓN FLEXIBLE
# ==========================
col_config, col_images, col_results = st.columns([1, 2, 1])

# ---------- IZQUIERDA: Credenciales AWS ----------
with col_config:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("⚙️ Configuración AWS")
    
    # Opción para usar secrets de Streamlit
    try:
        aws_secrets = st.secrets["aws"]
        access_key = aws_secrets["access_key_id"]
        secret_key = aws_secrets["secret_access_key"]
        region = aws_secrets["region"]
        st.success("✅ Credenciales cargadas desde Secrets")
    except:
        access_key = st.text_input("Access Key ID", placeholder="AWS_ACCESS_KEY_ID")
        secret_key = st.text_input("Secret Access Key", type="password", placeholder="AWS_SECRET_ACCESS_KEY")
        region = st.text_input("Región AWS", placeholder="us-east-1")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- CENTRO: Imágenes ----------
with col_images:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("📸 Imágenes a comparar")
    col1, col2 = st.columns(2)

    with col1:
        image1_file = st.file_uploader("Imagen 1", type=["png", "jpg", "jpeg"], key="img1")
        if image1_file:
            try:
                image1 = Image.open(image1_file)
                max_width = 250
                ratio = max_width / image1.width
                resized = image1.resize((max_width, int(image1.height * ratio)))
                st.image(resized, caption="Imagen 1", use_container_width=False)
            except Exception as e:
                st.error(f"Error al cargar imagen 1: {e}")

    with col2:
        image2_file = st.file_uploader("Imagen 2", type=["png", "jpg", "jpeg"], key="img2")
        if image2_file:
            try:
                image2 = Image.open(image2_file)
                max_width = 250
                ratio = max_width / image2.width
                resized = image2.resize((max_width, int(image2.height * ratio)))
                st.image(resized, caption="Imagen 2", use_container_width=False)
            except Exception as e:
                st.error(f"Error al cargar imagen 2: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- DERECHA: Resultados ----------
with col_results:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("📊 Resultados")
    placeholder_result = st.empty()
    placeholder_download = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# BOTÓN CENTRAL DE ACCIÓN
# ==========================
st.markdown("<div style='text-align:center; margin-top:1em;'>", unsafe_allow_html=True)
start = st.button("🔍 Iniciar Comparación")
st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# LÓGICA DE COMPARACIÓN
# ==========================
if start:
    if not all([access_key, secret_key, region, image1_file, image2_file]):
        st.error("⚠️ Debes ingresar las credenciales y seleccionar ambas imágenes.")
    else:
        try:
            progress = st.progress(0)
            status = st.empty()
            status.text("Inicializando cliente AWS...")

            client = boto3.client(
                'rekognition',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )

            progress.progress(25)
            
            # Resetear punteros de archivo por si acaso
            image1_file.seek(0)
            image2_file.seek(0)
            
            source_bytes = image1_file.getvalue()
            target_bytes = image2_file.getvalue()

            hash1 = hashlib.sha1(source_bytes).hexdigest()
            hash2 = hashlib.sha1(target_bytes).hexdigest()

            progress.progress(60)
            status.text("Comparando rostros...")

            response = client.compare_faces(
                SourceImage={'Bytes': source_bytes},
                TargetImage={'Bytes': target_bytes}
            )

            progress.progress(100)
            status.text("✅ Comparación finalizada")

            # Mostrar resultados en su columna
            if response.get('FaceMatches'):
                similarity = response['FaceMatches'][0]['Similarity']
                result_text = f"🎯 Coincidencia detectada con **{similarity:.2f}%** de similitud."
                placeholder_result.success(result_text)
            else:
                similarity = None
                result_text = "😕 No se encontraron rostros coincidentes."
                placeholder_result.warning(result_text)

            with st.expander("📄 Detalles técnicos"):
                st.json(response)

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

            placeholder_download.download_button(
                label="📥 Descargar Informe TXT",
                data=report_content.encode("utf-8"),
                file_name=f"reporte_rekognition_{int(time.time())}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ Ocurrió un error: {str(e)}")
            st.exception(e)  # Muestra el traceback completo para debugging
