import statistics

def detecter_gradee(titre):
    """Détecte si une carte est gradée (notée sous coque)."""
    organismes = ["psa", "pca", "ccc", "bgs", "cgc", "beckett", "ace", "mga", "gradée", "gradee", "graded"]
    titre_min = titre.lower()
    for org in organismes:
        if org in titre_min:
            return True
    return False


def calculer_cotes(annonces):
    """
    annonces = liste de (titre, prix)
    Sépare brutes / gradées et calcule la médiane de chaque groupe.
    """
    prix_brutes = []
    prix_gradees = []

    for titre, prix in annonces:
        if detecter_gradee(titre):
            prix_gradees.append(prix)
        else:
            prix_brutes.append(prix)

    resultat = {}
    if prix_brutes:
        cote = statistics.median(prix_brutes)
        resultat["brute"] = {
            "cote": cote,
            "seuil_achat": round(cote * 0.90, 2),   # -10%
            "seuil_revente": round(cote * 1.10, 2), # +10%
            "nb": len(prix_brutes)
        }
    if prix_gradees:
        cote = statistics.median(prix_gradees)
        resultat["gradee"] = {
            "cote": cote,
            "seuil_achat": round(cote * 0.90, 2),
            "seuil_revente": round(cote * 1.10, 2),
            "nb": len(prix_gradees)
        }
    return resultat


# --- TEST ---
annonces_test = [
    ("Dracaufeu ex 199/165 151 Neuf", 350.00),
    ("Dracaufeu ex 199/165 151 NM", 340.00),
    ("Dracaufeu ex 199/165 151 Near Mint", 365.00),
    ("Dracaufeu EX 199/165 151 CCC 9.5", 653.95),
    ("Dracaufeu EX 199/165 151 PSA 10", 720.00),
]

print("💰 TEST CALCUL DE COTE — Dracaufeu ex 199/165\n")
cotes = calculer_cotes(annonces_test)

for categorie, infos in cotes.items():
    print(f"📊 Cartes {categorie.upper()} ({infos['nb']} annonces)")
    print(f"   Cote médiane   : {infos['cote']} €")
    print(f"   🟢 Acheter si ≤ : {infos['seuil_achat']} € (-10%)")
    print(f"   🔴 Revendre si ≥: {infos['seuil_revente']} € (+10%)\n")

print("🎉 Test du calcul de cote terminé !")
