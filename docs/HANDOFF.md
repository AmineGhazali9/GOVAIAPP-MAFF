# Stratégie de Handoff — Personas Copilot

Ce document formalise les transitions entre personas lors de la migration AutoGen → MAF.

## Flux de handoff

```
ArchitecteModernisation
    │
    ├─ Livrable: MIGRATION_PLAN.md, structure projet, .env.example
    │
    ▼
DevMAF
    │
    ├─ Livrable: src/maf_app/ (config, adapter, agents, orchestrator)
    ├─ Validation: python -m maf_app.orchestrator (stub OK)
    │
    ▼
QAMA
    │
    ├─ Livrable: tests/ (≥10 tests déterministes, test Foundry conditionnel)
    ├─ Validation: pytest exit code 0
    │
    ▼
DocMAF
    │
    ├─ Livrable: README.md, docs/HANDOFF.md, docs/MAPPING_AUTOGEN_MAF.md
    ├─ Validation: toutes sections présentes, liens valides
    │
    ▼
ValidatorPR
    │
    ├─ Livrable: branche feature/maf-migration-skeleton, PR ouverte
    ├─ Validation: zéro secret, Copilot Reviewer demandé
    │
    ▼
QAMA (reprise)
    │
    ├─ Livrable: docs/E2E_EVIDENCE.md
    ├─ Validation: pipeline stub produit politique markdown
    │
    ▼
Validation humaine finale
```

## Détail des transitions

### 1. ArchitecteModernisation → DevMAF
| | |
|---|---|
| **Quand** | MIGRATION_PLAN.md validé par l'humain |
| **Livrable transmis** | Plan de migration, mapping AutoGen→MAF, structure projet |
| **Prérequis** | pyproject.toml, .env.example, .gitignore créés |

### 2. DevMAF → QAMA
| | |
|---|---|
| **Quand** | `python -m maf_app.orchestrator` fonctionne en mode stub |
| **Livrable transmis** | Code source complet dans `src/maf_app/` |
| **Prérequis** | 3 agents, orchestrateur, adapter Foundry fonctionnels |

### 3. QAMA → DocMAF
| | |
|---|---|
| **Quand** | `pytest` exit code 0, ≥10 tests passants |
| **Livrable transmis** | Suite de tests verte, rapport de couverture |
| **Prérequis** | Tests déterministes (stub), test Foundry conditionnel |

### 4. DocMAF → ValidatorPR
| | |
|---|---|
| **Quand** | README, HANDOFF, MAPPING complets |
| **Livrable transmis** | Documentation complète |
| **Prérequis** | Toutes sections présentes, aucun secret |

### 5. ValidatorPR → QAMA (reprise)
| | |
|---|---|
| **Quand** | PR ouverte avec Copilot Reviewer |
| **Livrable transmis** | URL de la PR, branche |
| **Prérequis** | Zéro secret dans le diff, tests passent |

### 6. QAMA → Validation humaine
| | |
|---|---|
| **Quand** | Evidence E2E documentée |
| **Livrable transmis** | docs/E2E_EVIDENCE.md, logs de run |
| **Prérequis** | Pipeline produit politique markdown en mode stub |
