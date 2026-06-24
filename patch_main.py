# ============================================================
# PATCH MAIN.PY — 4 corrections à appliquer
# ============================================================
# Chaque section indique exactement QUOI remplacer par QUOI.
# ============================================================


# ─────────────────────────────────────────────────────────────
# CORRECTION 1 — init_db()
# Dans CREATE TABLE IF NOT EXISTS prix_speciaux_clients,
# remplacer le bloc actuel par celui-ci (ajout date_modification)
# ─────────────────────────────────────────────────────────────

# AVANT :
"""
        CREATE TABLE IF NOT EXISTS prix_speciaux_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            produit_id INTEGER NOT NULL,
            prix_special REAL NOT NULL,
            date_debut TEXT,
            date_fin TEXT,
            actif INTEGER DEFAULT 1,
            FOREIGN KEY(client_id) REFERENCES clients(id),
            FOREIGN KEY(produit_id) REFERENCES produits(id),
            UNIQUE(client_id, produit_id)
        );
"""

# APRÈS :
"""
        CREATE TABLE IF NOT EXISTS prix_speciaux_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            produit_id INTEGER NOT NULL,
            prix_special REAL NOT NULL,
            date_debut TEXT,
            date_fin TEXT,
            actif INTEGER DEFAULT 1,
            date_modification TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(id),
            FOREIGN KEY(produit_id) REFERENCES produits(id),
            UNIQUE(client_id, produit_id)
        );
"""

# Ajouter aussi dans init_db(), après les ALTER TABLE existants,
# ce bloc pour migrer les bases existantes :
"""
        # Migration : ajouter date_modification si absente
        c.execute("PRAGMA table_info(prix_speciaux_clients)")
        psc_cols = [row[1] for row in c.fetchall()]
        if "date_modification" not in psc_cols:
            c.execute("ALTER TABLE prix_speciaux_clients ADD COLUMN date_modification TEXT")
"""


# ─────────────────────────────────────────────────────────────
# CORRECTION 2 — PrixSpeciauxClientDialog.refresh()
# Remplacer la méthode refresh() en entier
# ─────────────────────────────────────────────────────────────

# AVANT (ligne ~1134) :
"""
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        
        conn = get_conn()
        prix_speciaux = conn.execute(\"\"\"
            SELECT psc.*, pr.code, pr.designation, pr.prix_detail as prix_standard
            FROM prix_speciaux_clients psc
            JOIN produits pr ON psc.produit_id = pr.id
            WHERE psc.client_id = ? AND psc.actif = 1
        \"\"\", (self.client_id,)).fetchall()
        conn.close()
        
        for ps in prix_speciaux:
            remise = ((ps[\"prix_standard\"] - ps[\"prix_special\"]) / ps[\"prix_standard\"] * 100) if ps[\"prix_standard\"] > 0 else 0
            self.tree.insert("", "end", iid=ps["id"], values=(
                ps["code"], ps["designation"],
                f"{ps['prix_standard']:.2f} DA",
                f"{ps['prix_special']:.2f} DA",
                f"{remise:.1f}%",
                "✏ Modifier"
            ))
"""

# APRÈS :
"""
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        
        conn = get_conn()
        prix_speciaux = conn.execute(\"\"\"
            SELECT psc.*, pr.code, pr.designation,
                   COALESCE(NULLIF(pr.prix_vente, 0), pr.prix_detail, 0) as prix_standard
            FROM prix_speciaux_clients psc
            JOIN produits pr ON psc.produit_id = pr.id
            WHERE psc.client_id = ? AND psc.actif = 1
        \"\"\", (self.client_id,)).fetchall()
        conn.close()
        
        for ps in prix_speciaux:
            prix_std = ps["prix_standard"] or 0
            remise = ((prix_std - ps["prix_special"]) / prix_std * 100) if prix_std > 0 else 0
            self.tree.insert("", "end", iid=ps["id"], values=(
                ps["code"], ps["designation"],
                f"{prix_std:.2f} DA",
                f"{ps['prix_special']:.2f} DA",
                f"{remise:.1f}%",
                "✏ Modifier"
            ))
"""


# ─────────────────────────────────────────────────────────────
# CORRECTION 3 — PrixSpeciauxClientDialog.ajouter_prix_special()
# Corriger le UPDATE pour utiliser date_modification
# ─────────────────────────────────────────────────────────────

# AVANT :
"""
            if existing:
                conn.execute(\"\"\"
                    UPDATE prix_speciaux_clients 
                    SET prix_special = ?, date_modification = CURRENT_TIMESTAMP
                    WHERE id = ?
                \"\"\", (prix_special, existing["id"]))
"""

# APRÈS :
"""
            if existing:
                conn.execute(\"\"\"
                    UPDATE prix_speciaux_clients 
                    SET prix_special = ?,
                        date_modification = datetime('now')
                    WHERE id = ?
                \"\"\", (prix_special, existing["id"]))
"""


# ─────────────────────────────────────────────────────────────
# CORRECTION 4 — VenteComptoirDialog._build()
# Déplacer self.prix_var AVANT l'instanciation du PrixSelectorWidget
# ─────────────────────────────────────────────────────────────

# AVANT (dans _build, section "left_panel") :
"""
        self.prix_selector = prix_niveaux.PrixSelectorWidget(
        left_panel,
        prix_var=self.prix_var,
        client_id_fn=lambda: self.clients_map.get(self.client_nom.get()) if hasattr(self, 'clients_map') else None
        )
        self.prix_selector.pack(fill="x", pady=5)
        qty_frame = tk.Frame(left_panel, bg=CLR_CARD)
        qty_frame.pack(fill="x", pady=8)
        
        lbl(qty_frame, "Qté:", color=CLR_MUTED, size=9).pack(side="left", padx=2)
        self.qty_var = tk.StringVar(value="1")
        entry(qty_frame, width=8, textvariable=self.qty_var, font=("Segoe UI", 11)).pack(side="left", padx=5)
        
        lbl(qty_frame, "Prix:", color=CLR_MUTED, size=9).pack(side="left", padx=(15,2))
        self.prix_var = tk.StringVar()
        entry(qty_frame, width=10, textvariable=self.prix_var, font=("Segoe UI", 11)).pack(side="left", padx=5)
"""

# APRÈS :
"""
        qty_frame = tk.Frame(left_panel, bg=CLR_CARD)
        qty_frame.pack(fill="x", pady=8)
        
        lbl(qty_frame, "Qté:", color=CLR_MUTED, size=9).pack(side="left", padx=2)
        self.qty_var = tk.StringVar(value="1")
        entry(qty_frame, width=8, textvariable=self.qty_var, font=("Segoe UI", 11)).pack(side="left", padx=5)
        
        lbl(qty_frame, "Prix:", color=CLR_MUTED, size=9).pack(side="left", padx=(15,2))
        self.prix_var = tk.StringVar()
        entry(qty_frame, width=10, textvariable=self.prix_var, font=("Segoe UI", 11)).pack(side="left", padx=5)

        # PrixSelectorWidget instancié APRÈS la création de self.prix_var
        self.prix_selector = prix_niveaux.PrixSelectorWidget(
            left_panel,
            prix_var=self.prix_var,
            client_id_fn=lambda: self.clients_map.get(self.client_nom.get()) if hasattr(self, 'clients_map') else None
        )
        self.prix_selector.pack(fill="x", pady=5)
"""
