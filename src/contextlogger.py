from collections import UserDict
from collections.abc import Callable
from contextvars import ContextVar
import logging
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from exceptions import CLogVarError


class CLogVar():
    """ Class representing a context variable to be used by the CLogger. """
    def __init__(self, name: str, setter: Optional[Callable] = None):
        self.name = name
        self.setter = setter
        self.context_var = ContextVar(name, default=None)

    def set(self, value: Optional[Any] = None):
        """ Sets the value of a CLogVar instance.

            Values can be passed directly into the function.
            If a setter callable has been provided on initialization
            and no value is passed, the setter callable will attempt
            to set the value of the context variable.
        """
        if value:
            self.context_var.set(value)
            return value

        if self.setter:
            if not callable(self.setter):
                _type = self.setter.__class__.__name__
                raise TypeError(f"Setter should be a callable, not {_type}")

            value = self.setter()
            self.context_var.set(value)
            return value

    def get(self) -> Any:
        """ Returns the current value of a CLogVar instance """
        value = self.context_var.get()
        return value


class CLogVars(UserDict):
    """ A custom UserDict container that adds some basic validation """
    def __setitem__(self, index, val):
        if not isinstance(val, CLogVar):
            _type = val.__class__.__name__
            raise TypeError(
                f"Items should be CLogVar instances, not {_type}"
            )
        super().__setitem__(index, val)


class CLoggingAdapter(logging.LoggerAdapter):
    """ Custom logging adapter. """
    def __init__(self, logger: logging.Logger, structured: Optional[bool] = False):
        self.structured = structured
        super().__init__(logger, extra={})

    def process(self, msg: str, kwargs: dict) -> Tuple[str, dict]:
        """ Processes the message passed to the logger, as per logging.LoggerAdapter """
        clogvars = {
            clogvar_name: clogvar.get()
            for clogvar_name, clogvar in self.extra.items()
            if clogvar.get()
        }

        message = self._format_msg(msg, clogvars)

        return message, kwargs

    def _format_msg(self, msg: str, clogvars: Dict[str, CLogVar]) -> str:
        """ Formats the message accordingly. """
        if self.structured:
            msg = f"'msg': '{msg}'"
            for var_name, var_val in clogvars.items():
                msg += f", '{var_name}': '{var_val}'"
        else:
            if clogvars:
                msg = f"{clogvars} - {msg}"

        return msg


class CLogger():
    """ Class representing a context logger """
    def __init__(self, name: str , level: Optional[str] = 'INFO', structured: Optional[bool] = False):
        self.logger = logging.getLogger(name)
        self.clogger = CLoggingAdapter(logger=self.logger, structured=structured)
        self.clogger.setLevel(level)
        self._clogvars = CLogVars()

    @property
    def clogvars(self) -> CLogVars:
        return self._clogvars

    @clogvars.setter
    def clogvars(self, cvars: CLogVars):
        if not isinstance(cvars, CLogVars):
            _type = cvars.__class__.__name__
            raise TypeError(
                f"Value should be a CLogVars instance, not {_type}"
            )
        self._clogvars = cvars
        self.clogger.extra = cvars.data

    def getvar(self, name: str) -> CLogVar:
        """ Returns the value of a CLogVar by name. """
        cvar = self.clogvars.get(name)
        if cvar:
            return cvar.get()

    def setvar(self, name: str, value: Any = None):
        """ Sets the value of a CLogVar by name. """
        cvar = self.clogvars.get(name)
        if cvar:
            self.clogvars[name].set(value)

    def addHandler(self, *args, **kwargs):
        self.logger.addHandler(*args, **kwargs)

    def setLevel(self, level: str):
        self.clogger.setLevel(level)

    def info(self, *args, **kwargs):
        self.clogger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.clogger.warning(*args, **kwargs)

    def debug(self, *args, **kwargs):
        self.clogger.debug(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.clogger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs):
        self.clogger.exception(*args, **kwargs)


def getCLogger(name: str, level: Optional[str] = 'INFO', structured: Optional[bool] = False) -> CLogger:
    return CLogger(name, level=level, structured=structured)
