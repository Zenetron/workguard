import streamlit as st
import hashlib
import time
import random
import requests
import qrcode
from io import BytesIO
import os
import tempfile
from datetime import datetime
from web3 import Web3

from eth_account import Account
from fpdf import FPDF
import base64
from translations import TRANSLATIONS

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="WorkGuard - Preuve d'Antériorité",
    page_icon="favicon.png",
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
# RÉCUPÉRATION SÉCURISÉE (Local vs Prod)
# 1. D'abord on regarde si une Variable d'Environnement existe (Render/Prod)
# 1. D'abord on regarde si une Variable d'Environnement existe (Render/Prod)
COMPANY_PRIVATE_KEY = os.environ.get("private_key", "0x...")

# 2. Sinon on tente le fichier local secrets.toml (Dev Local) - Uniquement si le fichier existe
if COMPANY_PRIVATE_KEY == "0x..." and os.path.exists(".streamlit/secrets.toml"):
    try:
        COMPANY_PRIVATE_KEY = st.secrets.get("private_key", "0x...")
    except Exception:
        pass


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
st.markdown('<link rel="apple-touch-icon" href="app/static/apple-touch-icon.png">', unsafe_allow_html=True) # Try app/static path for Render
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

# -----------------------------------------------------------------------------
# GLOBAL STATE (ANTI-REPLAY CACHE)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_used_tx_registry():
    """Retourne un set partagé pour stocker les TX déjà utilisées."""
    return set()

used_tx_registry = get_used_tx_registry()

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

def find_proof_in_history(target_hash):
    """
    Scanne l'historique du Wallet Company sur PolygonScan pour retrouver une preuve.
    Retourne (proof_dict, debug_info_dict).
    """
    debug_info = {"url": "", "status": "", "message": "", "tx_count": 0, "error": ""}
    try:
        # API PolygonScan (Gratuite, sans clé = limité à 5req/sec)
        # On récupère les 1000 dernières transactions (desc)
        url = f"https://api.polygonscan.com/api?module=account&action=txlist&address={COMPANY_WALLET_ADDRESS}&startblock=0&endblock=99999999&page=1&offset=1000&sort=desc"
        debug_info["url"] = url
        
        # Ajout du User-Agent pour éviter le blocage 403/NOTOK
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        debug_info["status"] = data.get('status')
        debug_info["message"] = data.get('message')
        
        if data['status'] != '1':
            debug_info["error"] = f"API Error: {data.get('message')}"
            return None, debug_info # Pas de data ou erreur
            
        txs = data['result']
        debug_info["tx_count"] = len(txs)
        
        for tx in txs:
            input_data = tx.get('input', '')
            
            # Si input vide ou trop court, on skip
            if not input_data or len(input_data) < 10:
                continue
                
            # Décodage Hex -> Texte
            try:
                decoded = bytes.fromhex(input_data[2:]).decode('utf-8', errors='ignore')
            except:
                continue
                
            # Recherche du pattern Blob:{hash}
            if f"Blob:{target_hash}" in decoded:
                # BINGO !
                import re
                match = re.search(r"Owner:([^|]+)", decoded)
                owner_name = match.group(1) if match else "Inconnu"
                
                proof_data = {
                    "success": True,
                    "tx_hash": tx['hash'],
                    "timestamp": datetime.fromtimestamp(int(tx['timeStamp'])),
                    "owner_name": owner_name,
                    "payload": decoded
                }
                return proof_data, debug_info
                
        return None, debug_info # Pas trouvé dans les 1000 dernières
        
    except Exception as e:
        debug_info["error"] = str(e)
        print(f"Erreur Scan History: {e}")
        return None, debug_info

