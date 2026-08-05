# Roadmap — Retour à AppDialog 100 % Python

## État

**Décision validée : abandonner `PaperNestAlertDialog` et reconstruire `AppDialog` directement sur `ft.AlertDialog`.**

La migration vers le fork Flutter n’est pas validée. Les contenus complexes de PaperNest utilisent des contrôles extensibles et des scrolls internes qui doivent rester libres. Une composition Python est plus simple, plus fiable et plus facile à maintenir.

## Architecture cible

```text
AppDialog(ft.AlertDialog)
├── DialogVariant local
├── header Python
├── content Python libre
└── actions PaperNestButton
```

PaperNestExtension ne doit plus intervenir dans la construction ou la mise en page des dialogues.

## Phase 1 — Reconstruction de AppDialog

- [ ] Faire hériter `AppDialog` de `ft.AlertDialog`.
- [ ] Conserver `DialogVariant` dans PaperNest.
- [ ] Construire le header sombre en Python.
- [ ] Construire la pastille d’icône selon le variant local.
- [ ] Gérer le titre, le sous-titre et `title_action` en Python.
- [ ] Conserver le contenu applicatif tel quel, sans le réenvelopper inutilement.
- [ ] Conserver les actions utilisant les boutons PaperNest.
- [ ] Conserver la barrière, la forme, l’ombre et les espacements PaperNest.
- [ ] Conserver `ConfirmDialog`, `DangerDialog` et `FormDialog`.

## Phase 2 — Compatibilité des contenus

- [ ] Préserver les contrôles avec `expand=True`.
- [ ] Préserver les `Column` et `ListView` qui gèrent leur propre scroll.
- [ ] Préserver les contenus courts à hauteur naturelle.
- [ ] Préserver les formulaires occupant une hauteur choisie.
- [ ] Garder le header et les actions fixes lorsque le contenu applicatif défile.
- [ ] Ne pas modifier les composants internes des dialogues pour contourner des contraintes Flutter.

## Phase 3 — Audit applicatif

- [ ] Vérifier `CategoryEditorDialog`.
- [ ] Vérifier `MetadataDialog`.
- [ ] Vérifier les dialogues de renommage et déplacement.
- [ ] Vérifier les suppressions et confirmations.
- [ ] Vérifier les restaurations et la corbeille.
- [ ] Vérifier les dialogues avec `title_action`.
- [ ] Vérifier les ouvertures successives et imbriquées.

## Phase 4 — Validation

- [ ] Lancer `flet run --recursive`.
- [ ] Vérifier les hauteurs et largeurs réelles.
- [ ] Vérifier le scroll.
- [ ] Vérifier les contenus extensibles.
- [ ] Valider le build Windows.
- [ ] Faire valider visuellement et fonctionnellement par l’utilisateur.

## Phase 5 — Nettoyage après validation

- [ ] Retirer l’import de `PaperNestAlertDialog`.
- [ ] Coordonner la suppression du contrôle dans PaperNestExtension.
- [ ] Nettoyer les anciens paramètres spécifiques au fork devenus inutiles.
- [ ] Mettre à jour la documentation et les changelogs.

## Pickers

Les pickers restent un chantier séparé :

- ColorPicker : prototype Python avec `flet-color-picker` avant décision finale.
- IconPicker : reconstruction 100 % Python.
- DatePicker : wrapper Python autour de `ft.DatePicker`.
- FilePicker : inchangé.

## Critère de finalisation

La roadmap sera terminée lorsque tous les dialogues PaperNest utiliseront `ft.AlertDialog`, que les contenus extensibles et scrollables seront validés sans régression, puis que la dépendance à `PaperNestAlertDialog` aura été supprimée.
