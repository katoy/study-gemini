import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
from ble_server.main import BLEGameServer, UART_TX_CHAR_UUID, UART_RX_CHAR_UUID


@pytest.fixture
def mock_adapter():
    with patch("ble_server.main.GameAdapter") as MockAdapter:
        yield MockAdapter.return_value


@pytest.fixture
def server(mock_adapter):
    return BLEGameServer()


@pytest.mark.asyncio
async def test_initialization(server, mock_adapter):
    assert server.client is None
    assert server.connected is False
    assert server.adapter == mock_adapter


@pytest.mark.asyncio
async def test_run_device_found_and_connect(server):
    """Test finding a device and connecting."""

    # Mock BleakScanner and BleakClient
    mock_device = MagicMock()
    mock_device.name = "BBC micro:bit [teguz]"
    mock_device.address = "AA:BB:CC:DD:EE:FF"

    mock_client = AsyncMock()
    # Context manager mock
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch(
        "ble_server.main.BleakScanner.find_device_by_filter", new_callable=AsyncMock
    ) as mock_find:
        with patch("ble_server.main.BleakClient", return_value=mock_client):
            # 1. First find -> returns device
            # 2. Second find (after disconnect) -> raises CancelledError to stop loop
            mock_find.side_effect = [mock_device, asyncio.CancelledError("Stop Loop")]

            async def sleep_side_effect(*args, **kwargs):
                # When sleeping inside the connection loop, disconnect to break the loop
                if server.connected:
                    server.connected = False
                    return
                # Other sleeps (e.g. retry delay) just return
                return

            with patch("asyncio.sleep", side_effect=sleep_side_effect):
                try:
                    await server.run()
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    raise e

            # Verify start_notify was called
            mock_client.start_notify.assert_called_with(
                UART_TX_CHAR_UUID, server.on_notification
            )


@pytest.mark.asyncio
async def test_run_connection_error(server):
    """Test handling of connection error."""
    with patch(
        "ble_server.main.BleakScanner.find_device_by_filter", new_callable=AsyncMock
    ) as mock_find:
        # First call raises Exception (simulating error), second raises CancelledError (to stop loop)
        mock_find.side_effect = [
            Exception("Connection Failed"),
            asyncio.CancelledError("Stop"),
        ]

        # Mock sleep to speed up test
        with patch("asyncio.sleep", new_callable=AsyncMock):
            try:
                await server.run()
            except asyncio.CancelledError:
                pass

            # Should have tried to find device
            assert mock_find.call_count == 2


@pytest.mark.asyncio
async def test_run_device_not_found(server):
    """Test logic when device is not found."""
    with patch(
        "ble_server.main.BleakScanner.find_device_by_filter", new_callable=AsyncMock
    ) as mock_find:
        # First return None (not found), then raise CancelledError
        mock_find.side_effect = [None, asyncio.CancelledError("Stop")]

        with patch("asyncio.sleep", new_callable=AsyncMock):
            try:
                await server.run()
            except asyncio.CancelledError:
                pass

            assert mock_find.call_count == 2


@pytest.mark.asyncio
async def test_on_notification(server, mock_adapter):
    # Mock adapter response
    mock_adapter.handle_command.return_value = "RESPONSE"

    server.client = AsyncMock()
    server.connected = True

    # Send data
    data = b"START:X"
    await server.on_notification(None, data)

    mock_adapter.handle_command.assert_called_with("START:X")
    server.client.write_gatt_char.assert_called_with(UART_RX_CHAR_UUID, b"RESPONSE\n")


@pytest.mark.asyncio
async def test_on_notification_game_over(server, mock_adapter):
    # Mock adapter returning tuple (Ongoing, Result)
    mock_adapter.handle_command.return_value = ("ONGOING_MSG", "RESULT_MSG")

    server.client = AsyncMock()
    server.connected = True

    await server.on_notification(None, b"MOVE:...")

    # Should fail data twice
    assert server.client.write_gatt_char.call_count == 2
    server.client.write_gatt_char.assert_any_call(UART_RX_CHAR_UUID, b"ONGOING_MSG\n")
    server.client.write_gatt_char.assert_any_call(UART_RX_CHAR_UUID, b"RESULT_MSG\n")


@pytest.mark.asyncio
async def test_send_update_not_connected(server):
    server.client = None
    server.connected = False

    # Should not raise
    await server.send_update("TEST")


def test_on_disconnect(server):
    server.connected = True
    server.on_disconnect(None)
    assert server.connected is False


@pytest.mark.asyncio
async def test_on_notification_empty(server, mock_adapter):
    """Test receiving empty string."""
    await server.on_notification(None, b"")
    mock_adapter.handle_command.assert_not_called()


@pytest.mark.asyncio
async def test_on_notification_decode_error(server, mock_adapter):
    """Test receiving invalid utf-8 bytes."""
    # This should trigger the generic exception handler in on_notification
    # data.decode("utf-8") will raise UnicodeDecodeError
    await server.on_notification(None, b"\xff")
    mock_adapter.handle_command.assert_not_called()


@pytest.mark.asyncio
async def test_send_update_error(server):
    """Test error during sending update."""
    server.client = AsyncMock()
    server.connected = True
    server.client.write_gatt_char.side_effect = Exception("Write Error")

    # Should not raise exception
    await server.send_update("TEST")
    server.client.write_gatt_char.assert_called_once()
