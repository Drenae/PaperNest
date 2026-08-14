# Roadmap — Intégration de PaperNestGlideRail

## État

`PaperNestGlideRail` est terminé, construit, testé et validé dans PaperNestExtension.

Son intégration dans PaperNest est également terminée et validée sous Windows. L’ancienne sidebar manuelle a été supprimée après validation complète.

## Objectif

Remplacer la sidebar manuelle par `PaperNestGlideRail` sans modifier la logique métier de navigation, la création des vues, leur destruction ou leur rafraîchissement.

## Contrôle source

- [x] API Python terminée dans PaperNestExtension.
- [x] Implémentation Flutter terminée.
- [x] Déploiement et repli au survol validés.
- [x] Superposition sans redimensionnement validée.
- [x] Padding, animation de survol et contrôles SVG validés.
- [x] Exemple Windows validé.
- [x] Roadmap PaperNestExtension finalisée.

Référence :

- `PaperNestExtension/docs/roadmaps/ROADMAP_GLIDE_RAIL.md`

## Intégration dans MainWindow

- [x] Importer `PaperNestGlideRail` et `PaperNestGlideRailDestination`.
- [x] Remplacer le `Row` principal par un `Stack`.
- [x] Réserver uniquement `SIDEBAR_COMPACT_WIDTH` pour le contenu.
- [x] Superposer la rail au-dessus du contenu.
- [x] Reprendre les destinations Accueil, Recherche, Documents importants, Corbeille et Administration.
- [x] Ajouter les icônes sélectionnées.
- [x] Brancher `on_change` sur `navigate_to`.
- [x] Synchroniser `selected_index` lors des navigations programmatiques.
- [x] Conserver `dispose_current_view` et `refresh_current_view`.
- [x] Conserver les callbacks Administration et Corbeille.
- [x] Supprimer l’ancien changement compact au redimensionnement, devenu inutile.

## Validation PaperNest

- [x] Lancer PaperNest avec l’extension reconstruite et installée.
- [x] Vérifier l’état compact au démarrage.
- [x] Vérifier le déploiement et le repli.
- [x] Vérifier que le contenu ne bouge jamais.
- [x] Vérifier Accueil.
- [x] Vérifier Recherche.
- [x] Vérifier Documents importants.
- [x] Vérifier Corbeille.
- [x] Vérifier Administration.
- [x] Vérifier le retour programmatique vers Accueil après restauration.
- [x] Vérifier la sélection visuelle après chaque navigation.
- [x] Vérifier les fenêtres étroites et larges.
- [x] Valider le comportement réel sous Windows.

## Identité visuelle

Le symbole compact officiel est intégré et validé. Le logo horizontal et de nouvelles déclinaisons d’icône ne sont pas nécessaires au périmètre actuel.

- [x] Créer le symbole compact PaperNest en SVG.
- [x] Intégrer le symbole officiel dans `brand_icon`.
- [x] Vérifier le rendu replié et déployé.
- [x] Confirmer que le logo horizontal n’est pas requis actuellement.
- [x] Conserver l’icône d’application existante validée par le build Windows.

Voir `ROADMAP_BRANDING.md`.

## Nettoyage après validation

- [x] Supprimer `NavigationButton`.
- [x] Supprimer `SidebarNavigation`.
- [x] Supprimer `NavigationItem` devenu inutile.
- [x] Remplacer l’ancienne sidebar par le `NavigationManager` centralisé dans `src/app/navigation/navigation.py`.
- [x] Supprimer les imports et constantes devenus obsolètes dans `MainWindow`.
- [x] Marquer cette roadmap comme terminée.

## Critère de finalisation

L’intégration est terminée : toutes les destinations fonctionnent dans PaperNest, la rail se superpose sans déplacer le contenu, le comportement est validé sous Windows et l’ancienne navigation a été supprimée proprement.
