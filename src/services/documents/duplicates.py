import hashlib
from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum
from pathlib import Path

from utils.text import normalize_search_text
from repositories.document_repository import document_repository


class DuplicateKind(Enum):
    EXACT = "exact"
    PROBABLE = "probable"


@dataclass(frozen=True, slots=True)
class DuplicateMatch:
    kind: DuplicateKind
    document_id: int
    display_name: str
    category_name: str
    relative_path: str
    extension: str
    size_bytes: int
    confidence: int
    reason: str


@dataclass(frozen=True, slots=True)
class DuplicateAnalysis:
    source_path: Path
    source_sha256: str
    source_size_bytes: int
    matches: tuple[DuplicateMatch, ...]

    @property
    def has_matches(self) -> bool:
        return bool(self.matches)

    @property
    def has_exact_match(self) -> bool:
        return any(match.kind is DuplicateKind.EXACT for match in self.matches)


class DuplicateDetectionService:
    COPY_BUFFER_SIZE = 1024 * 1024
    MAX_CANDIDATES = 120
    MAX_RESULTS = 5
    MIN_NAME_SIMILARITY = 0.72
    SIZE_TOLERANCE_RATIO = 0.03
    MIN_SIZE_TOLERANCE = 4096

    def analyze(self, source_file_path: str | Path, proposed_name: str) -> DuplicateAnalysis:
        source_path = Path(source_file_path).expanduser()

        if not source_path.exists() or not source_path.is_file():
            raise FileNotFoundError("Le fichier à analyser est introuvable.")

        source_size = source_path.stat().st_size
        source_hash = self._compute_sha256(source_path)
        exact = document_repository.find_by_hash(source_hash)

        if exact:
            match = self._build_exact_match(exact)
            return DuplicateAnalysis(source_path, source_hash, source_size, (match,))

        extension = source_path.suffix.casefold()
        tolerance = max(
            self.MIN_SIZE_TOLERANCE,
            int(source_size * self.SIZE_TOLERANCE_RATIO),
        )

        candidates = document_repository.find_duplicate_candidates(
            extension=extension,
            minimum_size=max(0, source_size - tolerance),
            maximum_size=source_size + tolerance,
            limit=self.MAX_CANDIDATES,
        )

        proposed_stem = self._normalize_name(proposed_name or source_path.stem)
        matches: list[DuplicateMatch] = []

        for candidate in candidates:
            candidate_name = self._normalize_name(str(candidate["display_name"]))
            name_similarity = SequenceMatcher(None, proposed_stem, candidate_name).ratio()
            candidate_size = int(candidate["size_bytes"])
            size_similarity = self._size_similarity(source_size, candidate_size)

            confidence = round((name_similarity * 0.78 + size_similarity * 0.22) * 100)

            if name_similarity < self.MIN_NAME_SIMILARITY and confidence < 82:
                continue

            reason_parts = [f"nom similaire à {round(name_similarity * 100)} %"]

            if candidate_size == source_size:
                reason_parts.append("taille identique")
            else:
                reason_parts.append("taille très proche")

            matches.append(
                DuplicateMatch(
                    kind=DuplicateKind.PROBABLE,
                    document_id=int(candidate["id"]),
                    display_name=str(candidate["display_name"]),
                    category_name=str(candidate["category_name"]),
                    relative_path=str(candidate["relative_path"]),
                    extension=str(candidate["extension"]),
                    size_bytes=candidate_size,
                    confidence=confidence,
                    reason=" et ".join(reason_parts),
                )
            )

        matches.sort(key=lambda item: item.confidence, reverse=True)

        return DuplicateAnalysis(
            source_path=source_path,
            source_sha256=source_hash,
            source_size_bytes=source_size,
            matches=tuple(matches[: self.MAX_RESULTS]),
        )

    @staticmethod
    def _build_exact_match(row: dict) -> DuplicateMatch:
        return DuplicateMatch(
            kind=DuplicateKind.EXACT,
            document_id=int(row["id"]),
            display_name=str(row["display_name"]),
            category_name=str(row["category_name"]),
            relative_path=str(row["relative_path"]),
            extension=str(row["extension"]),
            size_bytes=int(row["size_bytes"]),
            confidence=100,
            reason="contenu strictement identique",
        )

    @staticmethod
    def _normalize_name(value: str) -> str:
        normalized = normalize_search_text(Path(value).stem)
        return " ".join(part for part in normalized.replace("_", " ").replace("-", " ").split() if part)

    @staticmethod
    def _size_similarity(first: int, second: int) -> float:
        largest = max(first, second, 1)
        return max(0.0, 1.0 - abs(first - second) / largest)

    def _compute_sha256(self, path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as stream:
            while chunk := stream.read(self.COPY_BUFFER_SIZE):
                digest.update(chunk)

        return digest.hexdigest()


duplicate_detection_service = DuplicateDetectionService()
