import builtins
from gestion_magasin import produits, clients, ajouter_produit, ajouter_client

# --- TEST AJOUT PRODUIT ---
def test_ajouter_produit(monkeypatch):
    """
    Teste la fonction ajouter_produit() avec des valeurs simulées.
    """

    produits.clear()

    # Simule les saisies utilisateur (ajoute une 4ᵉ valeur pour la catégorie)
    inputs = iter(["Pomme", "10", "500", "Fruits"])  # nom, quantité, prix, catégorie

    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    ajouter_produit()

    assert len(produits) == 1
    assert produits[0]["nom"].lower() == "pomme"
    assert produits[0]["quantite"] == 10
    assert produits[0]["prix"] == 500
    assert produits[0]["categorie"].lower() == "fruits"



# --- TEST AJOUT CLIENT ---
def test_ajouter_client(monkeypatch):
    """
    Teste la fonction ajouter_client() avec des entrées simulées.
    """

    # vider la liste avant de commencer
    clients.clear()

    # Simule une saisie utilisateur
    inputs = iter(["Dilan", "Togoue", "123456789"])  # nom, prénom, téléphone
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    ajouter_client()

    # Vérifie que le client a bien été ajouté
    assert len(clients) == 1
    assert clients[0]["nom"].lower() == "dilan"
    assert clients[0]["telephone"] == "123456789"
