"""
Module centralisé pour la génération et l'affichage HTML/PDF.
Remplace la logique dupliquée dans BonDetailDialog, FactureDetailDialog,
BonDialog, SituationPage, ProduitPage, etc.
"""

import os
import sys
import shutil
import subprocess
import tempfile
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────
# CSS commun injecté dans TOUS les documents générés
# ──────────────────────────────────────────────────────────────────────
COMMON_CSS = """
:root {
  --blue:    #3b82f6;
  --green:   #22c55e;
  --orange:  #f97316;
  --red:     #ef4444;
  --muted:   #6b7280;
  --border:  #e5e7eb;
  --bg-page: #f8f9fa;
  --bg-card: #ffffff;
  --text:    #1a1a2e;
  --radius:  8px;
  --shadow:  0 2px 8px rgba(0,0,0,.08);
}

*, *::before, *::after { box-sizing: border-box; }

body {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 13px;
  color: var(--text);
  background: var(--bg-page);
  margin: 0;
  padding: 20px;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  background: var(--bg-card);
  padding: 30px 40px;
  border-radius: 12px;
  box-shadow: var(--shadow);
}

/* ── EN-TÊTE SOCIÉTÉ ──────────────────────────────────── */
.doc-header {
  text-align: center;
  padding-bottom: 20px;
  margin-bottom: 24px;
  border-bottom: 3px solid var(--blue);
}
.doc-header h1 { font-size: 22px; font-weight: 600; margin: 0 0 4px; color: var(--text); }
.doc-header .subtitle { font-size: 17px; font-weight: 600; color: var(--blue); margin: 6px 0 0; }
.doc-header p  { font-size: 12px; color: var(--muted); margin: 3px 0; }

/* ── BLOC D'INFO (2 colonnes) ─────────────────────────── */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 16px 0;
}
.info-box {
  border: 0.5px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 18px;
  background: #fafafa;
}
.info-box h3 {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--blue);
  margin: 0 0 10px;
  font-weight: 600;
}
.info-row { display: flex; gap: 8px; padding: 3px 0; font-size: 13px; }
.info-label { color: var(--muted); min-width: 130px; font-weight: 500; }
.info-val   { color: var(--text); font-weight: 400; }

/* ── TABLEAU DE LIGNES ────────────────────────────────── */
.doc-table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  border-radius: var(--radius);
  overflow: hidden;
}
.doc-table thead th {
  background: #1e293b;
  color: #fff;
  padding: 10px 12px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .4px;
  font-weight: 600;
}
.doc-table tbody td {
  padding: 8px 12px;
  border-bottom: 0.5px solid var(--border);
  font-size: 13px;
}
.doc-table tbody tr:nth-child(even) td { background: #f8fafc; }
.doc-table tbody tr:hover td           { background: #f1f5f9; }
.doc-table tfoot td {
  background: #eef2ff;
  font-weight: 600;
  padding: 10px 12px;
  border-top: 2px solid var(--blue);
}

.text-right  { text-align: right !important; }
.text-center { text-align: center !important; }

/* ── RÉCAPITULATIF FINANCIER ──────────────────────────── */
.recap {
  margin-top: 20px;
  padding: 16px 20px;
  background: #f0fdf4;
  border: 1.5px solid var(--green);
  border-radius: 10px;
  max-width: 340px;
  margin-left: auto;
}
.recap-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 14px;
}
.recap-label { color: var(--muted); font-weight: 500; }
.recap-val   { font-weight: 600; color: var(--text); }
.recap-sep   { border: none; border-top: 1px dashed var(--border); margin: 6px 0; }
.recap-total .recap-label { font-size: 15px; color: var(--text); }
.recap-total .recap-val   { font-size: 17px; color: var(--green); }

/* ── BADGES DE STATUT ─────────────────────────────────── */
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}
.badge-green  { background: #dcfce7; color: #15803d; }
.badge-orange { background: #fef3c7; color: #b45309; }
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-purple { background: #ede9fe; color: #7c3aed; }

/* ── KPI CARDS (stats) ────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.kpi-card {
  background: var(--bg-card);
  border: 0.5px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
}
.kpi-card .kpi-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .4px; }
.kpi-card .kpi-val   { font-size: 22px; font-weight: 600; margin-top: 4px; }

/* ── OBSERVATIONS / NOTE ──────────────────────────────── */
.note-box {
  margin-top: 16px;
  padding: 12px 16px;
  background: #fef9f0;
  border-left: 4px solid var(--orange);
  border-radius: 0 var(--radius) var(--radius) 0;
  font-size: 13px;
}
.note-box strong { color: var(--orange); }

/* ── PIED DE PAGE ─────────────────────────────────────── */
.doc-footer {
  text-align: center;
  margin-top: 32px;
  padding-top: 16px;
  border-top: 0.5px solid var(--border);
  font-size: 11px;
  color: var(--muted);
}

/* ── IMPRESSION ───────────────────────────────────────── */
@media print {
  body        { background: white; padding: 0; }
  .container  { box-shadow: none; padding: 10mm; border-radius: 0; }
  .doc-header { border-bottom-color: #1e293b; }
  @page       { size: A4; margin: 12mm; }
}
"""


