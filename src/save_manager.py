import json
from pathlib import Path

from .constants import SAVE_FILE


class SaveManager:
    def __init__(self, path=SAVE_FILE):
        self.path = Path(path)
        self.data = {
            "best_wave": 0,
            "top_scores": [],
            "settings": {"volume": 0, "fullscreen": False},
            "save": None,
        }
        self.load_meta()

    def load_meta(self):
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                pass

    def save_game(self, farm):
        self.data["save"] = farm.to_json()
        self.data["best_wave"] = max(self.data.get("best_wave", 0), farm.wave_manager.wave)
        self._add_score(farm.wave_manager.wave)
        self._write()

    def load_game(self):
        self.load_meta()
        return self.data.get("save")

    def record_score(self, wave):
        self.data["best_wave"] = max(self.data.get("best_wave", 0), wave)
        self._add_score(wave)
        self._write()

    def save_settings(self, settings):
        self.data["settings"] = settings
        self._write()

    def _write(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _add_score(self, wave):
        scores = self.data.setdefault("top_scores", [])
        scores.append({"wave": int(wave)})
        scores.sort(key=lambda item: item["wave"], reverse=True)
        self.data["top_scores"] = scores[:5]
