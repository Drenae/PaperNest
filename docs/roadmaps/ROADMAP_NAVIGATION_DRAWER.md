# Roadmap — NavigationDrawer PaperNest

## État

Prototype natif démarré dans `src/app/navigation/navigation_drawer_prototype.py`. Il n’est pas encore intégré à `MainWindow`, afin de préserver entièrement la navigation actuelle pendant l’étude. Aucun fork de `NavigationDrawer` ou `NavigationDrawerDestination` n’est prévu tant qu’une limite réelle et bloquante n’a pas été démontrée.

## Objectif

Remplacer la sidebar construite manuellement avec `Container`, `Row` et `Column` par un `NavigationDrawer` natif Flet, tout en conservant autant que possible le rendu visuel actuel et en ajoutant l’effet drawer.

## Contraintes validées

- [x] Conserver les destinations actuelles et leur ordre.
- [x] Conserver les couleurs, arrondis, icônes et libellés de PaperNest.
- [x] Ajouter un en-tête de marque en haut du drawer.
- [x] Conserver l’administration comme destination secondaire visuellement séparée.
- [x] Utiliser d’abord les contrôles natifs Flet sans fork.
- [x] Ne forker qu’après comparaison visuelle et identification précise d’une limite du contrôle natif.
- [x] Ne pas complexifier la navigation au-delà du besoin réel de PaperNest.

## Étude de l’existant

- [x] Lire `SidebarNavigation`, `NavigationButton` et `MainWindow`.
- [x] Inventorier les largeurs, espacements, couleurs et états sélectionnés actuels.
- [x] Identifier le comportement responsive actuel sous le seuil de 900 px.
- [x] Lire l’API Python de `NavigationDrawer` et `NavigationDrawerDestination`.
- [x] Lire l’implémentation Dart Flet correspondante.
- [x] Identifier les limites potentielles : hauteur des destinations, padding interne, bordure sélectionnée, mode compact et ancrage inférieur.

## Prototype natif

- [x] Créer un module de prototype séparé sans remplacer immédiatement la sidebar actuelle.
- [x] Construire le drawer avec `NavigationDrawer` et `NavigationDrawerDestination`.
- [x] Reproduire la largeur et la couleur de fond actuelles.
- [x] Reproduire l’indicateur sélectionné avec `indicator_color` et `indicator_shape`.
- [x] Ajouter un bloc de marque provisoire en haut en attendant le logo validé.
- [x] Ajouter les séparateurs et les destinations secondaires.
- [ ] Brancher le prototype sur les destinations réelles de `MainWindow`.
- [ ] Ajouter un bouton temporaire d’ouverture du drawer.
- [ ] Vérifier la fermeture après sélection d’une destination.
- [ ] Vérifier la compatibilité exacte des méthodes `show_drawer()` et `close_drawer()` avec Flet 0.85.3 lors du premier essai Windows.

## Comparaison visuelle

- [ ] Comparer le rendu natif à la sidebar actuelle sous Windows.
- [ ] Vérifier les dimensions des destinations.
- [ ] Vérifier l’espacement entre icône et libellé.
- [ ] Vérifier les couleurs et l’état sélectionné.
- [ ] Vérifier l’en-tête avec le futur logo.
- [ ] Vérifier le comportement d’ouverture, de fermeture et de redimensionnement.
- [ ] Vérifier si la destination Administration peut être positionnée suffisamment bas avec le contrôle natif.
- [ ] Lister précisément les différences impossibles à corriger par le thème natif.

## Décision de fork

- [ ] Confirmer que le rendu natif est suffisamment proche et poursuivre sans fork.
- [ ] Ou documenter une limite réellement bloquante avant de créer un fork PaperNestExtension.
- [ ] Si un fork devient nécessaire, limiter les modifications aux propriétés manquantes dont PaperNest a réellement besoin.

## Migration finale

- [ ] Intégrer le drawer validé dans `MainWindow`.
- [ ] Retirer la sidebar historique uniquement après validation.
- [ ] Supprimer `NavigationButton` et le code manuel devenu inutile.
- [ ] Préserver la création, la destruction et le rafraîchissement des vues actuelles.
- [ ] Valider toutes les destinations.
- [ ] Valider le comportement sous Windows.
- [ ] Valider le build Windows.
- [ ] Mettre à jour le changelog et la roadmap UI.

## Critère de finalisation

La migration sera terminée uniquement lorsque le drawer natif ou son éventuel fork reproduira suffisamment le rendu PaperNest, que toutes les destinations fonctionneront, que l’ancien code sera supprimé et que le comportement Windows sera validé par l’utilisateur.