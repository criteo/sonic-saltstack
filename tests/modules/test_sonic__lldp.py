"""Unit tests for sonic lldp functions."""
from tests.modules.resources import wanted_results

from _modules.sonic import lldp
from _utils.naming import normalize_plural

RES_DIR = "tests/modules/resources"


def _call_normalize(command, *args, **kwargs):  # pylint: disable=W0613
    return normalize_plural(*args)


def test_lldp__empty_response(mocker):
    """Test LLDP when there is no answer at all (buggy response)."""
    mocker.patch("_modules.sonic._get_lldp", return_value="")
    assert not lldp()


def test_lldp__interface_not_found(mocker):
    """Test LLDP when did not found the interface / did not find any LLDP info."""
    mocker.patch("_modules.sonic._get_lldp", return_value='{"lldp": {}}')
    assert not lldp()


# neighbor is a router


def test_lldp__one_interface_native_output__router(mocker):
    """Test LLDP for one interface with a linux output."""
    with open(f"{RES_DIR}/lldp_one_interface.json") as resource:
        fake_lldp = resource.read()

    mocker.patch("_modules.sonic._get_lldp", return_value=fake_lldp)

    assert lldp("Ethernet0") == wanted_results.native_one_interface


def test_lldp__one_interface_napalm_output__router(mocker):
    """Test LLDP for one interface with a napalm output."""
    with open(f"{RES_DIR}/lldp_one_interface.json") as resource:
        fake_lldp = resource.read()

    mocker.patch("_modules.sonic._utils_call", side_effect=_call_normalize)
    mocker.patch("_modules.sonic._get_lldp", return_value=fake_lldp)
    assert lldp("Ethernet0", napalm_output=True) == wanted_results.napalm_one_interface


def test_lldp__interfaces_native_output__router(mocker):
    """Test LLDP for multiple interfaces with a native output."""
    with open(f"{RES_DIR}/lldp_interfaces.json") as resource:
        fake_lldp = resource.read()
    mocker.patch("_modules.sonic._get_lldp", return_value=fake_lldp)

    assert lldp(napalm_output=False) == wanted_results.native_interfaces


def test_lldp__interfaces_napalm_output__router(mocker):
    """Test LLDP for multiple interfaces with a napalm output."""
    with open(f"{RES_DIR}/lldp_interfaces.json") as resource:
        fake_lldp = resource.read()
    mocker.patch("_modules.sonic._utils_call", side_effect=_call_normalize)
    mocker.patch("_modules.sonic._get_lldp", return_value=fake_lldp)
    assert lldp(napalm_output=True) == wanted_results.napalm_interfaces


# neighbor is a server


def test_lldp__interface_native_output__configured_server(mocker):
    """Test LLDP for one interface with a linux output."""
    with open(f"{RES_DIR}/lldp_server_configured.json") as resource:
        fake_lldp = resource.read()
    mocker.patch("_modules.sonic._get_lldp", return_value=fake_lldp)

    assert lldp("Ethernet16") == wanted_results.native_configured_server


def test_lldp__one_interface_napalm_output__configured_server(mocker):
    """Test LLDP for one interface with a napalm output."""
    with open(f"{RES_DIR}/lldp_server_configured.json") as resource:
        fake_lldp = resource.read()
    mocker.patch("_modules.sonic._utils_call", side_effect=_call_normalize)
    mocker.patch("_modules.sonic._get_lldp", return_value=fake_lldp)

    assert lldp("Ethernet16", napalm_output=True) == wanted_results.napalm_configured_server


def test_lldp__interfaces_native_output__unconfigured_server(mocker):
    """Test LLDP for multiple interfaces with a native output."""
    with open(f"{RES_DIR}/lldp_server_unconfigured.json") as resource:
        fake_lldp = resource.read()
    mocker.patch("_modules.sonic._get_lldp", return_value=fake_lldp)

    assert lldp("Ethernet96", napalm_output=False) == wanted_results.native_unconfigured_server


def test_lldp__interfaces_napalm_output__unconfigured_server(mocker):
    """Test LLDP for multiple interfaces with a napalm output."""
    with open(f"{RES_DIR}/lldp_server_unconfigured.json") as resource:
        fake_lldp = resource.read()
    mocker.patch("_modules.sonic._utils_call", side_effect=_call_normalize)
    mocker.patch("_modules.sonic._get_lldp", return_value=fake_lldp)

    assert lldp("Ethernet96", napalm_output=True) == wanted_results.napalm_unconfigured_server
