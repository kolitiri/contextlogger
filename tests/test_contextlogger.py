import logging
from logging.handlers import TimedRotatingFileHandler
import os
import pytest

from contextlogger import (
    CLoggingAdapter,
    CLogVars,
    CLogVar,
    getCLogger,
)
import exceptions


class TestCLogger():

    def setup_class(self):
        self.clogger = getCLogger(__name__)

        logging_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
        formatter = logging.Formatter(logging_format)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.clogger.addHandler(console_handler)

    def test_clogvars_invalid(self):
        """ Asserts clogvars does not accept the wrong types """
        with pytest.raises(TypeError):
            self.clogger.clogvars = "Not a list of CLogVar instances"

        with pytest.raises(TypeError):
            self.clogger.clogvars = [
                "Not a CLogVar instance",
            ]

    def test_setvar(self):
        """ Asserts setvar works as expected """
        self.clogger.clogvars = CLogVars(
            static=CLogVar(name='static'),
        )

        self.clogger.setvar('static', value=1)

        assert self.clogger.getvar('static') == 1

    def test_getvar_unknown(self):
        """ Asserts getvars returns None when the context variable is not set """
        self.clogger.clogvars = CLogVars(
            static=CLogVar(name='static'),
        )

        self.clogger.setvar('static', value=1)

        assert self.clogger.getvar('UNKNOWN') == None


class TestCLogVar():

    def test_set_value(self):
        """ Asserts cvar values are set as expected """
        cvar = CLogVar(name='static')

        cvar.set()
        assert cvar.get() == None

        cvar.set(1)
        assert cvar.get() == 1

    def test_set_setter(self):
        """ Asserts scvar etter behaves as expected when it is a callable or not """
        cvar = CLogVar(name='request_id', setter=1)

        with pytest.raises(TypeError):
            cvar.set()

        cvar = CLogVar(name='request_id', setter=lambda: 1)
        cvar.set()
        assert cvar.get() == 1


class TestCLoggingAdapter():

    def setup_class(self):
        self.logger = logging.getLogger(__name__)

    def test_format_msg_structured(self):
        """ Asserts the adapter produces structured message """
        adapter = CLoggingAdapter(logger=self.logger, structured=True)

        clogvars = {
            'static': 1
        }

        msg = "A test message"
        msg = adapter._format_msg(msg, clogvars)

        assert msg == "'msg': 'A test message', 'static': '1'"

    def test_format_msg_not_structured(self):
        """ Asserts the adapter produces non-structured message """
        adapter = CLoggingAdapter(logger=self.logger, structured=False)

        clogvars = {
            'static': 1
        }

        msg = "A test message"
        msg = adapter._format_msg(msg, clogvars)

        assert msg == "{'static': 1} - A test message"
