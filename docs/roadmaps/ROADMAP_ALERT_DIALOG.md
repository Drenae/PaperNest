# Roadmap — Migration vers PaperNestAlertDialog

## État

Migration implémentée dans PaperNest, avec une seconde passe corrective en attente de validation applicative et du build Windows.

`PaperNestAlertDialog` et `PaperNestDialogSurface` sont validés dans PaperNestExtension. Les dialogues internes compatibles des ColorPicker et IconPicker utilisent la surface partagée. Le DatePicker conserve son dialogue Material natif avec un thème PaperNest. Le FilePicker ne possède aucun dialogue Flutter interne à migrer : ses fenêtres sont fournies par le système via `file_picker`.

La première validation dans PaperNest a révélé deux points :

- les contenus ordinaires pouvaient être étirés verticalement à cause d’un `Flexible` systématique dans `PaperNestDialogSurface` ;
- plusieurs dialogues applicatifs instanciaient directement `AppDialog` sans fournir de variant explicite.

La surface Flutter a été corrigée pour conserver une hauteur naturelle lorsque le dialogue n’est ni scrollable ni limité par `max_height`. Tous les appels directs à `AppDialog` ont également été audités et reçoivent désormais un variant adapté.

## Objectif

Faire évoluer `AppDialog` pour qu’il hérite de `PaperNestAlertDialog` fourni par PaperNestExtension, tout en conservant les variantes et les comportements validés dans PaperNest.

## Architecture

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

- [x] Catégories, métadonnées, déplacement et renommage : `PRIMARY`.
- [x] Restauration de documents : `SUCCESS`.
- [x] Restauration de sauvegarde : `WARNING`.
- [x] Mise à la corbeille, suppression définitive, vidage de corbeille et suppression de classeur : `DANGER`.
- [x] Actions multiples de la corbeille : variant conditionnel `SUCCESS` ou `DANGER`.
- [x] Recherche enregistrée : `PRIMARY` déjà présent.
- [x] Auditer tous les appels directs à `AppDialog`.

## Pickers

- [x] Utiliser `PaperNestDialogSurface` dans ColorPicker.
- [x] Utiliser `PaperNestDialogSurface` dans IconPicker.
- [x] Conserver le DatePicker Material natif et lui appliquer un thème PaperNest via son `builder`.
- [x] Vérifier FilePicker : aucun `AlertDialog` Flutter interne à migrer.
- [x] Conserver les fenêtres natives de sélection, sauvegarde et dossier du système.

## Dialogues PaperNest à vérifier

- [ ] Vérifier que les formulaires reprennent leur hauteur naturelle.
- [ ] Vérifier que les actions restent directement sous le contenu lorsque celui-ci est court.
- [ ] Vérifier les grands formulaires et les contenus scrollables.
- [ ] Tester les variantes primary, success, warning et danger dans leurs écrans réels.
- [ ] Tester `title_action`.
- [ ] Tester les états modal et dismissible.
- [ ] Vérifier plusieurs dialogues successifs ou superposés.

## Validation

- [ ] Lancer PaperNest avec `flet run --recursive`.
- [ ] Vérifier les dialogues des catégories, recherches, déplacements, renommages, sauvegardes et corbeille.
- [ ] Vérifier qu’aucun appel direct à `AppDialog` ne dépend involontairement du variant standard.
- [ ] Vérifier qu’aucun import historique ou héritage direct de `ft.AlertDialog` ne subsiste dans `AppDialog`.
- [ ] Valider PaperNest sous Windows.
- [ ] Valider le build Windows.
- [ ] Faire valider visuellement et fonctionnellement la migration par l’utilisateur.

## Critère de finalisation

Le chantier sera terminé lorsque tous les dialogues applicatifs auront été testés, que leur hauteur et leur variant seront corrects, que `AppDialog` utilisera le contrôle de PaperNestExtension sans régression et que le build Windows aura été validé.
