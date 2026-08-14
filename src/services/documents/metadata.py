from datetime import date
from decimal import Decimal, InvalidOperation

from core.events.event_bus import (
    DocumentFavoriteChanged,
    DocumentMetadataUpdated,
    event_bus,
)
from core.errors.exceptions import PaperNestError
from models.document_metadata import DocumentDetails
from repositories.metadata_repository import metadata_repository


class InvalidMetadataError(PaperNestError):
    pass


class MetadataService:
    def get_details(self, document_id: int) -> DocumentDetails:
        data = metadata_repository.get(document_id)

        return DocumentDetails(
            document_id=int(data["id"]),
            is_favorite=bool(data["is_favorite"]),
            tags=tuple(data.get("tags", [])),
            document_date=self._parse_date(data.get("document_date")),
            due_date=self._parse_date(data.get("due_date")),
            amount=self._parse_decimal(data.get("amount")),
            person_name=str(data.get("person_name") or ""),
            notes=str(data.get("notes") or ""),
        )

    def update_details(
        self,
        document_id: int,
        *,
        is_favorite: bool,
        tags: list[str],
        document_date: str | date | None,
        due_date: str | date | None,
        amount: str | Decimal | None,
        person_name: str,
        notes: str,
    ) -> DocumentDetails:
        parsed_document_date = self.validate_date(
            document_date,
            "La date du document",
        )

        parsed_due_date = self.validate_date(
            due_date,
            "La date d’échéance",
        )

        parsed_amount = self.validate_amount(amount)

        metadata_repository.update(
            document_id,
            is_favorite=is_favorite,
            document_date=(
                parsed_document_date.isoformat()
                if parsed_document_date
                else None
            ),
            due_date=(
                parsed_due_date.isoformat()
                if parsed_due_date
                else None
            ),
            amount=(
                str(parsed_amount)
                if parsed_amount is not None
                else None
            ),
            person_name=person_name,
            notes=notes,
            tags=tags,
        )

        event_bus.publish(
            DocumentMetadataUpdated(
                document_id=document_id
            )
        )

        return self.get_details(document_id)

    def toggle_favorite(self, document_id: int) -> bool:
        value = metadata_repository.toggle_favorite(document_id)

        event_bus.publish(
            DocumentFavoriteChanged(
                document_id=document_id,
                is_favorite=value,
            )
        )

        return value

    def set_favorite(self, document_id: int, value: bool) -> None:
        metadata_repository.set_favorite(
            document_id,
            value,
        )

        event_bus.publish(
            DocumentFavoriteChanged(
                document_id=document_id,
                is_favorite=value,
            )
        )

    def clear_details(self, document_id: int) -> None:
        metadata_repository.clear(document_id)

        event_bus.publish(
            DocumentMetadataUpdated(
                document_id=document_id
            )
        )

    @staticmethod
    def validate_date(
        value: str | date | None,
        field_name: str,
    ) -> date | None:
        if value in (None, ""):
            return None

        if isinstance(value, date):
            return value

        try:
            return date.fromisoformat(
                value.strip()
            )

        except ValueError as error:
            raise InvalidMetadataError(
                f"{field_name} doit être au format AAAA-MM-JJ."
            ) from error

    @staticmethod
    def validate_amount(
        value: str | Decimal | None,
    ) -> Decimal | None:
        if value in (None, ""):
            return None

        if isinstance(value, Decimal):
            amount = value

        else:
            normalized_value = (
                value.strip()
                .replace("€", "")
                .replace(" ", "")
                .replace(",", ".")
            )

            try:
                amount = Decimal(normalized_value)

            except InvalidOperation as error:
                raise InvalidMetadataError(
                    "Le montant saisi est invalide."
                ) from error

        if not amount.is_finite():
            raise InvalidMetadataError(
                "Le montant saisi est invalide."
            )

        if amount < 0:
            raise InvalidMetadataError(
                "Le montant ne peut pas être négatif."
            )

        if amount > Decimal("999999999.99"):
            raise InvalidMetadataError(
                "Le montant saisi est trop élevé."
            )

        return amount.quantize(
            Decimal("0.01")
        )

    @staticmethod
    def _parse_date(value) -> date | None:
        if not value:
            return None

        try:
            return date.fromisoformat(
                str(value)
            )

        except ValueError:
            return None

    @staticmethod
    def _parse_decimal(value) -> Decimal | None:
        if value in (None, ""):
            return None

        try:
            return Decimal(
                str(value)
            )

        except InvalidOperation:
            return None


metadata_service = MetadataService()
