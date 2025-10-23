"""
The Terminal provides all features you will ever need when building your CLI applications.
"""

from typing import Optional, Literal, Union
from ._internal import Builder, FileSystem, Terminal, Mode
from ._internal.core import History, Manager, ClearScreenArg
from .tools.sync_stubs import sync_docs
from pathlib import Path
import sys

sync_docs(Path("Terminal/_internal/core.pyi"), Path("Terminal/__init__.pyi"))

__all__ = (
    "Module.terminal_init",
    "Module.terminal_deinit",
    "Module.Mode",
    "Module.Terminal",
    "Module.Simple",
    "Module.History",
    "Module.manager",
    "Module.print",
    "Module.input",
    "Module.space",
    "Module.clear",
    "Module.lookup",
    "Module.log",
    "Module.new_env",
    "Module.set_env_mode",
    "Module.build_progress_bar", 
    "Module.IOString",
    "Module.AnimatedString",
    "Module.ProgressBar",
)

class Module:
    @staticmethod
    def terminal_init() -> None:
        Terminal.init()

    @staticmethod
    def terminal_deinit() -> None:
        Terminal.deinit()
    
    @staticmethod
    def print(
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        flush: bool = False,
        color: bool = False,
        clear_screen: ClearScreenArg = False,
        prefix: str = "",
        suffix: str = "",
    ) -> None: 
        Terminal.print(
            *values, 
            sep=sep, 
            end=end, 
            flush=flush, 
            color=color, 
            clear_screen=clear_screen, 
            prefix=prefix,
            suffix=suffix
        )
    
    @staticmethod
    def input(
        *prompt: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "",
        flush: bool = False,
        color: bool = False,
        clear_screen: ClearScreenArg = False,
        input_text: Optional[str] = "",
        n: int = -1
    ) -> str:
        Terminal.input(
            *prompt, 
            sep=sep, 
            end=end, 
            flush=flush, 
            color=color, 
            clear_screen=clear_screen, 
            input_text=input_text, 
            n=n
        )
    
    def space() -> None:
        Terminal.space()
    
    @staticmethod
    def clear(*, ansi: bool = False, flush: bool = True) -> None:
        Terminal.clear(ansi=ansi,flush=flush)
    
    @staticmethod
    def lookup(tag: str) -> Optional[Terminal.Color]:
        return Terminal.lookup(tag)
    
    @staticmethod
    def log(level: Literal["INFO", "WARN", "ERROR"], *msg: object, color: bool = True) -> None:
        Terminal.log(level, *msg, color=color)
    
    @staticmethod
    def new_env(prefix: Optional[Terminal.Color] = None, suffix: Optional[Terminal.Color] = None) -> Manager.Environment:
        return Terminal.new_env(prefix, suffix)
    
    @staticmethod
    def set_env_mode(mode: Union[Mode, str] = Mode.SINGLE) -> None:
        Terminal.set_env_mode(mode)
    
    @staticmethod
    def progress_bar(
        formatted_string: str = "[had]|[need]|[prog]%",
        token: str = "-", length: int = 10,
        has: float = 0, need: float = 10,
        end: Optional[str] = "", color: bool = True
    ) -> str:
        return Terminal.progress_bar(
            formatted_string, 
            token, length,
            has, need, 
            end, color 
        )

    Mode = Mode
    Terminal = Terminal
    Simple = Terminal.Simple
    History = History
    Builder = Builder
    FileSystem = FileSystem
    manager = Terminal.manager

    IOString = Terminal.IOString
    AnimatedString = Terminal.AnimatedString
    ProgressBar = Terminal.ProgressBar

    terminal_init()

sys.modules[__name__] = Module