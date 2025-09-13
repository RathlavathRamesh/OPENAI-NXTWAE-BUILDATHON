from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path
import os

HERE = Path(__file__).resolve()
# If file is <repo>/ai_core/environment.py, then parents[1] is the repo root.
REPO_ROOT = HERE.parents[1]

CANDIDATES = [
    REPO_ROOT / "local_config.ini",
    REPO_ROOT / "config.ini",
    Path.cwd() / "local_config.ini",
    Path.cwd() / "config.ini",
]

config = ConfigParser()
loaded_path = None
for p in CANDIDATES:
    if p.is_file():
        config.read(p.as_posix(), encoding="utf-8")
        loaded_path = p
        break

def _get_cfg(section: str, option: str, env_var: str, default: str | None = None) -> str:
    # ENV wins; then INI; else default or raise.
    val = os.getenv(env_var)
    if val:
        return val
    try:
        return config.get(section, option)
    except (NoSectionError, NoOptionError):
        if default is not None:
            return default
        raise

class Config:
    WEATHER_API_KEY = _get_cfg("KEYS", "WEATHER_API_KEY", "WEATHER_API_KEY", default="")

# Optional visibility in Streamlit logs
if loaded_path:
    print(f"[env] Loaded config: {loaded_path}")
else:
    print("[env] No config file found; relying on environment variables")