def _badge(statut: str) -> str:
    """Retourne le HTML d'un badge coloré selon le statut."""
    mapping = {
        "Validé":  "green",
        "Payée":   "green",
        "Émise":   "orange",
        "Annulé":  "red",
        "Annulée": "red",
    }
    cls = mapping.get(statut, "blue")
    return f'<span class="badge badge-{cls}">{statut}</span>'


def _fmt(val, digits=2) -> str:
    """Formate un nombre avec séparateur de milliers."""
    try:
        return f"{float(val):,.{digits}f}"
    except (TypeError, ValueError):
        return str(val or "")


# ──────────────────────────────────────────────────────────────────────
# CONSTRUCTEUR D'EN-TÊTE SOCIÉTÉ
# ──────────────────────────────────────────────────────────────────────
def build_header_html(profil: dict | None, titre_document: str) -> str:
    """Génère l'en-tête avec logo/infos société + titre du document."""
    if not profil:
        return f"""
        <div class="doc-header">
          <h1>VOTRE SOCIÉTÉ</h1>
          <p class="subtitle">{titre_document}</p>
        </div>"""

    nom    = profil.get("nom", "VOTRE SOCIÉTÉ") or "VOTRE SOCIÉTÉ"
    adr    = profil.get("adresse", "") or ""
    ville  = profil.get("ville", "") or ""
    tel    = profil.get("telephone", "") or ""
    email  = profil.get("email", "") or ""
    nif    = profil.get("nif", "") or ""
    nis    = profil.get("nis", "") or ""
    nrc    = profil.get("nrc", "") or ""

    lines = [f"<h1>{nom}</h1>"]
    if adr:    lines.append(f"<p>{adr}</p>")
    if ville:  lines.append(f"<p>{ville}</p>")
    if tel or email:
        parts = []
        if tel:   parts.append(f"Tél : {tel}")
        if email: parts.append(f"Email : {email}")
        lines.append(f"<p>{' &nbsp;|&nbsp; '.join(parts)}</p>")
    if nif or nis or nrc:
        parts = []
        if nif: parts.append(f"NIF : {nif}")
        if nis: parts.append(f"NIS : {nis}")
        if nrc: parts.append(f"NRC : {nrc}")
        lines.append(f"<p>{' &nbsp;|&nbsp; '.join(parts)}</p>")
    lines.append(f'<p class="subtitle">{titre_document}</p>')

    return f'<div class="doc-header">\n  {"".join(lines)}\n</div>'


# ──────────────────────────────────────────────────────────────────────
# GÉNÉRATEURS SPÉCIALISÉS
# ──────────────────────────────────────────────────────────────────────

