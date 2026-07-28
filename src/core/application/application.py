import logging

from core.database.database import Database, database
from core.events.event_bus import EventBus, event_bus
from core.database.migrations import MigrationManager, migration_manager
from core.scheduling.scheduler import TaskScheduler, task_scheduler
from core.application.service_locator import ServiceLocator, services
from repositories.backup_repository import BackupRepository, backup_repository
from repositories.category_repository import CategoryRepository, category_repository
from repositories.document_repository import DocumentRepository, document_repository
from repositories.metadata_repository import MetadataRepository, metadata_repository
from repositories.statistics_repository import StatisticsRepository, statistics_repository
from repositories.tag_repository import TagRepository, tag_repository
from services.categories.service import CategoryService, category_service
from services.documents.delete import DocumentDeleteService, document_delete_service
from services.documents.metadata import MetadataService, metadata_service
from services.documents.move import DocumentMoveService, document_move_service
from services.documents.query import DocumentQueryService, document_query_service
from services.documents.rename import DocumentRenameService, document_rename_service
from services.documents.restore import DocumentRestoreService, document_restore_service
from services.statistics.service import StatisticsService, statistics_service

logger = logging.getLogger(__name__)


class Application:
    def __init__(self):
        self.database: Database = database
        self.event_bus: EventBus = event_bus
        self.scheduler: TaskScheduler = task_scheduler
        self.migrations: MigrationManager = migration_manager
        self.services: ServiceLocator = services
        self._started = False

    def start(self) -> None:
        if self._started: return
        self.migrations.migrate()
        self._register_services()
        self._started = True
        logger.info("Cœur de PaperNest démarré.")

    def shutdown(self) -> None:
        if not self._started: return
        self.scheduler.shutdown(wait=False)
        self.event_bus.clear()
        self.services.clear()
        self._started = False
        logger.info("Cœur de PaperNest arrêté." )

    def _register_services(self) -> None:
        self.services.register_if_missing(Database, self.database)
        self.services.register_if_missing(EventBus, self.event_bus)
        self.services.register_if_missing(TaskScheduler, self.scheduler)
        self.services.register_if_missing(MigrationManager, self.migrations)
        self.services.register_if_missing(DocumentRepository, document_repository)
        self.services.register_if_missing(CategoryRepository, category_repository)
        self.services.register_if_missing(TagRepository, tag_repository)
        self.services.register_if_missing(MetadataRepository, metadata_repository)
        self.services.register_if_missing(StatisticsRepository, statistics_repository)
        self.services.register_if_missing(BackupRepository, backup_repository)
        self.services.register_if_missing(CategoryService, category_service)
        self.services.register_if_missing(MetadataService, metadata_service)
        self.services.register_if_missing(DocumentQueryService, document_query_service)
        self.services.register_if_missing(DocumentMoveService, document_move_service)
        self.services.register_if_missing(DocumentRenameService, document_rename_service)
        self.services.register_if_missing(DocumentDeleteService, document_delete_service)
        self.services.register_if_missing(DocumentRestoreService, document_restore_service)
        self.services.register_if_missing(StatisticsService, statistics_service)

    @property
    def is_started(self) -> bool:
        return self._started

application = Application()