# Roadmap — Identité visuelle PaperNest

## État

La création graphique sera lancée après validation de l’intégration fonctionnelle de `PaperNestGlideRail`.

Les fichiers visuels ne seront intégrés qu’après validation du design par l’utilisateur.

## Objectif

Créer une identité PaperNest cohérente avec l’interface actuelle, lisible sous Windows et directement exploitable dans `PaperNestGlideRail`.

## Assets prévus

### Sources vectorielles

- [ ] `src/assets/branding/papernest_symbol.svg` — symbole compact sans texte.
- [ ] `src/assets/branding/papernest_logo.svg` — logo horizontal complet.
- [ ] Conserver les SVG comme sources principales, simples à redimensionner et à modifier.

### Déclinaisons raster

- [ ] `src/assets/icon.png` — icône principale carrée avec transparence réelle.
- [ ] `src/assets/icon_windows.png` — version 256 × 256 optimisée pour le build Windows.
- [ ] `src/assets/logo.png` — déclinaison PNG du logo uniquement si elle est réellement nécessaire.

## Direction visuelle

- [ ] Reprendre l’identité validée de PaperNest plutôt que créer une marque sans lien avec l’application.
- [ ] Conserver le jaune PaperNest proche de `ft.Colors.YELLOW_800`.
- [ ] Conserver un symbole simple lié aux documents, au classement ou au rangement.
- [ ] Garantir une bonne lisibilité aux petites tailles.
- [ ] Prévoir un rendu propre sur fond sombre et sur fond clair.
- [ ] Utiliser un fond réellement transparent.
- [ ] Éviter les détails trop fins, les dégradés gratuits et les effets inutiles.

## Validation graphique

- [ ] Créer plusieurs pistes de symbole compact.
- [ ] Comparer leur lisibilité à 16, 24, 32, 48 et 256 px.
- [ ] Valider le symbole, les proportions et les couleurs avec l’utilisateur.
- [ ] Construire le logo horizontal à partir du symbole validé.
- [ ] Vérifier le rendu sur fond clair et sur le fond sombre de `PaperNestGlideRail`.
- [ ] Vérifier la validité et la portabilité des SVG.
- [ ] Exporter ensuite les PNG nécessaires.
- [ ] Vérifier la transparence réelle et la netteté des fichiers raster.

## Intégration dans PaperNest

- [ ] Ajouter les fichiers validés dans `src/assets/branding`.
- [ ] Utiliser le symbole SVG dans `brand_icon` de `PaperNestGlideRail`.
- [ ] Déterminer si le titre texte natif de la rail reste préférable au logo horizontal complet.
- [ ] Configurer l’icône du build Windows selon les conventions Flet du projet.
- [ ] Tester l’icône dans l’exécutable Windows.
- [ ] Tester le symbole dans les états replié et déployé.
- [ ] Valider le build Windows.
- [ ] Mettre à jour le changelog et les roadmaps concernées.

## Critère de finalisation

Le chantier sera terminé lorsque le symbole et le logo auront été validés graphiquement, que les SVG sources seront propres et réutilisables, que les déclinaisons raster nécessaires auront été produites et que l’ensemble aura été testé dans `PaperNestGlideRail` et le build Windows.
