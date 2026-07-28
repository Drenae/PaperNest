class PaperNestError(Exception):
    """Erreur métier générale de PaperNest."""


class StorageError(PaperNestError):
    """Erreur liée au stockage physique des fichiers."""


class DatabaseError(PaperNestError):
    """Erreur liée à la base SQLite."""


class CategoryNotFoundError(PaperNestError):
    """La catégorie demandée n'existe pas."""


class CategoryAlreadyExistsError(PaperNestError):
    """Une catégorie portant cette clé existe déjà."""


class InvalidCategoryNameError(PaperNestError):
    """Le nom de catégorie fourni est invalide."""


class InvalidDocumentNameError(PaperNestError):
    """Le nom du document fourni est invalide."""


class DocumentNotFoundError(PaperNestError):
    """Le document demandé n'existe pas."""


class DuplicateDocumentError(PaperNestError):
    """Le document a déjà été importé."""


class DocumentImportError(PaperNestError):
    """L'import du document a échoué."""


class PdfExtractionError(PaperNestError):
    """Le contenu du PDF n'a pas pu être extrait."""