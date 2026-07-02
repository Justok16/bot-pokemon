import os
import base64
import requests
from dotenv import load_dotenv

# Charge les clés depuis le fichier .env
load_dotenv()

APP_ID = os.getenv("EBAY_APP_ID")
CERT_ID = os.getenv("EBAY_CERT_ID")

# Vérification que les clés sont bien chargées
if not APP_ID or not CERT_ID:
    print("❌ ERREUR : impossible de lire EBAY_APP_ID ou EBAY_CERT_ID dans le fichier .env")
    print("   Vérifiez que le fichier .env est bien dans le dossier bot-pokemon.")
    exit()

print("✅ Clés chargées depuis .env")

# Étape 1 : obtenir un token automatiquement
print("🔑 Demande d'un token à eBay...")

credentials = f"{APP_ID}:{CERT_ID}"
encoded = base64.b64encode(credentials.encode()).decode()

token_url = "https://api.ebay.com/identity/v1/oauth2/token"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {encoded}"
}
data = {
    "grant_type": "client_credentials",
    "scope": "https://api.ebay.com/oauth/api_scope"
}

response = requests.post(token_url, headers=headers, data=data)

if response.status_code != 200:
    print(f"❌ ERREUR lors de la demande de token : {response.status_code}")
    print(response.text)
    exit()

token = response.json()["access_token"]
print("✅ Token obtenu automatiquement !")

# Étape 2 : chercher une carte Pokémon
print("🔍 Recherche d'une carte de test sur eBay...")

search_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
search_headers = {
    "Authorization": f"Bearer {token}",
    "X-EBAY-C-MARKETPLACE-ID": "EBAY_FR"
}
params = {
    "q": "Pokemon 151 Dracaufeu",
    "limit": 5
}

search_response = requests.get(search_url, headers=search_headers, params=params)

if search_response.status_code != 200:
    print(f"❌ ERREUR lors de la recherche : {search_response.status_code}")
    print(search_response.text)
    exit()

results = search_response.json()

# Affichage des résultats
items = results.get("itemSummaries", [])
if not items:
    print("⚠️ Aucun résultat trouvé (mais la connexion fonctionne !)")
else:
    print(f"\n✅ SUCCÈS ! {len(items)} cartes trouvées :\n")
    for item in items:
        titre = item.get("title", "Sans titre")
        prix = item.get("price", {}).get("value", "?")
        devise = item.get("price", {}).get("currency", "")
        print(f"  • {titre[:60]}")
        print(f"    💰 {prix} {devise}\n")

print("🎉 TEST TERMINÉ AVEC SUCCÈS ! Tout fonctionne.")
