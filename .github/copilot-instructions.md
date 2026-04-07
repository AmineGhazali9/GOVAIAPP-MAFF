---
applyTo: "**/*.py"
---

# GOVAIAPP-MAFF — Copilot Instructions

## Projet
Migration AutoGen → Microsoft Agent Framework (MAF) pour la génération de politiques IA governance.

## Règles strictes
- **Zéro secret** : jamais de token, clé API, PAT, ou credential dans le code
- **DefaultAzureCredential** uniquement pour l'auth Azure
- **Fallback stub** : chaque agent doit fonctionner sans Azure
- **Tests déterministes** : aucune dépendance Azure active requise pour les tests stub
- **Code Python** : type hints, logging structuré, docstrings

## Architecture cible
```
src/maf_app/
├── config.py           # Settings via env vars
├── orchestrator.py     # Pipeline séquentiel
├── agents/             # 3 agents métier
└── foundry/            # Adaptateur Azure AI Foundry
```

## Flux métier (ne pas modifier l'ordre)
1. VeilleExterneAgent → signaux réglementaires
2. RagInterneAgent → enrichissement docs internes
3. ProducteurPolitiqueAgent → synthèse politique

## Conventions
- Imports : stdlib → third-party → local
- Logging : `logging.getLogger(__name__)`
- Config : `python-dotenv` + `os.getenv()`
- Tests : `pytest` + `monkeypatch` pour l'isolation
