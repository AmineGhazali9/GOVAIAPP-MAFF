# Mapping AutoGen → MAF

Ce document détaille la correspondance entre les concepts AutoGen (AG2 0.7) utilisés dans le legacy et leur implémentation dans le nouveau projet MAF Python.

## Tableau de correspondance

| # | Concept AutoGen (AG2 0.7) | Implémentation Legacy | Concept MAF Python | Implémentation MAF | Fichier |
|---|---|---|---|---|---|
| 1 | `BaseChatAgent` | Classe héritant de `BaseChatAgent` | Fonction agent | `def run(context: PipelineContext) -> AgentResult` | `agents/*.py` |
| 2 | `on_messages(messages)` | Méthode async recevant `Sequence[BaseChatMessage]` | `run(context)` | Fonction synchrone recevant `PipelineContext` | `agents/*.py` |
| 3 | `RoundRobinGroupChat` | Orchestrateur rotatif séquentiel | Boucle `for` sur agents | `for agent_fn in PIPELINE: agent_fn(ctx)` | `orchestrator.py` |
| 4 | `MaxMessageTermination(4)` | Arrêt après user + 3 agents | Fin de boucle | `len(PIPELINE)` itérations | `orchestrator.py` |
| 5 | `TextMessage` | Message texte AutoGen | `AgentResult` | `dataclass(content, source, metadata)` | `agents/__init__.py` |
| 6 | `Response(chat_message=...)` | Retour d'agent AutoGen | `return AgentResult(...)` | Retour direct depuis `run()` | `agents/*.py` |
| 7 | `CancellationToken` | Token d'annulation async | Non nécessaire | Pipeline synchrone, pas d'annulation | — |
| 8 | `call_foundry_generic()` | Appel Foundry commun dans `foundry_config.py` | `call_agent()` | Même pattern AgentsClient | `foundry/adapter.py` |
| 9 | `AGENT_ENV_VARS` dict | Mapping nom → env var | `AGENT_ENV_VARS` dict | Identique | `config.py` |
| 10 | `is_foundry_configured()` | Check endpoint + agent ID | `is_foundry_configured()` | Identique | `config.py` |
| 11 | `asyncio.run()` wrapper | Passage async→sync pour FastAPI | Non nécessaire | Pipeline nativement synchrone | — |
| 12 | `team.run(task=context)` | Lancement du GroupChat | `run_pipeline(context)` | Boucle séquentielle | `orchestrator.py` |

## Décisions de design

### Pourquoi des fonctions plutôt que des classes ?
Le legacy utilise des classes AutoGen par obligation du framework (`BaseChatAgent` impose l'héritage). MAF n'impose pas cette contrainte. Des fonctions simples `run(context)` sont :
- Plus légères (pas de boilerplate `__init__`, `produced_message_types`, `on_reset`)
- Plus testables (pas besoin d'instancier un objet)
- Suffisantes pour le pattern séquentiel

### Pourquoi synchrone plutôt qu'async ?
Le legacy utilise `async` par obligation de AutoGen (`on_messages` est async), puis wrap avec `asyncio.run()`. Notre pipeline est séquentiel (agent 2 attend agent 1), donc `async` n'apporte aucun bénéfice et ajoute de la complexité.

### Pourquoi conserver `PipelineContext` ?
- Accumule les résultats de chaque agent
- Permet au `ProducteurPolitiqueAgent` d'accéder aux sorties de Veille et RAG
- Équivalent fonctionnel de la liste de `messages` dans le `RoundRobinGroupChat`

## Flux comparatif

### Legacy (AutoGen)
```python
team = RoundRobinGroupChat(
    participants=[VeilleExterneAgent(), RagInterneAgent(), ProducteurPolitiqueAgent()],
    termination_condition=MaxMessageTermination(max_messages=4),
)
result = await team.run(task=company_context)
messages = [{"role": msg.source, "content": msg.content} for msg in result.messages]
```

### MAF Python
```python
ctx = PipelineContext(initial_input=company_context)
for agent_fn in [veille_externe.run, rag_interne.run, producteur.run]:
    agent_fn(ctx)
messages = [{"role": r.source, "content": r.content} for r in ctx.results]
```
