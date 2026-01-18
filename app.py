import streamlit as st
import hashlib
import time
import random
import requests
import qrcode
from io import BytesIO
from datetime import datetime
from web3 import Web3
from eth_account import Account

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="WorkGuard - Preuve d'Antériorité",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURATION DU "SERVICE MODEL" ---
# C'est ICI que l'argent arrive.
# Dans une vraie app, on génèrerait une adresse unique par client pour tracker les paiements.
# On convertit en Checksum Address pour éviter les erreurs Web3
COMPANY_WALLET_ADDRESS = Web3.to_checksum_address("0xd12ef43f0cd2e925d2d55ede9b886d2b6e80969f") 
# C'est CE wallet qui paie les frais de gaz pour ancrer la preuve.
# Il doit avoir un peu de MATIC.
# RÉCUPÉRATION SÉCURISÉE DEPUIS .streamlit/secrets.toml
try:
    COMPANY_PRIVATE_KEY = st.secrets["private_key"]
except FileNotFoundError:
    COMPANY_PRIVATE_KEY = "0x..." # Fallback pour éviter le crash si secrets.toml n'existe pas encore


# MOCK_MODE = False pour activer la vraie blockchain
MOCK_MODE = False 

# RPC Polygon (Infrastructure)
RPC_URL = "https://polygon-rpc.com"

# Prix du service en Euros
SERVICE_PRICE_EUR = 2.00

# -----------------------------------------------------------------------------
# MODE DÉVELOPPEUR (Pour tester avec le même wallet)
# -----------------------------------------------------------------------------
# Mettre à True pour contourner la vérification du paiement (utile si vous testez "Sender = Receiver")
DEV_BYPASS_PAYMENT = False 