def build_bon_html(profil, bon_data: dict, lignes: list, remises: list,
                   bon_type: str = "vente") -> str:
    """
    Génère le HTML complet d'un bon d'achat ou de vente.
    `bon_data` doit contenir : numero, date_bon, statut, tiers (nom),
      total, [date_livraison, num_facture_fournisseur, num_bl_fournisseur]
    `lignes` : liste de dicts avec designation, quantite, facteur_conversion,
               unite, prix_unitaire, total.
    `remises`: liste de dicts (produit_id, valeur, motif, total_avant, total_apres)
    """
    titre = f"BON D'ACHAT N° {bon_data['numero']}" if bon_type == "achat" \
            else f"BON DE VENTE N° {bon_data['numero']}"

    tiers_label = "Fournisseur" if bon_type == "achat" else "Client"

    # ── info-box gauche : doc
    doc_rows = f"""
    <div class="info-row"><span class="info-label">N° bon :</span><span class="info-val">{bon_data['numero']}</span></div>
    <div class="info-row"><span class="info-label">Date :</span><span class="info-val">{bon_data.get('date_bon','')}</span></div>
    <div class="info-row"><span class="info-label">Statut :</span><span class="info-val">{_badge(bon_data.get('statut',''))}</span></div>
    """
    if bon_type == "achat":
        dl = bon_data.get("date_livraison") or "—"
        ff = bon_data.get("num_facture_fournisseur") or "—"
        bl = bon_data.get("num_bl_fournisseur") or "—"
        doc_rows += f"""
    <div class="info-row"><span class="info-label">Date livraison :</span><span class="info-val">{dl}</span></div>
    <div class="info-row"><span class="info-label">N° Fact. Fourn. :</span><span class="info-val">{ff}</span></div>
    <div class="info-row"><span class="info-label">N° BL Fourn. :</span><span class="info-val">{bl}</span></div>
    <div class="info-row"><span class="info-label">Ancien solde :</span><span class="info-val">{_fmt(bon_data.get('ancien_solde',0))} DA</span></div>
    <div class="info-row"><span class="info-label">Nouveau solde :</span><span class="info-val">{_fmt(bon_data.get('nouveau_solde',0))} DA</span></div>
    """

    # ── info-box droite : tiers
    tiers_rows = f"""
    <div class="info-row"><span class="info-label">{tiers_label} :</span><span class="info-val">{bon_data.get('tiers','')}</span></div>
    """

    # ── lignes du tableau
    remises_dict = {r.get("produit_id"): r for r in remises if r.get("produit_id")}
    rows_html = ""
    total_ht = total_tva = 0.0

    for l in lignes:
        facteur = float(l.get("facteur_conversion") or 1) or 1
        qte_base = float(l.get("quantite") or 0)
        qte_carton = qte_base / facteur
        prix = float(l.get("prix_unitaire") or 0)
        ht_l = float(l.get("total") or qte_base * prix)
        tva_taux_l = float(l.get("tva_taux") or 0)
        tva_l = ht_l * tva_taux_l / 100
        ttc_l = ht_l + tva_l
        total_ht  += ht_l
        total_tva += tva_l

        rem = remises_dict.get(l.get("produit_id"))
        rem_html = f"{rem['valeur']:.0f}%" if rem else "—"

        rows_html += f"""
        <tr>
          <td>{l.get('code','')}</td>
          <td>{l.get('designation','')}</td>
          <td class="text-center">{qte_base:.2f}</td>
          <td class="text-center">{qte_carton:.2f}</td>
          <td class="text-center">{l.get('unite','')}</td>
          <td class="text-right">{_fmt(prix)}</td>
          <td class="text-center">{rem_html}</td>
          <td class="text-right">{_fmt(ht_l)}</td>
          <td class="text-center">{tva_taux_l:.0f}%</td>
          <td class="text-right">{_fmt(ttc_l)}</td>
        </tr>"""

    total_ttc = total_ht + total_tva

    # ── bloc récapitulatif
    recap_html = f"""
    <div class="recap">
      <div class="recap-row">
        <span class="recap-label">Total HT</span>
        <span class="recap-val">{_fmt(total_ht)} DA</span>
      </div>
      <div class="recap-row">
        <span class="recap-label">TVA</span>
        <span class="recap-val">{_fmt(total_tva)} DA</span>
      </div>
      <hr class="recap-sep">
      <div class="recap-row recap-total">
        <span class="recap-label">Total TTC</span>
        <span class="recap-val">{_fmt(total_ttc)} DA</span>
      </div>
    </div>"""

    header_html = build_header_html(profil, titre)
    footer_html = f"""
    <div class="doc-footer">
      Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titre}</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
<div class="container">
  {header_html}

  <div class="info-grid">
    <div class="info-box">
      <h3>Document</h3>
      {doc_rows}
    </div>
    <div class="info-box">
      <h3>{tiers_label}</h3>
      {tiers_rows}
    </div>
  </div>

  <table class="doc-table">
    <thead>
      <tr>
        <th>Code</th>
        <th>Désignation</th>
        <th class="text-center">Qté unités</th>
        <th class="text-center">Qté cartons</th>
        <th class="text-center">Unité</th>
        <th class="text-right">Prix unit.</th>
        <th class="text-center">Remise</th>
        <th class="text-right">Total HT</th>
        <th class="text-center">TVA</th>
        <th class="text-right">Total TTC</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
    <tfoot>
      <tr>
        <td colspan="7" class="text-right">Totaux</td>
        <td class="text-right">{_fmt(total_ht)} DA</td>
        <td class="text-right">{_fmt(total_tva)} DA</td>
        <td class="text-right">{_fmt(total_ttc)} DA</td>
      </tr>
    </tfoot>
  </table>

  {recap_html}
  {footer_html}
</div>
</body>
</html>"""


