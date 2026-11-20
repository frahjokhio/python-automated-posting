from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from app.config import Settings
from app.schemas import PlatformResult


class BasePlatform(ABC):
    name: str

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @abstractmethod
    def has_credentials(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        raise NotImplementedError

    async def post(self, message: str) -> PlatformResult:
        if self.settings.dry_run:
            return self._dry_run_result()

        if not self.has_credentials():
            return self._failed_result("Missing credentials")

        try:
            return await self.publish(message)
        except Exception as exc:  # noqa: BLE001 - isolate platform failures
            return self._failed_result(str(exc))

    def _now_parts(self) -> tuple[str, str]:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    def _success_result(
        self,
        posted_url: str | None,
        *,
        public_access: bool = True,
    ) -> PlatformResult:
        date_str, time_str = self._now_parts()
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=date_str,
            time=time_str,
            error=None,
        )

    def _failed_result(self, error: str) -> PlatformResult:
        return PlatformResult(
            platform=self.name,
            status="failed",
            posted_url=None,
            public_access=False,
            date=None,
            time=None,
            error=error,
        )

    def _dry_run_result(self) -> PlatformResult:
        date_str, time_str = self._now_parts()
        slug = self.name.lower().replace(".", "").replace(" ", "-")
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=f"https://example.com/dry-run/{slug}",
            public_access=True,
            date=date_str,
            time=time_str,
            error=None,
        )
