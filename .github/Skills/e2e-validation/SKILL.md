---
description: "Validation E2E du pipeline MAF : tests stub + Foundry optionnel + evidence"
---

# Skill : E2E Validation

## Déclencheur
Utiliser ce skill pour valider le pipeline MAF de bout en bout et produire l'evidence.

## Procédure

1. **Exécuter les tests stub**
   ```bash
   python -m pytest tests/ -v
   ```
   - Tous les tests doivent passer (exit code 0)

2. **Exécuter le pipeline CLI stub**
   ```bash
   python -m maf_app.orchestrator
   ```
   - Capturer stdout
   - Vérifier : 3 agents appelés, politique markdown produite

3. **Test Foundry optionnel** (si env vars OK)
   ```bash
   python -m pytest tests/ -v -k foundry_live
   ```
   - Skip automatique si pas de credentials

4. **Comparer avec le legacy**
   - Mode stub legacy (`python -m autogen.orchestrator`) vs MAF
   - Vérifier même structure de sortie

5. **Documenter l'evidence**
   - Créer `docs/E2E_EVIDENCE.md`
   - Inclure : commandes, sorties, timestamps

## Critères d'acceptation
- [ ] `pytest` exit code 0
- [ ] Pipeline stub produit politique markdown
- [ ] 3 agents appelés dans l'ordre : Veille → RAG → Producteur
- [ ] Evidence documentée dans `docs/E2E_EVIDENCE.md`