def build_facture_html(profil, facture: dict, lignes: list,
                       tva_details: list) -> str:
    """Génère le HTML complet d'une facture."""
    titre = f"FACTURE N° {facture['numero']}"

    statut_map = {"Payée": "green", "Émise": "orange", "Annulée": "red"}
    statut_cls = statut_map.get(facture.get("statut", ""), "blue")

    doc_rows = f"""
    <div class="info-row"><span class="info-label">N° Facture :</span><span class="info-val">{facture['numero']}</span></div>
    <div class="info-row"><span class="info-label">Date :</span><span class="info-val">{facture.get('date_facture','')}</span></div>
    <div class="info-row"><span class="info-label">Bon de vente :</span><span class="info-val">{facture.get('bon_numero','')}</span></div>
    <div class="info-row"><span class="info-label">Échéance :</span><span class="info-val">{facture.get('date_echeance') or '—'}</span></div>
    <div class="info-row"><span class="info-label">Statut :</span><span class="info-val"><span class="badge badge-{statut_cls}">{facture.get('statut','')}</span></span></div>
    """

    client_rows = f"""
    <div class="info-row"><span class="info-label">Client :</span><span class="info-val">{facture.get('client_nom','')}</span></div>
    """
    if facture.get("client_adresse"):
        client_rows += f'<div class="info-row"><span class="info-label">Adresse :</span><span class="info-val">{facture["client_adresse"]}</span></div>'
    if facture.get("client_tel"):
        client_rows += f'<div class="info-row"><span class="info-label">Tél :</span><span class="info-val">{facture["client_tel"]}</span></div>'

    rows_html = ""
    for l in lignes:
        rows_html += f"""
        <tr>
          <td>{l.get('designation','')}</td>
          <td class="text-center">{float(l.get('quantite',0)):.2f}</td>
          <td class="text-center">{l.get('unite','')}</td>
          <td class="text-right">{_fmt(l.get('prix_unitaire',0))}</td>
          <td class="text-right">{_fmt(l.get('total',0))}</td>
        </tr>"""

    total_ht  = float(facture.get("total_ht", 0))
    total_ttc = float(facture.get("total_ttc", 0))
    total_tva = total_ttc - total_ht

    tva_rows = ""
    for td in tva_details:
        taux = td.get("taux_tva", 0)
        ht_d = td.get("total_ht", 0)
        tv_d = td.get("total_tva", 0)
        tva_rows += f"""
      <div class="recap-row">
        <span class="recap-label">TVA {taux:.0f}% / {_fmt(ht_d)} DA</span>
        <span class="recap-val">{_fmt(tv_d)} DA</span>
      </div>"""

    if not tva_rows:
        tva_rows = f"""
      <div class="recap-row">
        <span class="recap-label">TVA {facture.get('tva',0):.0f}%</span>
        <span class="recap-val">{_fmt(total_tva)} DA</span>
      </div>"""

    obs_html = ""
    if facture.get("observations"):
        obs_html = f"""
    <div class="note-box">
      <strong>Observations :</strong> {facture['observations']}
    </div>"""

    header_html = build_header_html(profil, titre)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titre}</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
<div class="container">
  {header_html}

  <div class="info-grid">
    <div class="info-box">
      <h3>Facture</h3>
      {doc_rows}
    </div>
    <div class="info-box">
      <h3>Client</h3>
      {client_rows}
    </div>
  </div>

  <table class="doc-table">
    <thead>
      <tr>
        <th>Désignation</th>
        <th class="text-center">Quantité</th>
        <th class="text-center">Unité</th>
        <th class="text-right">Prix unit.</th>
        <th class="text-right">Total</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
    <tfoot>
      <tr>
        <td colspan="4" class="text-right">Total HT</td>
        <td class="text-right">{_fmt(total_ht)} DA</td>
      </tr>
    </tfoot>
  </table>

  <div class="recap">
    <div class="recap-row">
      <span class="recap-label">Total HT</span>
      <span class="recap-val">{_fmt(total_ht)} DA</span>
    </div>
    {tva_rows}
    <hr class="recap-sep">
    <div class="recap-row recap-total">
      <span class="recap-label">Total TTC</span>
      <span class="recap-val">{_fmt(total_ttc)} DA</span>
    </div>
  </div>

  {obs_html}

  <div class="doc-footer">
    Merci pour votre confiance !<br>
    Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
  </div>
