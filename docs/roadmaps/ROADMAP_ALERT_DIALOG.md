# Roadmap — Migration vers PaperNestAlertDialog

## État

Terminé, intégré et validé sous Windows.

`AppDialog` hérite maintenant de `PaperNestAlertDialog`. Les dialogues applicatifs ont été audités, leurs variants ont été attribués selon leur rôle et la correction de hauteur naturelle des contenus a été validée.

## Architecture validée

- [x] Étudier l’API Python et le code Flutter d’`AlertDialog`.
- [x] Définir l’API de `PaperNestAlertDialog` avec PaperNestExtension.
- [x] Créer un composant Flutter interne partagé par les pickers.
- [x] Faire hériter `AppDialog` de `PaperNestAlertDialog`.
- [x] Conserver l’API publique `DialogVariant` par alias vers `PaperNestDialogVariant`.
- [x] Conserver `ConfirmDialog`, `DangerDialog` et `FormDialog`.
- [x] Préserver l’en-tête sombre, les espacements, les actions et la barrière.
- [x] Conserver la personnalisation des actions avec les boutons PaperNest.
- [x] Supprimer la construction Python manuelle de l’en-tête et des palettes.
- [x] Corriger la hauteur naturelle des dialogues non scrollables.

## Attribution des variants

- [x] Catégories, métadonnées, déplacement, renommage et recherche enregistrée : `PRIMARY`.
- [x] Restauration de documents : `SUCCESS`.
- [x] Restauration de sauvegarde : `WARNING`.
- [x] Mise à la corbeille, suppression définitive, vidage de corbeille et suppression de classeur : `DANGER`.
- [x] Actions multiples de la corbeille : variant conditionnel `SUCCESS` ou `DANGER`.
- [x] Auditer tous les appels directs à `AppDialog`.

## Pickers

- [x] Utiliser `PaperNestDialogSurface` dans ColorPicker.
- [x] Utiliser `PaperNestDialogSurface` dans IconPicker.
- [x] Conserver le DatePicker Material natif avec un thème PaperNest via son `builder`.
- [x] Conserver les fenêtres natives du FilePicker.

## Validation

- [x] Vérifier la hauteur naturelle des formulaires.
- [x] Vérifier que les actions restent directement sous les contenus courts.
- [x] Vérifier les grands formulaires et les contenus scrollables.
- [x] Tester les variants primary, success, warning et danger dans leurs écrans réels.
- [x] Tester `title_action`, modalité et fermeture.
- [x] Vérifier plusieurs dialogues successifs.
- [x] Lancer PaperNest avec `flet run --recursive`.
- [x] Valider PaperNest sous Windows.
- [x] Valider le build Windows.
- [x] Faire valider visuellement et fonctionnellement la migration par l’utilisateur.

## Critère de finalisation

Atteint : tous les dialogues applicatifs utilisent `PaperNestAlertDialog` sans régression, avec une hauteur et un variant corrects, et le build Windows est validé.