# -----------------------------------------------------------------------------
# CSS PERSONNALISÉ (DESIGN "CYBER SECURITY" / DARK MODE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    .stApp {
        background-color: #020617; 
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #020617 75%);
    }
    
    #MainMenu, footer, header {visibility: hidden;}

    /* AGGRESSIVE ANCHOR HIDING */
    .st-emotion-cache-1plm3a3 a, .st-emotion-cache-16idsys a, div[data-baseweb="button"] > a, a[href^="#"] { 
        display: none !important; pointer-events: none;
    }
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { display: none !important; }

    /* TYPOGRAPHY */
    h1, h2, h3, h4, p { text-align: center !important; }
    h1 {
        color: #F8FAFC;
        font-weight: 700;
        font-size: 3rem;
        letter-spacing: -0.03em;
        text-shadow: 0 0 40px rgba(56, 189, 248, 0.2);
        padding-bottom: 0.5rem;
    }
    h2, h3, h4 { color: #E2E8F0; font-weight: 600; }
    p, div, span, label { color: #94A3B8; }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        border-bottom: 1px solid #1E293B;
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border: none; color: #64748B; font-weight: 500; padding-bottom: 15px; background-color: transparent;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #38BDF8; border-bottom: 2px solid #38BDF8; font-weight: 600;
    }

    /* COMPONENTS */
    /* EXTENDER / EXPANDER - SIMPLIFIED TO AVOID ARROW BUG */
    .streamlit-expanderHeader { 
        background-color: #0F172A !important; 
        color: #F8FAFC !important; 
        border-radius: 8px !important;
    }
    /* HIDE ALL ICONS AND ARROWS AGGRESSIVELY */
    .streamlit-expanderHeader svg, .streamlit-expanderHeader i, [data-testid="stExpanderToggleIcon"] { 
        display: none !important; 
        opacity: 0 !important; 
        width: 0 !important; 
    }
    
    /* REMOVE "arrow" TEXT IF IT APPEARS AS CONTENT */
    .streamlit-expanderHeader p { margin-left: 0 !important; }
    
    div[data-testid="stExpander"] { 
        border: 1px solid #1E293B; 
        border-radius: 8px; 
        background-color: #0F172A;
    }

    [data-testid='stFileUploader'] {
        background-color: #0F172A; padding: 20px; border-radius: 12px; border: 1px dashed #334155;
    }
    [data-testid='stFileUploader']:hover { border-color: #38BDF8; background-color: #1E293B; }
    [data-testid='stFileUploader'] section { text-align: center; }
    div[data-testid="stFileUploader"] div, div[data-testid="stFileUploader"] span { color: #E2E8F0 !important; }

    /* ALERTS */
    .stAlert { border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background-color: #0F172A; }
    .stSuccess { background-color: rgba(6, 78, 59, 0.5); border: 1px solid #059669; color: #34D399; }
    .stInfo { background-color: rgba(30, 58, 138, 0.4); border: 1px solid #2563EB; color: #60A5FA; }

    /* BUTTONS */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #38BDF8; border: 1px solid #334155; padding: 14px 28px;
        border-radius: 8px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); width: 100%; margin-top: 10px;
    }
    div.stButton > button:first-child:hover {
        border-color: #38BDF8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.25); color: #E0F2FE; transform: translateY(-1px);
    }
    
    /* FORM SUBMIT (Active) */
    div[data-testid="stForm"] div.stButton > button:first-child {
        background: #059669; color: white; border: none; box-shadow: 0 0 10px rgba(5, 150, 105, 0.4);
    }
    div[data-testid="stForm"] div.stButton > button:first-child:hover {
        background: #10B981; box-shadow: 0 0 20px rgba(16, 185, 129, 0.6); border: none;
    }

    .stProgress > div > div > div > div { background-color: #38BDF8; box-shadow: 0 0 10px #38BDF8; }
    code { color: #38BDF8; background-color: #0F172A; border: 1px solid #1E293B; }
    img { border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.5); display: block; margin-left: auto; margin-right: auto; }
    hr { border-color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FONCTIONS MÉTIER
# -----------------------------------------------------------------------------

def calculate_file_hash(uploaded_file):
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: uploaded_file.read(4096), b""):
         sha256_hash.update(byte_block)
    uploaded_file.seek(0)
    return sha256_hash.hexdigest()

def get_matic_price_eur():
    """Récupère le prix du MATIC en EUR via CoinGecko API."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=matic-network&vs_currencies=eur"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data['matic-network']['eur']
    except Exception:
        return 0.50 # Fallback si l'API échoue

def generate_qr_code(data):
    """Génère un QR Code pour le paiement."""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#38BDF8", back_color="#020617") # Cyber colors
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return buf

def anchor_hash_on_polygon(file_hash, author_name):
    """
    Envoie une transaction REAL sur Polygon pour ancrer le hash + le nom de l'auteur.
    Le champ 'data' contient : "Blob:{hash}|Owner:{name}"
    """
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not w3.is_connected():
            return {"success": False, "error": "Erreur connexion RPC Polygon."}
        
        account = w3.eth.account.from_key(COMPANY_PRIVATE_KEY)
        my_address = account.address
        
        # Préparation de la data unique
        # On nettoie le nom pour éviter des caractères bizarres
        safe_name = "".join(x for x in author_name if x.isalnum() or x in " -_")
        payload = f"Blob:{file_hash}|Owner:{safe_name}"
        
        # Convert to Hex
        data_hex = w3.to_hex(text=payload)

        # Préparation de la transaction
        # UTILISATION DE 'pending' POUR ÉVITER L'ERREUR "REPLACEMENT TRANSACTION UNDERPRICED"
        nonce = w3.eth.get_transaction_count(my_address, 'pending')
        gas_price = w3.eth.gas_price
        
        tx = {
            'nonce': nonce,
            'to': my_address, # Self-transaction
            'value': 0,
            'gas': 60000, # Augmenté pour être sûr
            'gasPrice': int(gas_price * 1.1), # +10% de pourboire pour passer devant
            'chainId': 137, 
            'data': data_hex 
        }
        
        signed_tx = w3.eth.account.sign_transaction(tx, COMPANY_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return {
            "success": True,
            "tx_hash": w3.to_hex(tx_hash),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payload": payload
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# -----------------------------------------------------------------------------
# APPLICATION
# -----------------------------------------------------------------------------

st.title("🛡️ WorkGuard")
st.markdown("### La Preuve d'Antériorité Décentralisée.")
st.markdown("Protégez vos créations (Design, Audio, Contrats) en les ancrant immuablement sur la Blockchain Polygon.")
st.markdown("---")

# IMPLÉMENTATION "MANUELLE" DE L'ACCORDÉON POUR ÉVITER LE BUG VISUEL
if "show_help" not in st.session_state:
    st.session_state.show_help = False

_, col_help, _ = st.columns([1, 10, 1]) # Centrage large
with col_help:
    if st.button(f"{'🔽' if st.session_state.show_help else '▶️'} Guide & Mode d'Emploi - À LIRE AVANT D'UTILISER", use_container_width=True):
        st.session_state.show_help = not st.session_state.show_help
        st.rerun()

if st.session_state.show_help:
    st.info("""
    ### 🛡️ Comment ça marche ?
    WorkGuard crée une **Preuve d'Antériorité** irréfutable pour vos fichiers.
    
    1.  **Empreinte Numérique** : Nous calculons le "Hash" (SHA-256) de votre fichier. C'est comme son empreinte digitale unique.
    2.  **Ancrage Blockchain** : Ce Hash est envoyé sur la Blockchain Polygon. Comme la Blockchain est ineffaçable, cela prouve que ce fichier existait à cette date précise.
    3.  **Paternité (Votre Nom)** : Nous inscrivons aussi votre **Nom** (ou Pseudo) à côté de l'empreinte pour prouver que c'est VOUS l'auteur.
    4.  **Confidentialité** : Votre fichier **reste sur votre ordinateur**. Seul le Hash crypté est publié.
    
    ### ⚠️ RÈGLE D'OR : NE MODIFIEZ PAS VOTRE FICHIER
    Pour prouver que vous êtes l'auteur, vous devrez présenter **exactement le même fichier** dans le futur.
    
    *   Si vous changez un seul pixel, une virgule, ou un métadonnée, **le Hash changera**.
    *   La preuve ne fonctionnera plus pour ce nouveau fichier.
    
    👉 **Conseil :** Archivez une copie originale de votre œuvre dans un dossier sûr (ex: "Mes Créations Protégées") et n'y touchez plus.
    """)

# CHECK CONFIGURATION
if not MOCK_MODE and (COMPANY_PRIVATE_KEY == "0x..." or "YourCompany" in COMPANY_WALLET_ADDRESS):
    st.error("🚨 **CONFIGURATION REQUISE**")
    st.warning("Vous êtes en mode **RÉEL** mais vous n'avez pas configuré vos clés Polygon.")
    st.markdown("""
    1. Ouvrez `app.py`.
    2. Remplacez `COMPANY_WALLET_ADDRESS` par votre adresse publique (pour recevoir les 2€).
    3. Créez `.streamlit/secrets.toml` avec votre clé privée (pour payer le gaz).
    """)
    st.info("💡 En attendant, repassez `MOCK_MODE = True` pour tester l'interface.")
    st.stop()

tab1, tab2 = st.tabs(["🔒 PROTÉGER UNE ŒUVRE", "🔍 VÉRIFIER UNE PREUVE"])

# --- ONGLET 1 : PROTECTION & PAIEMENT ---
with tab1:
    st.markdown("#### 1. Importez votre fichier")
    st.info("ℹ️ Vos fichiers sont traités localement. Seule l'empreinte cryptographique est envoyée.")
    
    uploaded_file = st.file_uploader("Glissez votre fichier ici", type=['png', 'jpg', 'jpeg', 'pdf', 'mp3', 'wav', 'mp4', 'mov', 'avi', 'mkv'])

    if uploaded_file:
        file_hash = calculate_file_hash(uploaded_file)
        st.write("Empreinte unique (SHA-256) :")
        st.code(file_hash, language="text")
        
        st.divider()
        st.markdown("#### 2. Identité de l'Auteur")
        author_name = st.text_input("Votre Nom ou Pseudonyme (sera gravé sur la Blockchain)", placeholder="Ex: Satoshi Nakamoto")
        
        if author_name:
            st.divider()
            st.markdown("#### 3. Paiement du Service")
            
            # Prix Fixe en POL
            cost_in_pol = 20
            
            # CENTERED LAYOUT
            _, col_center, _ = st.columns([1, 2, 1])  # Middle column is 2x width of sides
            
            with col_center:
                # Card-like container
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <h2 style="color: #38BDF8; margin: 0;">{cost_in_pol} POL</h2>
                        <p style="color: #94A3B8; font-size: 0.8em; margin-bottom: 15px;">TOTAL À PAYER (POLYGON)</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # EIP-681 Payment URI
                    amount_wei = int(cost_in_pol * 10**18)
                    payment_uri = f"ethereum:{COMPANY_WALLET_ADDRESS}@137?value={amount_wei}"
                    qr_img = generate_qr_code(payment_uri)
                    
                    # Centering Image
                    st.image(qr_img, width=220, caption="Scanner depuis votre app (Phantom, MetaMask...)", use_column_width=False)
                    
                    st.divider()
                    
                    st.markdown("<p style='text-align: center; font-size: 0.8em; margin-bottom: 5px;'>Ou envoyez manuellement à cette adresse :</p>", unsafe_allow_html=True)
                    st.code(COMPANY_WALLET_ADDRESS, language="text")

            # --- LOGIQUE DE VÉRIFICATION DU SOLDE (VIGILE) ---
            
            # 1. On mémorise le solde AVANT le paiement (si pas déjà fait pour ce fichier)
            if 'initial_balance_wei' not in st.session_state:
                w3 = Web3(Web3.HTTPProvider(RPC_URL))
                try:
                    balance_wei = w3.eth.get_balance(COMPANY_WALLET_ADDRESS)
                    st.session_state['initial_balance_wei'] = balance_wei
                except Exception as e:
                    st.error(f"Erreur lecture solde: {str(e)}")
                    st.stop()

            # CENTER BUTTON & WARNING
            _, col_cta, _ = st.columns([1, 2, 1])
            with col_cta:
                st.warning("⚠️ Une fois le paiement envoyé, cliquez sur le bouton ci-dessous.")
                do_check = st.button("✅ VÉRIFIER LE PAIEMENT & ANCRER")

            # Bouton de validation SÉCURISÉ
            # On utilise un container vide pour le résultat ou on vérifie le state
            if "proof_cache" not in st.session_state:
                st.session_state.proof_cache = {}

            if do_check:
                
                if MOCK_MODE:
                    payment_verified = True # En Mock, on laisse passer
                else:
                    with st.spinner("Vérification de la réception des fonds sur la Blockchain..."):
                        time.sleep(1) # Petit temps pour laisser la blockchain respirer
                        w3 = Web3(Web3.HTTPProvider(RPC_URL))
                        current_balance_wei = w3.eth.get_balance(COMPANY_WALLET_ADDRESS)
                        
                        # Calcul de la différence
                        diff_wei = current_balance_wei - st.session_state['initial_balance_wei']
                        diff_pol = float(w3.from_wei(diff_wei, 'ether'))
                        
                        # Seuil de tolérance (on accepte si on a reçu au moins 98% du prix)
                        expected_pol = cost_in_pol * 0.98
                        
                        # LOGIQUE PRINCIPALE : On vérifie le paiement OU on est en mode Dev
                        if diff_pol >= expected_pol or DEV_BYPASS_PAYMENT:
                            payment_verified = True
                            if DEV_BYPASS_PAYMENT:
                                st.warning("⚠️ PAIEMENT NON VÉRIFIÉ (Mode Développeur Actif)")
                            else:
                                st.success(f"Paiement confirmé ! Reçu: {diff_pol:.4f} POL")
                        else:
                            payment_verified = False
                            st.error(f"❌ Paiement non détecté ou insuffisant.")
                            st.warning(f"Attendu: +{cost_in_pol:.4f} POL | Reçu: {diff_pol:.4f} POL")
                
                if payment_verified:
                    st.success("Paiement reçu ! Ancrage en cours...")
                    
                    my_bar = st.progress(0, text="Connexion à Polygon...")
                    steps = [(30, "Signature de la transaction..."), (60, "Diffusion sur le réseau..."), (90, "Confirmation...")]
                    
                    for p, t in steps:
                        time.sleep(0.5)
                        my_bar.progress(p, text=t)
                    
                    # REEL ANCRAGE
                    if MOCK_MODE:
                         result = {"success": True, "tx_hash": "0xMOCK_HASH_" + file_hash[:10], "timestamp": str(datetime.now()), "payload": f"Blob:{file_hash}|Owner:{author_name}"}
                    else:
                        result = anchor_hash_on_polygon(file_hash, author_name)
                    
                    my_bar.progress(100, text="Terminé !")

                    if result["success"]:
                        st.balloons()
                        # SAUVEGARDE DU RÉSULTAT DANS LE STATE
                        st.session_state.proof_cache[file_hash] = result
                    else:
                        st.error(f"Echec de l'ancrage : {result.get('error')}")

            # AFFICHAGE DU RÉSULTAT (PERSISTANT)
            if file_hash in st.session_state.proof_cache:
                result = st.session_state.proof_cache[file_hash]
                st.success("✅ **FÉLICITATIONS ! VOTRE ŒUVRE EST PROTÉGÉE.**")
                
                # Manual Expander Logic
                if "show_cert" not in st.session_state:
                    st.session_state.show_cert = True
                
                _, col_cert, _ = st.columns([1, 2, 1])
                with col_cert:
                    if st.button(f"{'🔽' if st.session_state.show_cert else '▶️'} Voir le Certificat de Preuve", use_container_width=True):
                        st.session_state.show_cert = not st.session_state.show_cert
                        st.rerun()
                
                if st.session_state.show_cert:
                    with st.container(border=True):
                        st.markdown("### 📜 Certificat WorkGuard")
                        
                        st.write("**Propriétaire**")
                        st.info(author_name)
                        
                        st.write("**Fichier**")
                        st.text(uploaded_file.name)
                        
                        st.write("**Empreinte (Hash)**")
                        st.code(file_hash, language="text")
                        
                        st.write("**Donnée Gravée**")
                        st.code(result.get('payload'), language="text")
                        
                        col_date, col_tx = st.columns([1, 2])
                        with col_date:
                            st.write("**Date**")
                            st.text(result['timestamp'])
                        with col_tx:
                            st.write("**Transaction ID (TX)**")
                            st.code(result['tx_hash'], language="text")
                        
                        link = f"https://polygonscan.com/tx/{result['tx_hash']}"
                        st.markdown(f"[🔎 Voir sur PolygonScan]({link})")
                        st.caption("Sur PolygonScan, cliquez sur 'Click to see More' -> 'Input Data' -> 'View as UTF-8' pour lire votre nom.")

# --- ONGLET 2 : VÉRIFICATION ---
with tab2:
    st.markdown("#### Vérifier l'authenticité d'un fichier")
    check_file = st.file_uploader("Upload le fichier à vérifier", key="verify")
    if check_file:
        check_hash = calculate_file_hash(check_file)
        st.write(f"Hash calculé : `{check_hash}`")
        st.info("Pour vérifier, collez ce hash dans la barre de recherche de PolygonScan (Input Data).")
        st.markdown(f"[Ouvrir PolygonScan](https://polygonscan.com/)")

st.markdown("---")
st.caption("🔒 WorkGuard v2.0 (Live Polygon) - Sécurisé par la Mathématique.")
