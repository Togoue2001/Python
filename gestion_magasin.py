import json
from datetime import datetime
from copy import deepcopy
import os

DATA_FILE = "magasin_donnees.json"

# creations des listes
produits = []
clients = []
ventes = []

# IDs auto-incrémentés (seront recalculés au chargement si nécessaire)
prochain_id_produit = 1
prochain_id_client = 1
prochain_id_vente = 1

# creation du menu principal
def menu_principal():
    while True:
        print("\n" + "=" * 50)
        print("   SYSTÈME DE GESTION DE MAGASIN".center(50))
        print("=" * 50)
        print("[1] 📦 Gestion des Produits")
        print("[2] 👥 Gestion des Clients")
        print("[3] 💰 Enregistrer une Vente")
        print("[4] 📊 Statistiques")
        print("[5] 💾 Sauvegarder manuellement")
        print("[6] 📜 Afficher les ventes (historique)")
        print("[7] 🧾 Générer reçu d'une vente (afficher)")
        print("[8] 🔄 Recharger les données depuis le fichier")
        print("[9] 🧹 Réinitialiser tout (ATTENTION)")
        print("[0] 🚪 Quitter")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            menu_produits()
        elif choix == "2":
            menu_clients()
        elif choix == "3":
            enregistrer_vente()
        elif choix == "4":
            afficher_statistiques()
        elif choix == "5":
            sauvegarder_donnees()
            print("✅ Données sauvegardées.")
        elif choix == "6":
            afficher_ventes()
        elif choix == "7":
            vid = input_int("ID vente pour reçu : ")
            v = next((x for x in ventes if x["id"] == vid), None)
            if v:
                generer_recu(v)
            else:
                print("Vente introuvable.")
        elif choix == "8":
            charger_donnees()
            print("✅ Données rechargées depuis le fichier.")
        elif choix == "9":
            confirm = input("Confirmer réinitialisation complète ? Toutes les données seront perdues (o/N): ").lower()
            if confirm == "o":
                open(DATA_FILE, "w").write(json.dumps({"produits": [], "clients": [], "ventes": []}, ensure_ascii=False))
                charger_donnees()
                print("✅ Données réinitialisées.")
            else:
                print("Annulé.")
        elif choix == "0":
            print("👋 Au revoir !")
            break
        else:
            print("Choix invalide.")

def menu_produits():
    while True:
        print("\n--- GESTION DES PRODUITS ---")
        print("[1] Ajouter un produit")
        print("[2] Afficher les produits")
        print("[3] Modifier un produit")
        print("[4] Supprimer un produit")
        print("[5] Rechercher un produit")
        print("[6] Produits en rupture de stock")
        print("[0] Retour")
        choix = input("Choix : ").strip()
        if choix == "1":
            ajouter_produit()
        elif choix == "2":
            afficher_produits()
        elif choix == "3":
            modifier_produit()
        elif choix == "4":
            supprimer_produit()
        elif choix == "5":
            rechercher_produit()
        elif choix == "6":
            produits_en_rupture()
        elif choix == "0":
            break
        else:
            print("Choix invalide.")


def menu_clients():
    while True:
        print("\n--- GESTION DES CLIENTS ---")
        print("[1] Ajouter un client")
        print("[2] Afficher les clients")
        print("[3] Rechercher un client")
        print("[0] Retour")
        choix = input("Choix : ").strip()
        if choix == "1":
            ajouter_client()
        elif choix == "2":
            afficher_clients()
        elif choix == "3":
            rechercher_client()
        elif choix == "0":
            break
        else:
            print("Choix invalide.")

# Gestions des produits

def ajouter_produit():
    global prochain_id_produit
    print("\n--- AJOUTER UN PRODUIT ---")
    nom = input("Nom du produit : ").strip()
    if nom == "":
        print("⚠ Nom vide annulé.")
        return
    prix = input_float("Prix (€) : ", min_val=0.0)
    quantite = input_int("Quantité en stock : ", min_val=0)
    categorie = input("Catégorie : ").strip() or "Non renseignée"

    produit = {
        "id": prochain_id_produit,
        "nom": nom,
        "prix": round(prix, 2),
        "quantite": quantite,
        "categorie": categorie
    }
    produits.append(produit)
    prochain_id_produit += 1
    sauvegarder_donnees()
    print(f"✅ Produit '{nom}' ajouté (ID {produit['id']}).")


def afficher_produits():
    print("\n--- LISTE DES PRODUITS ---")
    if not produits:
        print("Aucun produit en inventaire.")
        return
    header = f"{'ID':<4} {'NOM':<30} {'PRIX':>8} {'QTE':>6} {'CATEGORIE':<20}"
    print(header)
    print("-" * len(header))
    for p in produits:
        print(f"{p['id']:<4} {p['nom']:<30} {p['prix']:>8.2f}€ {p['quantite']:>6} {p['categorie']:<20}")


