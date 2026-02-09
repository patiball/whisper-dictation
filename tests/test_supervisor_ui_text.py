import importlib.util
import sys


def load_module():
    spec = importlib.util.spec_from_file_location(
        "whisper_dictation_supervisor_main",
        "whisper-dictation-supervisor.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["whisper_dictation_supervisor_main"] = module
    spec.loader.exec_module(module)
    return module


def test_shorten_menu_text_truncates_long_warning():
    module = load_module()
    long_text = (
        "Warning: OpenVINO artifacts missing for ggml-medium.bin; CPU fallback likely "
        "(missing: ggml-medium-encoder-openvino.xml, ggml-medium-encoder-openvino.bin)"
    )
    shortened = module.shorten_menu_text(long_text, max_len=80)
    assert len(shortened) <= 80
    assert shortened.endswith("...")


def test_shorten_menu_text_keeps_short_text():
    module = load_module()
    short_text = "Warning: none"
    assert module.shorten_menu_text(short_text, max_len=80) == short_text
