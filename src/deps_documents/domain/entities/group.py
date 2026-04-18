from dataclasses import dataclass


@dataclass
class GroupEntity:
    id: str
    name: str

    def asdict(self):
        return {
            "id": self.id,
            "name": self.name,
        }
