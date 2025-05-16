# Documentation des Rapports par Email

Ce document détaille la fonctionnalité des rapports par email et l'interface utilisateur associée.

## Rapports par Email

### Vue d'ensemble

Le système permet de générer et d'envoyer automatiquement des rapports d'analyse bancaire par email aux directeurs des différentes banques. Ces rapports sont générés à l'aide d'un modèle d'IA qui analyse les données bancaires et produit des insights pertinents.

### Fonctionnalités

1. **Génération de rapports personnalisés** : Les rapports sont générés pour chaque banque avec des analyses spécifiques à leurs données.
2. **Envoi automatique par email** : Les rapports peuvent être envoyés automatiquement par email à des destinataires spécifiés.
3. **Programmation des envois** : Les envois peuvent être programmés pour être exécutés à des jours et heures spécifiques.
4. **Stockage des rapports** : Tous les rapports envoyés sont stockés dans la base de données pour consultation ultérieure.
5. **Interface utilisateur** : Une interface web permet de consulter l'historique des rapports envoyés et les visualisations associées.

### Utilisation

#### Envoi manuel d'un rapport

Pour envoyer manuellement un rapport par email :

```bash
python3.10 src/scripts/generate_global_report.py --format markdown --email --recipients "directeur@banque.com"
```

Options disponibles :
- `--format` : Format du rapport (markdown, html, pdf)
- `--email` : Active l'envoi par email
- `--recipients` : Liste des destinataires séparés par des virgules
- `--subject` : Sujet de l'email (optionnel)
- `--bank` : Nom de la banque pour un rapport spécifique (optionnel)

#### Programmation des rapports

Pour programmer l'envoi automatique des rapports :

```bash
python3.10 src/scripts/schedule_reports.py --day Monday --time "08:00" --format markdown --email --recipients "directeur@banque.com"
```

Options disponibles :
- `--day` : Jour de la semaine pour l'envoi (Monday, Tuesday, etc.)
- `--time` : Heure d'envoi au format "HH:MM"
- `--format` : Format du rapport (markdown, html, pdf)
- `--email` : Active l'envoi par email
- `--recipients` : Liste des destinataires séparés par des virgules
- `--subject` : Sujet de l'email (optionnel)

#### Journalisation des exécutions

Le système enregistre chaque exécution programmée dans la base de données, avec les informations suivantes :
- Date et heure d'exécution
- Statut (succès ou échec)
- Message d'erreur (le cas échéant)
- Banques analysées
- Destinataires

Pour consulter les logs d'exécution, utilisez l'interface utilisateur ou interrogez directement la base de données.

## Interface Utilisateur

### Vue d'ensemble

L'interface utilisateur web permet de consulter les rapports générés, les visualisations par banque, et l'historique des rapports envoyés par email.

### Pages principales

#### 1. Liste des Rapports

Cette page affiche la liste de tous les rapports générés, avec des options de filtrage par date, banque, et type de rapport.

URL : `/ai_reports/list/`

#### 2. Rapports par Email

Cette page affiche l'historique des rapports envoyés par email, avec la possibilité de filtrer par banque. Elle permet de visualiser le contenu des emails envoyés.

URL : `/ai_reports/email-reports/`

Fonctionnalités :
- Sélecteur de banque
- Affichage du contenu des emails
- Visualisation des métadonnées (date d'envoi, destinataires, etc.)

#### 3. Graphiques par Banque

Cette page affiche les visualisations générées pour chaque banque, avec la possibilité de filtrer par banque et par type de graphique.

URL : `/ai_reports/bank-charts/`

Fonctionnalités :
- Sélecteur de banque
- Affichage des graphiques par onglets
- Visualisation des tendances sur différentes périodes

### Modèle de Données

Le modèle `EmailReport` stocke les informations sur les rapports envoyés par email :

```python
class EmailReport(Base):
    __tablename__ = "email_reports"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    bank_name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    recipients = Column(String(1024), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    scheduled_report_id = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default='sent')
```

## Intégration avec le Service d'IA

Les rapports par email sont générés par le service d'IA, qui analyse les données bancaires et produit des insights pertinents. Le service utilise les fonctions suivantes :

- `analyze_bank_by_name` : Analyse les données d'une banque spécifique
- `analyze_all_filtered_banks` : Analyse toutes les banques filtrées
- `send_report_by_email` : Envoie un rapport par email

Ces fonctions sont définies dans le module `src/ia/ai_service.py`.

## Dépannage

### Problèmes d'envoi d'emails

Si les emails ne sont pas envoyés correctement :

1. Vérifiez les paramètres SMTP dans le fichier `.env`
2. Assurez-vous que le serveur SMTP est accessible
3. Vérifiez les logs d'erreur dans la console ou dans la base de données

### Problèmes de programmation

Si les rapports programmés ne sont pas exécutés :

1. Vérifiez que le script `schedule_reports.py` est en cours d'exécution
2. Vérifiez les logs d'exécution dans la base de données
3. Assurez-vous que le jour et l'heure spécifiés sont corrects

### Problèmes d'interface utilisateur

Si l'interface utilisateur ne fonctionne pas correctement :

1. Vérifiez que le serveur Django est en cours d'exécution
2. Assurez-vous que la base de données est accessible
3. Vérifiez les logs Django pour les erreurs éventuelles 