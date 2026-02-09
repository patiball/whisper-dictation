from __future__ import annotations

from pathlib import Path

import pytest

from supervisor_worker import (
    SupervisorSettings,
    WorkerProcessSupervisor,
    WorkerProfile,
    build_worker_command,
    resolve_cpp_model_path,
)


class FakeProcess:
    _next_pid = 2000

    def __init__(self, command, **kwargs):
        self.command = command
        self.kwargs = kwargs
        self.returncode = None
        self.pid = FakeProcess._next_pid
        FakeProcess._next_pid += 1
        self.terminated = False
        self.killed = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = 0

    def wait(self, timeout=None):
        if self.returncode is None:
            self.returncode = 0
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9


class FakePopenFactory:
    def __init__(self):
        self.calls = []
        self.processes = []

    def __call__(self, command, **kwargs):
        process = FakeProcess(command, **kwargs)
        self.calls.append((command, kwargs))
        self.processes.append(process)
        return process


def test_build_worker_command_python_profile():
    settings = SupervisorSettings(
        python_executable="python",
        worker_script="whisper-dictation.py",
        runtime_mode="headless",
        key_combination="ctrl_l+alt_l",
    )
    profile = WorkerProfile(name="python-medium", backend="python", model="medium")
    command = build_worker_command(profile, settings)
    assert command[:2] == ["python", "whisper-dictation.py"]
    assert "--runtime-mode" in command
    assert "headless" in command
    assert ["-m", "medium"] == command[-2:]


def test_build_worker_command_whispercpp_profile():
    settings = SupervisorSettings(
        python_executable="python",
        worker_script="whisper-dictation.py",
        runtime_mode="headless",
        key_combination="ctrl_l+alt_l",
        whispercpp_cli="C:/bin/whisper-cli.exe",
        fallback_backend="python",
    )
    profile = WorkerProfile(
        name="cpp-base",
        backend="whispercpp",
        model="C:/models/ggml-base.bin",
    )
    command = build_worker_command(profile, settings)
    assert "--whispercpp-cli" in command
    assert "C:/bin/whisper-cli.exe" in command
    assert "--whispercpp-model" in command
    assert "C:/models/ggml-base.bin" in command
    assert "--fallback-backend" in command


def test_supervisor_start_stop_and_switch_profile(tmp_path):
    popen_factory = FakePopenFactory()
    settings = SupervisorSettings(
        python_executable="python",
        worker_script="whisper-dictation.py",
        worker_log_file=str(tmp_path / "worker.log"),
        runtime_mode="headless",
    )
    supervisor = WorkerProcessSupervisor(
        settings=settings,
        initial_profile=WorkerProfile("python-base", "python", "base"),
        popen_factory=popen_factory,
        sleep_fn=lambda _seconds: None,
    )

    assert supervisor.start_worker() is True
    assert supervisor.start_worker() is False
    assert supervisor.status_snapshot().running is True

    supervisor.switch_profile(WorkerProfile("python-medium", "python", "medium"))
    assert len(popen_factory.calls) == 2
    assert popen_factory.calls[1][0][-2:] == ["-m", "medium"]

    assert supervisor.stop_worker() is True
    assert supervisor.status_snapshot().running is False
    assert popen_factory.processes[-1].terminated is True
    supervisor.shutdown()


def test_supervisor_bounded_auto_restart(tmp_path):
    popen_factory = FakePopenFactory()
    sleeps: list[float] = []
    settings = SupervisorSettings(
        python_executable="python",
        worker_script="whisper-dictation.py",
        worker_log_file=str(tmp_path / "worker.log"),
        runtime_mode="headless",
    )
    supervisor = WorkerProcessSupervisor(
        settings=settings,
        initial_profile=WorkerProfile("python-base", "python", "base"),
        max_restart_attempts=1,
        restart_backoff_sec=0.25,
        popen_factory=popen_factory,
        sleep_fn=lambda seconds: sleeps.append(seconds),
    )

    supervisor.start_worker()
    first_process = popen_factory.processes[0]
    first_process.returncode = 1
    restarted = supervisor.check_worker_health()
    assert restarted is True
    assert len(popen_factory.calls) == 2
    assert sleeps == [0.25]

    second_process = popen_factory.processes[1]
    second_process.returncode = 1
    restarted_again = supervisor.check_worker_health()
    assert restarted_again is False
    assert len(popen_factory.calls) == 2
    assert supervisor.status_snapshot().restart_attempts == 1
    supervisor.shutdown()


