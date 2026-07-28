from dataclasses import dataclass, field


@dataclass
class AdminState:
    backups: list[dict] = field(default_factory=list)
    backups_loading: bool = False
    backups_error: str = ""

    def set_backups(self, backups: list[dict]) -> None:
        self.backups = backups
        self.backups_error = ""
