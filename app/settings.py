"""Public config.json; provider-isolated credentials in the Windows user environment."""
from __future__ import annotations

import ctypes
import json
import os
import sys
from pathlib import Path
from core.providers import (BIGMODEL_ENV, CUSTOM, DRAFT_PROVIDERS, JEV_ENV,
                            JEV_PROVIDERS, LEGACY, LLM_ENV)

_ROOT = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
_CONFIG = _ROOT / "config.json"


def _config() -> dict:
    try:
        value = json.loads(Path(_CONFIG).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def _read(name, default=None):
    value = _config().get(name)
    return default if value is None else value


def relationship():
    return str(_read("relationship") or "romantic partners")


def context():
    try:
        return max(3, min(30, int(_read("context", 10))))
    except (TypeError, ValueError):
        return 10


def style():
    return str(_read("style") or "")


def _provider(field, table, old_default):
    data = _config()
    value = data.get(field)
    fallback = old_default if data and "config_version" not in data else "zhipu"
    return value if value in table else fallback


def jev_provider():
    return _provider("jev_provider", JEV_PROVIDERS, "openrouter")


def draft_provider():
    return _provider("draft_provider", DRAFT_PROVIDERS, "deepseek")


def jev_model():
    return str(_read("jev_model") or JEV_PROVIDERS[jev_provider()].default)


def draft_model():
    return str(_read("draft_model") or DRAFT_PROVIDERS[draft_provider()].default)


def draft_provider_name():
    return DRAFT_PROVIDERS[draft_provider()].name


def draft_base_url():
    return str(_read("draft_base_url") or "") if draft_provider() in CUSTOM else ""


def reply_target():
    return bool(_read("reply_target", False))


def thinking():
    return bool(_read("thinking", False))


def check_update():
    return False  # Upstream releases must not replace the GLM fork.


def debug_view():
    return bool(_read("debug_view", False))


def _read_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                value = str(winreg.QueryValueEx(key, name)[0]).strip()
        except (OSError, ImportError):
            value = ""
        if value:
            os.environ[name] = value
    return value


def _get_key(name):
    return _read_env(name) or (_read_env(LEGACY[name]) if name in LEGACY else "")


def _set_key(name, value):
    import winreg
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
    os.environ[name] = value
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x1A, 0, "Environment", 2, 1000, None)


def key_for(kind, provider):
    if provider == "zhipu":
        return _get_key(BIGMODEL_ENV)
    saved = jev_provider() if kind == "jev" else draft_provider()
    if provider != saved:
        return ""
    return _get_key(JEV_ENV if kind == "jev" else LLM_ENV)


def jev_key():
    return key_for("jev", jev_provider())


def llm_key():
    return key_for("draft", draft_provider())


def has_jev_key():
    return bool(jev_key())


def has_llm_key():
    return bool(llm_key())


has_key = has_jev_key


def snapshot():
    return dict(relationship=relationship(), context=context(), style=style(),
                provider=draft_provider(), model=draft_model(), base_url=draft_base_url() or None,
                jev_provider=jev_provider(), jev_model=jev_model(), thinking=thinking(),
                judge_api_key=jev_key(), draft_api_key=llm_key())


def save(relationship_text=None, context_n=None, *, jev_provider_text=None,
         jev_key_text=None, jev_model_text=None, draft_provider_text=None,
         llm_key_text=None, draft_model_text=None, draft_base_url_text=None,
         reply_target_on=None, style_text=None, thinking_on=None,
         check_update_on=None, debug_view_on=None):
    jev = jev_provider_text if jev_provider_text in JEV_PROVIDERS else jev_provider()
    draft = draft_provider_text if draft_provider_text in DRAFT_PROVIDERS else draft_provider()
    if jev == draft == "zhipu" and jev_key_text and llm_key_text and jev_key_text != llm_key_text:
        raise ValueError("智谱只需填写一把密钥")
    old = _config()
    keep = lambda new, name: str(old.get(name) or "") if new is None else str(new).strip()
    flag = lambda new, current: current() if new is None else bool(new)
    data = dict(config_version=1, relationship=relationship_text or relationship(),
                context=context() if context_n is None else max(3, min(30, int(context_n))),
                style=keep(style_text, "style"), jev_provider=jev, draft_provider=draft,
                jev_model=keep(jev_model_text, "jev_model"),
                draft_model=keep(draft_model_text, "draft_model"),
                draft_base_url=keep(draft_base_url_text, "draft_base_url"),
                reply_target=flag(reply_target_on, reply_target),
                thinking=flag(thinking_on, thinking), check_update=False,
                debug_view=flag(debug_view_on, debug_view))
    for kind, provider, typed in (("jev", jev, jev_key_text), ("draft", draft, llm_key_text)):
        if typed and typed.strip():
            env = BIGMODEL_ENV if provider == "zhipu" else (JEV_ENV if kind == "jev" else LLM_ENV)
            _set_key(env, typed.strip())
    path = Path(_CONFIG)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)
