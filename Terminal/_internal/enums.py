from typing import Optional, Literal, Union
from enum import Enum

class Mode(Enum):
    SINGLE = Literal["Single"]
    MULTIPLE = Literal["Multiple"]

    @classmethod
    def get(cls, item: Union["Mode", str]) -> Optional[Union["Mode", str]]:
        if not isinstance(item, (str, Mode)):
            return None
        if isinstance(item, Mode): 
            return item
        item = item.upper()
        return cls.__members__.get(item)