@st.cache_data(ttl=300) # Cache 5 minutes
def scan_company_stats():
    """Récupère les stats : CA Total, Nombre de Clients, etc."""
    stats = {"revenue_pol": 0.0, "client_count": 0, "proof_count": 0, "voucher_est": 0, "last_sales": []}
    
    try:
        url = f"https://api.polygonscan.com/api?module=account&action=txlist&address={COMPANY_WALLET_ADDRESS}&startblock=0&endblock=99999999&page=1&offset=10000&sort=desc"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data['status'] == '1':
            txs = data['result']
            payment_tx_count = 0
            
            for tx in txs:
                # 1. Revenu (Incoming TX > 0)
                if tx['to'].lower() == COMPANY_WALLET_ADDRESS.lower() and int(tx['value']) > 0:
                    val_pol = float(Web3.from_wei(int(tx['value']), 'ether'))
                    stats['revenue_pol'] += val_pol
                    stats['client_count'] += 1
                    stats['client_count'] += 1
                    
                    # On ne compte PAS les "gros" transferts (ex: > 100 POL) comme des ventes
                    # On suppose que ce sont des fonds d'exploitation ("Funding")
                    if val_pol < 100:  
                        payment_tx_count += 1
                    
                    
                    if len(stats['last_sales']) < 5:
                        stats['last_sales'].append({
                            "date": datetime.fromtimestamp(int(tx['timeStamp'])).strftime("%Y-%m-%d %H:%M"),
                            "amount": f"{val_pol:.2f} POL",
                            "from": tx['from']
                        })
                
                # 2. Preuves (Outgoing TX avec Data)
                if tx['from'].lower() == COMPANY_WALLET_ADDRESS.lower() and len(tx['input']) > 10:
                     stats['proof_count'] += 1
            
            # Estimation Vouchers = Total Preuves - Paiements Reçus
            # (Si on a ancré plus qu'on a été payé, c'est du gratuit/voucher)
            stats['voucher_est'] = max(0, stats['proof_count'] - payment_tx_count)
                     
    except Exception as e:
        print(f"Stats Error: {e}")
        
    return stats

