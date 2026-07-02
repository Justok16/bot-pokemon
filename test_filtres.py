# Test des filtres pour ne garder que les cartes à l'unité

# Mots qui font REJETER une annonce (lots, boosters, box, accessoires...)
MOTS_INTERDITS = [
    "lot", "lots", "bundle", "playset", "coffret", "coffrets",
    "display", "booster", "boosters", "box", "mystery", "mystére", "mystère",
    "sleeve", "sleeves", "protège", "protege", "protection", "protections",
    "classeur", "portfolio", "magnétique", "magnetique",
    "x2", "x3", "x4", "x5", "x 2", "x 3", "x 4",
    "ensemble", "collection complète", "reconditionné", "reconditionne",
    "deck", "structure", "étui", "etui", "toploader", "penny sleeve"
]

# Mots qui font ACCEPTER (indiquent l'état neuf / near mint)
MOTS_ETAT_OK = [
    "neuf", "neuve", "near mint", "nm", "mint", "excellent", "excellent état"
]


def annonce_valide(titre):
    """Retourne True si l'annonce semble être une carte à l'unité en bon état."""
    titre_min = titre.lower()

    # 1. Rejet si un mot interdit apparaît
    for mot in MOTS_INTERDITS:
        if mot in titre_min:
            return False, f"rejeté (contient '{mot}')"

    # Sinon on accepte
    return True, "accepté"


# --- TESTS avec les résultats réels de tout à l'heure ---
annonces_test = [
    "Carte Pokémon - Dracaufeu ex 199/165 - 151 - Illustration rare",
    "Booster Pokémon reconditionné Hit garanti (ex/FA/AR/Alt)",
    "Dracaufeu EX 199/165 – 151 – Français – CCC 9.5",
    "🔥Mystery Box Charizard Pokémon – Spécial DRACAUFEU !!!🔥",
    "Protections Magnétiques Illustrées Pokémon - Série 151",
    "Lot de 5 cartes Pokémon 151 Dracaufeu",
    "Carte Pokémon Ronflex 143/165 151 Neuve NM",
]

print("🧪 TEST DES FILTRES\n")
for annonce in annonces_test:
    valide, raison = annonce_valide(annonce)
    icone = "✅" if valide else "🚫"
    print(f"{icone} {raison.upper()}")
    print(f"   {annonce[:60]}\n")

print("🎉 Test des filtres terminé !")
