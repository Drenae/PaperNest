# Roadmap — Identité visuelle PaperNest

## État

La création graphique est lancée après validation complète de `PaperNestGlideRail` dans PaperNest.

Trois premières pistes de symbole compact ont été créées en SVG dans `src/assets/branding/concepts`. Elles ne sont pas encore utilisées par l’application : leur rôle est de permettre une comparaison honnête avant de figer l’identité finale.

## Objectif

Créer une identité PaperNest cohérente avec l’interface actuelle, lisible sous Windows et directement exploitable dans `PaperNestGlideRail`.

## Assets prévus

### Sources vectorielles

- [ ] `src/assets/branding/papernest_symbol.svg` — symbole compact final sans texte.
- [ ] `src/assets/branding/papernest_logo.svg` — logo horizontal complet final.
- [x] Conserver les SVG comme sources principales, simples à redimensionner et à modifier.

### Concepts de travail

- [x] `src/assets/branding/concepts/papernest_symbol_fold.svg`.
- [x] `src/assets/branding/concepts/papernest_symbol_stack.svg`.
- [x] `src/assets/branding/concepts/papernest_symbol_box.svg`.
- [x] `src/assets/branding/concepts/papernest_concepts_board.svg`.
- [x] Documenter les pistes dans `src/assets/branding/concepts/README.md`.

### Déclinaisons raster

- [ ] `src/assets/icon.png` — icône principale carrée avec transparence réelle.
- [ ] `src/assets/icon_windows.png` — version 256 × 256 optimisée pour le build Windows.
- [ ] `src/assets/logo.png` — déclinaison PNG du logo uniquement si elle est réellement nécessaire.

## Direction visuelle

- [x] Reprendre l’identité actuelle de PaperNest plutôt que créer une marque sans lien avec l’application.
- [x] Conserver le jaune PaperNest `#F9A825`, cohérent avec `ft.Colors.YELLOW_800`.
- [x] Utiliser l’anthracite `#17191F`, cohérent avec le fond de `PaperNestGlideRail`.
- [x] Explorer des symboles simples liés aux documents, au classement ou au rangement.
- [x] Prévoir un rendu propre sur fond sombre et sur fond clair.
- [x] Utiliser un fond réellement transparent dans chaque symbole SVG.
- [x] Éviter les détails trop fins, les dégradés gratuits et les effets inutiles.
- [ ] Garantir la lisibilité finale aux très petites tailles après sélection du symbole.

## Validation graphique

- [x] Créer plusieurs pistes de symbole compact.
- [ ] Comparer leur lisibilité à 16, 24, 32, 48 et 256 px.
- [ ] Sélectionner ou combiner une piste avec l’utilisateur.
- [ ] Affiner le symbole retenu, ses proportions et ses courbes.
- [ ] Construire le logo horizontal à partir du symbole validé.
- [ ] Vérifier le rendu sur fond clair et sur le fond sombre de `PaperNestGlideRail`.
- [ ] Vérifier la validité et la portabilité des SVG finaux.
- [ ] Exporter ensuite les PNG nécessaires.
- [ ] Vérifier la transparence réelle et la netteté des fichiers raster.

## Intégration dans PaperNest

- [ ] Ajouter les fichiers finaux dans `src/assets/branding`.
- [ ] Utiliser le symbole SVG dans `brand_icon` de `PaperNestGlideRail`.
- [ ] Déterminer si le titre texte natif de la rail reste préférable au logo horizontal complet.
- [ ] Configurer l’icône du build Windows selon les conventions Flet du projet.
- [ ] Tester l’icône dans l’exécutable Windows.
- [ ] Tester le symbole dans les états replié et déployé.
- [ ] Valider le build Windows.
- [ ] Mettre à jour le changelog et les roadmaps concernées.

## Critère de finalisation

Le chantier sera terminé lorsque le symbole et le logo auront été validés graphiquement, que les SVG sources seront propres et réutilisables, que les déclinaisons raster nécessaires auront été produites et que l’ensemble aura été testé dans `PaperNestGlideRail` et le build Windows.
