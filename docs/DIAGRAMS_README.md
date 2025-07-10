# 📊 Guide des Diagrammes d'Architecture

Ce dossier contient les diagrammes illustrant l'architecture hybride des bases de données du projet.

## 📁 Fichiers de diagrammes

### 1. `database_architecture_diagram.mmd`
**Diagramme détaillé du système de fallback**

- Montre le processus complet de démarrage de l'application
- Illustre les tests de connexion automatiques
- Détaille les chemins de fallback et de récupération
- Inclut la configuration et les variables d'environnement

### 2. `database_overview_diagram.mmd`
**Vue d'ensemble simplifiée de l'architecture**

- Présentation claire des environnements
- Relations entre les composants
- Outils de gestion disponibles
- Architecture modulaire

## 🖼️ Génération des images

### Méthode 1 : Éditeurs supportant Mermaid
- **VS Code** : Extension "Mermaid Preview"
- **GitHub/GitLab** : Rendu automatique dans les README
- **Obsidian** : Support natif Mermaid
- **Notion** : Import de code Mermaid

### Méthode 2 : Outils en ligne
- **Mermaid Live Editor** : https://mermaid.live/
  1. Copier le contenu du fichier `.mmd`
  2. Coller dans l'éditeur
  3. Exporter en PNG/SVG

### Méthode 3 : CLI Mermaid (si installé)
```bash
# Installation
npm install -g @mermaid-js/mermaid-cli

# Génération d'images
mmdc -i docs/database_architecture_diagram.mmd -o docs/database_architecture.png
mmdc -i docs/database_overview_diagram.mmd -o docs/database_overview.png
```

### Méthode 4 : Docker Mermaid
```bash
# Générer l'image avec Docker
docker run --rm -v $(pwd):/data minlag/mermaid-cli -i /data/docs/database_architecture_diagram.mmd -o /data/docs/database_architecture.png
```

## 🎨 Personnalisation

### Couleurs utilisées
- **PostgreSQL** : `#e1f5fe` (bleu clair)
- **SQLite** : `#fff3e0` (orange clair)  
- **API/Frontend** : `#f3e5f5` (violet clair)
- **Configuration** : `#e8f5e8` (vert clair)

### Modification des diagrammes
1. Éditer le fichier `.mmd` correspondant
2. Tester avec Mermaid Live Editor
3. Mettre à jour la documentation si nécessaire

## 📋 Utilisation dans la documentation

### Inclusion dans Markdown
```markdown
```mermaid
<!-- Copier le contenu du fichier .mmd ici -->
```
```

### Référence aux fichiers
```markdown
![Architecture des BDD](docs/database_architecture.png)
```

## 🔄 Mise à jour

Quand l'architecture évolue :

1. **Modifier** le fichier `.mmd` approprié
2. **Régénérer** l'image si nécessaire
3. **Mettre à jour** `DATABASE_ARCHITECTURE.md`
4. **Documenter** les changements

## 📚 Références

- [Documentation Mermaid](https://mermaid-js.github.io/mermaid/)
- [Syntaxe des graphiques](https://mermaid-js.github.io/mermaid/#/flowchart)
- [Éditeur en ligne](https://mermaid.live/)

---

> 💡 **Astuce** : Ces diagrammes sont particulièrement utiles pour expliquer l'architecture aux nouvelles personnes de l'équipe ou lors de présentations ! 