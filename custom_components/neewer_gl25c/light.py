"""Platform for Neewer GL25C light integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
    COMMAND_POWER_ON,
    COMMAND_POWER_OFF,
)
from .udp_client import NeewerUDPClient

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
})


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up the Neewer GL25C Light platform from YAML."""
    name = config[CONF_NAME]
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    
    async_add_entities([NeewerGL25CLight(name, host, port)], True)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Neewer GL25C Light from a config entry."""
    name = config_entry.data.get(CONF_NAME, DEFAULT_NAME)
    host = config_entry.data[CONF_HOST]
    port = config_entry.data.get(CONF_PORT, DEFAULT_PORT)
    
    async_add_entities([NeewerGL25CLight(name, host, port)], True)


class NeewerGL25CLight(LightEntity):
    """Representation of a Neewer GL25C Light."""

    def __init__(self, name: str, host: str, port: int) -> None:
        """Initialize a Neewer GL25C Light."""
        self._name = name
        self._host = host
        self._port = port
        self._is_on = False
        self._brightness = 255
        self._color_temp = 370  # Default to 2700K in mireds
        self._udp_client = NeewerUDPClient(host, port)
        self._available = False
        
    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name
        
    @property
    def unique_id(self) -> str:
        """Return the unique ID of this light."""
        return f"neewer_gl25c_{self._host.replace('.', '_')}"
        
    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on
        
    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return self._brightness
        
    @property
    def color_temp(self) -> int:
        """Return the color temperature in mireds."""
        return self._color_temp
        
    @property
    def min_mireds(self) -> int:
        """Return the coldest color_temp that this light supports."""
        return 143  # 7000K
        
    @property
    def max_mireds(self) -> int:
        """Return the warmest color_temp that this light supports."""
        return 345  # 2900K
        
    @property
    def supported_color_modes(self) -> set[ColorMode]:
        """Return the list of supported color modes."""
        return {ColorMode.COLOR_TEMP}
        
    @property
    def color_mode(self) -> ColorMode:
        """Return the current color mode."""
        return ColorMode.COLOR_TEMP
        
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available
        
    @property
    def assumed_state(self) -> bool:
        """Return True as we can't query the device state."""
        return True
        
    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        # Try to connect to the light
        connected = await self._udp_client.connect()
        if connected:
            self._available = True
        else:
            _LOGGER.warning(f"Failed to connect to {self._name} at {self._host}")
            
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await self._udp_client.disconnect()
        
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if not self._available:
            return
            
        # Send power on command
        success = await self._udp_client.send_command(COMMAND_POWER_ON)
        if success:
            self._is_on = True
            
        # Handle brightness
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
            # Convert HA brightness (0-255) to light brightness (0-100)
            light_brightness = int(self._brightness * 100 / 255)
            
            # Handle color temperature
            if ATTR_COLOR_TEMP in kwargs:
                self._color_temp = kwargs[ATTR_COLOR_TEMP]
                
            # Convert mireds to Kelvin and then to light's temperature value
            kelvin = 1000000 // self._color_temp
            # Map 2900K-7000K to 0-100
            temp_value = int((kelvin - 2900) * 100 / (7000 - 2900))
            temp_value = max(0, min(100, temp_value))
            
            # Send brightness and temperature command
            await self._udp_client.set_brightness_temperature(light_brightness, temp_value)
            
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        if not self._available:
            return
            
        success = await self._udp_client.send_command(COMMAND_POWER_OFF)
        if success:
            self._is_on = False
            
    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        # Since the light doesn't provide feedback, we just ensure connection
        # is still alive by checking if we can send a command
        pass