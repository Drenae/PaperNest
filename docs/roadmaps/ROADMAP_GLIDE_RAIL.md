# Roadmap — Intégration de PaperNestGlideRail

## État

`PaperNestGlideRail` est terminé, construit, testé et validé dans PaperNestExtension.

Son intégration dans PaperNest a commencé. La sidebar historique est encore conservée dans le dépôt tant que le remplacement n’a pas été validé dans l’application réelle sous Windows.

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

- [ ] Lancer PaperNest avec l’extension reconstruite et installée.
- [ ] Vérifier l’état compact au démarrage.
- [ ] Vérifier le déploiement et le repli.
- [ ] Vérifier que le contenu ne bouge jamais.
- [ ] Vérifier Accueil.
- [ ] Vérifier Recherche.
- [ ] Vérifier Documents importants.
- [ ] Vérifier Corbeille.
- [ ] Vérifier Administration.
- [ ] Vérifier le retour programmatique vers Accueil après restauration.
- [ ] Vérifier la sélection visuelle après chaque navigation.
- [ ] Vérifier les fenêtres étroites et larges.
- [ ] Valider le build Windows de PaperNest.

## Identité visuelle

Le bloc de marque reste provisoire jusqu’à la création des assets officiels.

- [ ] Créer le symbole compact PaperNest en SVG.
- [ ] Créer le logo horizontal PaperNest en SVG.
- [ ] Créer l’icône d’application dans les formats de build nécessaires.
- [ ] Intégrer le symbole ou le logo dans `brand_icon`.
- [ ] Vérifier le rendu replié et déployé.

Voir `ROADMAP_BRANDING.md`.

## Nettoyage après validation

- [ ] Supprimer `NavigationButton`.
- [ ] Supprimer `SidebarNavigation`.
- [ ] Supprimer `NavigationItem` devenu inutile.
- [ ] Supprimer `src/app/navigation/navigation.py` si plus aucun import ne subsiste.
- [ ] Supprimer les imports et constantes devenus obsolètes.
- [ ] Mettre à jour le changelog.
- [ ] Marquer cette roadmap comme terminée.

## Critère de finalisation

L’intégration sera terminée lorsque toutes les destinations fonctionneront dans PaperNest, que la rail se superposera sans déplacement du contenu, que le build Windows sera validé et que l’ancienne navigation aura été supprimée proprement.
