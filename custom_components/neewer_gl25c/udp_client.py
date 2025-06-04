"""UDP client for Neewer GL25C light communication."""
import asyncio
import logging
import socket
import struct
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class NeewerUDPClient:
    """UDP client for controlling Neewer GL25C lights."""
    
    def __init__(self, host: str, port: int = 5052):
        """Initialize the UDP client."""
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._connected = False
        
    async def connect(self) -> bool:
        """Connect to the light and send handshake."""
        try:
            # Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setblocking(False)
            
            # Send handshake
            # Format: 80 02 10 00 00 0d [IP_ADDRESS_IN_HEX] 2e
            ip_parts = self.host.split('.')
            ip_hex = ''.join([f'{int(part):02x}' for part in ip_parts])
            handshake = f"80021000000d{ip_hex}2e"
            
            await self._send_raw(handshake)
            self._connected = True
            
            # Start heartbeat
            await self.start_heartbeat()
            
            _LOGGER.info(f"Connected to Neewer GL25C at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Failed to connect to Neewer GL25C: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the light."""
        await self.stop_heartbeat()
        
        if self.sock:
            self.sock.close()
            self.sock = None
            
        self._connected = False
        _LOGGER.info("Disconnected from Neewer GL25C")
    
    async def send_command(self, command_hex: str) -> bool:
        """Send a command to the light."""
        if not self._connected:
            _LOGGER.warning("Not connected to light")
            return False
            
        try:
            await self._send_raw(command_hex)
            return True
        except Exception as e:
            _LOGGER.error(f"Failed to send command: {e}")
            return False
    
    async def _send_raw(self, hex_data: str):
        """Send raw hex data to the light."""
        if not self.sock:
            raise RuntimeError("Socket not initialized")
            
        data = bytes.fromhex(hex_data)
        loop = asyncio.get_event_loop()
        await loop.sock_sendto(self.sock, data, (self.host, self.port))
        _LOGGER.debug(f"Sent: {hex_data}")
    
    async def start_heartbeat(self):
        """Start sending heartbeat to keep connection alive."""
        async def heartbeat_loop():
            while self._connected:
                try:
                    # Send power query command as heartbeat
                    await self._send_raw("8004020106")
                    await asyncio.sleep(0.2)  # 200ms interval
                except Exception as e:
                    _LOGGER.error(f"Heartbeat failed: {e}")
                    break
        
        self._heartbeat_task = asyncio.create_task(heartbeat_loop())
        _LOGGER.debug("Heartbeat started")
    
    async def stop_heartbeat(self):
        """Stop the heartbeat task."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
            _LOGGER.debug("Heartbeat stopped")
    
    def calculate_checksum(self, data: bytes) -> int:
        """Calculate checksum for command data."""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
    
    async def set_brightness_temperature(self, brightness: int, temperature: int) -> bool:
        """Set brightness and color temperature."""
        # Command format: 80 05 03 02 [BRIGHTNESS] [TEMP] [CHECKSUM]
        cmd_data = bytes([0x80, 0x05, 0x03, 0x02, brightness, temperature])
        checksum = self.calculate_checksum(cmd_data)
        command = cmd_data.hex() + f"{checksum:02x}"
        return await self.send_command(command)