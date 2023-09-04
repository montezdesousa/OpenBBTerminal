"""Test the system module."""
import asyncio
from unittest.mock import MagicMock, patch

from openbb_core.api.dependency.system import (
    SystemSettings,
    get_system_settings,
)


@patch("openbb_core.api.dependency.system.SystemService")
def test_get_system_settings(mock_system_service):
    """Test get_system_settings."""
    mock_system_settings = MagicMock(spec=SystemSettings)
    mock_system_service.return_value.system_settings = mock_system_settings

    system_settings = asyncio.run(get_system_settings())

    assert system_settings == mock_system_settings