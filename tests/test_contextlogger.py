import logging
from logging.handlers import TimedRotatingFileHandler
import os
import pytest

import contextlogger
import exceptions


class TestCLogger():

    def setup_class(self):
        # Create a CLogger instance
        self.clogger = contextlogger.getCLogger(__name__)

        # Create a logging formatter
        logging_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
        formatter = logging.Formatter(logging_format)

        # Create handlers for console logger
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.clogger.addHandler(console_handler)

    def test_clogvars_invalid(self):
        """ Asserts clogvars is in the correct format """
        with pytest.raises(exceptions.CLoggerArgumentError):
            self.clogger.clogvars = "Not a list of CLogVar instances"

        with pytest.raises(exceptions.CLoggerArgumentError):
            self.clogger.clogvars = [
                "Not a CLogVar instance",
            ]

    def test_setvar(self):
        """ Asserts setvar works as expected """
        self.clogger.clogvars = [
            contextlogger.CLogVar(name='static'),
        ]

        self.clogger.setvar('static', value=1)

        assert self.clogger.getvar('static') == 1

    def test_getvar_unknown(self):
        """ Asserts getvars returns None when the context variable is not set """
        self.clogger.clogvars = [
            contextlogger.CLogVar(name='static'),
        ]

        self.clogger.setvar('static', value=1)

        assert self.clogger.getvar('UNKNOWN') == None


class TestCLogVar():

    def test_set_value(self):
        cvar = contextlogger.CLogVar(name='static')
        with pytest.raises(exceptions.ClogVarSetError):
            cvar.set()

        cvar.set(1)
        assert cvar.get() == 1

    def test_set_setter(self):
        cvar = contextlogger.CLogVar(name='request_id', setter=1)
        with pytest.raises(exceptions.ClogVarSetError):
            cvar.set()

        cvar = contextlogger.CLogVar(name='request_id', setter=lambda: 1)
        cvar.set()
        assert cvar.get() == 1