def modifier_produit():
    print("\n--- MODIFIER UN PRODUIT ---")
    if not produits:
        print("Aucun produit disponible.")
        return
    pid = input_int("ID du produit à modifier : ")
    p = trouver_produit_by_id(pid)
    if not p:
        print("⚠ Produit non trouvé.")
        return
    print("Laisser vide pour conserver la valeur actuelle.")
    nom = input(f"Nom [{p['nom']}]: ").strip() or p['nom']
    try:
        prix_input = input(f"Prix ({p['prix']}€): ").strip()
        prix = p['prix'] if prix_input == "" else float(prix_input.replace(",", "."))
    except ValueError:
        print("⚠ Prix invalide, modification annulée.")
        return
    try:
        q_input = input(f"Quantité ({p['quantite']}): ").strip()
        quantite = p['quantite'] if q_input == "" else int(q_input)
    except ValueError:
        print("⚠ Quantité invalide, modification annulée.")
        return
    categorie = input(f"Catégorie [{p['categorie']}]: ").strip() or p['categorie']

    p.update({
        "nom": nom,
        "prix": round(prix, 2),
        "quantite": quantite,
        "categorie": categorie
    })
    sauvegarder_donnees()
    print("✅ Produit modifié avec succès.")


def supprimer_produit():
    print("\n--- SUPPRIMER UN PRODUIT ---")
    if not produits:
        print("Aucun produit disponible.")
        return
    pid = input_int("ID du produit à supprimer : ")
    p = trouver_produit_by_id(pid)
    if not p:
        print("⚠ Produit non trouvé.")
        return
    confirm = input(f"Confirmer suppression de '{p['nom']}' ? (o/N): ").lower()
    if confirm == "o":
        produits.remove(p)
        sauvegarder_donnees()
        print("✅ Produit supprimé.")
    else:
        print("Annulé.")


def rechercher_produit():
    print("\n--- RECHERCHER PRODUITS ---")
    q = input("Recherche (nom ou catégorie) : ").strip().lower()
    if q == "":
        print("⚠ Recherche vide.")
        return
    results = [p for p in produits if q in p['nom'].lower() or q in p['categorie'].lower()]
    if not results:
        print("Aucun produit trouvé.")
    else:
        for p in results:
            print(f"[{p['id']}] {p['nom']} - {p['prix']}€ - Qte: {p['quantite']} - Cat: {p['categorie']}")



def produits_en_rupture():
    print("\n--- PRODUITS EN RUPTURE ---")
    out = [p for p in produits if p['quantite'] == 0]
    if not out:
        print("Aucun produit en rupture de stock.")
        return
    for p in out:
        print(f"[{p['id']}] {p['nom']} - Cat: {p['categorie']}")



# Gestions des clients

def ajouter_client():
    global prochain_id_client
    print("\n--- AJOUTER UN CLIENT ---")
    nom = input("Nom complet : ").strip()
    if nom == "":
        print("⚠ Nom vide annulé.")
        return
    email = input("Email : ").strip()
    telephone = input("Téléphone : ").strip()

    client = {
        "id": prochain_id_client,
        "nom": nom,
        "email": email,
        "telephone": telephone,
        "total_achats": 0.0
    }
    clients.append(client)
    prochain_id_client += 1
    sauvegarder_donnees()
    print(f"✅ Client '{nom}' ajouté (ID {client['id']}).")


def afficher_clients():
    print("\n--- LISTE DES CLIENTS ---")
    if not clients:
        print("Aucun client enregistré.")
        return
    header = f"{'ID':<4} {'NOM':<30} {'EMAIL':<25} {'TEL':<12} {'TOTAL_ACHATS':>12}"
    print(header)
    print("-" * len(header))
    for c in clients:
        print(f"{c['id']:<4} {c['nom']:<30} {c['email']:<25} {c['telephone']:<12} {c['total_achats']:>12.2f}€")


def rechercher_client():
    print("\n--- RECHERCHER CLIENT ---")
    q = input("Recherche (nom / email / téléphone) : ").strip().lower()
    if q == "":
        print("⚠ Recherche vide.")
        return
    results = [c for c in clients if q in c['nom'].lower() or q in c['email'].lower() or q in c['telephone'].lower()]
    if not results:
        print("Aucun client trouvé.")
    else:
        for c in results:
            print(f"[{c['id']}] {c['nom']} - Email: {c['email']} - Tel: {c['telephone']} - Total achats: {c['total_achats']:.2f}€")

