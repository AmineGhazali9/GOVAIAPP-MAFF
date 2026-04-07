---
description: "Adaptateur Azure AI Foundry pour appeler les agents via AgentsClient"
---

# Skill : Foundry Adapter

## Déclencheur
Utiliser ce skill pour implémenter ou modifier l'adaptateur qui appelle les agents Azure AI Foundry.

## Procédure

1. **Vérifier la configuration**
   - `FOUNDRY_ENABLED` == `"true"`
   - `FOUNDRY_PROJECT_ENDPOINT` non vide
   - Agent ID correspondant présent

2. **Implémenter call_agent()**
   ```python
   def call_agent(agent_name: str, prompt: str) -> str:
       client = AgentsClient(endpoint, DefaultAzureCredential())
       agent = client.get_agent(agent_id)
       thread = client.threads.create()
       client.messages.create(thread_id=thread.id, role="user", content=prompt)
       run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
       # Extract last text message
   ```

3. **Gérer les erreurs**
   - `ImportError` → RuntimeError avec message clair
   - `Exception` → log + raise RuntimeError
   - Timeout recommandé

4. **Mode stub**
   - Si non configuré → retourner `"[STUB agent_name] ..."`
   - Jamais d'exception en mode stub

## Critères d'acceptation
- [ ] `call_agent()` fonctionne avec DefaultAzureCredential
- [ ] Fallback stub si Foundry non configuré
- [ ] Aucun secret hardcodé
- [ ] Lazy imports pour azure-ai-agents
