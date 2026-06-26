"""
GUIDE D'INTÉGRATION — html_renderer.py dans votre gestion_stock.py
====================================================================
Ce fichier montre les remplacements à effectuer dans votre code principal.
Chaque bloc "AVANT" → "APRÈS" correspond à une méthode existante.
"""

# ══════════════════════════════════════════════════════════════════════
# 1. IMPORT À AJOUTER en haut de gestion_stock.py (après les autres imports)
# ══════════════════════════════════════════════════════════════════════
import html_renderer as hr   # ← ajouter cette ligne


# ══════════════════════════════════════════════════════════════════════
# 2. BonDetailDialog — remplacer _create_bon_html + print_bon + export_pdf
# ══════════════════════════════════════════════════════════════════════

# ─── AVANT ─────────────────────────────────────────────────────────
# class BonDetailDialog:
#     def _create_bon_html(self, path, title): ...   (~120 lignes)
#     def print_bon(self): ...                        (ouvrir + webbrowser)
#     def export_pdf(self): ...                       (wkhtmltopdf + fallback)

# ─── APRÈS ─────────────────────────────────────────────────────────
class BonDetailDialog_PATCH:

    def _get_html(self) -> str:
        """Génère le HTML via le module centralisé."""
        from gestion_stock import get_profil_by_type, get_conn
        profil = get_profil_by_type("bon_livraison")
        conn = get_conn()
        remises = conn.execute(
            "SELECT * FROM remises WHERE vente_id = ?" if self.bon_type == "vente"
            else "SELECT * FROM remises WHERE achat_id = ?",
            (self.bon_id,)
        ).fetchall()
        conn.close()
        remises_dicts = [dict(r) for r in remises]
        lignes_dicts  = [dict(l) for l in self.lignes_data]
        return hr.build_bon_html(
            profil        = profil,
            bon_data      = self.bon_data,
            lignes        = lignes_dicts,
            remises       = remises_dicts,
            bon_type      = self.bon_type,
        )

    def print_bon(self):
        viewer = hr.DocumentViewer(self)
        viewer.show(self._get_html(), f"BON N°{self.bon_data['numero']}")

    def export_pdf(self):
        viewer = hr.DocumentViewer(self)
        viewer.export_pdf(
            self._get_html(),
            default_name=f"Bon_{self.bon_data['numero']}.pdf",
        )


# ══════════════════════════════════════════════════════════════════════
# 3. FactureDetailDialog — remplacer _generate_html + print_facture + export_pdf
# ══════════════════════════════════════════════════════════════════════

# ─── AVANT ─────────────────────────────────────────────────────────
# class FactureDetailDialog:
#     def _generate_html(self): ...   (~130 lignes)
#     def print_facture(self): ...
#     def export_pdf(self): ...

# ─── APRÈS ─────────────────────────────────────────────────────────
class FactureDetailDialog_PATCH:

    def _get_html(self) -> str:
        from gestion_stock import get_profil_by_type
        profil = get_profil_by_type("facture")
        # Enrichir bon_data avec les champs attendus
        fac = dict(self.facture)
        fac["bon_numero"] = self.facture.get("bon_numero", "")
        return hr.build_facture_html(
            profil      = profil,
            facture     = fac,
            lignes      = [dict(l) for l in self.lignes],
            tva_details = [dict(t) for t in self.tva_details],
        )

    def print_facture(self):
        viewer = hr.DocumentViewer(self)
        viewer.show(self._get_html(), f"Facture {self.facture['numero']}")

    def export_pdf(self):
        viewer = hr.DocumentViewer(self)
        viewer.export_pdf(
            self._get_html(),
            default_name=f"Facture_{self.facture['numero']}.pdf",
        )


# ══════════════════════════════════════════════════════════════════════
# 4. ProduitPage — remplacer export_inventaire_pdf + export_inventaire_html
# ══════════════════════════════════════════════════════════════════════

# ─── APRÈS ─────────────────────────────────────────────────────────
class ProduitPage_PATCH:

    def export_inventaire_pdf(self):
        from gestion_stock import get_conn
        conn = get_conn()
        rows = conn.execute(
            "SELECT * FROM produits WHERE actif=1 ORDER BY designation"
        ).fetchall()
        conn.close()
        html = hr.build_inventaire_html(
            [dict(r) for r in rows], titre="Inventaire des produits"
        )
        viewer = hr.DocumentViewer(self)
        viewer.export_pdf(html, "inventaire.pdf")

    def export_inventaire_html(self):
        from gestion_stock import get_conn
        conn = get_conn()
        rows = conn.execute(
            "SELECT * FROM produits WHERE actif=1 ORDER BY designation"
        ).fetchall()
        conn.close()
        html = hr.build_inventaire_html(
            [dict(r) for r in rows], titre="Inventaire des produits"
        )
        viewer = hr.DocumentViewer(self)
        viewer.export_html(html, "inventaire.html")


# ══════════════════════════════════════════════════════════════════════
# 5. SituationPage — remplacer _generate_situation_html + print_filtered
# ══════════════════════════════════════════════════════════════════════

# ─── APRÈS ─────────────────────────────────────────────────────────
class SituationPage_PATCH:

    def print_filtered(self):
        from gestion_stock import get_profil_by_type
        transactions, total_ops, total_ret, total_vers = self.get_filtered_transactions()
        if not transactions:
            from tkinter import messagebox
            messagebox.showwarning("Avertissement", "Aucune donnée à imprimer")
            return
        profil = get_profil_by_type("situation")
        html = hr.build_situation_html(
            profil      = profil,
            tiers_nom   = self.current_tiers_nom,
            tiers_label = self.tiers_label,
            transactions= [dict(t) for t in transactions],
            total_ops   = total_ops,
            total_ret   = total_ret,
            total_vers  = total_vers,
            date_debut  = self.date_debut_var.get(),
            date_fin    = self.date_fin_var.get(),
        )
        viewer = hr.DocumentViewer(self)
        viewer.show(html, f"Situation {self.current_tiers_nom}")

    def export_filtered_html(self):
        from gestion_stock import get_profil_by_type
        transactions, total_ops, total_ret, total_vers = self.get_filtered_transactions()
        if not transactions:
            from tkinter import messagebox
            messagebox.showwarning("Avertissement", "Aucune donnée à exporter")
            return
        profil = get_profil_by_type("situation")
        html = hr.build_situation_html(
            profil      = profil,
            tiers_nom   = self.current_tiers_nom,
            tiers_label = self.tiers_label,
            transactions= [dict(t) for t in transactions],
            total_ops   = total_ops,
            total_ret   = total_ret,
            total_vers  = total_vers,
            date_debut  = self.date_debut_var.get(),
            date_fin    = self.date_fin_var.get(),
        )
        viewer = hr.DocumentViewer(self)
        viewer.export_html(html, f"situation_{self.current_tiers_nom}.html")
