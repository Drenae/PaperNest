# Roadmap — Sidebar PaperNest déployable au survol

## État

Le besoin a été redéfini. PaperNest ne doit pas utiliser un `NavigationDrawer` modal ouvert par bouton.

La future navigation sera une rail compacte toujours visible, développée comme nouveau contrôle dans PaperNestExtension. Elle s’agrandira au survol, se superposera au contenu et se repliera lorsque la souris quittera sa zone.

## Objectif

Remplacer la sidebar manuelle actuelle par une navigation latérale animée qui conserve les icônes visibles en permanence et affiche les libellés uniquement lorsque la souris survole la sidebar.

## Structure attendue

### État compact

- [ ] Logo PaperNest compact.
- [ ] Séparateur.
- [ ] Icône Accueil.
- [ ] Icône Recherche.
- [ ] Icône Documents importants.
- [ ] Icône Corbeille.
- [ ] Espace extensible.
- [ ] Séparateur.
- [ ] Icône Administration.

### État déployé

- [ ] Logo PaperNest complet.
- [ ] Séparateur.
- [ ] Icône Accueil et libellé « Accueil ».
- [ ] Icône Recherche et libellé « Recherche ».
- [ ] Icône Documents importants et libellé « Documents importants ».
- [ ] Icône Corbeille et libellé « Corbeille ».
- [ ] Espace extensible.
- [ ] Séparateur.
- [ ] Icône Administration et libellé « Administration ».

## Comportement validé

- [x] La sidebar compacte reste visible en permanence.
- [x] Le survol de n’importe quelle zone compacte déclenche le déploiement.
- [x] La sidebar reste ouverte tant que la souris se trouve dans toute sa zone déployée.
- [x] La sortie complète de la souris déclenche le repli.
- [x] L’ouverture et la fermeture utilisent un glissement horizontal animé.
- [x] Le contenu de la page ne change jamais de taille.
- [x] La partie déployée se superpose au contenu.
- [x] Aucun bouton d’ouverture n’est nécessaire.
- [x] Le contrôle sera développé dans PaperNestExtension.

## Étude technique

- [x] Lire la sidebar manuelle actuelle et `MainWindow`.
- [x] Lire l’API Python de `NavigationDrawer`.
- [x] Lire l’implémentation Dart de `NavigationDrawer`.
- [x] Constater que le contrôle natif est modal et ne correspond pas au comportement demandé.
- [x] Abandonner le prototype modal précédent.
- [x] Décider de construire un nouveau contrôle autonome dans PaperNestExtension.
- [ ] Définir le nom public final du contrôle et de ses destinations.
- [ ] Définir l’API exacte avec PaperNestExtension.

## Développement PaperNestExtension

Roadmap de référence :

- `PaperNestExtension/docs/roadmaps/ROADMAP_HOVER_SIDEBAR.md`

- [ ] Créer l’API Python.
- [ ] Créer l’implémentation Flutter.
- [ ] Créer les destinations typées.
- [ ] Implémenter le survol global de la zone.
- [ ] Implémenter l’animation de largeur.
- [ ] Implémenter la superposition sans redimensionnement du contenu.
- [ ] Implémenter l’état sélectionné.
- [ ] Implémenter les séparateurs, l’espace extensible et les logos.
- [ ] Créer et valider un exemple Windows.

## Intégration PaperNest

- [ ] Conserver la sidebar actuelle pendant le développement du contrôle.
- [ ] Installer le nouveau contrôle dans une structure superposée.
- [ ] Réserver uniquement la largeur compacte dans le layout principal.
- [ ] Brancher les destinations sur `MainWindow.navigate_to`.
- [ ] Synchroniser `selected_index`.
- [ ] Conserver la création, la destruction et le rafraîchissement actuels des vues.
- [ ] Intégrer les futurs assets PaperNest.
- [ ] Comparer le rendu compact à la sidebar actuelle.
- [ ] Comparer le rendu déployé à la sidebar actuelle.
- [ ] Vérifier que le contenu ne bouge jamais pendant l’animation.

## Nettoyage après validation

- [ ] Supprimer `NavigationButton`.
- [ ] Supprimer `SidebarNavigation`.
- [ ] Supprimer le code manuel devenu inutile.
- [ ] Supprimer les imports obsolètes.
- [ ] Valider toutes les destinations.
- [ ] Valider le comportement sous Windows.
- [ ] Valider le build Windows.
- [ ] Mettre à jour le changelog et la roadmap UI.

## Critère de finalisation

La migration sera terminée lorsque la rail compacte restera visible en permanence, que son déploiement et son repli seront fluides au survol, que la partie ouverte se superposera au contenu sans provoquer le moindre redimensionnement et que toutes les destinations seront validées sous Windows.