from modules.epidemiological_surveillance.interfaces.scheduler import (
    build_ingestion_command,
    parse_years,
    run_scheduler_loop,
)


class _SettingsStub:
    ingestion_interval_hours = 1
    ingestion_default_years = "2018,2019,2020"
    ingestion_default_limit = 15000
    ingestion_validate_territorial_codes = True


def test_parse_years_splits_comma_separated_values() -> None:
    assert parse_years("2018, 2019,2020") == (2018, 2019, 2020)


def test_build_ingestion_command_uses_default_years() -> None:
    command = build_ingestion_command(_SettingsStub())
    assert command.years == (2018, 2019, 2020)
    assert command.limit == 15000
    assert command.validate_territorial_codes is True


def test_run_scheduler_loop_exits_after_shutdown(monkeypatch) -> None:
    import modules.epidemiological_surveillance.interfaces.scheduler as scheduler_module

    calls: list[str] = []

    def fake_run_once(_settings) -> None:
        calls.append("run")
        scheduler_module._shutdown_requested = True

    monkeypatch.setattr(scheduler_module, "_shutdown_requested", False)
    exit_code = run_scheduler_loop(
        _SettingsStub(),
        sleep_fn=lambda _seconds: None,
        run_once_fn=fake_run_once,
    )

    assert exit_code == 0
    assert calls == ["run"]
