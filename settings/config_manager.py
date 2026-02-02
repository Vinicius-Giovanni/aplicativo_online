import json
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.path = Path("app/config/settings.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self._default()

    def _default(self):
        self.save({
            "rotas": []
        })
    
    def load(self) -> dict:
        with open(self.path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def save(self, data: dict):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
    def get_rotas(self) -> list[str]:
        return self.load().get("rotas", [])
    
    def set_rotas(self, rotas: list[str]):
        data = self.load()
        data['rotas'] = rotas