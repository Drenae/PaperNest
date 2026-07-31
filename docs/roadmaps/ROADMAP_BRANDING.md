# Roadmap — Identité visuelle PaperNest

## État

Le symbole PaperNest a été choisi par l’utilisateur, nettoyé et intégré dans `PaperNestGlideRail`.

La source de travail reste conservée dans `src/assets/branding/concepts/logo.svg`. Une version finale nettoyée et portable a été créée dans `src/assets/branding/papernest_symbol.svg`.

## Objectif

Créer une identité PaperNest cohérente avec l’interface actuelle, lisible sous Windows et directement exploitable dans `PaperNestGlideRail`.

## Assets prévus

### Sources vectorielles

- [x] `src/assets/branding/papernest_symbol.svg` — symbole compact final sans texte.
- [ ] `src/assets/branding/papernest_logo.svg` — logo horizontal complet final, uniquement si un besoin réel apparaît.
- [x] Conserver les SVG comme sources principales, simples à redimensionner et à modifier.

### Source de travail

- [x] `src/assets/branding/concepts/logo.svg` — fichier original importé par l’utilisateur.
- [x] Nettoyer les métadonnées Inkscape et conserver uniquement le dessin utile dans le symbole final.
- [x] Conserver un fond transparent.
- [x] Conserver les couleurs anthracite et jaune du symbole validé.

### Déclinaisons raster

- [ ] `src/assets/icon.png` — icône principale carrée avec transparence réelle.
- [ ] `src/assets/icon_windows.png` — version 256 × 256 optimisée pour le build Windows.
- [ ] `src/assets/logo.png` — déclinaison PNG du logo uniquement si elle est réellement nécessaire.

## Direction visuelle

- [x] Reprendre l’identité actuelle de PaperNest plutôt que créer une marque sans lien avec l’application.
- [x] Conserver le jaune PaperNest proche de `#F9A825`.
- [x] Utiliser un anthracite cohérent avec le fond de `PaperNestGlideRail`.
- [x] Retenir un monogramme `PN` identifiable comme symbole de marque.
- [x] Prévoir un rendu propre sur fond sombre et sur fond clair.
- [x] Utiliser un fond réellement transparent dans le SVG final.
- [x] Éviter les détails trop fins, les dégradés gratuits et les effets inutiles.
- [ ] Confirmer la lisibilité finale à 24, 32 et 40 px dans l’application réelle.

## Validation graphique

- [x] Créer plusieurs pistes de symbole compact.
- [x] Sélectionner le symbole avec l’utilisateur.
- [x] Produire un SVG final propre et réutilisable.
- [x] Vérifier la validité structurelle et la transparence du SVG final.
- [ ] Valider le rendu sur le fond sombre de `PaperNestGlideRail`.
- [ ] Valider le rendu dans les états replié et déployé.
- [ ] Exporter ensuite les PNG nécessaires.
- [ ] Vérifier la transparence réelle et la netteté des fichiers raster.

## Intégration dans PaperNest

- [x] Ajouter le symbole final dans `src/assets/branding`.
- [x] Utiliser le symbole SVG dans `brand_icon` de `PaperNestGlideRail`.
- [x] Conserver le titre texte natif de la rail plutôt qu’un logo horizontal complet.
- [ ] Ajuster la taille du symbole si le test visuel le nécessite.
- [ ] Configurer l’icône du build Windows selon les conventions Flet du projet.
- [ ] Tester l’icône dans l’exécutable Windows.
- [ ] Valider le build Windows avec les assets finaux.
- [x] Mettre à jour les roadmaps concernées.

## Critère de finalisation

Le chantier sera terminé lorsque le symbole SVG intégré aura été validé dans `PaperNestGlideRail`, que les déclinaisons PNG nécessaires auront été produites et que l’icône aura été testée dans le build Windows.
