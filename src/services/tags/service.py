import re
from pathlib import Path

from utils.text import normalize_search_text
from repositories.tag_repository import tag_repository


class TagService:
    MAX_SUGGESTIONS = 10

    STOP_WORDS = {
        "avec",
        "dans",
        "des",
        "document",
        "documents",
        "du",
        "est",
        "et",
        "fichier",
        "les",
        "pour",
        "sur",
        "the",
        "une",
    }

    KEYWORD_TAGS = {
        "assurance": "Assurance",
        "assurances": "Assurance",
        "banque": "Banque",
        "bancaire": "Banque",
        "carte": "Carte",
        "certificat": "Certificat",
        "contrat": "Contrat",
        "devis": "Devis",
        "ecole": "École",
        "edf": "EDF",
        "energie": "Énergie",
        "facture": "Facture",
        "factures": "Facture",
        "fiscal": "Impôts",
        "garantie": "Garantie",
        "impot": "Impôts",
        "impots": "Impôts",
        "logement": "Maison",
        "maison": "Maison",
        "medical": "Santé",
        "mutuelle": "Santé",
        "ordonnance": "Santé",
        "paiement": "Paiement",
        "sante": "Santé",
        "scolaire": "École",
        "travail": "Travail",
        "vehicule": "Voiture",
        "voiture": "Voiture",
    }

    def list_all(self) -> list[str]:
        return tag_repository.list_names()

    def list_popular(self, limit: int = 12) -> list[str]:
        tags = tag_repository.list_all()

        ordered = sorted(
            tags,
            key=lambda tag: (
                -int(tag.get("document_count", 0)),
                normalize_search_text(str(tag.get("name", ""))),
            ),
        )

        return [
            str(tag["name"])
            for tag in ordered[: max(1, limit)]
            if str(tag.get("name", "")).strip()
        ]

    def suggest_for_document(
        self,
        *,
        file_name: str,
        category_name: str = "",
        person_name: str = "",
        notes: str = "",
        selected_tags: list[str] | tuple[str, ...] = (),
        limit: int = MAX_SUGGESTIONS,
    ) -> list[str]:
        selected_normalized = {
            normalize_search_text(tag)
            for tag in selected_tags
            if normalize_search_text(tag)
        }

        context = " ".join(
            (
                Path(file_name).stem,
                category_name,
                person_name,
                notes,
            )
        )
        normalized_context = normalize_search_text(context)
        context_tokens = set(self._tokenize(normalized_context))

        scores: dict[str, tuple[int, str]] = {}

        def add(tag_name: str, score: int) -> None:
            clean_name = " ".join(tag_name.strip().split())
            normalized_name = normalize_search_text(clean_name)

            if not normalized_name or normalized_name in selected_normalized:
                return

            current = scores.get(normalized_name)
            if current is None or score > current[0]:
                scores[normalized_name] = (score, clean_name)

        for token in context_tokens:
            mapped_tag = self.KEYWORD_TAGS.get(token)
            if mapped_tag:
                add(mapped_tag, 100)

        clean_category = " ".join(category_name.strip().split())
        if clean_category and normalize_search_text(clean_category) not in {
            "autre",
            "autres",
            "documents",
        }:
            add(clean_category, 90)

        for year in re.findall(r"\b(?:19|20)\d{2}\b", normalized_context):
            add(year, 80)

        all_tags = tag_repository.list_all()
        for tag in all_tags:
            name = str(tag.get("name", "")).strip()
            normalized_name = normalize_search_text(name)
            usage = int(tag.get("document_count", 0))

            if not normalized_name:
                continue

            tag_tokens = set(self._tokenize(normalized_name))
            overlap = len(context_tokens.intersection(tag_tokens))

            if normalized_name in normalized_context:
                add(name, 85 + min(usage, 10))
            elif overlap:
                add(name, 65 + overlap * 8 + min(usage, 10))
            elif usage:
                add(name, min(usage, 20))

        ordered = sorted(
            scores.values(),
            key=lambda item: (
                -item[0],
                normalize_search_text(item[1]),
            ),
        )

        return [name for _, name in ordered[: max(1, limit)]]

    def filter_suggestions(
        self,
        query: str,
        *,
        selected_tags: list[str] | tuple[str, ...] = (),
        limit: int = 8,
    ) -> list[str]:
        normalized_query = normalize_search_text(query)
        selected = {
            normalize_search_text(tag)
            for tag in selected_tags
        }

        candidates = []
        for tag in tag_repository.list_all():
            name = str(tag.get("name", "")).strip()
            normalized_name = normalize_search_text(name)

            if not normalized_name or normalized_name in selected:
                continue

            if normalized_query and normalized_query not in normalized_name:
                continue

            candidates.append(
                (
                    0 if normalized_name.startswith(normalized_query) else 1,
                    -int(tag.get("document_count", 0)),
                    normalized_name,
                    name,
                )
            )

        candidates.sort()
        return [item[3] for item in candidates[: max(1, limit)]]

    @classmethod
    def _tokenize(cls, text: str) -> list[str]:
        return [
            token
            for token in re.findall(r"[a-z0-9]+", text)
            if len(token) >= 3 and token not in cls.STOP_WORDS
        ]


tag_service = TagService()