def total_achats_par_client(cid):
    c = trouver_client_by_id(cid)
    if not c:
        return 0.0
    return c.get("total_achats", 0.0)

# Gestions des ventes

def enregistrer_vente():
    global prochain_id_vente
    print("\n--- ENREGISTRER UNE VENTE ---")
    if not produits:
        print("⚠ Aucun produit en stock.")
        return
    if not clients:
        print("⚠ Aucun client enregistré. Veuillez ajouter un client d'abord.")
        return

    # choisir client
    afficher_clients()
    cid = input_int("ID du client acheteur : ")
    client = trouver_client_by_id(cid)
    if not client:
        print("⚠ Client introuvable.")
        return

    # préparer la liste d'articles
    ligne_produits = []
    while True:
        afficher_produits()
        pid = input("ID du produit à ajouter (ou 'fin' pour terminer) : ").strip().lower()
        if pid == "fin":
            break
        try:
            pid = int(pid)
        except ValueError:
            print("⚠ Entrez un ID valide ou 'fin'.")
            continue
        produit = trouver_produit_by_id(pid)
        if not produit:
            print("⚠ Produit introuvable.")
            continue
        if produit["quantite"] <= 0:
            print("⚠ Produit en rupture.")
            continue
        qte = input_int(f"Quantité (max {produit['quantite']}) : ", min_val=1)
        if qte > produit["quantite"]:
            print("⚠ Quantité demandée supérieure au stock disponible.")
            continue
        # ajouter ligne
        ligne_produits.append({
            "produit_id": produit["id"],
            "quantite": qte,
            "prix_unitaire": produit["prix"]
        })
        # proposer de continuer ou non
        cont = input("Ajouter un autre produit ? (o/N): ").lower()
        if cont != "o":
            break

    if not ligne_produits:
        print("Vente vide annulée.")
        return

    # calcul total
    total = sum(lp["quantite"] * lp["prix_unitaire"] for lp in ligne_produits)
    total = round(total, 2)

    # confirmer vente
    print(f"Total de la vente : {total:.2f}€")
    confirm = input("Confirmer la vente ? (o/N): ").lower()
    if confirm != "o":
        print("Vente annulée.")
        return

    # déduire stock
    for lp in ligne_produits:
        p = trouver_produit_by_id(lp["produit_id"])
        if p:
            p["quantite"] -= lp["quantite"]

    # créer enregistrement vente
    vente = {
        "id": prochain_id_vente,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "client_id": client["id"],
        "produits": deepcopy(ligne_produits),
        "total": total
    }
    ventes.append(vente)
    prochain_id_vente += 1

    # mettre à jour total_achats client
    client["total_achats"] = round(client.get("total_achats", 0.0) + total, 2)

    sauvegarder_donnees()
    print("✅ Vente enregistrée.")
    generer_recu(vente)


def afficher_ventes():
    print("\n--- HISTORIQUE DES VENTES ---")
    if not ventes:
        print("Aucune vente enregistrée.")
        return
    for v in ventes:
        client = trouver_client_by_id(v["client_id"])
        nom_client = client["nom"] if client else "Client supprimé"
        print(f"[{v['id']}] {v['date']} - Client: {nom_client} - Total: {v['total']:.2f}€")
        for lp in v["produits"]:
            p = trouver_produit_by_id(lp["produit_id"])
            nomp = p["nom"] if p else f"Prod ID {lp['produit_id']}"
            print(f"   - {nomp} x{lp['quantite']} @ {lp['prix_unitaire']:.2f}€")
        print("-" * 40)


def generer_recu(vente):
    """Affiche (et sauvegarde en fichier text) le reçu d'une vente"""
    client = trouver_client_by_id(vente["client_id"])
    date = vente["date"]
    total = vente["total"]
    lines = []
    lines.append("====== RECU DE VENTE ======")
    lines.append(f"ID Vente: {vente['id']}")
    lines.append(f"Date: {date}")
    lines.append(f"Client: {client['nom'] if client else 'Client inconnu'}")
    lines.append("")
    lines.append("Articles:")
    for lp in vente["produits"]:
        p = trouver_produit_by_id(lp["produit_id"])
        nomp = p["nom"] if p else f"Prod ID {lp['produit_id']}"
        lines.append(f" - {nomp} x{lp['quantite']} @ {lp['prix_unitaire']:.2f}€ = {lp['quantite']*lp['prix_unitaire']:.2f}€")
    lines.append("")
    lines.append(f"TOTAL: {total:.2f}€")
    lines.append("===========================")

    recu_text = "\n".join(lines)
    print("\n" + recu_text + "\n")

    # sauvegarder reçu texte dans dossier receipts (optionnel)
    try:
        os.makedirs("receipts", exist_ok=True)
        filename = f"receipts/recu_{vente['id']}_{vente['date'].replace(':', '-')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(recu_text)
    except Exception:
        pass  # ne bloque pas si impossible d'écrire le recu


