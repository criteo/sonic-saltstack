"""Unit tests for sonic hardware functions."""
import json

import pytest

from salt import exceptions

import _modules.criteo_sonic as EXEC_MOD


def _fan_output_201911(*_, **__):
    return (
        "  Drawer    LED        FAN    Speed    Direction    Presence    Status          Timestamp\n"
        "--------  -----  ---------  -------  -----------  ----------  --------  -----------------\n"
        " drawer1  green       fan1      22%       intake     Present        OK  20221216 10:32:20\n"
        " drawer1  green       fan2      25%       intake     Present        OK  20221216 10:32:20\n"
        " drawer2  green       fan3      21%       intake     Present        OK  20221216 10:32:20\n"
        " drawer2  green       fan4      25%       intake     Present        OK  20221216 10:32:20\n"
        " drawer3  green       fan5      22%       intake     Present        OK  20221216 10:32:20\n"
        " drawer3  green       fan6      25%       intake     Present        OK  20221216 10:32:20\n"
        " drawer4  green       fan7      21%       intake     Present        OK  20221216 10:32:20\n"
        " drawer4  green       fan8      25%       intake     Present        OK  20221216 10:32:20\n"
        "     N/A  green  psu1_fan1      59%          N/A     Present        OK  20221216 10:32:20\n"
        "     N/A  green  psu2_fan1      59%          N/A     Present        OK  20221216 10:32:20\n"
    )


def _fan_output_202205(*_, **__):
    return (
        "        FAN    Speed    Direction    Presence    Status          Timestamp\n"
        "-----------  -------  -----------  ----------  --------  -----------------\n"
        "       fan1      28%          N/A     Present        OK  20221216 10:32:40\n"
        "       fan2      34%          N/A     Present        OK  20221216 10:32:40\n"
        "       fan3      28%          N/A     Present        OK  20221216 10:32:40\n"
        "       fan4      33%          N/A     Present        OK  20221216 10:32:40\n"
        "       fan5      28%          N/A     Present        OK  20221216 10:32:40\n"
        "       fan6      33%          N/A     Present        OK  20221216 10:32:40\n"
        "       fan7      28%          N/A     Present        OK  20221216 10:32:40\n"
        "       fan8      33%          N/A     Present        OK  20221216 10:32:40\n"
        "psu_1_fan_1      56%          N/A     Present        OK  20221216 10:32:40\n"
        "psu_2_fan_1      56%          N/A     Present        OK  20221216 10:32:40\n"
    )


def _only_headers(*_, **__):
    return (
        "        FAN    Speed    Direction    Presence    Status          Timestamp\n"
        "-----------  -------  -----------  ----------  --------  -----------------\n"
    )


def _missing_headers(*_, **__):
    return (
        "  Speed    Direction    Presence          Timestamp\n"
        "-------  -----------  ----------  -----------------\n"
    )


def test_fan_status_201911():
    """Test FAN status for SONiC 201911."""
    EXEC_MOD.__salt__ = {"cmd.run": _fan_output_201911}

    res = EXEC_MOD.fan_status()
    del EXEC_MOD.__salt__

    assert res == {
        "fan1": True,
        "fan2": True,
        "fan3": True,
        "fan4": True,
        "fan5": True,
        "fan6": True,
        "fan7": True,
        "fan8": True,
        "psu1_fan1": True,
        "psu2_fan1": True,
    }


def test_fan_status_202205():
    """Test FAN status for SONiC 202205."""
    EXEC_MOD.__salt__ = {"cmd.run": _fan_output_202205}

    res = EXEC_MOD.fan_status()
    del EXEC_MOD.__salt__

    assert res == {
        "fan1": True,
        "fan2": True,
        "fan3": True,
        "fan4": True,
        "fan5": True,
        "fan6": True,
        "fan7": True,
        "fan8": True,
        "psu_1_fan_1": True,
        "psu_2_fan_1": True,
    }


def test_fan_status_empty():
    """Test FAN status for SONiC 202205."""

    def _empty(*_, **__):
        return ""

    EXEC_MOD.__salt__ = {"cmd.run": _empty}

    res = EXEC_MOD.fan_status()
    del EXEC_MOD.__salt__

    assert res is None


def test_fan_status_only_headers():
    """Test FAN status for SONiC 202205."""
    EXEC_MOD.__salt__ = {"cmd.run": _only_headers}

    res = EXEC_MOD.fan_status()
    del EXEC_MOD.__salt__

    assert res == {}


def test_fan_status_missing_headers():
    """Test FAN status for SONiC 202205."""
    EXEC_MOD.__salt__ = {"cmd.run": _missing_headers}

    res = EXEC_MOD.fan_status()
    del EXEC_MOD.__salt__

    assert res is None
