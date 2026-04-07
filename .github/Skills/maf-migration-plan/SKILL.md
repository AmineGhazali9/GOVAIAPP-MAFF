---
description: "Plan de migration AutoGen → MAF avec analyse, mapping et étapes"
---

# Skill : MAF Migration Plan

## Déclencheur
Utiliser ce skill quand on doit analyser un code AutoGen existant et produire un plan de migration vers MAF.

## Procédure

1. **Analyser le repo legacy** (lecture seule)
   - Lister tous les fichiers Python
   - Identifier les imports AutoGen (`autogen_agentchat`, `autogen_core`)
   - Cartographier agents, orchestrateur, config

2. **Extraire les patterns AutoGen**
   - `BaseChatAgent` → noter les méthodes overridées
   - `RoundRobinGroupChat` → noter participants et termination
   - `on_messages()` → noter le flux de données

3. **Produire le mapping**
   - Pour chaque concept AutoGen, identifier l'équivalent MAF
   - Documenter dans un tableau

4. **Écrire MIGRATION_PLAN.md**
   - Sections : Analyse, Stratégie, Mapping, Étapes, Handoff, Risques, Critères

5. **Valider**
   - Vérifier que le flux métier est conservé
   - Vérifier zéro secret dans le plan

## Critères d'acceptation
- [ ] MIGRATION_PLAN.md créé avec toutes les sections
- [ ] Mapping AutoGen → MAF complet
- [ ] Flux métier identique documenté
- [ ] Aucun secret dans le document
