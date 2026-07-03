import os
import json
import statistics
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

# ═══════════════ CONFIGURATION ═══════════════
EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🃏 Cartes à surveiller — recherche LARGE, langue détectée automatiquement
# On surveille chaque carte en JP ET en FR à partir d'une seule recherche
CARTES = [
    {"recherche": "Dracaufeu ex 199/165 151", "nom": "Dracaufeu ex SIR 199/165"},
    {"recherche": "Pikachu AR 173/165 151",   "nom": "Pikachu AR 173/165"},
    {"recherche": "Mew ex 151/165 151",       "nom": "Mew ex 151/165"},
    {"recherche": "Ronflex 143/165 151",      "nom": "Ronflex 143/165"},
]

# 🎯 Seuils
SEUIL_ACHAT = 0.90       # acheter si ≤ -10% de la cote
PRIX_MINIMUM = 3.0       # on ignore les cartes < 3 €
ECART_MAX_COTE = 0.5     # on ignore les prix < 50% ou > 150% de la cote
MIN_ANNONCES = 3         # au moins 3 annonces pour une cote fiable
FRAIS_PORT_MAX = 6.0     # on ignore si les frais de port dépassent 6 €


FICHIER_MEMOIRE = "deja_alertees.json"

# 🚫 Mots interdits (lots, coffrets, accessoires ET gradées)
MOTS_INTERDITS = [
    "lot", "lots", "booster", "box", "coffret", "display", "bundle",
    "protection", "sleeve", "classeur", "album", "playmat", "tapis",
    "psa", "pca", "ccc", "cca", "gradée", "graded", "grade", "gradee",
]

# 🌍 Détection de langue (mots-clés dans le titre)
INDICES_JP = ["japonais", "japonaise", "japanese", "jpn", "jp", "sv2a", "japan"]
INDICES_FR = ["français", "francaise", "française", "francais", "ev3.5", "ev 3.5", "neuve", "neuf"]



def detecter_langue(titre):
    """Devine la langue de la carte à partir du titre. Retourne 'JP', 'FR' ou None."""
    t = titre.lower()
    jp = any(mot in t for mot in INDICES_JP)
    fr = any(mot in t for mot in INDICES_FR)
    if jp and not fr:
        return "JP"
    if fr and not jp:
        return "FR"
    return None  # ambigu ou inconnu → on ignore (prudence)


def titre_interdit(titre):
    """Retourne True si le titre contient un mot interdit."""
    t = titre.lower()
    return any(mot in t for mot in MOTS_INTERDITS)


def charger_memoire():
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def sauver_memoire(memoire):
    with open(FICHIER_MEMOIRE, "w", encoding="utf-8") as f:
        json.dump(list(memoire), f)


def obtenir_token():
    """Récupère un token OAuth eBay automatiquement."""
    creds = f"{EBAY_APP_ID}:{EBAY_CERT_ID}"
    creds_b64 = base64.b64encode(creds.encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {creds_b64}",
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }
    r = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers=headers, data=data, timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]
    
def get_frais_port(annonce):
    """Renvoie les frais de port en €, ou None si l'info est absente."""
    options = annonce.get("shippingOptions", [])
    if not options:
        return None  # port inconnu
    cout = options[0].get("shippingCost", {})
    try:
        return float(cout.get("value"))
    except (ValueError, TypeError):
        return None  # port inconnu
 


def rechercher_ebay(token, recherche):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_FR",
    }
    params = {
        "q": recherche,
        "limit": 50,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("itemSummaries", [])



def envoyer_alerte(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    requests.post(url, data=data, timeout=30)


def analyser_langue(annonces, langue, nom, memoire):
    """Calcule la cote pour une langue donnée et alerte les bonnes affaires."""
    nb = 0
    # On garde les prix valides pour cette langue
    prix_valides = [p for p, a in annonces]
    if len(prix_valides) < MIN_ANNONCES:
        print(f"   ⏭️ [{langue}] Pas assez d'annonces ({len(prix_valides)}) → ignoré")
        return 0

    cote = statistics.median(prix_valides)
    seuil = cote * SEUIL_ACHAT
    print(f"   📊 [{langue}] Cote : {cote:.2f} € | 🟢 Acheter si ≤ {seuil:.2f} €")

       for prix, a in annonces:
        # Anti-aberrant
        if prix < cote * (1 - ECART_MAX_COTE) or prix > cote * (1 + ECART_MAX_COTE):
            continue

        # Filtre frais de port
        port = get_frais_port(a)
        if port is not None and port > FRAIS_PORT_MAX:
            continue
        a["_port"] = port

        if prix <= seuil:

            item_id = a.get("itemId", "")
            if item_id in memoire:
                continue
            remise = round((1 - prix / cote) * 100)
            lien = a.get("itemWebUrl", "https://www.ebay.fr")
            titre = a.get("title", "")
            drapeau = "🇯🇵" if langue == "JP" else "🇫🇷"
            message = (
                "🎯 <b>BONNE AFFAIRE DÉTECTÉE !</b>\n\n"
                f"🃏 <b>{nom}</b> {drapeau}\n"
                f"📝 {titre}\n"
                f"📊 Cote médiane : <b>{cote:.2f} €</b>\n"
                f"💰 Prix : <b>{prix:.2f} €</b>\n"
                f"📉 <b>-{remise}%</b> sous la cote ✅\n"
                               f"📦 Frais de port : <b>{('%.2f €' % a['_port']) if a.get('_port') is not None else '⚠️ à vérifier'}</b>\n"
                f"🏪 Source : eBay\n\n"

                f"🔗 <a href='{lien}'>Voir l'annonce</a>"
            )
            envoyer_alerte(message)
            memoire.add(item_id)
            nb += 1
            print(f"      🎯 ALERTE ! {titre[:40]} → {prix} €")
    return nb


def main():
    print("🤖 BOT POKÉMON — Démarrage\n")
    token = obtenir_token()
    print("✅ Connecté à eBay\n")

    memoire = charger_memoire()
    nb_alertes = 0

    for carte in CARTES:
        print(f"🔍 Recherche : {carte['nom']}")
        try:
            annonces = rechercher_ebay(token, carte["recherche"])
        except Exception as e:
            print(f"   ⚠️ Erreur eBay : {e}")
            continue

        # On trie les annonces par langue détectée
        annonces_jp = []
        annonces_fr = []

        for a in annonces:
            titre = a.get("title", "")
            if titre_interdit(titre):
                continue
            # Prix
            prix_info = a.get("price", {})
            try:
                prix = float(prix_info.get("value", 0))
            except (ValueError, TypeError):
                continue
            if prix < PRIX_MINIMUM:
                continue

            langue = detecter_langue(titre)
            if langue == "JP":
                annonces_jp.append((prix, a))
            elif langue == "FR":
                annonces_fr.append((prix, a))
            # None → ignorée (prudence)

        # Analyse séparée JP et FR
        nb_alertes += analyser_langue(annonces_jp, "JP", carte["nom"], memoire)
        nb_alertes += analyser_langue(annonces_fr, "FR", carte["nom"], memoire)

    sauver_memoire(memoire)
    print(f"\n🎉 Terminé ! {nb_alertes} nouvelle(s) alerte(s) envoyée(s).")
    if nb_alertes == 0:
        print("ℹ️ Aucune NOUVELLE bonne affaire (c'est normal et sain ✅).")


if __name__ == "__main__":
    main()
