from dataclasses import dataclass

from repositories.statistics_repository import statistics_repository


@dataclass(frozen=True, slots=True)
class DashboardStatistics:
    total_documents: int
    total_size_bytes: int
    favorite_documents: int
    upcoming_documents: int
    imported_last_30_days: int
    category_count: int
    tag_count: int
    overdue_documents: int

    @property
    def formatted_total_size(self) -> str:
        return StatisticsService.format_size(self.total_size_bytes)


@dataclass(frozen=True, slots=True)
class CategoryStatistic:
    category_key: str
    category_name: str
    color: str
    document_count: int
    size_bytes: int

    @property
    def formatted_size(self) -> str:
        return StatisticsService.format_size(self.size_bytes)


@dataclass(frozen=True, slots=True)
class RecentDocument:
    document_id: int
    display_name: str
    relative_path: str
    extension: str
    size_bytes: int
    imported_at: str
    is_favorite: bool
    category_key: str
    category_name: str

    @property
    def formatted_size(self) -> str:
        return StatisticsService.format_size(self.size_bytes)


@dataclass(frozen=True, slots=True)
class UpcomingDeadline:
    document_id: int
    display_name: str
    relative_path: str
    due_date: str
    person_name: str
    amount: str | None
    category_key: str
    category_name: str
    days_remaining: int


@dataclass(frozen=True, slots=True)
class MonthlyImport:
    month: str
    document_count: int
    size_bytes: int


class StatisticsService:
    def get_dashboard_statistics(self) -> DashboardStatistics:
        data = statistics_repository.get_dashboard_statistics()

        return DashboardStatistics(
            total_documents=int(data["total_documents"]),
            total_size_bytes=int(data["total_size_bytes"]),
            favorite_documents=int(data["favorite_documents"]),
            upcoming_documents=int(data["upcoming_documents"]),
            imported_last_30_days=int(data["imported_last_30_days"]),
            category_count=int(data["category_count"]),
            tag_count=int(data["tag_count"]),
            overdue_documents=statistics_repository.count_overdue_documents(),
        )

    def get_category_distribution(self) -> list[CategoryStatistic]:
        rows = statistics_repository.get_category_distribution()

        return [
            CategoryStatistic(
                category_key=str(row["category_key"]),
                category_name=str(row["category_name"]),
                color=str(row["color"]),
                document_count=int(row["document_count"]),
                size_bytes=int(row["size_bytes"]),
            )
            for row in rows
        ]

    def get_recent_documents(self, limit: int = 10) -> list[RecentDocument]:
        rows = statistics_repository.get_recent_documents(limit)

        return [
            RecentDocument(
                document_id=int(row["id"]),
                display_name=str(row["display_name"]),
                relative_path=str(row["relative_path"]),
                extension=str(row["extension"]),
                size_bytes=int(row["size_bytes"]),
                imported_at=str(row["imported_at"]),
                is_favorite=bool(row["is_favorite"]),
                category_key=str(row["category_key"]),
                category_name=str(row["category_name"]),
            )
            for row in rows
        ]

    def get_upcoming_deadlines(
        self,
        days: int = 30,
        limit: int = 10,
    ) -> list[UpcomingDeadline]:
        rows = statistics_repository.get_upcoming_deadlines(
            days,
            limit,
        )

        return [
            UpcomingDeadline(
                document_id=int(row["id"]),
                display_name=str(row["display_name"]),
                relative_path=str(row["relative_path"]),
                due_date=str(row["due_date"]),
                person_name=str(row["person_name"] or ""),
                amount=(
                    str(row["amount"])
                    if row["amount"] is not None
                    else None
                ),
                category_key=str(row["category_key"]),
                category_name=str(row["category_name"]),
                days_remaining=int(row["days_remaining"]),
            )
            for row in rows
        ]

    def get_monthly_imports(self, months: int = 12) -> list[MonthlyImport]:
        rows = statistics_repository.get_monthly_imports(months)

        return [
            MonthlyImport(
                month=str(row["month"]),
                document_count=int(row["document_count"]),
                size_bytes=int(row["size_bytes"]),
            )
            for row in rows
        ]

    @staticmethod
    def format_size(size_bytes: int) -> str:
        size = float(size_bytes)
        units = ("o", "Ko", "Mo", "Go", "To")

        for unit in units:
            if size < 1024 or unit == units[-1]:
                if unit == "o":
                    return f"{int(size)} {unit}"

                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size_bytes} o"


statistics_service = StatisticsService()