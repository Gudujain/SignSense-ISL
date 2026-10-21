"""
SignSense Curriculum Manager
Loads and queries structured ISL curriculum metadata.
"""
import os
import json
from typing import Dict, List, Optional, Any

CURRICULUM_FILE = os.path.join(os.path.dirname(__file__), "curriculum_data.json")

class CurriculumManager:
    def __init__(self, data_path: str = CURRICULUM_FILE):
        self.data_path = data_path
        self._data: Dict[str, Any] = {}
        self._signs_by_id: Dict[str, Dict[str, Any]] = {}
        self._signs_by_label: Dict[str, Dict[str, Any]] = {}
        self._signs_by_model_index: Dict[int, Dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Curriculum data file not found: {self.data_path}")
        with open(self.data_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

        self._signs_by_id.clear()
        self._signs_by_label.clear()
        self._signs_by_model_index.clear()

        for sign in self._data.get("signs", []):
            self._signs_by_id[sign["id"]] = sign
            self._signs_by_label[sign["label"]] = sign
            if "model_class_index" in sign:
                self._signs_by_model_index[sign["model_class_index"]] = sign

    def get_all_signs(self) -> List[Dict[str, Any]]:
        return self._data.get("signs", [])

    def get_stages(self) -> List[Dict[str, Any]]:
        return self._data.get("stages", [])

    def get_sign_by_id(self, sign_id: str) -> Optional[Dict[str, Any]]:
        return self._signs_by_id.get(sign_id)

    def get_sign_by_label(self, label: str) -> Optional[Dict[str, Any]]:
        return self._signs_by_label.get(label)

    def get_sign_by_model_index(self, index: int) -> Optional[Dict[str, Any]]:
        return self._signs_by_model_index.get(index)

    def get_signs_by_stage(self, stage_id: int) -> List[Dict[str, Any]]:
        return [s for s in self.get_all_signs() if s.get("stage") == stage_id]

    def get_signs_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [s for s in self.get_all_signs() if s.get("category", "").lower() == category.lower()]

    def get_summary(self) -> Dict[str, Any]:
        return {
            "name": self._data.get("name"),
            "version": self._data.get("version"),
            "total_signs": len(self.get_all_signs()),
            "total_stages": len(self.get_stages()),
            "provenance": self._data.get("provenance_notes")
        }

# Global singleton
curriculum = CurriculumManager()
