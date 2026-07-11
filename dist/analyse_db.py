# analyse_db.py
import sqlite3
import os
import re

DB_PATH = "gestion_stock.db"

def analyser_base():
    """Analyse la base de données et trouve toutes les valeurs problématiques"""
    print("="*80)
    print("🔍 ANALYSE DE LA BASE DE DONNÉES")
    print("="*80)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Base non trouvée: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_problemes = 0
    
    # ============================================================
    # 1. ANALYSE DE LA TABLE produits
    # ============================================================
    print("\n📦 TABLE PRODUITS")
    print("-"*80)
    
    cols_numeriques = [
        'prix_achat', 'prix_vente', 'stock_actuel', 'stock_min', 
        'facteur_conversion', 'tva', 'prix_moyen_pondere', 
        'cout_total_stock', 'prix_detail', 'prix_gros', 
        'prix_super_gros', 'prix_special'
    ]
    
    cursor.execute("SELECT id, code, designation, " + ", ".join(cols_numeriques) + " FROM produits")
    produits = cursor.fetchall()
    
    for p in produits:
        produit_id = p[0]
        code = p[1]
        designation = p[2]
        valeurs = p[3:]
        
        for i, col in enumerate(cols_numeriques):
            valeur = valeurs[i]
            
            # Vérifier si la valeur est problématique
            if valeur is None:
                print(f"  ⚠️ PRODUIT {produit_id} ({code}) - {col}: NULL")
                total_problemes += 1
            elif isinstance(valeur, str):
                # Si c'est une chaîne, vérifier si elle est vide ou a des espaces
                if valeur.strip() == '':
                    print(f"  ⚠️ PRODUIT {produit_id} ({code}) - {col}: CHAÎNE VIDE ''")
                    total_problemes += 1
                elif valeur.strip() != valeur:
                    print(f"  ⚠️ PRODUIT {produit_id} ({code}) - {col}: ESPACES DÉTECTÉS: '{valeur}'")
                    total_problemes += 1
                else:
                    # Vérifier si la chaîne peut être convertie en nombre
                    try:
                        # Nettoyer la chaîne
                        cleaned = valeur.strip().replace(',', '.')
                        cleaned = re.sub(r'[^\d.\-]', '', cleaned)
                        if cleaned == '':
                            print(f"  ⚠️ PRODUIT {produit_id} ({code}) - {col}: '{valeur}' (non numérique)")
                            total_problemes += 1
                        else:
                            float(cleaned)
                    except ValueError:
                        print(f"  ⚠️ PRODUIT {produit_id} ({code}) - {col}: '{valeur}' (non numérique)")
                        total_problemes += 1
    
    # ============================================================
    # 2. ANALYSE DE LA TABLE lignes_achat
    # ============================================================
    print("\n📄 TABLE LIGNES_ACHAT")
    print("-"*80)
    
    cols_lignes = ['quantite', 'prix_unitaire', 'total', 'tva_taux', 'total_ht', 'total_ttc']
    
    cursor.execute("SELECT id, bon_id, produit_id, " + ", ".join(cols_lignes) + " FROM lignes_achat")
    lignes = cursor.fetchall()
    
    for l in lignes:
        ligne_id = l[0]
        bon_id = l[1]
        produit_id = l[2]
        valeurs = l[3:]
        
        for i, col in enumerate(cols_lignes):
            valeur = valeurs[i]
            
            if valeur is None:
                print(f"  ⚠️ LIGNE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: NULL")
                total_problemes += 1
            elif isinstance(valeur, str):
                if valeur.strip() == '':
                    print(f"  ⚠️ LIGNE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: CHAÎNE VIDE ''")
                    total_problemes += 1
                elif valeur.strip() != valeur:
                    print(f"  ⚠️ LIGNE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: ESPACES: '{valeur}'")
                    total_problemes += 1
                else:
                    try:
                        cleaned = valeur.strip().replace(',', '.')
                        cleaned = re.sub(r'[^\d.\-]', '', cleaned)
                        if cleaned == '':
                            print(f"  ⚠️ LIGNE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: '{valeur}'")
                            total_problemes += 1
                        else:
                            float(cleaned)
                    except ValueError:
                        print(f"  ⚠️ LIGNE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: '{valeur}'")
                        total_problemes += 1
    
    # ============================================================
    # 3. ANALYSE DE LA TABLE bons_achat
    # ============================================================
    print("\n📄 TABLE BONS_ACHAT")
    print("-"*80)
    
    cols_bons = ['total', 'ancien_solde', 'nouveau_solde']
    
    cursor.execute("SELECT id, numero, " + ", ".join(cols_bons) + " FROM bons_achat")
    bons = cursor.fetchall()
    
    for b in bons:
        bon_id = b[0]
        numero = b[1]
        valeurs = b[2:]
        
        for i, col in enumerate(cols_bons):
            valeur = valeurs[i]
            
            if valeur is None:
                print(f"  ⚠️ BON {bon_id} ({numero}) - {col}: NULL")
                total_problemes += 1
            elif isinstance(valeur, str):
                if valeur.strip() == '':
                    print(f"  ⚠️ BON {bon_id} ({numero}) - {col}: CHAÎNE VIDE ''")
                    total_problemes += 1
                elif valeur.strip() != valeur:
                    print(f"  ⚠️ BON {bon_id} ({numero}) - {col}: ESPACES: '{valeur}'")
                    total_problemes += 1
                else:
                    try:
                        cleaned = valeur.strip().replace(',', '.')
                        cleaned = re.sub(r'[^\d.\-]', '', cleaned)
                        if cleaned == '':
                            print(f"  ⚠️ BON {bon_id} ({numero}) - {col}: '{valeur}'")
                            total_problemes += 1
                        else:
                            float(cleaned)
                    except ValueError:
                        print(f"  ⚠️ BON {bon_id} ({numero}) - {col}: '{valeur}'")
                        total_problemes += 1
    
    # ============================================================
    # 4. ANALYSE DE LA TABLE bons_vente
    # ============================================================
    print("\n📄 TABLE BONS_VENTE")
    print("-"*80)
    
    cursor.execute("SELECT id, numero, total FROM bons_vente")
    bons_vente = cursor.fetchall()
    
    for b in bons_vente:
        bon_id = b[0]
        numero = b[1]
        total = b[2]
        
        if total is None:
            print(f"  ⚠️ BON VENTE {bon_id} ({numero}) - total: NULL")
            total_problemes += 1
        elif isinstance(total, str):
            if total.strip() == '':
                print(f"  ⚠️ BON VENTE {bon_id} ({numero}) - total: CHAÎNE VIDE ''")
                total_problemes += 1
            elif total.strip() != total:
                print(f"  ⚠️ BON VENTE {bon_id} ({numero}) - total: ESPACES: '{total}'")
                total_problemes += 1
            else:
                try:
                    cleaned = total.strip().replace(',', '.')
                    cleaned = re.sub(r'[^\d.\-]', '', cleaned)
                    if cleaned == '':
                        print(f"  ⚠️ BON VENTE {bon_id} ({numero}) - total: '{total}'")
                        total_problemes += 1
                    else:
                        float(cleaned)
                except ValueError:
                    print(f"  ⚠️ BON VENTE {bon_id} ({numero}) - total: '{total}'")
                    total_problemes += 1
    
    # ============================================================
    # 5. ANALYSE DE LA TABLE lignes_vente
    # ============================================================
    print("\n📄 TABLE LIGNES_VENTE")
    print("-"*80)
    
    cols_lignes_vente = ['quantite', 'prix_unitaire', 'total']
    
    cursor.execute("SELECT id, bon_id, produit_id, " + ", ".join(cols_lignes_vente) + " FROM lignes_vente")
    lignes_vente = cursor.fetchall()
    
    for l in lignes_vente:
        ligne_id = l[0]
        bon_id = l[1]
        produit_id = l[2]
        valeurs = l[3:]
        
        for i, col in enumerate(cols_lignes_vente):
            valeur = valeurs[i]
            
            if valeur is None:
                print(f"  ⚠️ LIGNE VENTE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: NULL")
                total_problemes += 1
            elif isinstance(valeur, str):
                if valeur.strip() == '':
                    print(f"  ⚠️ LIGNE VENTE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: CHAÎNE VIDE ''")
                    total_problemes += 1
                elif valeur.strip() != valeur:
                    print(f"  ⚠️ LIGNE VENTE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: ESPACES: '{valeur}'")
                    total_problemes += 1
                else:
                    try:
                        cleaned = valeur.strip().replace(',', '.')
                        cleaned = re.sub(r'[^\d.\-]', '', cleaned)
                        if cleaned == '':
                            print(f"  ⚠️ LIGNE VENTE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: '{valeur}'")
                            total_problemes += 1
                        else:
                            float(cleaned)
                    except ValueError:
                        print(f"  ⚠️ LIGNE VENTE {ligne_id} (bon={bon_id}, produit={produit_id}) - {col}: '{valeur}'")
                        total_problemes += 1
    
    # ============================================================
    # 6. ANALYSE DE LA TABLE factures
    # ============================================================
    print("\n📄 TABLE FACTURES")
    print("-"*80)
    
    cols_factures = ['total_ht', 'tva', 'total_ttc']
    
    cursor.execute("SELECT id, numero, " + ", ".join(cols_factures) + " FROM factures")
    factures = cursor.fetchall()
    
    for f in factures:
        facture_id = f[0]
        numero = f[1]
        valeurs = f[2:]
        
        for i, col in enumerate(cols_factures):
            valeur = valeurs[i]
            
            if valeur is None:
                print(f"  ⚠️ FACTURE {facture_id} ({numero}) - {col}: NULL")
                total_problemes += 1
            elif isinstance(valeur, str):
                if valeur.strip() == '':
                    print(f"  ⚠️ FACTURE {facture_id} ({numero}) - {col}: CHAÎNE VIDE ''")
                    total_problemes += 1
                elif valeur.strip() != valeur:
                    print(f"  ⚠️ FACTURE {facture_id} ({numero}) - {col}: ESPACES: '{valeur}'")
                    total_problemes += 1
                else:
                    try:
                        cleaned = valeur.strip().replace(',', '.')
                        cleaned = re.sub(r'[^\d.\-]', '', cleaned)
                        if cleaned == '':
                            print(f"  ⚠️ FACTURE {facture_id} ({numero}) - {col}: '{valeur}'")
                            total_problemes += 1
                        else:
                            float(cleaned)
                    except ValueError:
                        print(f"  ⚠️ FACTURE {facture_id} ({numero}) - {col}: '{valeur}'")
                        total_problemes += 1
    
    # ============================================================
    # RÉSUMÉ
    # ============================================================
    print("\n" + "="*80)
    print(f"📊 RÉSUMÉ DE L'ANALYSE")
    print("="*80)
    print(f"  ✅ {total_problemes} problèmes détectés")
    
    if total_problemes == 0:
        print("  🎉 Aucun problème trouvé !")
    else:
        print("  ⚠️ Vous devez corriger ces problèmes avant de lancer l'application.")
        print("  💡 Exécutez le script fix_db.py pour corriger automatiquement.")
    
    conn.close()

if __name__ == "__main__":
    analyser_base()