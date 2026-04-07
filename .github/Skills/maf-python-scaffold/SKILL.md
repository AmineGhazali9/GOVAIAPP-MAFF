---
description: "Scaffolding du projet MAF Python avec structure, config et orchestrateur"
---

# Skill : MAF Python Scaffold

## Déclencheur
Utiliser ce skill pour créer la structure de base d'un projet MAF Python avec orchestration séquentielle d'agents.

## Procédure

1. **Créer la structure de répertoires**
   ```
   src/maf_app/
   ├── __init__.py
   ├── config.py
   ├── orchestrator.py
   ├── agents/
   │   ├── __init__.py
   │   ├── veille_externe.py
   │   ├── rag_interne.py
   │   └── producteur.py
   └── foundry/
       ├── __init__.py
       └── adapter.py
   ```

2. **Implémenter config.py**
   - Charger les env vars via `python-dotenv`
   - Dataclass `Settings` avec defaults
   - Fonction `get_settings()` singleton

3. **Implémenter les agents**
   - Classe de base avec `run(context) → AgentResult`
   - Mode stub si Foundry non configuré
   - Mode Foundry via adapter

4. **Implémenter l'orchestrateur**
   - Pipeline séquentiel : boucle sur les agents
   - `PipelineContext` accumule les résultats
   - Entry point CLI : `python -m maf_app.orchestrator`

5. **Valider**
   ```bash
   python -c "from maf_app.orchestrator import run_pipeline; print('OK')"
   python -m maf_app.orchestrator
   ```

## Critères d'acceptation
- [ ] `python -m maf_app.orchestrator` s'exécute sans erreur en mode stub
- [ ] 3 agents appelés dans l'ordre : Veille → RAG → Producteur
- [ ] Résultat final = politique markdown
- [ ] Zéro dépendance Azure pour le mode stub
