# Roadmap — Migration vers PaperNestAlertDialog

## État

Chantier planifié. Le développement ne commencera qu’après l’étude complète des sources Python et Flutter d’`AlertDialog` pour la version Flet utilisée par les projets.

## Objectif

Faire évoluer `AppDialog` pour qu’il hérite du futur contrôle `PaperNestAlertDialog` fourni par PaperNestExtension, tout en conservant les variantes et les comportements actuellement validés dans PaperNest.

## Architecture prévue

- [ ] Étudier l’API Python et le code Flutter d’`AlertDialog`.
- [ ] Définir l’API minimale de `PaperNestAlertDialog` avec PaperNestExtension.
- [ ] Conserver un composant Flutter interne partagé par les pickers.
- [ ] Faire hériter `AppDialog` de `PaperNestAlertDialog`.
- [ ] Conserver `DialogVariant`, `ConfirmDialog`, `DangerDialog` et `FormDialog`.
- [ ] Préserver l’en-tête sombre, les palettes, les espacements, les actions et la barrière.
- [ ] Migrer les dialogues applicatifs sans régression.

## Pickers

- [ ] Utiliser le composant de dialogue partagé dans ColorPicker et IconPicker.
- [ ] Étudier FilePicker selon les dialogues réellement concernés.
- [ ] Utiliser le nouveau dialogue pour DatePicker uniquement si toutes les fonctions natives sont préservées.
- [ ] Conserver le dialogue natif du DatePicker si la migration dégrade son ergonomie ou ses fonctions.

## Validation

- [ ] Tester les variantes standard, primary, success, warning et danger.
- [ ] Tester les dialogues avec formulaires et contenus scrollables.
- [ ] Tester les états modal et dismissible.
- [ ] Valider PaperNest sous Windows.
- [ ] Valider le build Windows.

## Critère de finalisation

Le chantier sera terminé lorsque `AppDialog` utilisera le contrôle de l’extension, que les pickers compatibles partageront le même rendu Flutter, et qu’aucune fonctionnalité native utile n’aura été perdue.
