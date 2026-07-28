# Règles de développement — PaperNest

## Finalité privée du projet

PaperNest est une application strictement privée. Elle est développée uniquement pour faciliter l’utilisation quotidienne de la compagne d’Adrien sur son ordinateur portable.

Le projet n’a pas vocation à être distribué, commercialisé ou rendu compatible avec tous les environnements possibles.

Les décisions techniques doivent donc privilégier :

- la simplicité ;
- la fiabilité ;
- le confort d’utilisation ;
- la facilité de maintenance ;
- les besoins réels de l’utilisatrice.

La compatibilité Linux, macOS, multi-utilisateur, la rétrocompatibilité générale et les fonctions destinées à un large public ne doivent pas être ajoutées sans besoin explicite.

## Règles obligatoires

- Toujours étudier le code actuel avant de modifier un fichier.
- Ne pas supposer l’API d’un contrôle de PaperNestExtension : la vérifier dans le dépôt.
- Ne pas effectuer de mise à niveau de Flet, Flutter, Pyodide ou d’une autre dépendance importante sans validation explicite.
- Ne développer que les fonctionnalités utiles à l’usage réel de l’application.
- Éviter la duplication et préférer les composants de base avec variantes spécialisées.
- Utiliser les contrôles de PaperNestExtension lorsqu’ils répondent au besoin.
- Ne pas activer une fonction spécialisée sur tous les champs sans justification, par exemple un bouton d’effacement réservé aux filtres de recherche.
- Préserver les comportements déjà validés par l’utilisateur.
- Corriger la cause réelle des bugs, y compris les caches ou anciens dossiers de build lorsqu’ils sont en cause.
- Vérifier les imports, événements, valeurs affichées et comportements visuels après une migration.
- Supprimer le code obsolète uniquement après validation de son remplacement.
- Mettre à jour la roadmap concernée après toute modification importante.
- Créer une nouvelle roadmap lorsqu’un chantier fonctionnel important commence.
- Mettre à jour `docs/CHANGELOG.md` pour toute évolution notable.
- Utiliser des messages de commit explicites et ciblés.

## Définition de terminé

Une fonctionnalité est terminée uniquement lorsque :

- le code est fonctionnel ;
- son intégration est validée dans l’application ;
- les anciens éléments devenus inutiles sont nettoyés ;
- les erreurs connues sont résolues ;
- la roadmap et le changelog sont à jour.
