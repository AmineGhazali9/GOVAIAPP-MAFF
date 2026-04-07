# MIGRATION_PLAN.md — AutoGen → Microsoft Agent Framework (MAF)

## 1. Analyse du Legacy (GOVAIAPP)

### Architecture actuelle
| Couche | Techno | Rôle |
|--------|--------|------|
| UI | Streamlit (`app/ui/app.py`) | Formulaire web, POST httpx vers API |
| API | FastAPI (`app/api/`) | `/health`, `/generate-policy`, mode Foundry/Stub |
| Orchestration | AutoGen AG2 0.7 (`autogen/`) | `RoundRobinGroupChat` séquentiel, 3 agents |
| Agents Foundry | `autogen/agents/` + `foundry_config.py` | `BaseChatAgent` → `call_foundry_generic()` |
| RAG | `app/rag/retriever.py` | Azure AI Search ou fallback local |
| Foundry Client | `app/foundry/client.py` | `AgentsClient` + `DefaultAzureCredential` |
| Data | `data/` | Template policy + cache veille |

### Flux métier (immutable)
```
CompanyContext
  → VeilleExterneAgent  (signaux réglementaires externes)
  → RagInterneAgent     (enrichissement docs internes)
  → ProducteurPolitiqueAgent (synthèse politique IA)
  → PolicyDraftResponse (markdown + sources)
```

### Patterns AutoGen utilisés
- `BaseChatAgent` avec `on_messages()` async
- `RoundRobinGroupChat(participants=[...], termination_condition=MaxMessageTermination(4))`
- Sync wrapper `asyncio.run()` pour FastAPI/CLI
- Fallback par agent : `[STUB]` ou `[FALLBACK]`

### Technos / Frameworks
- Python 3.10+, FastAPI, Streamlit, httpx, Pydantic v2
- autogen-agentchat ≥0.7, autogen-core ≥0.7
- azure-ai-agents ≥1.1, azure-identity ≥1.16, azure-search-documents ≥11.4
- pytest ≥8.2 (23 tests déterministes)

### Points de dette technique
| Risque | Impact | Priorité |
|--------|--------|----------|
| Pas de rate-limiting API | DoS / coût Foundry | Haut |
| Pas de timeout Foundry | API bloquée | Haut |
| Pas de sanitization prompt | Injection prompt | Haut |
| Logs exposent contexte user | Privacy | Moyen |
| Pas de lock file dépendances | Builds instables | Moyen |

---

## 2. Stratégie de Migration

### Principe directeur
> Minimum de changement : remplacer **uniquement** la couche d'orchestration AutoGen par un pipeline séquentiel natif Python, en réutilisant exactement les mêmes agents Azure AI Foundry (mêmes IDs, même auth).

### Ce qui change
- `autogen-agentchat` / `autogen-core` → supprimés des dépendances
- `RoundRobinGroupChat` → pipeline séquentiel Python (boucle simple)
- `BaseChatAgent.on_messages()` → classe Agent MAF avec `run(context)` 

### Ce qui ne change PAS
- Azure AI Foundry : mêmes endpoints, mêmes agent IDs
- Auth : `DefaultAzureCredential` (Entra ID)
- Flux métier : Veille → RAG → Producteur (séquentiel, même ordre)
- Fallback : stub si Foundry non configuré

---

## 3. Mapping AutoGen → MAF

| Concept AutoGen (AG2 0.7) | Concept MAF Python | Fichier cible |
|---|---|---|
| `BaseChatAgent` | Classe `Agent` avec `run(context) → str` | `src/maf_app/agents/*.py` |
| `RoundRobinGroupChat` | `SequentialPipeline.run(agents, context)` | `src/maf_app/orchestrator.py` |
| `MaxMessageTermination(4)` | Contrôle explicite (len(agents) itérations) | `src/maf_app/orchestrator.py` |
| `on_messages(messages)` | `agent.run(context: PipelineContext)` | `src/maf_app/agents/*.py` |
| `TextMessage` | `AgentResult(content, source, metadata)` | `src/maf_app/agents/__init__.py` |
| `Response(chat_message=...)` | Return `AgentResult` | `src/maf_app/agents/*.py` |
| `call_foundry_generic()` | `foundry_adapter.call_agent()` | `src/maf_app/foundry/adapter.py` |
| `foundry_config.py` | `config.py` + `.env` | `src/maf_app/config.py` |

---

## 4. Étapes de Migration

### Étape 1 — Fondations
- Structure projet, `pyproject.toml`, `.env.example`, `.gitignore`
- `MIGRATION_PLAN.md`, personas, skills, copilot-instructions
- **Critère** : tous les fichiers de config présents, zéro secret

### Étape 2 — Adaptateur Foundry
- `src/maf_app/foundry/adapter.py` : appels AgentsClient
- `src/maf_app/config.py` : chargement env vars
- **Critère** : import OK en mode stub

### Étape 3 — Orchestrateur MAF
- 3 agents Python (`veille_externe`, `rag_interne`, `producteur`)
- Pipeline séquentiel dans `orchestrator.py`
- **Critère** : `python -m maf_app.orchestrator` produit une politique stub

### Étape 4 — Tests
- Tests stub déterministes (≥10)
- Test Foundry conditionnel (`@pytest.mark.skipif`)
- **Critère** : `pytest` exit code 0

### Étape 5 — Documentation
- README complet, HANDOFF.md, MAPPING_AUTOGEN_MAF.md
- **Critère** : toutes sections présentes, liens valides

### Étape 6 — PR via MCP GitHub
- Branche `feature/maf-migration-skeleton`
- PR avec template What/Why/How/Evidence/Risks
- Copilot Reviewer
- **Critère** : PR ouverte, aucun secret dans diff

### Étape 7 — Validation E2E
- Run pipeline stub complet
- Evidence documentée
- **Critère** : politique markdown produite, 3 agents appelés en séquence

---

## 5. Stratégie Handoff (Personas)

```
ArchitecteModernisation ──[MIGRATION_PLAN.md + structure]──► DevMAF
DevMAF                  ──[adapter + orchestrateur]────────► QAMA
QAMA                    ──[tests OK]──────────────────────► DocMAF
DocMAF                  ──[README + docs]─────────────────► ValidatorPR
ValidatorPR             ──[PR ouverte, Copilot Review]────► QAMA
QAMA                    ──[E2E evidence]──────────────────► Validation humaine
```

---

## 6. Risques et Mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| MAF SDK change d'API | Moyen | Moyen | Wrapper adapter isolé, facile à mettre à jour |
| Foundry agents indisponibles | Faible | Haut | Fallback stub automatique, tests déterministes |
| Secret leaké dans la PR | Faible | Critique | Scan automatique, `.env` gitignored, review |
| Régression fonctionnelle | Moyen | Haut | Tests E2E comparatifs stub legacy vs MAF |

---

## 7. Critères de Réussite

- [ ] Pipeline MAF produit la même sortie que le pipeline AutoGen (en mode stub)
- [ ] 3 agents Foundry appelés dans le bon ordre (Veille → RAG → Producteur)
- [ ] ≥10 tests déterministes passent sans Azure
- [ ] Zéro secret dans le code, la PR, et le repo
- [ ] PR ouverte avec Copilot Reviewer
- [ ] Documentation complète : README, HANDOFF, MAPPING
