---
description: "Automatisation PR via MCP GitHub : branche, commits, PR, Copilot Reviewer"
---

# Skill : PR Automation MCP

## Déclencheur
Utiliser ce skill pour créer une branche, pousser les fichiers et ouvrir une PR via MCP GitHub.

## Procédure

1. **Vérifier les prérequis**
   - MCP GitHub actif dans l'environnement
   - PAT configuré (jamais affiché)
   - Repo destination : `AmineGhazali9/GOVAIAPP-MAFF`

2. **Scanner les secrets**
   ```bash
   grep -rn "ghp_\|github_pat_\|sk-\|Bearer \|api_key" src/ tests/ docs/
   ```
   - Doit retourner zéro résultat

3. **Créer la branche**
   - Nom : `feature/maf-migration-skeleton`
   - Base : `main`

4. **Pousser les fichiers**
   - Commits atomiques par étape logique
   - Messages de commit descriptifs

5. **Ouvrir la PR**
   - Template :
     ```markdown
     ## What
     Migration skeleton AutoGen → MAF Python

     ## Why
     Moderniser l'orchestration multi-agents en conservant le métier identique

     ## How to test
     1. `pip install -e ".[dev]"`
     2. `python -m pytest tests/ -v`
     3. `python -m maf_app.orchestrator`

     ## Evidence
     - Tests : X/X passants
     - Pipeline stub : politique markdown générée

     ## Risks
     - Aucun secret dans le diff
     - Fallback stub fonctionnel
     ```

6. **Demander Copilot Reviewer**
   - Via MCP GitHub `request_copilot_review`

## Critères d'acceptation
- [ ] Branche créée sur le bon repo
- [ ] PR ouverte avec template complet
- [ ] Zéro secret dans le diff
- [ ] Copilot Reviewer demandé
