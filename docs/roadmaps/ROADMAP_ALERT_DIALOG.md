# Roadmap — Intégration du nouveau PaperNestAlertDialog

## État

**Phase 7 implémentée et en attente de validation dans PaperNest.**

PaperNest utilise désormais le nouveau fork `PaperNestAlertDialog`, sans dépendre d’un variant fourni par PaperNestExtension. Les variantes restent disponibles uniquement dans l’application et déterminent la palette Python de la pastille d’icône.

## Architecture retenue

- [x] Faire hériter `AppDialog` de `PaperNestAlertDialog`.
- [x] Supprimer l’import de `PaperNestDialogVariant`.
- [x] Définir `DialogVariant` localement dans PaperNest.
- [x] Ne jamais transmettre `variant` à l’extension.
- [x] Construire les palettes `STANDARD`, `PRIMARY`, `SUCCESS`, `WARNING` et `DANGER` côté Python.
- [x] Conserver `ConfirmDialog`, `DangerDialog` et `FormDialog`.
- [x] Conserver les boutons PaperNest dans les actions.
- [x] Préserver l’API existante des dialogues applicatifs.

## Apparence PaperNest

- [x] En-tête `GREY_900`.
- [x] Pastille d’icône colorée selon le variant local.
- [x] Titre blanc et gras.
- [x] Sous-titre facultatif.
- [x] `title_action` facultatif.
- [x] Contenu blanc et compact.
- [x] Actions alignées à droite avec espacement PaperNest.
- [x] Forme arrondie et clipping anti-aliasé.
- [x] Barrière et ombre PaperNest.
- [x] Support de `max_height` et du scroll limité au contenu.

## Compatibilité des dialogues existants

- [x] Conserver les imports `DialogVariant` existants.
- [x] Conserver les appels directs à `AppDialog(variant=...)`.
- [x] Conserver les variantes attribuées aux formulaires, restaurations et suppressions.
- [x] Conserver le chargement de `FormDialog` via `PaperNestButton`.
- [x] Ne migrer aucun picker pendant cette phase.

## Validation à effectuer

- [ ] Lancer `flet run --recursive`.
- [ ] Vérifier les dialogues de formulaires.
- [ ] Vérifier les confirmations.
- [ ] Vérifier les suppressions et la corbeille.
- [ ] Vérifier les restaurations de documents et sauvegardes.
- [ ] Vérifier `title_action`.
- [ ] Vérifier les contenus courts.
- [ ] Vérifier les contenus longs et scrollables.
- [ ] Vérifier la fermeture extérieure et la modalité.
- [ ] Valider le build Windows.
- [ ] Validation visuelle et fonctionnelle par l’utilisateur.

## Pickers — phase séparée

La migration des pickers ne commence pas maintenant.

Elle sera réalisée uniquement après la refonte de :

- `PaperNestColorPicker` ;
- `PaperNestIconPicker` ;
- `PaperNestDatePicker`.

Jusqu’à cette refonte, les pickers actuels conservent leur fonctionnement interne existant.

## Critère de finalisation

La phase 7 sera terminée lorsque tous les dialogues applicatifs auront été validés dans PaperNest et que le build Windows sera réussi. La migration des pickers restera hors de cette clôture.
