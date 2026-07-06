from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class OutbreakPromotionState:
    active_version: str | None
    previous_version: str | None
    promoted_at: datetime | None


class OutbreakModelRegistry:
    """File-based promotion registry for outbreak ML artifacts."""

    MANIFEST_FILENAME = "promoted-outbreak.json"

    def __init__(self, artifacts_dir: Path) -> None:
        self._artifacts_dir = artifacts_dir
        self._manifest_path = artifacts_dir / self.MANIFEST_FILENAME

    @property
    def artifacts_dir(self) -> Path:
        return self._artifacts_dir

    def get_promotion_state(self) -> OutbreakPromotionState:
        payload = self._read_manifest()
        promoted_at_raw = payload.get("promoted_at")
        promoted_at = None
        if promoted_at_raw:
            promoted_at = datetime.fromisoformat(str(promoted_at_raw).replace("Z", "+00:00"))
        return OutbreakPromotionState(
            active_version=payload.get("active_version"),
            previous_version=payload.get("previous_version"),
            promoted_at=promoted_at,
        )

    def promote(self, version: str) -> OutbreakPromotionState:
        artifact_path = self._artifacts_dir / f"{version}.joblib"
        metadata_path = self._artifacts_dir / f"{version}.json"
        if not artifact_path.exists() or not metadata_path.exists():
            msg = f"Outbreak model artifacts not found for version {version!r}."
            raise FileNotFoundError(msg)

        current = self.get_promotion_state()
        payload = {
            "active_version": version,
            "previous_version": current.active_version,
            "promoted_at": datetime.now(tz=UTC).isoformat(),
            "history": self._read_manifest().get("history", []),
        }
        payload["history"] = list(payload["history"]) + [
            {"action": "promote", "version": version, "at": payload["promoted_at"]},
        ]
        self._write_manifest(payload)
        return self.get_promotion_state()

    def rollback(self) -> OutbreakPromotionState:
        current = self.get_promotion_state()
        restored_version = current.previous_version
        payload = {
            "active_version": restored_version,
            "previous_version": None,
            "promoted_at": datetime.now(tz=UTC).isoformat() if restored_version else None,
            "history": self._read_manifest().get("history", []),
        }
        payload["history"] = list(payload["history"]) + [
            {
                "action": "rollback",
                "version": restored_version,
                "at": datetime.now(tz=UTC).isoformat(),
            },
        ]
        self._write_manifest(payload)
        return self.get_promotion_state()

    def _read_manifest(self) -> dict[str, object]:
        if not self._manifest_path.exists():
            return {"active_version": None, "previous_version": None, "history": []}
        return json.loads(self._manifest_path.read_text(encoding="utf-8"))

    def _write_manifest(self, payload: dict[str, object]) -> None:
        self._artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
