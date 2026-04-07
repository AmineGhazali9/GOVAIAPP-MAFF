# GOVAIAPP-MAFF — Migration AutoGen → MAF

> Migration de l'orchestration multi-agents AutoGen vers Microsoft Agent Framework (MAF) Python, en conservant le métier identique (génération de politiques de gouvernance IA).

## Approche Copilot

Cette migration a été réalisée avec GitHub Copilot comme assistant principal, en suivant une stratégie structurée :

1. **Analyse du legacy** : Copilot analyse le repo AutoGen existant (lecture seule)
2. **Plan de migration** : mapping AutoGen → MAF, étapes progressives
3. **Exécution incrémentale** : scaffolding, tests, documentation
4. **Validation** : tests déterministes, E2E, PR avec Copilot Reviewer

Voir [MIGRATION_PLAN.md](MIGRATION_PLAN.md) pour le plan complet.

## Architecture

```
src/maf_app/
├── __init__.py
├── __main__.py          # Entry point: python -m maf_app.orchestrator
├── config.py            # Settings via env vars (.env)
├── orchestrator.py      # Pipeline séquentiel (Veille → RAG → Producteur)
├── agents/
│   ├── __init__.py      # AgentResult, PipelineContext
│   ├── veille_externe.py
│   ├── rag_interne.py
│   └── producteur.py
└── foundry/
    ├── __init__.py
    └── adapter.py       # AgentsClient + DefaultAzureCredential
```

## Handoff (Personas Copilot)

| Persona | Rôle | Livrable |
|---------|------|----------|
| ArchitecteModernisation | Analyse + stratégie | MIGRATION_PLAN.md |
| DevMAF | Scaffolding + intégration | src/maf_app/ |
| QAMA | Tests + E2E | tests/ |
| DocMAF | Documentation | README, docs/ |
| ValidatorPR | PR + conformité | PR GitHub |

Voir [docs/HANDOFF.md](docs/HANDOFF.md) pour le détail des transitions.

## Skills (Playbooks Copilot)

| Skill | But |
|-------|-----|
| `maf-migration-plan` | Analyser un legacy AutoGen et produire un plan de migration |
| `maf-python-scaffold` | Créer la structure MAF Python |
| `foundry-adapter` | Implémenter l'adaptateur Azure AI Foundry |
| `e2e-validation` | Valider le pipeline de bout en bout |
| `pr-automation-mcp` | Automatiser la PR via MCP GitHub |

## Commandes

### Installation
```bash
# Cloner le repo
git clone https://github.com/AmineGhazali9/GOVAIAPP-MAFF.git
cd GOVAIAPP-MAFF

# Créer un environnement virtuel
python -m venv .venv
.venv/Scripts/activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -e ".[dev]"

# Copier et remplir la config
cp .env.example .env
```

### Exécuter le pipeline (mode stub)
```bash
python -m maf_app.orchestrator
```

### Exécuter les tests
```bash
# Tests stub (déterministes, sans Azure)
pytest tests/ -v

# Tests Foundry live (si credentials configurées)
pytest tests/ -v -k foundry_live
```

## Configuration

Copier `.env.example` vers `.env` et remplir les valeurs :

| Variable | Description | Requis |
|----------|-------------|--------|
| `FOUNDRY_ENABLED` | Active le mode Foundry (`true`/`false`) | Non (default: `false`) |
| `FOUNDRY_PROJECT_ENDPOINT` | URL du projet Azure AI Foundry | Si Foundry activé |
| `FOUNDRY_AGENT_VEILLE_EXTERNE_ID` | ID agent veille externe | Si Foundry activé |
| `FOUNDRY_AGENT_RAG_ID` | ID agent RAG interne | Si Foundry activé |
| `FOUNDRY_AGENT_PRODUCTEUR_ID` | ID agent producteur | Si Foundry activé |

**Auth** : `DefaultAzureCredential` (Entra ID). Jamais de clé API dans le code.

## Licence

MIT
GOVAIAPP withMAF
