# Roadmap architecture — Dashboard

## Objectif

Appliquer réellement la séparation `State / Controller / Builder / View` au dashboard avant d’étendre cette organisation aux autres pages de PaperNest.

Le comportement et l’apparence actuels doivent être conservés. Cette migration est un rangement architectural, pas une refonte fonctionnelle ou visuelle.

## Responsabilités finales

### `state.py`

- [x] Conserver la catégorie actuellement ouverte.
- [x] Conserver les catégories affichées sur l’accueil.
- [x] Conserver les fichiers préparés pour l’import et leur classeur cible.
- [x] Conserver les états de chargement, de progression et de résumé.
- [x] Ne dépendre d’aucun contrôle Flet.

### `controller.py`

- [x] Charger et actualiser les catégories.
- [x] Gérer l’ouverture et la fermeture du détail d’un classeur.
- [x] Gérer la sélection, le retrait et le classement des fichiers.
- [x] Gérer le choix du classeur par défaut et les exceptions par fichier.
- [x] Gérer la détection des doublons et l’import asynchrone.
- [x] Gérer les abonnements aux événements métier utiles au dashboard.
- [x] Notifier la vue après chaque changement d’état.
- [x] Ne construire aucun contrôle visuel.

### `builder.py`

- [x] Construire les contrôles du dashboard.
- [x] Construire la disposition de l’accueil.
- [x] Construire les lignes de fichiers préparés.
- [x] Construire la vue détail d’un classeur.
- [x] Ne contenir aucune requête vers les repositories ou services métier.

### `dashboard_view.py`

- [x] Créer et relier le state, le builder et le controller.
- [x] Transmettre les événements de l’interface au controller.
- [x] Appliquer le state aux contrôles lors du rendu.
- [x] Gérer uniquement le cycle de vie Flet et le remplacement accueil/détail.
- [x] Ne dupliquer aucun affichage du builder ni logique du controller.

### `components/`

- [x] Conserver des composants visuels simples et spécialisés.
- [x] Retirer les accès directs aux repositories, services métier et event bus.
- [x] Recevoir leurs données et callbacks depuis le builder ou la vue.

## Migration

- [x] Déplacer `StagedFile` dans `state.py`.
- [x] Transformer `CabinetPanel` en composant de rendu passif.
- [x] Transformer `UploadPanel` en composant de rendu passif.
- [x] Activer réellement `DashboardState` et `DashboardController`.
- [x] Utiliser exclusivement `DashboardBuilder` pour construire l’affichage.
- [x] Alléger `DashboardView` et supprimer les responsabilités dupliquées.

## Validation

- [ ] L’accueil conserve la même disposition responsive.
- [ ] Les compteurs des classeurs s’actualisent après les événements métier.
- [ ] Le clic sur un classeur ouvre toujours `DetailView`.
- [ ] Le bouton Accueil du rail permet toujours de quitter le détail.
- [ ] La sélection multiple et le glisser-déposer fonctionnent toujours.
- [ ] Le classeur par défaut et les exceptions par fichier fonctionnent toujours.
- [ ] La suppression individuelle et globale de la sélection fonctionne toujours.
- [ ] La détection et l’autorisation des doublons fonctionnent toujours.
- [ ] La progression et le résumé d’import restent visibles.
- [x] Les tests automatisés passent.
- [ ] Le build Windows est validé manuellement.

## Étapes suivantes

Une fois le dashboard validé sous Windows, appliquer la même analyse page par page dans cet ordre recommandé :

1. Recherche.
2. Important.
3. Détail.
4. Corbeille.
5. Administration.
6. Paramètres.
