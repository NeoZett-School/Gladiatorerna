from typing import Optional
from .core import Terminal, ClearScreenArg

__all__ = ("Builder",)

class Builder:
    def __init__(self, value: str = "") -> None:
        self.value = value
    
    def __str__(self) -> str:
        return self.value
    
    def clear(self) -> None:
        self.value = ""
    
    def space(self) -> None:
        self.value += "\n"
    
    def print(
        self,
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        color: bool = False,
        clear_screen: bool = False,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        if clear_screen: self.clear()
        self.value += Terminal.format(*values, sep=sep, end=end, color=color, prefix=prefix, suffix=suffix)
    
    def render(
        self,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        flush: bool = False,
        color: bool = False,
        clear_screen: ClearScreenArg = False,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        Terminal.print(
            self, 
            sep=sep, 
            end=end, 
            flush=flush,
            color=color,
            clear_screen=clear_screen,
            prefix=prefix,
            suffix=suffix
        )