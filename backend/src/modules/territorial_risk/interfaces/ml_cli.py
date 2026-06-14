"""CLI for promoting and rolling back territorial risk ML models."""

from __future__ import annotations

import argparse
import json
import sys

from config.settings import get_settings
from modules.territorial_risk.infrastructure.ml.file_promoted_model_adapter import (
    load_model_metadata,
    resolve_artifacts_dir,
)
from modules.territorial_risk.infrastructure.ml.model_registry import ModelRegistry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Territorial risk model promotion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    promote_parser = subparsers.add_parser("promote", help="Promote a trained model version")
    promote_parser.add_argument("version", help="Registered model version identifier")

    subparsers.add_parser("rollback", help="Rollback to the previous promoted version")
    subparsers.add_parser("status", help="Show current promotion state")
    return parser


def run_status(registry: ModelRegistry) -> int:
    state = registry.get_promotion_state()
    payload = {
        "active_version": state.active_version,
        "previous_version": state.previous_version,
        "promoted_at": state.promoted_at.isoformat() if state.promoted_at else None,
        "artifacts_dir": str(registry.artifacts_dir),
    }
    if state.active_version:
        payload["metadata"] = load_model_metadata(state.active_version, registry.artifacts_dir)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    registry = ModelRegistry(resolve_artifacts_dir(get_settings()))

    if args.command == "promote":
        state = registry.promote(args.version)
        print(
            f"Promoted model {state.active_version}. "
            f"Previous version: {state.previous_version or '-'}",
        )
        return 0

    if args.command == "rollback":
        state = registry.rollback()
        print(
            f"Rollback completed. Active version: {state.active_version or 'rule-based fallback'}",
        )
        return 0

    if args.command == "status":
        return run_status(registry)

    parser.error(f"Unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
