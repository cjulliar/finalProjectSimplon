Le projet prend en compte la grille d'evaluation comme objectif, le projet ne peut pas être fini tant que tous les points ne sont pas cochés.
Pendant le développement du projet, si un point qui n'était pas coché est réalisé, alors il faut cocher le point en question en transformant '[ ]' en '[X]'.

L'objectif global du projet est d’automatiser des rapports par mail aux directeurs des différentes banques du groupe. Ces rapports seront hebdomadaires et contiendront une analyse des chiffres faite par Intelligence artificielle.

Les technologies utilisées seront :
LLM : pour la génération du mail avec une analyse des chiffres
Agent IA : pour l’envoi du mail, générer des graphiques pertinents (ce sont les tools) et l’interaction avec le LLM. Agent. LangChain

Le LLM utilisera deux sources de données pour faire le rapport :
1. la requête SQL qui apportera les chiffres de la semaine
2. les rapports précédents, stockés en BDD, pour l’interprétation des chiffres et leurs évolutions
