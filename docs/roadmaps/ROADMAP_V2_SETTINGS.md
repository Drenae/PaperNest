# Roadmap v2.0.0 — Paramètres de l’application

## Objectif

Regrouper les préférences utilisateur dans une page dédiée afin de séparer la configuration de l’application des outils d’administration.

## Navigation et organisation

- [x] Ajouter la destination **Paramètres** au-dessus d’Administration.
- [x] Retirer Apparence de la page Administration.
- [x] Déplacer Apparence dans la page Paramètres.
- [x] Conserver une disposition responsive en deux colonnes sur grand écran.

## Apparence

- [x] Conserver le choix entre image et couleur.
- [x] Corriger le changement immédiat de mode du dropdown.
- [x] Retirer le `wrap` défectueux de la ligne d’actions.

## Corbeille

- [x] Ajouter une durée de conservation paramétrable.
- [x] Utiliser 30 jours par défaut.
- [x] Accepter une valeur comprise entre 1 et 3650 jours.
- [x] Persister le réglage dans les données PaperNest.
- [x] Appliquer la durée à la purge automatique.
- [x] Appliquer la durée aux jours restants et à la progression affichée.
- [x] Afficher la durée configurée dans l’en-tête de la Corbeille.
- [x] Ajouter des tests unitaires de persistance et de validation.

## Validation Windows

- [ ] Vérifier la nouvelle destination dans `PaperNestGlideRail`.
- [ ] Vérifier la disposition Paramètres en fenêtre réduite et maximisée.
- [ ] Vérifier la conservation après redémarrage.
- [ ] Vérifier les calculs avec plusieurs âges de documents supprimés.
