import sqlite3
from typing import Any

from core.database.database import database
from core.errors.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError, DatabaseError
from utils.time import local_now_iso


class CategoryRepository:
    """Accès aux catégories et à leur hiérarchie à deux niveaux."""

    SELECT_COLUMNS = """
        categories.id, categories.key, categories.name, categories.icon,
        categories.color, categories.bg, categories.parent_key,
        categories.position, categories.created_at, categories.updated_at,
        (
            SELECT COUNT(*)
            FROM documents direct_documents
            WHERE direct_documents.category_key = categories.key
        ) AS direct_document_count,
        (
            SELECT COUNT(*)
            FROM documents category_documents
            WHERE category_documents.category_key = categories.key
        ) AS document_count
    """

    def list_all(self) -> list[dict[str, Any]]:
        return self._list(None, roots_only=False)

    def list_roots(self) -> list[dict[str, Any]]:
        roots = self._list(None, roots_only=True)
        for root in roots:
            children = self.list_children(str(root["key"]))
            root["subcategory_count"] = len(children)
            root["document_count"] = int(root.get("direct_document_count", 0)) + sum(
                int(child.get("direct_document_count", child.get("document_count", 0)))
                for child in children
            )
        return roots

    def list_children(self, parent_key: str) -> list[dict[str, Any]]:
        return self._list(parent_key, roots_only=False)

    def list_tree(self) -> list[dict[str, Any]]:
        roots = self.list_roots()
        for root in roots:
            root["children"] = self.list_children(str(root["key"]))
        return roots

    def _list(self, parent_key: str | None, *, roots_only: bool) -> list[dict[str, Any]]:
        try:
            with database.connection() as connection:
                if roots_only:
                    where = "categories.parent_key IS NULL"
                    params: tuple = ()
                elif parent_key is not None:
                    where = "categories.parent_key = ?"
                    params = (parent_key,)
                else:
                    where = "1 = 1"
                    params = ()

                rows = connection.execute(
                    f"""
                    SELECT {self.SELECT_COLUMNS}
                    FROM categories
                    WHERE {where}
                    ORDER BY categories.position ASC, categories.name COLLATE NOCASE ASC
                    """,
                    params,
                ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as error:
            raise DatabaseError("Impossible de lire les catégories.") from error

    def get(self, category_key: str) -> dict[str, Any] | None:
        try:
            with database.connection() as connection:
                row = connection.execute(
                    f"""
                    SELECT {self.SELECT_COLUMNS}
                    FROM categories
                    WHERE categories.key = ?
                    LIMIT 1
                    """,
                    (category_key,),
                ).fetchone()
            if not row:
                return None
            result = dict(row)
            if result.get("parent_key") is None:
                children = self.list_children(category_key)
                result["subcategory_count"] = len(children)
                result["document_count"] = int(result.get("direct_document_count", 0)) + sum(
                    int(child.get("direct_document_count", child.get("document_count", 0)))
                    for child in children
                )
            return result
        except sqlite3.Error as error:
            raise DatabaseError("Impossible de lire la catégorie.") from error

    def exists(self, category_key: str) -> bool:
        return self.get(category_key) is not None

    def create(
        self,
        *,
        category_key: str,
        name: str,
        icon: str,
        color: str,
        background: str,
        parent_key: str | None = None,
        position: int = 0,
    ) -> dict[str, Any]:
        now = local_now_iso()
        try:
            with database.connection() as connection:
                connection.execute(
                    """
                    INSERT INTO categories
                    (key, name, icon, color, bg, parent_key, position, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (category_key, name.strip(), icon, color, background, parent_key, position, now, now),
                )
            category = self.get(category_key)
            if category is None:
                raise DatabaseError("La catégorie créée est introuvable.")
            return category
        except sqlite3.IntegrityError as error:
            raise CategoryAlreadyExistsError(f"La catégorie « {name} » existe déjà.") from error
        except sqlite3.Error as error:
            raise DatabaseError("Impossible de créer la catégorie.") from error

    def update(
        self,
        old_key: str,
        *,
        new_key: str,
        name: str,
        icon: str,
        color: str,
        background: str,
    ) -> dict[str, Any]:
        now = local_now_iso()
        try:
            with database.connection() as connection:
                current = connection.execute(
                    "SELECT key FROM categories WHERE key = ? LIMIT 1", (old_key,)
                ).fetchone()
                if current is None:
                    raise CategoryNotFoundError(f"La catégorie « {old_key} » n’existe pas.")
                connection.execute(
                    """
                    UPDATE categories SET key=?, name=?, icon=?, color=?, bg=?, updated_at=?
                    WHERE key=?
                    """,
                    (new_key, name.strip(), icon, color, background, now, old_key),
                )
                if old_key != new_key:
                    connection.execute(
                        "UPDATE categories SET parent_key=? WHERE parent_key=?",
                        (new_key, old_key),
                    )
                    old_prefix = f"{old_key}/"
                    new_prefix = f"{new_key}/"
                    connection.execute(
                        "UPDATE categories SET key=? || substr(key, length(?) + 1) WHERE key LIKE ?",
                        (new_prefix, old_prefix, f"{old_prefix}%"),
                    )
                    connection.execute(
                        "UPDATE documents SET category_key=? || substr(category_key, length(?) + 1) WHERE category_key LIKE ?",
                        (new_prefix, old_prefix, f"{old_prefix}%"),
                    )
                    connection.execute(
                        "UPDATE documents SET relative_path=? || substr(relative_path, length(?) + 1) WHERE relative_path LIKE ?",
                        (new_prefix, old_prefix, f"{old_prefix}%"),
                    )
            category = self.get(new_key)
            if category is None:
                raise DatabaseError("La catégorie modifiée est introuvable.")
            return category
        except (CategoryNotFoundError, CategoryAlreadyExistsError):
            raise
        except sqlite3.IntegrityError as error:
            raise CategoryAlreadyExistsError(f"La catégorie « {name} » existe déjà.") from error
        except sqlite3.Error as error:
            raise DatabaseError("Impossible de modifier la catégorie.") from error

    def delete(self, category_key: str) -> bool:
        try:
            with database.connection() as connection:
                cursor = connection.execute("DELETE FROM categories WHERE key = ?", (category_key,))
            if cursor.rowcount == 0:
                raise CategoryNotFoundError(f"La catégorie « {category_key} » n’existe pas.")
            return True
        except CategoryNotFoundError:
            raise
        except sqlite3.Error as error:
            raise DatabaseError("Impossible de supprimer la catégorie.") from error

    def count(self) -> int:
        try:
            with database.connection() as connection:
                row = connection.execute("SELECT COUNT(*) FROM categories").fetchone()
            return int(row[0]) if row else 0
        except sqlite3.Error as error:
            raise DatabaseError("Impossible de compter les catégories.") from error


category_repository = CategoryRepository()
