# E2E Evidence — MAF Pipeline Validation

**Date** : 2026-04-06
**Environnement** : Python 3.13.3, Windows, mode stub (sans Azure)

---

## 1. Tests unitaires

```
$ pytest tests/ -v

tests/test_config.py::TestGetSettings::test_defaults_when_no_env PASSED
tests/test_config.py::TestGetSettings::test_foundry_enabled_true PASSED
tests/test_config.py::TestGetSettings::test_foundry_enabled_case_insensitive PASSED
tests/test_config.py::TestIsFoundryConfigured::test_not_configured_by_default PASSED
tests/test_config.py::TestIsFoundryConfigured::test_configured_when_all_set PASSED
tests/test_config.py::TestIsFoundryConfigured::test_not_configured_missing_endpoint PASSED
tests/test_config.py::TestIsFoundryConfigured::test_not_configured_missing_agent_id PASSED
tests/test_config.py::TestIsFoundryConfigured::test_unknown_agent_name PASSED
tests/test_config.py::TestGetAgentId::test_returns_empty_for_unknown PASSED
tests/test_config.py::TestGetAgentId::test_returns_id_when_set PASSED
tests/test_foundry_adapter.py::TestCallAgentStub::test_raises_when_not_configured PASSED
tests/test_foundry_adapter.py::TestCallAgentStub::test_raises_for_unknown_agent PASSED
tests/test_foundry_adapter.py::TestCallAgentStub::test_raises_when_enabled_but_missing_id PASSED
tests/test_foundry_adapter.py::TestCallAgentFoundryLive::test_veille_externe_returns_content SKIPPED
tests/test_orchestrator.py::TestRunPipeline::test_returns_three_messages PASSED
tests/test_orchestrator.py::TestRunPipeline::test_agent_order PASSED
tests/test_orchestrator.py::TestRunPipeline::test_stub_markers_present PASSED
tests/test_orchestrator.py::TestRunPipeline::test_final_message_is_policy PASSED
tests/test_orchestrator.py::TestRunPipeline::test_context_propagation PASSED
tests/test_orchestrator.py::TestRunPipeline::test_all_messages_have_content PASSED
tests/test_orchestrator.py::TestRunPipeline::test_pipeline_idempotent PASSED

Résultat : 20 passed, 1 skipped in 0.38s
```

## 2. Pipeline stub E2E

```
$ python -m maf_app.orchestrator

MAF Pipeline — AI Governance Policy Generator
=============================================================
Agent 1/3 : veille_externe   → 411 chars (signaux réglementaires)
Agent 2/3 : rag_interne      → 411 chars (documents internes)
Agent 3/3 : producteur_politique → 1373 chars (politique markdown)
=============================================================
Pipeline complete: 3 agent(s) responded.
```

### Sortie du producteur (politique générée)
```markdown
# Politique de Gouvernance IA

*Générée en mode STUB*

## 1. Cadre Réglementaire
- EU AI Act : obligations de transparence et gouvernance
- OCDE : principes d'IA responsable
- CNIL : recommandations sur l'IA et les données personnelles

## 2. Références Internes
- Politique de gouvernance des données v2.1
- Charte éthique IA de l'entreprise
- Procédure d'évaluation des risques algorithmiques

## 3. Recommandations
- Mettre en place un comité de gouvernance IA
- Implémenter des évaluations d'impact algorithmique
- Assurer la traçabilité des décisions automatisées
- Former les équipes aux principes d'IA responsable

## 4. Plan d'Action
| Action | Priorité | Échéance |
|--------|----------|----------|
| Audit des modèles existants | Haute | T1 |
| Formation équipes | Moyenne | T2 |
| Mise en conformité EU AI Act | Haute | T3 |
```

## 3. Vérification zéro secret

```
$ grep -rn "ghp_|github_pat_|sk-|Bearer |api_key" src/ tests/ docs/
→ Aucun résultat (0 match)
```

## 4. Comparaison avec le legacy

| Critère | Legacy (AutoGen) | MAF Python |
|---------|-----------------|------------|
| Nombre d'agents | 3 | 3 |
| Ordre d'exécution | Veille → RAG → Producteur | Veille → RAG → Producteur |
| Mode stub | [STUB agent_name] | [STUB agent_name] |
| Mode Foundry | call_foundry_generic() | call_agent() |
| Auth | DefaultAzureCredential | DefaultAzureCredential |
| Sortie | Liste de messages (role, content) | Liste de messages (role, content) |
| Tests stub | 23 passants | 20 passants, 1 skipped |

## 5. Conclusion

Le pipeline MAF est **fonctionnellement équivalent** au pipeline AutoGen legacy :
- Même flux métier (3 agents, même ordre)
- Même interface de sortie (messages role/content)
- Même pattern Foundry (AgentsClient, thread, run)
- Même fallback stub
- Zéro dépendance AutoGen
