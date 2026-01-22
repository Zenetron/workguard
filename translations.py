TRANSLATIONS = {
    "fr": {
        "page_title": "WorkGuard - Preuve d'Antériorité",
        "header_title": "La preuve d'antériorité décentralisée.",
        "header_subtitle": "Protégez vos créations (Vidéos, Photos, Audios, Contrats) en les ancrant immuablement sur la Blockchain Polygon.",
        "tab_protect": "🔒 PROTÉGER UNE ŒUVRE",
        "tab_verify": "🔍 VÉRIFIER UNE PREUVE",
        
        # Guide
        "guide_title": "ℹ️ Guide & Mode d'Emploi - À LIRE AVANT D'UTILISER",
        "guide_html": """
        <div style="text-align: center; background-color: rgba(56, 189, 248, 0.1); padding: 20px; border-radius: 10px; border: 1px solid #38BDF8;">
            <h3 style="margin-top: 0;">🛡️ Comment ça marche ?</h3>
            <p>WorkGuard crée une <strong>Preuve d'Antériorité</strong> irréfutable pour vos fichiers.</p>
            <ul style="list-style-position: inside; text-align: left; display: inline-block;">
                <li><strong>Empreinte Numérique</strong> : Hash SHA-256 unique.</li>
                <li><strong>Ancrage Blockchain</strong> : Preuve ineffaçable sur Polygon.</li>
                <li><strong>Paternité</strong> : Votre Nom gravé à jamais.</li>
                <li><strong>Confidentialité</strong> : Vos fichiers restent chez vous.</li>
            </ul>
            <br><br>
            <h4>⚠️ RÈGLE D'OR : NE MODIFIEZ PAS VOTRE FICHIER</h4>
            <p>Un seul pixel changé = Hash différent = Preuve invalide.</p>
            <p>👉 <strong>Conseil :</strong> Archivez l'original précieusement.</p>
        </div>
        """,
        
        # Tab 1
        "step_1": "#### 1. Importez votre fichier",
        "step_1_info": "ℹ️ Vos fichiers sont traités localement. Seule l'empreinte cryptographique est envoyée.",
        "upload_label": "Glissez votre fichier ici",
        "hash_label": "Empreinte unique (SHA-256) :",
        
        "step_2": "#### 2. Identité de l'Auteur",
        "author_label": "Votre Nom ou Pseudonyme (sera gravé sur la Blockchain)",
        "author_placeholder": "Ex: Satoshi Nakamoto",
        "wallet_warning": "⚠️ **Attention** : Vous devez payer uniquement via le réseau **Polygon (MATIC / POL)**. Les paiements via Ethereum seront perdus.",
        "wallet_label": "Votre Adresse Polygon (Réseau Polygon uniquement)",
        "wallet_placeholder": "0x...",
        
        "step_3": "#### 3. Paiement du Service",
        "voucher_label": "Code Promo / Voucher (Optionnel)",
        "voucher_placeholder": "Ex: PARTNER24",
        "voucher_success": "✅ Code '{code}' appliqué ! Service GRATUIT !",
        
        "payment_free_title": "OFFERT !",
        "payment_free_desc": "Frais de service pris en charge par le code promo",
        "payment_free_success": "✨ **C'est cadeau !** Nous payons les frais de gaz pour vous.",
        "btn_free": "🎁 LANCER L'ANCRAGE GRATUIT 🎁",
        
        "payment_paid_desc": "TOTAL À PAYER (POLYGON)",
        "scan_caption": "Scanner avec votre Wallet",
        "manual_pay_label": "Ou envoyez manuellement à cette adresse :",
        
        "btn_verify_check": "✅ VÉRIFIER LE PAIEMENT & ANCRER",
        "payment_warning": "⚠️ Une fois le paiement envoyé, cliquez sur le bouton ci-dessous.",
        
        # Errors & Success
        "err_invalid_address": "❌ Adresse invalide. Veuillez renseigner VOTRE adresse Polygon ci-dessus.",
        "err_replay": "⛔️ Ce paiement a déjà été utilisé pour un autre ancrage.",
        "err_not_found": "❌ Aucun paiement trouvé venant de cette adresse.",
        "err_insufficient": "❌ Paiement non détecté ou insuffisant.",
        "success_paid": "✅ Paiement authentifié ! (TX: {tx}...)",
        "info_anchoring": "Paiement validé. Démarrage de l'ancrage...",
        "progress_conn": "Connexion à Polygon...",
        "progress_sign": "Signature de la transaction...",
        "progress_broadcast": "Diffusion sur le réseau...",
        "progress_confirm": "Confirmation...",
        "success_anchored": "✅ **FÉLICITATIONS ! VOTRE PREUVE EST ANCRÉE !**",
        "download_cert": "📄 **TÉLÉCHARGER LE CERTIFICAT (PDF)**",
        "btn_show_cert": "Détails du Certificat",
        "cert_title": "Certificat d'Antériorité Numérique",
        "cert_owner": "Propriétaire",
        "cert_file": "Fichier",
        "cert_hash": "Empreinte (Hash)",
        "cert_data": "Données Ancrées",
        "cert_date": "Date",
        "cert_txid": "Transaction ID",
        "cert_view_polygonscan": "Voir sur PolygonScan",
        "cert_polygonscan_tip": "Ce lien prouve que le fichier existait à cette date.",
        
        # Tab 2
        "verify_intro": "ℹ️ Pour vérifier un fichier, importez-le ci-dessous.",
        "btn_reverse_search": "🔍 Rechercher le Propriétaire (Reverse Search)",
        "spinner_scan": "🕵️‍♂️ Scan de la Blockchain en cours...",
        "success_found": "✅ **PREUVE AUTHENTIQUE TROUVÉE !**",
        "owner_label": "### 👤 Propriétaire : **{name}**",
        "date_label": "📅 **Date d'ancrage** : {date}",
        "raw_data_label": "**Data Brute Blockchain**",
        "tx_id_label": "**ID Transaction**",
        "link_label": "[🔎 Voir la preuve officielle sur PolygonScan]({link})",
        
        "err_verify_fail": "❌ **Preuve introuvable via scan automatique.**",
        "warn_verify_fail": "Le fichier ayant le hash `{hash}` n'a pas été trouvé dans les 1000 dernières transactions.",
        "expander_debug": "🛠 Détails Techniques (Debug)",
        
        "manual_search_title": "🕵️‍♂️ Recherche Avancée (Manuelle)",
        "manual_search_info": "Si la preuve est ancienne, collez l'ID de Transaction (TX) présent sur le certificat PDF.",
        "manual_tx_label": "ID de Transaction (TX Hash)",
        "btn_verify_manual": "Vérifier avec le TX ID",
        "err_tx_mismatch": "❌ Ce TX ne correspond pas à ce fichier.",
        
        # SOS
        "sos_title": "🆘 Mon paiement n'est pas détecté ?",
        "sos_info": "Copiez l'ID de Transaction (TX Hash) depuis votre Wallet.",
        "sos_submit": "Vérifier manuellement cette transaction",
        "sos_success": "✅ Transaction valide trouvée ! Reprise de l'ancrage...",

        # PDF content
        "pdf_title": "CERTIFICAT D'ANTÉRIORITÉ",
        "pdf_subtitle": "WorkGuard - Blockchain Polygon",
        "pdf_owner": "Propriétaire :",
        "pdf_file": "Fichier :",
        "pdf_date": "Date d'ancrage :",
        "pdf_hash": "Empreinte (Hash) :",
        "pdf_tx": "Transaction (TX) :",
        "pdf_disclaimer": "Ce document certifie que l'empreinte numérique du fichier susmentionné a été ancrée de manière immuable sur la Blockchain Polygon à la date indiquée. La présence de cette transaction prouve l'existence du fichier à cet instant précis.",
        "pdf_footer": "Vérifiable sur : https://polygonscan.com/",
        
        # Admin
        "admin_login": "🔐 Accès Admin",
        "admin_pass_placeholder": "Mot de passe...",
        "admin_dashboard": "📊 Tableau de Bord",
        "admin_revenue": "Chiffre d'Affaires",
        "admin_proofs": "Preuves Ancrées",
        "admin_last_sales": "Dernières Ventes",
        "admin_refresh": "🔄 Actualiser les données"
    },
    "en": {
        "page_title": "WorkGuard - Timestamping Proof",
        "header_title": "Decentralized Proof of Existence.",
        "header_subtitle": "Protect your creations (Videos, Photos, Audio, Contracts) by anchoring them immutably on the Polygon Blockchain.",
        "tab_protect": "🔒 PROTECT A FILE",
        "tab_verify": "🔍 VERIFY A PROOF",
        
        # Guide
        "guide_title": "ℹ️ Guide & Instructions - READ BEFORE USE",
        "guide_html": """
        <div style="text-align: center; background-color: rgba(56, 189, 248, 0.1); padding: 20px; border-radius: 10px; border: 1px solid #38BDF8;">
            <h3 style="margin-top: 0;">🛡️ How it works?</h3>
            <p>WorkGuard creates an irrefutable <strong>Proof of Timestamp</strong> for your files.</p>
            <ul style="list-style-position: inside; text-align: left; display: inline-block;">
                <li><strong>Digital Fingerprint</strong>: Unique SHA-256 Hash.</li>
                <li><strong>Blockchain Anchor</strong>: Unstoppable proof on Polygon.</li>
                <li><strong>Authorship</strong>: Your Name engraved forever.</li>
                <li><strong>Privacy</strong>: Your files stay on your device.</li>
            </ul>
            <br><br>
            <h4>⚠️ GOLDEN RULE: DO NOT MODIFY YOUR FILE</h4>
            <p>One single pixel changed = Different Hash = Invalid Proof.</p>
            <p>👉 <strong>Tip:</strong> Archive the original file safely.</p>
        </div>
        """,
        
        # Tab 1
        "step_1": "#### 1. Import your file",
        "step_1_info": "ℹ️ Your files are processed locally. Only the cryptographic fingerprint is sent.",
        "upload_label": "Drag and drop your file here",
        "hash_label": "Unique Fingerprint (SHA-256):",
        
        "step_2": "#### 2. Author Identity",
        "author_label": "Your Name or Alias (will be engraved on Blockchain)",
        "author_placeholder": "Ex: Satoshi Nakamoto",
        "wallet_warning": "⚠️ **Warning**: Use **Polygon Network (MATIC / POL)** only. Payments via Ethereum will be lost.",
        "wallet_label": "Your Polygon Address (Polygon Network only)",
        "wallet_placeholder": "0x...",
        
        "step_3": "#### 3. Service Payment",
        "voucher_label": "Promo Code / Voucher (Optional)",
        "voucher_placeholder": "Ex: PARTNER24",
        "voucher_success": "✅ Code '{code}' applied! Service FREE!",
        
        "payment_free_title": "FREE!",
        "payment_free_desc": "Service fees covered by promo code",
        "payment_free_success": "✨ **It's on us!** We pay the gas fees for you.",
        "btn_free": "🎁 START FREE ANCHORING 🎁",
        
        "payment_paid_desc": "TOTAL TO PAY (POLYGON)",
        "scan_caption": "Scan with your Wallet",
        "manual_pay_label": "Or send manually to this address:",
        
        "btn_verify_check": "✅ VERIFY PAYMENT & ANCHOR",
        "payment_warning": "⚠️ Once payment is sent, click the button below.",
        
        # Errors & Success
        "err_invalid_address": "❌ Invalid Address. Please provide YOUR Polygon address above for identification.",
        "err_replay": "⛔️ This payment has already been used for another anchor.",
        "err_not_found": "❌ No payment found from this address.",
        "err_insufficient": "❌ Payment not detected or insufficient.",
        "success_paid": "✅ Payment authenticated! (TX: {tx}...)",
        "info_anchoring": "Payment valid. Starting anchoring...",
        "progress_conn": "Connecting to Polygon...",
        "progress_sign": "Signing transaction...",
        "progress_broadcast": "Broadcasting to network...",
        "progress_confirm": "Confirmation...",
        "success_anchored": "✅ **CONGRATULATIONS! YOUR PROOF IS ANCHORED!**",
        "download_cert": "📄 **DOWNLOAD CERTIFICATE (PDF)**",
        "btn_show_cert": "Certificate Details",
        "cert_title": "Digital Timestamp Certificate",
        "cert_owner": "Owner",
        "cert_file": "File",
        "cert_hash": "Fingerprint (Hash)",
        "cert_data": "Anchored Data",
        "cert_date": "Date",
        "cert_txid": "Transaction ID",
        "cert_view_polygonscan": "View on PolygonScan",
        "cert_polygonscan_tip": "This link proves the file existed at this date.",
        
        # Tab 2
        "verify_intro": "ℹ️ To verify a file, import it below.",
        "btn_reverse_search": "🔍 Find Owner (Reverse Search)",
        "spinner_scan": "🕵️‍♂️ Scanning Blockchain...",
        "success_found": "✅ **AUTHENTIC PROOF FOUND!**",
        "owner_label": "### 👤 Owner: **{name}**",
        "date_label": "📅 **Anchored on**: {date}",
        "raw_data_label": "**Raw Blockchain Data**",
        "tx_id_label": "**Transaction ID**",
        "link_label": "[🔎 View official proof on PolygonScan]({link})",
        
        "err_verify_fail": "❌ **Proof not found via auto-scan.**",
        "warn_verify_fail": "File with hash `{hash}` was not found in the last 1000 transactions.",
        "expander_debug": "🛠 Technical Details (Debug)",
        
        "manual_search_title": "🕵️‍♂️ Advanced Search (Manual)",
        "manual_search_info": "If the proof is old, paste the Transaction ID (TX) from the PDF certificate.",
        "manual_tx_label": "Transaction ID (TX Hash)",
        "btn_verify_manual": "Verify with TX ID",
        "err_tx_mismatch": "❌ This TX does not correspond to this file.",
        
        # SOS
        "sos_title": "🆘 My payment is not detected?",
        "sos_info": "Copy Transaction ID (TX Hash) from your Wallet.",
        "sos_submit": "Manually Verify Transaction",
        "sos_success": "✅ Valid transaction found! Resuming anchoring...",

        # PDF content
        "pdf_title": "PROOF OF TIMESTAMP",
        "pdf_subtitle": "WorkGuard - Polygon Blockchain",
        "pdf_owner": "Owner:",
        "pdf_file": "File:",
        "pdf_date": "Timestamp Date:",
        "pdf_hash": "Fingerprint (Hash):",
        "pdf_tx": "Transaction (TX):",
        "pdf_disclaimer": "This document certifies that the digital fingerprint of the mentioned file has been immutably anchored on the Polygon Blockchain at the indicated date. The presence of this transaction proves the existence of the file at this precise moment.",
        "pdf_footer": "Verifiable on: https://polygonscan.com/",
        
        # Admin
        "admin_login": "🔐 Admin Access",
        "admin_pass_placeholder": "Password...",
        "admin_dashboard": "📊 Dashboard",
        "admin_revenue": "Revenue",
        "admin_proofs": "Anchored Proofs",
        "admin_last_sales": "Last Sales",
        "admin_refresh": "🔄 Refresh Data"
    }
}