</div>
</body>
</html>"""


def build_inventaire_html(rows: list, titre: str = "Inventaire") -> str:
    """Génère le HTML d'un inventaire produits."""
    rows_html = ""
    for r in rows:
        stock  = float(r.get("stock_actuel", 0))
        facteur = float(r.get("facteur_conversion") or 1) or 1
        cartons = stock / facteur
        status_cls = "badge-green" if stock > float(r.get("stock_min", 0)) else "badge-red"
        rows_html += f"""
        <tr>
          <td>{r.get('code','')}</td>
          <td>{r.get('designation','')}</td>
          <td class="text-center">{r.get('unite','')}</td>
          <td class="text-right">{_fmt(r.get('prix_achat',0))}</td>
          <td class="text-right">{_fmt(r.get('prix_vente',0))}</td>
          <td class="text-center">{stock:.2f}</td>
          <td class="text-center">{cartons:.2f}</td>
          <td class="text-center"><span class="badge {status_cls}">{'OK' if stock > float(r.get('stock_min',0)) else 'Alerte'}</span></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>{titre}</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
<div class="container">
  <div class="doc-header">
    <h1>{titre}</h1>
    <p>Édité le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
  </div>

  <table class="doc-table">
    <thead>
      <tr>
        <th>Code</th>
        <th>Désignation</th>
        <th class="text-center">Unité</th>
        <th class="text-right">Prix Achat</th>
        <th class="text-right">Prix Vente</th>
        <th class="text-center">Stock unités</th>
        <th class="text-center">Stock cartons</th>
        <th class="text-center">État</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>

  <div class="doc-footer">
    {len(rows)} produit(s) — Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
  </div>
</div>
</body>
</html>"""