# Gestions des statistique

def calculer_chiffre_affaires_total():
    return round(sum(v["total"] for v in ventes), 2)


def produit_plus_vendu():
    # compter quantités vendues par produit_id
    counts = {}
    for v in ventes:
        for lp in v["produits"]:
            counts[lp["produit_id"]] = counts.get(lp["produit_id"], 0) + lp["quantite"]
    if not counts:
        return None, 0
    pid = max(counts, key=lambda k: counts[k])
    p = trouver_produit_by_id(pid)
    return (p["nom"] if p else f"ID {pid}"), counts[pid]


def meilleur_client():
    if not clients:
        return None, 0.0
    c = max(clients, key=lambda x: x.get("total_achats", 0.0))
    return c["nom"], c.get("total_achats", 0.0)


def stock_total_restant():
    return sum(p["quantite"] for p in produits)


def ventes_par_categorie():
    stats = {}
    for v in ventes:
        for lp in v["produits"]:
            p = trouver_produit_by_id(lp["produit_id"])
            cat = p["categorie"] if p else "Inconnue"
            stats[cat] = stats.get(cat, 0.0) + lp["quantite"] * lp["prix_unitaire"]
    return stats


def afficher_statistiques():
    print("\n--- STATISTIQUES ---")
    ca = calculer_chiffre_affaires_total()
    ppv_name, ppv_qte = produit_plus_vendu()
    best_name, best_total = meilleur_client()
    stock_total = stock_total_restant()
    ventes_cat = ventes_par_categorie()

    print(f"Chiffre d'affaires total : {ca:.2f}€")
    if ppv_name:
        print(f"Produit le plus vendu : {ppv_name} (quantité vendue : {ppv_qte})")
    else:
        print("Produit le plus vendu : Aucun")
    if best_name:
        print(f"Meilleur client : {best_name} (total achats : {best_total:.2f}€)")
    else:
        print("Meilleur client : Aucun")
    print(f"Stock total restant (somme quantités) : {stock_total}")
    print("Ventes par catégorie :")
    if ventes_cat:
        for cat, montant in ventes_cat.items():
            print(f" - {cat} : {montant:.2f}€")
    else:
        print(" Aucune vente par catégorie.")


# Gestions des sauvegarder

def charger_donnees():
    global produits, clients, ventes
    global prochain_id_produit, prochain_id_client, prochain_id_vente

    if not os.path.exists(DATA_FILE):
        # fichier absent -> initialiser vide
        produits, clients, ventes = [], [], []
        prochain_id_produit = prochain_id_client = prochain_id_vente = 1
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            produits = data.get("produits", [])
            clients = data.get("clients", [])
            ventes = data.get("ventes", [])
    except Exception as e:
        print(f"⚠ Erreur en chargeant les données : {e}")
        produits, clients, ventes = [], [], []

    # recalculer prochains IDs pour éviter collision
    prochain_id_produit = max([p["id"] for p in produits], default=0) + 1
    prochain_id_client = max([c["id"] for c in clients], default=0) + 1
    prochain_id_vente = max([v["id"] for v in ventes], default=0) + 1


def sauvegarder_donnees():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produits": produits,
                "clients": clients,
                "ventes": ventes
            }, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠ Échec de sauvegarde : {e}")


# Utilitaires

def trouver_produit_by_id(pid):
    for p in produits:
        if p["id"] == pid:
            return p
    return None

def trouver_client_by_id(cid):
    for c in clients:
        if c["id"] == cid:
            return c
    return None

def input_int(prompt, min_val=None):
    while True:
        try:
            v = int(input(prompt))
            if min_val is not None and v < min_val:
                print(f"⚠ Valeur minimale : {min_val}")
                continue
            return v
        except ValueError:
            print("⚠ Entrez un entier valide.")

def input_float(prompt, min_val=None):
    while True:
        try:
            v = float(input(prompt).replace(",", "."))
            if min_val is not None and v < min_val:
                print(f"⚠ Valeur minimale : {min_val}")
                continue
            return v
        except ValueError:
            print("⚠ Entrez un nombre valide (ex: 12.50).")


def main():
    print("\n🎉 Bienvenue dans le Système de Gestion de Magasin !")
    charger_donnees()
    menu_principal()


if __name__ == "__main__":
    main()