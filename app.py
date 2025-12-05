import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="WorkShow - Social Generator", page_icon="📸")

# --- CSS PER MOBILE ---
st.markdown("""
<style>
    .stButton>button {
        height: 3em;
        font-size: 20px;
        background-color: #007bff;
        color: white;
        border-radius: 10px;
    }
    h1 { text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI GRAFICHE ---

def get_font(size):
    """Cerca un font decente nel sistema, altrimenti usa quello default"""
    try:
        # Prova a caricare un font standard (funziona su Linux/Streamlit Cloud)
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except IOError:
        try:
            # Fallback per Windows
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            # Fallback estremo
            return ImageFont.load_default()

def create_social_post(img_before, img_after, primary_color, contact_text, logo=None):
    # 1. Impostazioni Tela (Formato Instagram Quadrato 1080x1080)
    W, H = 1080, 1080
    canvas = Image.new('RGB', (W, H), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # 2. Preparazione Immagini (Split Verticale: 540x1080 ognuna)
    # ImageOps.fit ritaglia automaticamente l'immagine al centro senza deformarla
    target_size = (int(W/2), H)
    
    img_before = ImageOps.fit(img_before, target_size, method=Image.Resampling.LANCZOS)
    img_after = ImageOps.fit(img_after, target_size, method=Image.Resampling.LANCZOS)
    
    # 3. Incolla le immagini
    canvas.paste(img_before, (0, 0))
    canvas.paste(img_after, (int(W/2), 0))
    
    # 4. Aggiungi Separatore Centrale
    draw.line([(W/2, 0), (W/2, H)], fill="white", width=15)
    
    # 5. Aggiungi Etichette "PRIMA" e "DOPO"
    # Badge Prima
    font_badge = get_font(40)
    draw.rectangle([(20, 20), (200, 80)], fill="white") # Sfondo bianco badge
    draw.text((110, 50), "PRIMA", fill="black", font=font_badge, anchor="mm")
    
    # Badge Dopo (Colorato col brand)
    draw.rectangle([(W/2 + 20, 20), (W/2 + 200, 80)], fill=primary_color)
    draw.text((W/2 + 110, 50), "DOPO", fill="white", font=font_badge, anchor="mm")
    
    # 6. Aggiungi Footer (Fascia in basso con contatti)
    footer_height = 120
    draw.rectangle([(0, H - footer_height), (W, H)], fill="white") # Sfondo footer
    draw.line([(0, H - footer_height), (W, H - footer_height)], fill=primary_color, width=5) # Linea decorativa
    
    # Aggiungi Logo (se c'è)
    if logo is not None:
        # Ridimensiona logo mantenendo proporzioni
        logo.thumbnail((250, 100))
        # Posiziona a sinistra nel footer
        logo_y = H - int(footer_height/2) - int(logo.height/2)
        canvas.paste(logo, (30, logo_y), mask=logo if logo.mode == 'RGBA' else None)
        text_start_x = 350 # Sposta il testo se c'è il logo
    else:
        text_start_x = 50
        
    # Aggiungi Contatti
    font_contact = get_font(35)
    draw.text((text_start_x, H - 60), contact_text, fill="black", font=font_contact, anchor="lm")
    
    return canvas

# --- INTERFACCIA UTENTE ---

st.title("📸 WorkShow")
st.caption("Crea post 'Prima & Dopo' professionali in 30 secondi.")

# 1. SETUP AZIENDA (Sidebar)
with st.sidebar:
    st.header("⚙️ Il tuo Brand")
    brand_color = st.color_picker("Colore Aziendale", "#007bff")
    contact_info = st.text_input("Testo Footer (Sito/Tel)", "www.miosito.it | 333 1234567")
    uploaded_logo = st.file_uploader("Carica Logo (PNG trasparente)", type=['png', 'jpg'])
    
    logo_img = None
    if uploaded_logo:
        logo_img = Image.open(uploaded_logo)

# 2. CARICAMENTO FOTO (Main)
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Il Passato 🏚️")
    file_before = st.file_uploader("Carica foto PRIMA", type=['jpg', 'png', 'jpeg'], key="bef")

with col2:
    st.subheader("2. Il Risultato ✨")
    file_after = st.file_uploader("Carica foto DOPO", type=['jpg', 'png', 'jpeg'], key="aft")

# 3. GENERAZIONE
if file_before and file_after:
    st.markdown("---")
    if st.button("🚀 GENERA POST SOCIAL", type="primary"):
        
        with st.spinner("Applicando la magia..."):
            image_b = Image.open(file_before)
            image_a = Image.open(file_after)
            
            # Genera
            final_post = create_social_post(image_b, image_a, brand_color, contact_info, logo_img)
            
            # Mostra anteprima
            st.image(final_post, caption="Anteprima Post", use_container_width=True)
            
            # Pulsante Download
            buf = io.BytesIO()
            final_post.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 SCARICA POST (HD)",
                data=byte_im,
                file_name="workshow_social_post.jpg",
                mime="image/jpeg"
            )
else:
    st.info("👆 Carica entrambe le foto per vedere l'anteprima.")
