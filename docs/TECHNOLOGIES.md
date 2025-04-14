# Technologies du Système d'Automatisation des Rapports Bancaires

Ce document présente les technologies utilisées dans le projet, ainsi que les justifications de ces choix. Il sera mis à jour au fur et à mesure de l'avancement du projet.

## Technologies de base

### Backend

| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **Python** | 3.10+ | Langage principal | Écosystème riche pour l'analyse de données et l'IA, syntaxe claire, grande communauté |
| **FastAPI** | 0.109.2 | API REST | Performance (basé sur Starlite), documentation automatique avec Swagger/ReDoc, typage fort |
| **SQLAlchemy** | 2.0.27 | ORM | Abstraction efficace de la base de données, support de migrations, indépendance du SGBD |
| **Pandas** | 2.2.0 | Manipulation de données | Standard de l'industrie pour l'analyse de données en Python, intégration Excel |
| **Pydantic** | 2.6.1 | Validation de données | Validation et sérialisation typée, intégration native avec FastAPI |

### Base de données

| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **SQLite** | 3.x | Stockage des données (dev) | Léger, sans serveur, idéal pour le développement et les tests |
| **PostgreSQL** | (futur) | Stockage des données (prod) | Robuste, performant, adapté aux déploiements en production |

### Sécurité

| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **JWT** | 3.3.0 | Authentification | Standard pour l'authentification API sans état (stateless), facilement vérifiable |
| **Bcrypt** | (via passlib) | Hashage des mots de passe | Algorithme sécurisé et lent, résistant aux attaques par force brute |
| **HTTPS/TLS** | 1.3 | Sécurisation des communications | Protocole standard pour le chiffrement des données en transit |

### Infrastructure

| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **Docker** | - | Conteneurisation | Isolation des environnements, déploiement cohérent, orchestration simplifiée |
| **GitHub Actions** | - | CI/CD | Intégration native avec GitHub, configuration YAML simple, marketplace d'actions |

## Technologies d'Intelligence Artificielle

### Modèles de Langage (LLM)

| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **Azure OpenAI** | GPT-4 | Analyse des données bancaires | Conformité réglementaire (données sensibles), intégration Azure, hébergement UE (RGPD), haute performance |

*Alternatives considérées :*
- **Claude d'Anthropic** : Bonne compréhension contextuelle, mais moins d'intégration avec l'écosystème Azure
- **Llama 3 (Meta)** : Option open-source viable, mais nécessite plus de ressources pour le déploiement et le fine-tuning

### Frameworks d'agents IA

| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **LangChain** | 0.1.x | Orchestration d'agents IA | Architecture flexible d'agents, intégration d'outils externes, gestion de l'état conversationnel |
| **LlamaIndex** | - | Indexation des données | Optimisé pour l'accès contextuel aux données structurées et non structurées |

### Analyse et visualisation

| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **Matplotlib/Seaborn** | - | Génération de graphiques | Bibliothèques standard pour la visualisation de données en Python |
| **Jinja2** | - | Templates de rapports | Moteur de templates flexible, syntaxe intuitive, extensions puissantes |

## Infrastructure Cloud (Planifiée)

| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **Azure OpenAI Service** | - | Accès aux modèles d'IA | Conforme aux normes financières, SLA entreprise, scaling automatique |
| **Azure Functions** | - | Déploiement serverless | Coût optimisé, scaling automatique, intégration aux autres services Azure |
| **Azure Logic Apps** | - | Orchestration des workflows | Automation des processus, déclencheurs temporels, interface visuelle |
| **Azure SQL** | - | Base de données | Managed service, haute disponibilité, backups automatiques |
| **Azure Key Vault** | - | Gestion des secrets | Stockage sécurisé des clés API et identifiants, rotation des secrets |
| **Azure Monitor** | - | Monitoring | Tableaux de bord personnalisables, alertes, insights applicatifs |

## Évolution des choix technologiques

### 03/2024 - Choix initiaux
- **FastAPI** choisi pour ses performances et sa documentation automatique
- **SQLite** choisi pour la simplicité du développement initial
- **Docker** choisi pour l'isolation et la portabilité

### 04/2024 - Intégration IA
- **Azure OpenAI** sélectionné pour la conformité réglementaire et la sécurité
- **LangChain** choisi pour l'orchestration d'agents et l'intégration d'outils
- **Azure** identifié comme plateforme cloud cible pour le déploiement

## Justifications détaillées des choix d'IA

### Pourquoi Azure OpenAI ?

1. **Conformité réglementaire** : Le secteur bancaire est hautement régulé. Azure OpenAI offre des garanties de conformité (SOC 1/2, ISO 27001, RGPD) essentielles pour les applications financières.

2. **Contrôle des données** : Les données restent dans l'environnement Azure de l'entreprise et ne sont pas utilisées pour l'entraînement des modèles.

3. **Filtres de contenu** : Azure OpenAI fournit des filtres de contenu configurables, importants pour les applications professionnelles.

4. **Intégration écosystème** : S'intègre nativement avec d'autres services Azure comme Azure Functions, Logic Apps, et Azure SQL.

5. **SLA entreprise** : Garanties de disponibilité nécessaires pour une application critique.

### Pourquoi LangChain ?

1. **Architecture d'agents** : Permet de créer des agents IA qui peuvent prendre des décisions, utiliser des outils, et exécuter des actions (comme l'envoi d'emails).

2. **Mémoire conversationnelle** : Gestion efficace du contexte et de l'historique des interactions.

3. **Extensibilité** : Facilité d'ajout de nouveaux outils et capacités aux agents.

4. **Chaînes de traitement** : Permettent de séquencer les opérations complexes (analyse de données → génération de rapport → envoi d'email).

5. **Communauté active** : Mises à jour fréquentes et ressources abondantes.

---

*Ce document sera mis à jour régulièrement pour refléter l'évolution des choix technologiques du projet.* 