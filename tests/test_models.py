"""Tests for pyairobotrest models."""

import pytest

from pyairobotrest.models import ThermostatStatus


@pytest.mark.parametrize(
    "hw_raw,fw_raw,expected_hw,expected_fw",
    [
        (256, 262, "1.0", "1.6"),
        (267, 257, "1.11", "1.1"),
        (512, 768, "2.0", "3.0"),
        (0, 1, "0.0", "0.1"),
        (255, 511, "0.255", "1.255"),
    ],
)
def test_version_decoding(hw_raw, fw_raw, expected_hw, expected_fw):
    """Test various version decoding patterns."""
    data = {
        "DEVICE_ID": "T01TEST123",
        "HW_VERSION": hw_raw,
        "FW_VERSION": fw_raw,
        "TEMP_AIR": 220,
        "HUM_AIR": 400,
        "TEMP_FLOOR": 32767,
        "CO2": 65535,
        "DEVICE_UPTIME": 124,
        "HEATING_UPTIME": 117,
        "ERRORS": 0,
        "SETPOINT_TEMP": 245,
        "STATUS_FLAGS": [{"WINDOW_OPEN_DETECTED": 0, "HEATING_ON": 0}],
    }

    status = ThermostatStatus.from_dict(data)

    assert status.hw_version == hw_raw
    assert status.fw_version == fw_raw
    assert status.hw_version_string == expected_hw
    assert status.fw_version_string == expected_fw
