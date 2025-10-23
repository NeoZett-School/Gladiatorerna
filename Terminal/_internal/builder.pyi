from typing import Optional
from .core import ClearScreenArg

class Builder:
    """Use the builder to build your page before you print it."""
    
    value: str

    def __init__(self, value: str = "") -> None:
        ...
    
    def __str__(self) -> str:
        ...
    
    def clear(self) -> None:
        """Simply clears the screen. No ansi, no complexity. Simple and disconnected."""
        ...
    
    def space(self) -> None:
        """Simply print a space in the terminal."""
        ...
    
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
        """
        Print values to the terminal with optional formatting.

        Supports:
        - Color tags (like $red)
        - Prefix/suffix
        - Screen clearing
        """
        ...
    
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
        """Render this to the terminal."""
        ...