def anchor_hash_on_polygon(file_hash, author_name, recipient_address=None):
    """
    Envoie une transaction REAL sur Polygon pour ancrer le hash + le nom de l'auteur.
    Le champ 'data' contient : "Blob:{hash}|Owner:{name}"
    Si recipient_address est fourni (et valide), la transaction est envoyée vers lui (0 POL).
    Sinon, c'est une self-transaction.
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
        
        # Validation de l'adresse destinataire (si fournie)
        target_address = my_address # Par défaut : Self-transaction
        if recipient_address and Web3.is_address(recipient_address):
            try:
                target_address = Web3.to_checksum_address(recipient_address)
            except:
                pass # On reste sur my_address si invalide

        tx = {
            'nonce': nonce,
            'to': target_address,  # VERS le client ou VERS nous-même
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

    except Exception as e:
        return {"success": False, "error": str(e)}

    except Exception as e:
        return {"success": False, "error": str(e)}

def scan_recent_blocks(expected_sender, expected_amount_pol, company_address, lookback_blocks=60):
    """Scanne les derniers blocs pour trouver une transaction spécifique (Sécurité stricte)."""
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        latest_block = w3.eth.block_number
        
        # On regarde les N derniers blocs (60 blocs ~ 2-3 minutes) - Optimisé pour éviter timeouts
        for block_num in range(latest_block, latest_block - lookback_blocks, -1):
            block = w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                # Vérification match
                if (tx['to'] and tx['to'].lower() == company_address.lower()) and \
                   (tx['from'].lower() == expected_sender.lower()):
                    
                    # Vérif montant
                    val_eth = float(w3.from_wei(tx['value'], 'ether'))
                    if val_eth >= (expected_amount_pol * 0.98):
                        return True, tx['hash'].hex()
                        
        return False, None
    except Exception as e:
        return False, None

def verify_manual_tx(tx_hash, expected_amount_pol, company_address, expected_sender=None):
    """Vérifie manuellement une transaction donnée par son hash."""
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        tx = w3.eth.get_transaction(tx_hash)
        
        # 1. Vérifier le destinataire
        if tx['to'].lower() != company_address.lower():
            return False, "Ce paiement n'a pas été envoyé à la bonne adresse."
            
        # 2. Vérifier le montant (avec tolérance 98%)
        value_pol = float(w3.from_wei(tx['value'], 'ether'))
        if value_pol < (expected_amount_pol * 0.98):
             return False, f"Montant insuffisant ({value_pol} POL). Requis : {expected_amount_pol} POL."

        # 3. Vérifier l'expéditeur (si fourni)
        if expected_sender and expected_sender.strip():
             if tx['from'].lower() != expected_sender.lower().strip():
                 return False, f"Mauvais expéditeur. Le paiement vient de {tx['from']} mais vous avez déclaré {expected_sender}."
             
             
        # 4. Vérification Temporelle (Anti-Replay)
        # On rejette les transactions vieilles de plus de 3 minutes (180s)
        try:
            block = w3.eth.get_block(tx['blockNumber'])
            tx_timestamp = block['timestamp']
            current_timestamp = time.time()
            if (current_timestamp - tx_timestamp) > 180: # 3 minutes
                 return False, f"Transaction expirée. Elle date de plus de 3 minutes. Veuillez refaire un paiement récent."
        except:
             pass # Si on arrive pas à lire le temps, on laisse passer (fail-open) ou fail-close selon besoin. Ici fail-open pour UX.

        return True, "OK"
    except Exception as e:
        return False, f"Transaction invalide ou introuvable : {str(e)}"

def create_pdf_certificate(author_name, file_name, file_hash, tx_hash, timestamp, payload, lang="fr"):
    """Génère un PDF officiel pour le certificat."""
    T_PDF = TRANSLATIONS[lang]
    
    pdf = FPDF()
    pdf.add_page()
    
    # Cadre
    pdf.set_line_width(1)
    pdf.rect(5, 5, 200, 287)
    pdf.set_line_width(0.5)
    pdf.rect(8, 8, 194, 281)

    # AJOUT LOGO (Top Gauche)
    try:
        # On utilise le favicon généré (128x128)
        # Position X=10, Y=10, Width=35 (Plus gros)
        pdf.image("favicon.png", x=10, y=10, w=35)
    except Exception as e:
        print(f"Erreur Logo PDF: {e}")

    # AJOUT QR CODE (En PREMIER pour être sur la bonne page)
    try:
        # Lien direct vers la transaction
        tx_link = f"https://polygonscan.com/tx/{tx_hash}"
        
        # Génération QR
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(tx_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarde temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            img.save(tmp_file.name)
            tmp_path = tmp_file.name
            
        # Placement au CENTRE, EN HAUT (au-dessus du titre)
        # Page A4 width = 210mm. Img width = 25mm. X = (210-25)/2 = 92.5.
        # Y=10 pour laisser une marge absolue
        pdf.image(tmp_path, x=92.5, y=10, w=25)
        
        # Nettoyage
        os.unlink(tmp_path)
    except Exception as e:
        print(f"Erreur QR PDF: {e}")
    
    # Header
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(23, 37, 84) # Dark Blue
    # On pousse le titre vers le bas de manière EXPLICITE (Force Y=45)
    # Le QR code finit vers Y=38 (8 + 30).
    pdf.set_y(45)
    pdf.cell(0, 10, T_PDF['pdf_title'], 0, 1, 'C')
    pdf.set_font("Arial", '', 14)
    pdf.set_text_color(100, 116, 139) # Gray
    pdf.cell(0, 10, T_PDF['pdf_subtitle'], 0, 1, 'C')
    pdf.ln(20)
    
    # Details Body
    pdf.set_text_color(0, 0, 0)
    
    def add_field(label, value):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(50, 10, label, 0, 0)
        pdf.set_font("Courier", '', 11) # Monospace pour les codes
        pdf.multi_cell(0, 10, value)
        pdf.ln(5)

    add_field(T_PDF['pdf_owner'], author_name)
    add_field(T_PDF['pdf_file'], file_name)
    add_field(T_PDF['pdf_date'], str(timestamp))
    pdf.ln(5)
    
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_x(15)
    add_field(T_PDF['pdf_hash'], file_hash)
    
    pdf.ln(5)
    pdf.set_x(15)
    add_field(T_PDF['pdf_tx'], tx_hash)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, T_PDF['pdf_disclaimer'], 0, 'C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, T_PDF['pdf_footer'], 0, 1, 'C')


    
    return pdf.output(dest='S').encode('latin-1')

# -----------------------------------------------------------------------------
# APPLICATION
# -----------------------------------------------------------------------------

# LANGUAGE SELECTOR (Sidebar)
with st.sidebar:
    st.markdown("### 🌍 Language")
    lang_choice = st.selectbox("Language", ["Français 🇫🇷", "English 🇬🇧"], label_visibility="collapsed")

lang = "fr" if "Français" in lang_choice else "en"
T = TRANSLATIONS[lang]

# ADMIN SECTION (SIDEBAR BOTTOM)
st.sidebar.markdown("---")
with st.sidebar.expander(T['admin_login']):
    # Utilisation d'un key pour pouvoir reset le mot de passe
    if "admin_pass_input" not in st.session_state: st.session_state.admin_pass_input = ""
    
    password = st.text_input(T['admin_pass_placeholder'], type="password", key="admin_pass_input")
    
    # Check Password (Priorité Env Var pour Render, puis Secrets, puis Default)
    ADMIN_PASS = os.environ.get("admin_password", "admin123")
    
    # Si on est en local avec secrets.toml, on regarde dedans
    if os.path.exists(".streamlit/secrets.toml"):
        try:
            ADMIN_PASS = st.secrets.get("admin_password", ADMIN_PASS)
        except: pass
    
    if password == ADMIN_PASS:
        if not st.session_state.get('admin_unlocked'):
            st.success("🔓 Access Granted")
            st.session_state['admin_unlocked'] = True
    else:
        # Seul cas où on verrouille : si le mot de passe est faux (et non vide)
        if password: 
            st.error("❌ Invalid")
            st.session_state['admin_unlocked'] = False
        # Si vide, on ne fait rien (ou on laisse verrouillé si c'était verrouillé)
        if not password and st.session_state.get('admin_unlocked'):
             # Cas spécial : Si on vient de se déconnecter, on veut pas se reconnecter
             pass

# ADMIN DASHBOARD OVERLAY
def logout_admin():
    st.session_state['admin_unlocked'] = False
    st.session_state['admin_pass_input'] = ""

if st.session_state.get('admin_unlocked'):
    st.markdown(f"## {T['admin_dashboard']}")
    
    # Boutons côte à côte égalité (50/50)
    col_refresh, col_logout = st.columns(2)
    with col_refresh:
        if st.button(T['admin_refresh'], use_container_width=True):
            scan_company_stats.clear()
            st.rerun()
    with col_logout:
        st.button("🔒 Déconnexion", type="primary", use_container_width=True, on_click=logout_admin)
        
    stats = scan_company_stats()
    
    # 1. METRICS
    ac1, ac2, ac3, ac4 = st.columns(4)
    matic_price = get_matic_price_eur()
    
    ac1.metric(T['admin_revenue'], f"{stats['revenue_pol']:.2f} POL", f"{stats['revenue_pol'] * matic_price:.2f} €")
    ac2.metric(T['admin_proofs'], stats['proof_count'])
    ac3.metric("Clients (Payants)", stats['client_count'])
    ac4.metric("Vouchers (Est.)", stats['voucher_est'])
    
    st.markdown("---")
    
    # 2. LAST SALES
    st.markdown(f"### {T['admin_last_sales']}")
    for sale in stats['last_sales']:
        st.text(f"💰 {sale['date']} | {sale['amount']} | {sale['from']}")
    
    st.markdown("---")

# IMPLÉMENTATION STANDARD
# Logo Centré + Titre (Base64 pour centrage parfait + désactivation click)
try:
    with open("favicon.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(
            f"""
            <div style='display: flex; justify-content: center; margin-bottom: 0px;'>
                <img src="data:image/png;base64,{data}" width="120" style="pointer-events: none; position: relative; left: 12px;">
            </div>
            """,
            unsafe_allow_html=True
        )
except Exception as e:
    st.error(f"Erreur chargement logo: {e}")

st.markdown("<h1 style='text-align: center; margin-top: -20px;'>WorkGuard</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>{T['header_title']}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>{T['header_subtitle']}</p>", unsafe_allow_html=True)
st.markdown("---")

# IMPLÉMENTATION STANDARD (Car fixée par CSS)
with st.expander(T['guide_title']):
    st.markdown(T['guide_html'], unsafe_allow_html=True)

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

tab1, tab2 = st.tabs([T['tab_protect'], T['tab_verify']])

# --- ONGLET 1 : PROTECTION & PAIEMENT ---
with tab1:
    st.markdown(T['step_1'])
    st.info(T['step_1_info'])
    
    uploaded_file = st.file_uploader(T['upload_label'], type=['png', 'jpg', 'jpeg', 'pdf', 'mp3', 'wav', 'mp4', 'mov', 'avi', 'mkv'])

    if uploaded_file:
        file_hash = calculate_file_hash(uploaded_file)
        st.write(T['hash_label'])
        st.code(file_hash, language="text")
        
        st.divider()
        st.markdown(T['step_2'])
        author_name = st.text_input(T['author_label'], placeholder=T['author_placeholder'])
        
        # AJOUT : Adresse Wallet Client (OBLIGATOIRE POUR SÉCURITÉ)
        st.caption(T['wallet_warning'])
        recipient_address = st.text_input(T['wallet_label'], placeholder=T['wallet_placeholder'])
        
        # UX : On affiche la suite si le NOM est rempli (l'adresse est optionnelle si Voucher)
        if author_name:
            st.divider()
            st.markdown(T['step_3'])
            
            # Prix Fixe en POL
            cost_in_pol = 20
            
            # --- VOUCHER SYSTEM ---
            voucher_code = st.text_input(T['voucher_label'], placeholder=T['voucher_placeholder'])
            
            # Liste des codes valides (Récupérés depuis secrets/env pour sécurité)
            # Format attendu dans secrets.toml : voucher_codes = "CODE1,CODE2,CODE3"
            VALID_VOUCHERS = []
            
            # 1. Chargement depuis Secrets TOML (Local) - Seulement si fichier existe
            if os.path.exists(".streamlit/secrets.toml"):
                try:
                     if "voucher_codes" in st.secrets:
                         VALID_VOUCHERS = st.secrets["voucher_codes"].split(",")
                except: pass
            
            # 2. Chargement depuis ENV (Render) - Priorité Absolue
            if "VOUCHER_CODES" in os.environ:
                 VALID_VOUCHERS = os.environ["VOUCHER_CODES"].split(",")
            
            # Fallback par défaut (au cas où, pour démo)
            if not VALID_VOUCHERS:
                 VALID_VOUCHERS = ["VIP2025", "FRIEND50"]
            
            is_free = False
            if voucher_code and voucher_code.strip().upper() in VALID_VOUCHERS:
                cost_in_pol = 0
                is_free = True
                st.success(T['voucher_success'].format(code=voucher_code.upper()))
            # ----------------------
            
            # CENTERED LAYOUT
            _, col_center, _ = st.columns([1, 2, 1])  # Middle column is 2x width of sides
            
            with col_center:
                # Card-like container
                with st.container(border=True):
                    
                    if is_free:
                         st.markdown(f"""
                        <div style="text-align: center;">
                            <h2 style="color: #34D399; margin: 0;">{T['payment_free_title']}</h2>
                            <p style="color: #94A3B8; font-size: 0.8em; margin-bottom: 15px;">{T['payment_free_desc']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                         
                         st.success(T['payment_free_success'])
                         
                         # Bouton spécial "Gasless"
                         if st.button(T['btn_free'], type="primary", use_container_width=True):
                             st.session_state.payment_validated = True
                             st.session_state.tx_hash = "VOUCHER_OFFERT" # Fake hash pour le suivi
                             st.rerun()

                    # --- MODE PAYANT (STANDARD) ---
                    else:
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <h2 style="color: #38BDF8; margin: 0;">{cost_in_pol} POL</h2>
                            <p style="color: #94A3B8; font-size: 0.8em; margin-bottom: 15px;">{T['payment_paid_desc']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # EIP-681 Payment URI
                        amount_wei = int(cost_in_pol * 10**18)
                        payment_uri = f"ethereum:{COMPANY_WALLET_ADDRESS}@137?value={amount_wei}"
                        qr_img = generate_qr_code(payment_uri)
                        
                        # Centering Image with nested columns
                        # On utilise 3 colonnes invisibles [1, 2, 1] pour centrer l'image au milieu du container
                        sub_c1, sub_c2, sub_c3 = st.columns([1, 4, 1])
                        with sub_c2:
                            st.image(qr_img, width=220, caption=T['scan_caption'], use_column_width=False)
                        
                        st.divider()
                        
                        st.markdown(f"<p style='text-align: center; font-size: 0.8em; margin-bottom: 5px;'>{T['manual_pay_label']}</p>", unsafe_allow_html=True)
                        st.code(COMPANY_WALLET_ADDRESS, language="text")

            # --- LOGIQUE DE VÉRIFICATION DU SOLDE (VIGILE) ---
            
            # 1. On mémorise le solde AVANT le paiement (si pas déjà fait pour ce fichier)
            if not is_free and 'initial_balance_wei' not in st.session_state:
                w3 = Web3(Web3.HTTPProvider(RPC_URL))
                try:
                    balance_wei = w3.eth.get_balance(COMPANY_WALLET_ADDRESS)
                    st.session_state['initial_balance_wei'] = balance_wei
                except Exception as e:
                    # st.error(f"Erreur lecture solde: {str(e)}") # On évite de bloquer pour si peu
                    pass

            # CENTER BUTTON & WARNING (Seulement si payant)
            if not is_free:
                _, col_cta, _ = st.columns([1, 2, 1])
                with col_cta:
                    st.warning(T['payment_warning'])
                    do_check = st.button(T['btn_verify_check'])
            else:
                do_check = False # Pas de bouton de vérif en mode gratuit (le bouton spécial gère tout)

            # Bouton de validation SÉCURISÉ
            # On utilise un container vide pour le résultat ou on vérifie le state
            if "proof_cache" not in st.session_state:
                st.session_state.proof_cache = {}
            
            # Initialisation du flag de validation dans la session
            if "payment_validated" not in st.session_state:
                st.session_state.payment_validated = False
                
            # --- LOGIQUE DE VÉRIFICATION ---
            
            # Cas 1 : Bouton Principal
            if do_check:
                # SÉCURITÉ : On exige une adresse valide pour vérifier l'origine
                # SÉCURITÉ : On exige une adresse valide pour vérifier l'origine
                if not recipient_address or len(recipient_address) < 10:
                     st.error(T['err_invalid_address'])
                     st.stop()
                     
                if MOCK_MODE:
                    st.session_state.payment_validated = True
                else:
                    # Reset pour nouvelle tentative
                    st.session_state.payment_validated = False
                    
                    found_tx_hash = None
                    
                    # MODE STRICT : Si l'utilisateur nous a donné son adresse
                    if recipient_address and len(recipient_address) > 10:
                        with st.spinner(f"🔍 Scan des 120 derniers blocs (~5 min) de {recipient_address}..."):
                            found, tx_id = scan_recent_blocks(recipient_address, cost_in_pol, COMPANY_WALLET_ADDRESS)
                            if found:
                                # ANTI-REPLAY CHECK
                                if tx_id in used_tx_registry:
                                     st.error(T['err_replay'])
                                     st.warning("Chaque transaction de paiement ne peut servir qu'une seule fois.")
                                else:
                                    st.session_state.payment_validated = True
                                    st.session_state.tx_hash = tx_id # On stocke le hash
                                    # On marque comme utilisé
                                    used_tx_registry.add(tx_id)
                                    st.success(T['success_paid'].format(tx=tx_id[:10]))
                            else:
                                 st.error(T['err_not_found'])
                                 st.info(T['sos_info'])
                                 
                    # MODE CLASSIQUE (Fallback) : Vérification du solde global
                    else:
                        with st.spinner(" Vérification standard (Solde)..."):
                            time.sleep(1)
                            try:
                                w3 = Web3(Web3.HTTPProvider(RPC_URL))
                                current_balance_wei = w3.eth.get_balance(COMPANY_WALLET_ADDRESS)
                                diff_wei = current_balance_wei - st.session_state.get('initial_balance_wei', 0)
                                if diff_wei < 0: diff_wei = 0
                                diff_pol = float(w3.from_wei(diff_wei, 'ether'))
                                
                                if diff_pol >= (cost_in_pol * 0.98):
                                     st.session_state.payment_validated = True
                                else:
                                    st.error(T['err_insufficient'])
                                    st.warning(f"Attendu: +{cost_in_pol:.4f} POL | Reçu: {diff_pol:.4f} POL")
                            except Exception as e:
                                st.error(f"Erreur vérif solde: {e}")

            # SOS FALBACK - VÉRIFICATION MANUELLE
            # On affiche le SOS seulement si pas encore validé ET si ce n'est pas un mode gratuit
            if not st.session_state.payment_validated and not is_free:
                 with st.expander(T['sos_title'], expanded=False):
                    with st.form("sos_form"):
                        st.info(T['sos_info'])
                        manual_tx = st.text_input(T['manual_tx_label'], placeholder="0x...")
                        submit_sos = st.form_submit_button(T['sos_submit'])
                    
                    if submit_sos:
                        # SÉCURITÉ : On exige une adresse valide pour vérifier l'origine
                        if not recipient_address or len(recipient_address) < 10:
                             st.error(T['err_invalid_address'])
                             success = False
                        elif MOCK_MODE:
                            success, msg = True, "Mock OK"
                        else:
                            # On vérifie montant + expéditeur (si fourni)
                            success, msg = verify_manual_tx(manual_tx, cost_in_pol, COMPANY_WALLET_ADDRESS, recipient_address)
                        
                        if success:
                            # ANTI-REPLAY CHECK
                            if manual_tx in used_tx_registry:
                                 st.error(T['err_replay'])
                            else:
                                st.session_state.payment_validated = True
                                st.session_state.tx_hash = manual_tx # On stocke le hash
                                used_tx_registry.add(manual_tx)
                                st.success(T['sos_success'])
                                st.rerun() # Refresh pour afficher la suite
                        else:
                            st.error(f"❌ Erreur : {msg}")
            
            # --- ANCRAGE (SI VALIDÉ ET PAS ENCORE DANS LE CACHE) ---
            if st.session_state.payment_validated and file_hash not in st.session_state.proof_cache:
                
                # Si on a pas de TX hash (mode classique), on met un placeholder
                if "tx_hash" not in st.session_state:
                     st.session_state.tx_hash = "Non spécifié (Mode Solde)"
                     
                st.info(T['info_anchoring'])
                    
                my_bar = st.progress(0, text=T['progress_conn'])
                steps = [(30, T['progress_sign']), (60, T['progress_broadcast']), (90, T['progress_confirm'])]
                
                for p, t in steps:
                    time.sleep(0.5)
                    my_bar.progress(p, text=t)
                
                # REEL ANCRAGE
                if MOCK_MODE:
                        result = {"success": True, "tx_hash": "0xMOCK_HASH_" + file_hash[:10], "timestamp": str(datetime.now()), "payload": f"Blob:{file_hash}|Owner:{author_name}"}
                else:
                    result = anchor_hash_on_polygon(file_hash, author_name, recipient_address)
                
                my_bar.progress(100, text="Terminé !")

                if result["success"]:
                    # SAUVEGARDE DU RÉSULTAT DANS LE STATE
                    st.session_state.proof_cache[file_hash] = result
                    
                    st.balloons()
                    st.success(T['success_anchored'])
                    st.rerun() # Refresh pour afficher le certificat immédiatement
                else:
                    st.error(f"Echec de l'ancrage : {result.get('error')}")

            # AFFICHAGE DU RÉSULTAT (PERSISTANT)
            if file_hash in st.session_state.proof_cache:
                result = st.session_state.proof_cache[file_hash]
                
                # Manual Expander Logic
                if "show_cert" not in st.session_state:
                    st.session_state.show_cert = True
                
                _, col_cert, _ = st.columns([1, 2, 1])
                with col_cert:
                    if st.button(f"{'🔽' if st.session_state.show_cert else '▶️'} {T['btn_show_cert']}", use_container_width=True):
                        st.session_state.show_cert = not st.session_state.show_cert
                        st.rerun()
                
                if st.session_state.show_cert:
                    with st.container(border=True):
                        st.markdown(f"### 📜 {T['cert_title']}")
                        
                        st.write(f"**{T['cert_owner']}**")
                        st.info(author_name)
                        
                        st.write(f"**{T['cert_file']}**")
                        st.text(uploaded_file.name)
                        
                        st.write(f"**{T['cert_hash']}**")
                        st.code(file_hash, language="text")
                        
                        st.write(f"**{T['cert_data']}**")
                        st.code(result.get('payload'), language="text")
                        
                        col_date, col_tx = st.columns([1, 2])
                        with col_date:
                            st.write(f"**{T['cert_date']}**")
                            st.text(result['timestamp'])
                        with col_tx:
                            st.write(f"**{T['cert_txid']}**")
                            st.code(result['tx_hash'], language="text")
                        
                        link = f"https://polygonscan.com/tx/{result['tx_hash']}"
                        st.markdown(f"[🔎 {T['cert_view_polygonscan']}]({link})")
                        st.caption(T['cert_polygonscan_tip'])
                        
                        st.divider()
                        
                        # PDF DOWNLOAD BUTTON
                        # PASSAGE DU LANGUE À CREATE_PDF (Sera implémenté dans Chunk 4)
                        pdf_bytes = create_pdf_certificate(author_name, uploaded_file.name, file_hash, result['tx_hash'], result['timestamp'], result['payload'], lang=lang)
                        
                        st.download_button(
                            label=T['download_cert'],
                            data=pdf_bytes,
                            file_name=f"WorkGuard_Certificat_{file_hash[:8]}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

# --- ONGLET 2 : VÉRIFICATION ---
with tab2:
    st.markdown(T['verify_intro'])
    uploaded_check = st.file_uploader(T['upload_label'] + " (Check)", type=['png', 'jpg', 'jpeg', 'pdf', 'mp3', 'wav', 'mp4', 'mov', 'avi', 'mkv'], key="check")
    
    if uploaded_check:
        check_hash = calculate_file_hash(uploaded_check)
        st.write(T['hash_label'])
        st.code(check_hash, language="text")
        
        if st.button(T['btn_reverse_search']):
            with st.spinner(T['spinner_scan']):
                proof, debug_info = find_proof_in_history(check_hash)
                
            if proof:
                st.balloons()
                st.success(T['success_found'])
                
                # Joli affichage
                with st.container(border=True):
                    st.markdown(T['owner_label'].format(name=proof['owner_name']))
                    st.markdown(T['date_label'].format(date=proof['timestamp']))
                    
                    st.divider()
                    st.write(T['raw_data_label'])
                    st.code(proof['payload'])
                    
                    st.write(T['tx_id_label'])
                    st.code(proof['tx_hash'])
                    
                    link = f"https://polygonscan.com/tx/{proof['tx_hash']}"
                    st.markdown(T['link_label'].format(link=link))
            else:
                 st.error(T['err_verify_fail'])
                 st.warning(T['warn_verify_fail'].format(hash=check_hash))
                 
                 # DEBUG INFO
                 with st.expander(T['expander_debug'], expanded=False):
                     st.write("**Statut API** :", debug_info.get('status'), "| **Message** :", debug_info.get('message'))
                     st.write("**Transactions Scannées** :", debug_info.get('tx_count'))
                     st.write("**Erreur éventuelle** :", debug_info.get('error'))
                     st.write("**Wallet Scanné** :", COMPANY_WALLET_ADDRESS)
                     st.info("Astuce : Si le nombre de TX est 0 ou si l'API status est != 1, le service PolygonScan est peut-être saturé.")
                 
                 # On active le mode manuel persistant
                 st.session_state['show_manual_search'] = True
    
    # Affichage persistant de la recherche manuelle (DÉSINDENTÉ pour être hors du "if button")
    if st.session_state.get('show_manual_search'):
         st.markdown("---")
         with st.expander(T['manual_search_title'], expanded=True):
             st.info(T['manual_search_info'])
             
             with st.form("manual_verify_form"):
                 check_tx_manual = st.text_input(T['manual_tx_label'], placeholder="0x...")
                 submit_manual = st.form_submit_button(T['btn_verify_manual'])
             
             if submit_manual:
                 if not check_tx_manual:
                     st.error("Veuillez entrer un TX Hash.")
                 else:
                    try:
                        w3 = Web3(Web3.HTTPProvider(RPC_URL))
                        tx = w3.eth.get_transaction(check_tx_manual)
                        input_data = tx['input']
                        try:
                            if isinstance(input_data, bytes):
                                decoded = input_data.decode('utf-8', errors='ignore')
                            else:
                                decoded = bytes.fromhex(input_data[2:]).decode('utf-8', errors='ignore')
                        except:
                            decoded = str(input_data)
                            
                        if f"Blob:{check_hash}" in decoded:
                            import re
                            match = re.search(r"Owner:([^|]+)", decoded)
                            owner_name = match.group(1) if match else "Inconnu"
                            
                            st.balloons()
                            st.success(T['success_found'])
                            st.markdown(T['owner_label'].format(name=owner_name))
                        else:
                            st.error(T['err_tx_mismatch'])
                            st.write(f"Hash fichier: {check_hash}")
                            st.write(f"Data TX: {decoded}")
                    except Exception as e:
                        st.error(f"Erreur TX: {e}")

st.markdown("---")
st.caption("🔒 WorkGuard - Sécurisé par la Blockchain.")
