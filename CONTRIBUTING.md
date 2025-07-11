# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer au projet Système d'Analyse et de Génération de Rapports Bancaires !

## 📋 Comment Contribuer

### 1. Fork et Clone

1. **Fork le projet** sur GitHub
2. **Clone votre fork** localement :
   ```bash
   git clone https://github.com/VOTRE_USERNAME/finalProjectSimplon.git
   cd finalProjectSimplon
   ```

### 2. Configuration de l'Environnement

1. **Créer une branche** pour votre fonctionnalité :
   ```bash
   git checkout -b feature/nom-de-votre-fonctionnalite
   ```

2. **Installer les dépendances** :
   ```bash
   ./install_and_run.sh
   ```

3. **Lancer le projet** en mode développement :
   ```bash
   ./dev_start.sh
   ```

### 3. Développement

1. **Faites vos modifications** dans le code
2. **Testez vos changements** :
   ```bash
   # Tests unitaires
   python -m pytest tests/ -v
   
   # Tests Django
   cd frontend && python manage.py test && cd ..
   
   # Linting
   flake8 src/ frontend/
   
   # Formatage
   black src/ frontend/
   ```

3. **Commitez vos changements** :
   ```bash
   git add .
   git commit -m "feat: ajouter nouvelle fonctionnalité"
   ```

### 4. Pull Request

1. **Poussez votre branche** :
   ```bash
   git push origin feature/nom-de-votre-fonctionnalite
   ```

2. **Créez une Pull Request** sur GitHub
3. **Remplissez le template** de PR
4. **Attendez la review** de l'équipe

## 🎯 Types de Contributions

### 🐛 Bug Fixes
- Corriger des bugs existants
- Améliorer la gestion d'erreurs
- Optimiser les performances

### ✨ Nouvelles Fonctionnalités
- Ajouter de nouvelles fonctionnalités
- Améliorer l'interface utilisateur
- Étendre l'API

### 📚 Documentation
- Améliorer la documentation
- Ajouter des exemples
- Corriger des erreurs de documentation

### 🧪 Tests
- Ajouter des tests unitaires
- Améliorer la couverture de tests
- Ajouter des tests d'intégration

## 📝 Standards de Code

### Python
- **PEP 8** : Respecter les conventions Python
- **Black** : Formatage automatique du code
- **Flake8** : Linting et détection d'erreurs
- **Docstrings** : Documentation des fonctions en français

### Django
- **Style guide Django** : Respecter les conventions Django
- **Modèles** : Utiliser des noms explicites
- **Vues** : Séparer la logique métier
- **Templates** : Utiliser l'héritage de templates

### FastAPI
- **Style guide FastAPI** : Respecter les conventions FastAPI
- **Modèles Pydantic** : Validation des données
- **Documentation** : Docstrings pour les endpoints

### Git
- **Conventional Commits** : Format des messages de commit
- **Branches** : Noms explicites (feature/, bugfix/, hotfix/)
- **Messages** : Descriptions claires et concises

## 🧪 Tests

### Tests Obligatoires
Avant chaque PR, assurez-vous que :

```bash
# Tous les tests passent
python -m pytest tests/ -v

# Le code est formaté
black src/ frontend/

# Pas d'erreurs de linting
flake8 src/ frontend/

# La couverture de tests est suffisante (>80%)
python -m pytest tests/ --cov=src --cov=frontend --cov-report=html
```

### Écrire des Tests
```python
# Exemple de test unitaire
def test_calculate_performance():
    """Test du calcul de performance."""
    data = {"transactions": 100, "amount": 50000}
    result = calculate_performance(data)
    assert result["performance_score"] > 0
    assert result["performance_score"] <= 100
```

## 📋 Checklist PR

Avant de soumettre votre PR, vérifiez que :

- [ ] Le code respecte les standards de code
- [ ] Tous les tests passent
- [ ] La documentation est à jour
- [ ] Les changements sont testés localement
- [ ] Le message de commit suit les conventions
- [ ] La PR a une description claire
- [ ] Les labels appropriés sont ajoutés

## 🚀 Processus de Review

1. **Review automatique** : Les tests et le linting s'exécutent automatiquement
2. **Review manuelle** : L'équipe examine votre code
3. **Feedback** : Vous recevez des commentaires et suggestions
4. **Modifications** : Vous apportez les corrections nécessaires
5. **Approbation** : Votre PR est approuvée et mergée

## 🎉 Reconnaissance

Toutes les contributions sont reconnues dans :
- Le fichier `CONTRIBUTORS.md`
- Les releases GitHub
- La documentation du projet

## 📞 Besoin d'Aide ?

Si vous avez des questions ou besoin d'aide :

1. **Issues GitHub** : Créez une issue avec le label `question`
2. **Documentation** : Consultez `README.md` et `DEVELOPER.md`
3. **Discussions** : Utilisez les discussions GitHub

## 📄 Licence

En contribuant, vous acceptez que vos contributions soient sous la même licence que le projet (MIT).

---

Merci de contribuer à ce projet ! 🎉 