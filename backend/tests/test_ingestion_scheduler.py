from modules.epidemiological_surveillance.interfaces.scheduler import run_scheduler_loop


class _SettingsStub:
    ingestion_interval_hours = 1
    ingestion_batch_size = 1000
    ingestion_end_year = 2018
    ingestion_validate_territorial_codes = True


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