def build_situation_html(profil, tiers_nom: str, tiers_label: str,
                         transactions: list, total_ops: float,
                         total_ret: float, total_vers: float,
                         date_debut: str, date_fin: str) -> str:
    """Génère le HTML de la situation financière d'un client/fournisseur."""
    titre = f"SITUATION DE {tiers_nom.upper()}"
    solde_final = total_ops - total_ret - total_vers

    kpi_html = f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total opérations</div>
        <div class="kpi-val" style="color:var(--blue)">{_fmt(total_ops)} DA</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total retours</div>
        <div class="kpi-val" style="color:var(--orange)">{_fmt(total_ret)} DA</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total versements</div>
        <div class="kpi-val" style="color:#8b5cf6">{_fmt(total_vers)} DA</div>
      </div>
      <div class="kpi-card" style="border-color:var(--green)">
        <div class="kpi-label">Solde final</div>
        <div class="kpi-val" style="color:{'var(--green)' if solde_final>=0 else 'var(--red)'}">{_fmt(solde_final)} DA</div>
      </div>
    </div>"""

    COLOR_MAP = {
        "VENTE":     "var(--green)",
        "ACHAT":     "var(--blue)",
        "RETOUR":    "var(--orange)",
        "VERSEMENT": "#8b5cf6",
    }
    rows_html = ""
    solde_cumule = 0.0
    for t in transactions:
        solde_cumule += float(t.get("montant", 0))
        clr = COLOR_MAP.get(t.get("type", ""), "var(--text)")
        rows_html += f"""
        <tr>
          <td class="text-center">{t.get('date','')}</td>
          <td class="text-center" style="color:{clr};font-weight:600">{t.get('type','')}</td>
          <td class="text-center">{t.get('document','')}</td>
          <td class="text-right" style="color:{clr};font-weight:600">{float(t.get('montant',0)):+,.2f} DA</td>
          <td class="text-right">{_fmt(solde_cumule)} DA</td>
        </tr>"""

    header_html = build_header_html(profil, titre)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>{titre}</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
<div class="container">
  {header_html}

  <div class="info-box" style="margin-bottom:16px">
    <div class="info-row">
      <span class="info-label">{tiers_label} :</span>
      <span class="info-val">{tiers_nom}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Période :</span>
      <span class="info-val">{date_debut} → {date_fin}</span>
    </div>
  </div>

  {kpi_html}

  <table class="doc-table">
    <thead>
      <tr>
        <th class="text-center">Date</th>
        <th class="text-center">Type</th>
        <th class="text-center">Document</th>
        <th class="text-right">Montant</th>
        <th class="text-right">Solde après</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
    <tfoot>
      <tr>
        <td colspan="3" class="text-right">Total général</td>
        <td class="text-right">{_fmt(total_ops - total_ret - total_vers)} DA</td>
        <td class="text-right">{_fmt(solde_final)} DA</td>
      </tr>
    </tfoot>
  </table>

  <div class="doc-footer">
    Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
  </div>
</div>
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────
# AFFICHAGE / EXPORT COMMUN
# ──────────────────────────────────────────────────────────────────────

class DocumentViewer:
    """
    Utilitaire pour afficher, imprimer et exporter des documents HTML/PDF.
    Utilisation :
        viewer = DocumentViewer(parent_widget)
        viewer.show(html_content, "Facture FC202600001")
        viewer.export_pdf(html_content, "facture.pdf")
    """

    def __init__(self, parent: tk.Widget):
        self.parent = parent

    # ── AFFICHAGE NAVIGATEUR ──────────────────────────────────────────
    def show(self, html: str, title: str = "Document") -> None:
        """Ouvre le HTML dans le navigateur par défaut."""
        tmp = self._write_temp(html)
        try:
            webbrowser.open(tmp)
            messagebox.showinfo(
                "Impression",
                "Document ouvert dans votre navigateur.\n"
                "Utilisez Ctrl+P pour imprimer ou 'Enregistrer en PDF'.",
                parent=self.parent,
            )
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self.parent)
        finally:
            self._schedule_cleanup(tmp)

    # ── EXPORT PDF ────────────────────────────────────────────────────
    def export_pdf(self, html: str, default_name: str = "document.pdf") -> None:
        """Exporte vers un fichier PDF (via wkhtmltopdf si disponible)."""
        path = filedialog.asksaveasfilename(
            parent=self.parent,
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("Tous", "*.*")],
            initialfile=default_name,
        )
        if not path:
            return

        tmp = self._write_temp(html)
        try:
            exe = shutil.which("wkhtmltopdf")
            if exe:
                result = subprocess.run(
                    [exe, "--quiet", tmp, path],
                    capture_output=True, timeout=30,
                )
                if result.returncode == 0:
                    messagebox.showinfo("Succès", f"PDF créé :\n{path}", parent=self.parent)
                    return
                # wkhtmltopdf a échoué → fallback navigateur
                messagebox.showwarning(
                    "Avertissement",
                    "wkhtmltopdf a signalé une erreur.\nLe document va s'ouvrir dans le navigateur.",
                    parent=self.parent,
                )
            webbrowser.open(tmp)
            messagebox.showinfo(
                "Info",
                "wkhtmltopdf introuvable ou en échec.\n"
                "Utilisez Fichier › Imprimer › Enregistrer au format PDF.",
                parent=self.parent,
            )
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self.parent)
        finally:
            self._schedule_cleanup(tmp)

    # ── EXPORT HTML ───────────────────────────────────────────────────
    def export_html(self, html: str, default_name: str = "document.html") -> None:
        path = filedialog.asksaveasfilename(
            parent=self.parent,
            defaultextension=".html",
            filetypes=[("HTML", "*.html"), ("Tous", "*.*")],
            initialfile=default_name,
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            messagebox.showinfo("Succès", f"Fichier HTML créé :\n{path}", parent=self.parent)
            if messagebox.askyesno("Ouvrir", "Voulez-vous l'ouvrir maintenant ?", parent=self.parent):
                webbrowser.open(path)
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self.parent)

    # ── HELPERS ───────────────────────────────────────────────────────
    def _write_temp(self, html: str) -> str:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        )
        tmp.write(html)
        tmp.close()
        return tmp.name

    def _schedule_cleanup(self, path: str, delay_ms: int = 90_000) -> None:
        """Supprime le fichier temporaire après `delay_ms` ms."""
        def _del():
            try:
                os.unlink(path)
            except OSError:
                pass
        if hasattr(self.parent, "after"):
            self.parent.after(delay_ms, _del)
