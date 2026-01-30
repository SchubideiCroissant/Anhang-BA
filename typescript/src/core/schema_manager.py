import json
import shutil 
from pathlib import Path

class SchemaManager:
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)

    def _schema_dir(self, name: str) -> Path:
        return self.base_path / name

    def _schema_file(self, name: str, variant: str) -> Path:
        return self._schema_dir(name) / f"{variant}.json"

    def list_schemas(self) -> list[str]:
        return [
            p.name for p in self.base_path.iterdir()
            if p.is_dir()
        ]

    def list_variants(self, name: str) -> list[str]:
        schema_dir = self._schema_dir(name)
        if not schema_dir.exists():
            return []

        return [
            p.stem for p in schema_dir.glob("*.json")
        ]

    def load(self, name: str, variant: str) -> dict:
        path = self._schema_file(name, variant)
        if not path.exists():
            raise FileNotFoundError(path)

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, name: str, variant: str, data: dict):
        path = self._schema_file(name, variant)
        try:
            path.parent.mkdir(parents=True, exist_ok=True) # Erstellt Directory

            self.validate(data)
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return f"{name}/{variant} gespeichert"
        except Exception as e:
            return f"Fehler beim Speichern des Schemas: {str(e)}"


    def delete_variant(self, name: str, variant: str):
        path = Path(self.base_path) / name / f"{variant}.json"
        if not path.exists() or not path.is_file():
            raise ValueError(
                f"Variante '{variant}' in Schema '{name}' existiert nicht"
            )

        path.unlink()
        return f"Variante '{variant}' gelöscht"

    def delete_schema(self, name: str):
        schema_dir = self._schema_dir(name)
        if not schema_dir.exists():
            raise ValueError(f"Schema '{name}' existiert nicht")
    
        shutil.rmtree(schema_dir)
        return f"Schema '{name}' und alle Varianten gelöscht"


    def validate(self, data: dict):
        if "name" not in data:
            raise ValueError("Schema hat kein 'name'-Feld")

        if "aliases" not in data:
            raise ValueError("Schema hat kein 'aliases'-Feld")

        if not isinstance(data["aliases"], list):
            raise ValueError("'aliases' muss eine Liste sein")

"""
if __name__ == "__main__":
    s = SchemaManager("test")
    print(s.base_path)

    user_data = {
    "name": "YY",
    "aliases": ["OU","IP"]
}

    s.save("YZ", "Motor", user_data)
    
"""