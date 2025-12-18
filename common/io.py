import json
from pathlib import Path

class JsonLoader:
    
    def __init__(self, file_path: str):
        self.file_path=Path(file_path)
        self.data = None

    def load(self) -> bool:
        try:
            if not self.file_path.exists():
                raise FileNotFoundError("JSON No encontrado " + self.file_path)
        
            with open(self.file_path) as file:
                self.data = json.load(file)
        
            return True
        
        except Exception:      
        
            return False
    
    def get_data(self):
        if self.data is None:
            raise RuntimeError("JSON no cargado")
        return self.data