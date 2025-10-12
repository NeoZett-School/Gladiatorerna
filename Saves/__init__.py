from typing import List, Dict, Self, Optional
import datetime
import json
import os

__all__ = ("SaveHandler",)


class SaveHandler:
    """The save file handler lets you save and load any JSON file from and into basic Python dictionaries."""

    def __init__(self) -> Self:
        """Create a new local save file handler."""
        self.dir_path: str = os.path.dirname(os.path.abspath(__file__))
        self.metadata_path = os.path.join(self.dir_path, ".save_metadata.json")

        # Load metadata if it exists, otherwise initialize
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {"last_saves": {}}

    def save(self, data: Dict, file: str) -> None:
        """Save a dictionary as JSON to a file and record its last save time."""
        file_path = os.path.join(self.dir_path, file)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Update metadata with timestamp for this file
        self._metadata["last_saves"][file] = datetime.datetime.now().isoformat()
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, indent=4)

    def load(self, file: str) -> Dict:
        """Load a dictionary from a JSON file."""
        with open(os.path.join(self.dir_path, file), "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def last_save(self) -> Dict[str, Optional[str]]:
        """Return a dictionary of {filename: last_save_time} for saved files."""
        return self._metadata.get("last_saves", {})
    
    @property
    def last_save_file(self) -> Optional[str]:
        """Returns the last save time for only the most recently saved file."""
        if not self._metadata["last_saves"]:
            return None
        return max(self._metadata["last_saves"], key=self._metadata["last_saves"].get)

    @property
    def files(self) -> List[str]:
        """List all JSON files in the same directory as this script, excluding internal files."""
        return [
            f for f in os.listdir(self.dir_path)
            if (
                f.endswith(".json")
                and os.path.isfile(os.path.join(self.dir_path, f))
                and not f.startswith(".")  # exclude hidden
                and f.count(".") == 1      # exclude internal files (multiple dots)
            )
        ]
