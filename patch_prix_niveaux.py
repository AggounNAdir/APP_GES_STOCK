# ============================================================
# PATCH prix_niveaux.py
# Ajouter la consultation de la table prix_speciaux_clients
# dans PrixSelectorWidget
# ============================================================
#
# Ce fichier décrit les modifications à apporter dans prix_niveaux.py.
# Si vous n'avez pas accès à ce fichier, les extraits ci-dessous
# constituent une implémentation complète à intégrer.
# ============================================================


# ─────────────────────────────────────────────────────────────
# Dans la classe PrixSelectorWidget, ajouter cette méthode :
# ─────────────────────────────────────────────────────────────

def _get_prix_special_client(self, produit_id):
    """
    Consulte prix_speciaux_clients pour le client courant.
    Retourne le prix spécial (float) ou None si aucun.
    """
    if not hasattr(self, '_client_id_fn') or self._client_id_fn is None:
        return None
    try:
        client_id = self._client_id_fn()
    except Exception:
        return None
    if not client_id or not produit_id:
        return None
    try:
        import sqlite3
        # Import local pour éviter la circularité
        # Remplacez get_conn() par votre propre import si nécessaire
        from gestion_stock import get_conn  # adapter selon votre structure
        conn = get_conn()
        row = conn.execute("""
            SELECT prix_special FROM prix_speciaux_clients
            WHERE client_id = ? AND produit_id = ? AND actif = 1
        """, (client_id, produit_id)).fetchone()
        conn.close()
        if row:
            return float(row["prix_special"])
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────
# Modifier set_produit() pour intégrer le prix spécial :
# ─────────────────────────────────────────────────────────────

# AVANT (votre méthode set_produit actuelle, structure probable) :
"""
    def set_produit(self, produit):
        self._produit = produit
        self._selectionner_defaut()
        self._afficher_prix()
"""

# APRÈS :
"""
    def set_produit(self, produit):
        self._produit = produit
        
        # Vérifier d'abord si un prix spécial existe pour ce client
        prix_special = self._get_prix_special_client(produit.get("id"))
        if prix_special is not None:
            # Appliquer directement le prix spécial
            if self._prix_var:
                self._prix_var.set(str(prix_special))
            self._afficher_badge_prix_special(prix_special)
            return
        
        # Sinon comportement standard (niveau de prix)
        self._selectionner_defaut()
        self._afficher_prix()
"""


# ─────────────────────────────────────────────────────────────
# Ajouter _afficher_badge_prix_special() dans PrixSelectorWidget
# ─────────────────────────────────────────────────────────────

"""
    def _afficher_badge_prix_special(self, prix):
        \"\"\"Affiche un indicateur visuel que le prix spécial client est actif.\"\"\"
        # Effacer l'affichage courant des niveaux
        for btn in getattr(self, '_boutons_niveau', []):
            try:
                btn.config(relief="flat", bg=CLR_INPUT)
            except Exception:
                pass
        
        # Mettre à jour le label de prix si présent
        if hasattr(self, '_label_prix'):
            self._label_prix.config(
                text=f"💰 Prix spécial : {prix:.2f} DA",
                fg=CLR_GREEN
            )
"""


# ─────────────────────────────────────────────────────────────
# Si prix_niveaux.py utilise client_id_fn dans __init__,
# s'assurer qu'il est stocké comme attribut d'instance :
# ─────────────────────────────────────────────────────────────

# AVANT (probable) :
"""
    def __init__(self, parent, prix_var=None, client_id_fn=None, **kw):
        super().__init__(parent, **kw)
        self._prix_var = prix_var
        self._client_id_fn = client_id_fn  # ← vérifier que cette ligne existe
        ...
"""

# APRÈS (s'assurer que c'est bien là) :
"""
    def __init__(self, parent, prix_var=None, client_id_fn=None, **kw):
        super().__init__(parent, **kw)
        self._prix_var = prix_var
        self._client_id_fn = client_id_fn  # indispensable pour _get_prix_special_client
        self._produit = None
        ...
"""


# ─────────────────────────────────────────────────────────────
# BONUS — Correction dans BonDialog.on_tiers_change()
# S'assurer que le changement de client recharge le prix spécial
# ─────────────────────────────────────────────────────────────

# APRÈS (dans main.py, méthode on_tiers_change de BonDialog) :
"""
    def on_tiers_change(self, event=None):
        \"\"\"Met à jour le niveau de prix quand le client change\"\"\"
        if hasattr(self, 'prix_selector'):
            # Recharger le produit courant pour déclencher la vérif prix spécial
            key = self.prod_var.get()
            if key and key in self.prod_map:
                self.prix_selector.set_produit(self.prod_map[key])
            else:
                self.prix_selector._selectionner_defaut()
                self.prix_selector._afficher_prix()
"""


# ─────────────────────────────────────────────────────────────
# BONUS — VenteComptoirDialog : recharger prix si client change
# Ajouter un binding sur le client_combo
# ─────────────────────────────────────────────────────────────

# Dans VenteComptoirDialog._build(), après la création du client_combo :
"""
        self.client_combo.bind("<<ComboboxSelected>>", self._on_client_change)
"""

# Ajouter la méthode :
"""
    def _on_client_change(self, event=None):
        \"\"\"Recharger le prix spécial si le client change.\"\"\"
        key = self.prod_var.get()
        if key and key in self.prod_map and hasattr(self, 'prix_selector'):
            self.prix_selector.set_produit(self.prod_map[key])
"""
