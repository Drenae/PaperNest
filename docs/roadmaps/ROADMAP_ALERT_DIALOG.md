# Roadmap — Retour à AppDialog 100 % Python

## État

**Clôturée : AppDialog 100 % Python validé et ancien contrôle supprimé de PaperNestExtension.**

`AppDialog` hérite désormais directement de `ft.AlertDialog`. La mise en page, le header, les variantes et les actions sont entièrement construits côté Python. `PaperNestAlertDialog` n’est plus importé ni utilisé par PaperNest.

## Architecture cible

```text
AppDialog(ft.AlertDialog)
├── DialogVariant local
├── DialogHeader Python
├── content Python libre
└── actions PaperNestButton
```

PaperNestExtension ne doit plus intervenir dans la construction ou la mise en page des dialogues.

## Phase 1 — Reconstruction de AppDialog

- [x] Faire hériter `AppDialog` de `ft.AlertDialog`.
- [x] Conserver `DialogVariant` dans PaperNest.
- [x] Créer `DialogHeader` en Python.
- [x] Construire le header sombre en Python.
- [x] Construire la pastille d’icône selon le variant local.
- [x] Gérer le titre, le sous-titre et `title_action` en Python.
- [x] Conserver les actions utilisant les boutons PaperNest.
- [x] Conserver la barrière, la forme, l’ombre et les espacements PaperNest.
- [x] Conserver `ConfirmDialog`, `DangerDialog` et `FormDialog`.
- [x] Supprimer l’import de `PaperNestAlertDialog` dans PaperNest.

## Phase 2 — Compatibilité des contenus

- [x] Revenir à la structure Python historique validée avant le fork Flutter.
- [x] Conserver les contrôles avec `expand=True`.
- [x] Restaurer les `expand=True` retirés pendant les essais précédents.
- [x] Préserver les `Column` qui gèrent leur propre scroll.
- [x] Préserver les contenus courts à hauteur naturelle avec `tight=True` et `expand=False`.
- [x] Garder le header dans le `title` natif et les actions dans la zone native.
- [x] Fournir un mode scrollable Python avec une hauteur bornée lorsque demandé explicitement.
- [x] Ne plus interpréter les contenus côté Flutter.

## Phase 3 — Audit applicatif

- [x] Vérifier `CategoryEditorDialog`.
- [x] Vérifier `MetadataDialog`.
- [x] Vérifier les dialogues de renommage et déplacement.
- [x] Vérifier les suppressions et confirmations.
- [x] Vérifier les restaurations et la corbeille.
- [x] Vérifier les dialogues avec `title_action`.
- [x] Vérifier les ouvertures successives et imbriquées.

## Phase 4 — Validation

- [x] Lancer `flet run --recursive`.
- [x] Vérifier les hauteurs et largeurs réelles.
- [x] Vérifier le scroll.
- [x] Vérifier les contenus extensibles.
- [x] Valider le build Windows.
- [x] Faire valider visuellement et fonctionnellement par l’utilisateur.

## Phase 5 — Nettoyage après validation

- [x] Coordonner la suppression de `PaperNestAlertDialog` dans PaperNestExtension.
- [x] Supprimer sa page d’exemple et ses exports.
- [x] Supprimer son contrôle Flutter et Python.
- [x] Supprimer `PaperNestDialogSurface` après la migration des pickers.
- [x] Mettre à jour la documentation et les changelogs.

## Pickers

Les pickers ont été traités dans leurs roadmaps dédiées :

- ColorPicker : composition Python validée avec `flet-color-pickers`.
- IconPicker : reconstruction 100 % Python validée.
- DatePicker : wrapper Python validé autour de `ft.DatePicker`.
- FilePicker : inchangé.

## Critère de finalisation

La roadmap sera terminée lorsque tous les dialogues PaperNest utiliseront `ft.AlertDialog`, que les contenus extensibles et scrollables seront validés sans régression, puis que le contrôle `PaperNestAlertDialog` aura été supprimé de PaperNestExtension.
