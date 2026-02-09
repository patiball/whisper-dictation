from runtime_contracts import (
    create_key_listener,
    create_runtime_app,
    validate_runtime_controller,
    validate_transcription_backend,
)


class DummyBackend:
    def transcribe(self, audio_data, language=None):
        return {"text": "ok", "language": language}


class InvalidBackend:
    pass


class DummyRuntime:
    def __init__(self, recorder, languages=None, max_time=None):
        self.started = False
        self.recorder = recorder
        self.languages = languages
        self.max_time = max_time

    def start_app(self, _):
        self.started = True

    def stop_app(self, _):
        self.started = False

    def toggle(self):
        self.started = not self.started

    def run(self):
        return None


class InvalidRuntime:
    def __init__(self, *_args, **_kwargs):
        self.started = False


class DummyGlobalListener:
    def __init__(self, app, key_combination):
        self.app = app
        self.key_combination = key_combination
        self.kind = "global"


class DummyDoubleCmdListener:
    def __init__(self, app):
        self.app = app
        self.kind = "double_cmd"


def test_validate_transcription_backend_accepts_backend_with_transcribe():
    backend = validate_transcription_backend(DummyBackend())
    assert backend.transcribe([], "en")["text"] == "ok"


def test_validate_transcription_backend_rejects_backend_without_transcribe():
    try:
        validate_transcription_backend(InvalidBackend())
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert "transcribe" in str(exc)


def test_validate_runtime_controller_accepts_valid_runtime():
    runtime = validate_runtime_controller(DummyRuntime(recorder=object()))
    runtime.start_app(None)
    assert runtime.started is True


def test_validate_runtime_controller_rejects_missing_methods():
    try:
        validate_runtime_controller(InvalidRuntime())
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert "start_app" in str(exc)


def test_create_runtime_app_selects_windows_runtime():
    app = create_runtime_app(
        system="Windows",
        recorder=object(),
        languages=["en"],
        max_time=10,
        status_bar_app_cls=InvalidRuntime,
        windows_tray_app_cls=DummyRuntime,
        headless_runtime_app_cls=InvalidRuntime,
    )
    assert isinstance(app, DummyRuntime)


def test_create_runtime_app_selects_headless_for_other_systems():
    app = create_runtime_app(
        system="Linux",
        recorder=object(),
        languages=None,
        max_time=None,
        status_bar_app_cls=InvalidRuntime,
        windows_tray_app_cls=InvalidRuntime,
        headless_runtime_app_cls=DummyRuntime,
    )
    assert isinstance(app, DummyRuntime)


def test_create_key_listener_uses_double_cmd_only_on_macos():
    app = DummyRuntime(recorder=object())
    mac_listener = create_key_listener(
        use_double_cmd=True,
        system="Darwin",
        app=app,
        key_combination="ctrl+alt",
        double_command_key_listener_cls=DummyDoubleCmdListener,
        global_key_listener_cls=DummyGlobalListener,
    )
    win_listener = create_key_listener(
        use_double_cmd=True,
        system="Windows",
        app=app,
        key_combination="ctrl+alt",
        double_command_key_listener_cls=DummyDoubleCmdListener,
        global_key_listener_cls=DummyGlobalListener,
    )
    assert mac_listener.kind == "double_cmd"
    assert win_listener.kind == "global"