def test_supervisor_preflight_warns_when_openvino_encoder_artifacts_missing(tmp_path):
    popen_factory = FakePopenFactory()
    model_path = tmp_path / "ggml-medium.bin"
    model_path.write_text("stub", encoding="utf-8")
    settings = SupervisorSettings(
        python_executable="python",
        worker_script="whisper-dictation.py",
        worker_log_file=str(tmp_path / "worker.log"),
        runtime_mode="headless",
        whispercpp_cli="C:/bin/whisper-cli.exe",
    )
    supervisor = WorkerProcessSupervisor(
        settings=settings,
        initial_profile=WorkerProfile("cpp-medium", "whispercpp", str(model_path)),
        popen_factory=popen_factory,
        sleep_fn=lambda _seconds: None,
    )

    supervisor.start_worker()
    status = supervisor.status_snapshot()
    assert status.acceleration == "pending"
    assert status.warning is not None
    assert "OpenVINO encoder artifacts missing" in status.warning
    supervisor.shutdown()


def test_supervisor_updates_warning_from_worker_status_line(tmp_path):
    popen_factory = FakePopenFactory()
    model_path = tmp_path / "ggml-medium.bin"
    model_path.write_text("stub", encoding="utf-8")
    settings = SupervisorSettings(
        python_executable="python",
        worker_script="whisper-dictation.py",
        worker_log_file=str(tmp_path / "worker.log"),
        runtime_mode="headless",
        whispercpp_cli="C:/bin/whisper-cli.exe",
    )
    supervisor = WorkerProcessSupervisor(
        settings=settings,
        initial_profile=WorkerProfile("cpp-medium", "whispercpp", str(model_path)),
        popen_factory=popen_factory,
        sleep_fn=lambda _seconds: None,
    )
    supervisor.start_worker()

    worker_log = Path(settings.worker_log_file)
    with worker_log.open("a", encoding="utf-8") as handle:
        handle.write(
            "WHISPERCPP_STATUS expected_model=ggml-medium.bin "
            "loaded_model=ggml-medium.bin model_match=true "
            "acceleration=cpu_fallback reason=openvino_encoder_init_failed\n"
        )
        handle.flush()
    supervisor._consume_worker_status_events()
    status = supervisor.status_snapshot()
    assert status.acceleration == "cpu_fallback"
    assert status.warning is not None
    assert "CPU fallback" in status.warning

    with worker_log.open("a", encoding="utf-8") as handle:
        handle.write(
            "WHISPERCPP_STATUS expected_model=ggml-medium.bin "
            "loaded_model=ggml-medium.bin model_match=true "
            "acceleration=gpu_openvino reason=openvino_encoder_loaded\n"
        )
        handle.flush()
    supervisor._consume_worker_status_events()
    status2 = supervisor.status_snapshot()
    assert status2.acceleration == "gpu_openvino"
    assert status2.warning is None
    supervisor.shutdown()


def test_resolve_cpp_model_path_alias(tmp_path):
    model_path = tmp_path / "ggml-large-v3.bin"
    model_path.write_text("stub", encoding="utf-8")
    resolved = resolve_cpp_model_path("large-v3", models_dir=tmp_path)
    assert Path(resolved) == model_path.resolve()


def test_resolve_cpp_model_path_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_cpp_model_path("large-v3", models_dir=tmp_path)
