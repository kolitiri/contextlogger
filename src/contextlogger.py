from collections.abc import Callable
from contextvars import ContextVar
import logging
from typing import (
	Any,
	Dict,
	Optional,
	Tuple,
)

from exceptions import (
	CLoggerArgumentError,
	ClogVarArgumentError,
	ClogVarSetError,
)


class CLogVar():
	""" Class representing a context variable to be used by the CLogger. """

	def __init__(self, name: str, setter: Optional[Callable] = None):
		self.name = name
		self.setter = setter
		self.context_var = ContextVar(name, default=None)

	def set(self, value: Optional[Any] = None):
		"""	Sets the value of a CLogVar instance.

			Values can be passed directly into the function.
			If a setter callable has been provided on initialization
			and no value is passed, the setter callable will attempt
			to set the value of the context variable.

			Args:
				value: The new value of the CLogVar instance
		"""
		if value is None and self.setter is None:
			raise ClogVarSetError("Nothing to set")

		if value:
			self.context_var.set(value)

		elif self.setter:
			if not callable(self.setter):
				ClogVarSetError("Nothing to set")

			value = self.setter()
			self.context_var.set(value)

	def get(self) -> Any:
		""" Returns the current value of a CLogVar instance.

			Returns:
				value: The current value of the CLogVar instance.
		"""
		value = self.context_var.get()
		return value


class CLoggingAdapter(logging.LoggerAdapter):
	""" Custom logging adapter. """

	def process(self, msg: str, kwargs: dict) -> Tuple[str, dict]:
		""" Processes the message passed to the logger,
			as per logging.LoggerAdapter.

			Args:
				msg: The message passed to the logger
				kwargs: Extra keyword arguments

			Returns:
				message: The processed message
				kwargs: Extra keyword arguments
		"""
		clogvars = {
			clogvar_name: clogvar.get()
			for clogvar_name, clogvar in self.extra.items()
			if clogvar.get()
		}

		if clogvars:
			return f'{clogvars} {msg}', kwargs

		message = f'{msg}'

		return message, kwargs


class CLogger():
	""" Class representing a context logger. """
	def __init__(self, name: str , level: Optional[str] = 'INFO'):
		self.logger = logging.getLogger(name)
		self.clogger = CLoggingAdapter(self.logger, extra={})
		self.clogger.setLevel(level)
		self.cvars = {}

	@property
	def clogvars(self) -> Dict[str, CLogVar]:
		""" Returns the CLogVar instances of the current CLogger

			Return:
				cvars: A dictionary mapping names to CLogVar instances
		"""
		cvars = self.cvars
		return cvars

	@clogvars.setter
	def clogvars(self, cvars: Dict[str, CLogVar]):
		""" Sets a variable number of context variables to be used
			by the context logger.

			Args:
				cvars: Dictionary mapping names to CLogVar instances
		"""
		if not isinstance(cvars, list):
			raise CLoggerArgumentError(
				"Argument 'cvars' should be a list of CLogVar instances"
			)

		extra = {}
		for cvar in cvars:
			if not isinstance(cvar, CLogVar):
				raise CLoggerArgumentError(
					"Argument 'cvars' should be a list of CLogVar instances"
				)
			extra[cvar.name] = cvar

		self.cvars = extra
		self.clogger.extra = extra

	def getvar(self, name: str) -> CLogVar:
		""" Returns the value of a CLogVar by name. """
		return self.cvars.get(name)

	def setvar(self, name: str, value: Any = None):
		""" Sets the value of a CLogVar by name. """
		cvar = self.cvars.get(name)
		if cvar:
			self.cvars[name].set(value)

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


def getCLogger(name: str) -> CLogger:
	return CLogger(name)
