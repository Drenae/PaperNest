# Roadmap — Identité visuelle PaperNest

## État

Préparation démarrée. Les fichiers visuels ne seront intégrés qu’après validation du design par l’utilisateur.

## Objectif

Créer une icône d’application et un logo PaperNest cohérents avec l’interface actuelle, lisibles sous Windows et adaptés au futur `NavigationDrawer`.

## Assets prévus

- [ ] `src/assets/icon.png` — icône principale carrée, sans texte et avec fond transparent réel.
- [ ] `src/assets/icon_windows.png` — version 256 × 256 optimisée pour le build Windows.
- [ ] `src/assets/logo.png` — logo horizontal pour l’en-tête du futur drawer.
- [ ] Étudier l’utilité d’une variante compacte uniquement si la navigation finale en a réellement besoin.

## Direction visuelle

- [ ] Reprendre l’identité validée de PaperNest plutôt que créer une nouvelle marque.
- [ ] Conserver le jaune PaperNest proche de `ft.Colors.YELLOW_800`.
- [ ] Conserver un symbole simple lié au classement documentaire.
- [ ] Garantir une bonne lisibilité aux petites tailles.
- [ ] Utiliser un fond réellement transparent pour les fichiers qui le nécessitent.
- [ ] Éviter les détails trop fins et les effets inutiles.

## Validation graphique

- [ ] Générer une première proposition d’icône.
- [ ] Valider le symbole, les proportions et les couleurs avec l’utilisateur.
- [ ] Générer le logo horizontal dérivé de l’icône validée.
- [ ] Vérifier le rendu sur fond clair et sur le fond sombre du drawer.
- [ ] Vérifier la transparence réelle des PNG.
- [ ] Vérifier les dimensions et la netteté des fichiers.

## Intégration dans PaperNest

- [ ] Ajouter les fichiers validés dans `src/assets`.
- [ ] Utiliser le logo dans l’en-tête du `NavigationDrawer`.
- [ ] Configurer l’icône du build Windows selon les conventions Flet retenues par le projet.
- [ ] Tester l’icône dans l’exécutable Windows.
- [ ] Tester le logo dans le drawer aux dimensions normales.
- [ ] Valider le build Windows.
- [ ] Mettre à jour le changelog et les roadmaps concernées.

## Critère de finalisation

Le chantier sera terminé lorsque l’icône et le logo auront été validés graphiquement, intégrés dans `src/assets`, vérifiés avec une transparence réelle et testés dans le drawer et le build Windows.