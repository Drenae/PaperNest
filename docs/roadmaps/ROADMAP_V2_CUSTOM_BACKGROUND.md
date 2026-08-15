# Roadmap v2.0.0 — Fond personnalisable

## Vision

Faire du fond personnalisable le premier chantier de PaperNest 2.0.0. L’utilisateur peut conserver l’identité PaperNest, choisir une couleur ou utiliser une image personnelle, sans déformation et sans dépendre du fichier d’origine.

Cette fondation préparera une évolution glassmorphism ultérieure. Le glassmorphism n’est pas inclus dans ce chantier.

## Expérience attendue

- [x] Fournir un fond abstrait PaperNest jaune, blanc et gris par défaut.
- [x] Ajouter une section **Apparence** dans l’administration.
- [x] Permettre de choisir le mode **Image** ou **Couleur**.
- [x] Utiliser `BaseColorPicker` pour la couleur.
- [x] Utiliser `BaseFilePicker` / `PaperNestFilePicker` pour l’image.
- [x] Afficher une prévisualisation avant application.
- [x] Appliquer immédiatement le nouveau fond après validation.
- [x] Proposer **Restaurer le fond PaperNest**.

## Rendu de l’image

- [x] Utiliser `Page.decoration` et `BoxDecoration`.
- [x] Utiliser `DecorationImage` avec `BoxFit.COVER` pour conserver les proportions.
- [x] Centrer l’image par défaut.
- [ ] Permettre ultérieurement de choisir l’alignement de l’image.
- [ ] Ajouter ultérieurement un voile clair/sombre réglable si nécessaire.

## Stockage et sécurité

- [x] Enregistrer les préférences dans `Documents/PaperNest/data`.
- [x] Copier l’image choisie dans les données PaperNest.
- [x] Ne jamais dépendre du chemin du fichier source.
- [x] Accepter PNG, JPG, JPEG et WebP.
- [x] Vérifier réellement le contenu avec Pillow.
- [x] Conserver la résolution originale et accepter les images jusqu’à 50 Mo.
- [x] Revenir automatiquement au fond par défaut si le fichier est absent ou corrompu.
- [x] Remplacer proprement l’ancienne image personnalisée.

## Architecture

- [x] Créer un modèle immuable de préférences d’arrière-plan.
- [x] Créer un service responsable du chargement, de la validation et de la persistance.
- [x] Centraliser l’application de la décoration de page.
- [x] Appliquer le changement d’apparence sans redémarrer l’application.
- [x] Ajouter des tests unitaires pour la configuration et la validation d’image.

## Validation finale

- [ ] Tester le fond par défaut sous Windows.
- [ ] Tester une photo portrait, paysage et carrée.
- [ ] Vérifier le redimensionnement de la fenêtre.
- [ ] Vérifier le redémarrage de l’application.
- [ ] Vérifier le cas d’une image supprimée ou corrompue.
- [ ] Valider le build Windows PaperNest 2.0.0.

## Hors périmètre de ce chantier

- Glassmorphism des cartes et dialogues.
- Synchronisation du fond entre plusieurs appareils.
- Diaporama ou rotation automatique de plusieurs images.
- Retouche d’image intégrée.
