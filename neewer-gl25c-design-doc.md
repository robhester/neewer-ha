# Neewer GL25C Home Assistant Integration - Project Design Document

## Summary for Claude Code

**Task**: Create a Home Assistant custom component by combining:
1. The GL1's working UDP protocol (convert JavaScript to Python)
2. Home Assistant's example light component (use as template)
3. Patterns from other UDP-based HA integrations (DMX, WiZ)

**The integration is 90% existing code** - we're just adapting and connecting pieces together!

## Project Overview

### Purpose
Create a custom Home Assistant integration that allows control of Neewer GL25C LED RGB streaming lights via WiFi using UDP commands.

### What We're Building vs. Reusing
**We're Building:**
- UDP client that adapts GL1's protocol to Python
- Command mappings specific to GL25C
- Integration configuration

**We're Reusing:**
- Home Assistant's LightEntity base class (provides 90% of functionality)
- GL1's proven UDP protocol and command structure
- Standard Python libraries (no external dependencies needed)
- Example patterns from other HA integrations

### Background
- The Neewer GL25C is a WiFi-enabled RGB LED panel light used for streaming and video production
- Neewer provides PC/Mac software but no Home Assistant integration exists
- Similar Neewer lights (GL1) use UDP protocol on port 5052 for control
- The lights do not provide status feedback - they only receive commands

### User Requirements
- The user is not a programmer but is experienced with Home Assistant
- Integration should appear and function like other light entities in Home Assistant
- Should support all major light functions available on the physical device

## Technical Specifications

### Device Capabilities
Based on manufacturer specifications, the GL25C supports:
- Power on/off
- Brightness control (0-100%)
- Color temperature (2900K-7000K)
- Green/Magenta adjustment (±50 GM value)
- Full RGB color control
- HSI mode (Hue: 0-360°, Saturation: 0-100%, Intensity: 0-100%)
- RGBCW mode (R/G/B/C/W: 0-255)
- 18 special effects scenes (including Music Sync mode)

### Communication Protocol
Based on the GL1 reverse engineering:
- **Protocol**: UDP
- **Port**: 5052
- **Direction**: One-way (light receives only, no status feedback)
- **Heartbeat**: Required every ~200-250ms to keep connection alive
- **IP Requirements**: Both Home Assistant and light must be on same network

### Known Command Structure
```
Handshake: 80 02 10 00 00 0d [IP_ADDRESS_IN_HEX] 2e
Power On: 80 05 02 01 01 89
Power Off: 80 05 02 01 00 88
Brightness/Temperature: 80 05 03 02 [BRIGHTNESS] [TEMP] [CHECKSUM]
```

## Architecture Design

### Integration Structure
```
custom_components/
└── neewer_gl25c/
    ├── __init__.py          # Integration setup
    ├── manifest.json        # Integration metadata
    ├── light.py            # Light platform implementation
    ├── const.py            # Constants and configuration
    ├── udp_client.py       # UDP communication handler
    └── translations/
        └── en.json         # English translations
```

### Component Classes

#### 1. UDPClient Class (NEW CODE - Adapt from GL1)
**Purpose**: Handle all UDP communication with the light
```python
class NeewerUDPClient:
    - __init__(self, host, port=5052)
    - connect() # Send handshake
    - disconnect() # Stop heartbeat
    - send_command(command_hex)
    - start_heartbeat() # Send keepalive every 200ms
    - stop_heartbeat()
    - _calculate_checksum(data)
```

#### 2. NeewerGL25CLight Class (MOSTLY BOILERPLATE)
**Purpose**: Implement Home Assistant Light entity
```python
class NeewerGL25CLight(LightEntity):
    # Most of this is standard HA boilerplate!
    # We just fill in these methods:
    - turn_on(**kwargs) → calls udp_client.send_command()
    - turn_off(**kwargs) → calls udp_client.send_command()
    # Everything else is provided by LightEntity base class
```

## Implementation Steps

### Build Order (IMPORTANT)
1. **Copy the example_light component verbatim** as your starting point
2. **Test it loads in HA** before making any changes
3. **Add UDP client** using GL1 code as reference
4. **Test on/off** commands work
5. **Then add features** one at a time

### Phase 1: Basic On/Off Control
1. Create integration file structure
2. Implement basic manifest.json with requirements
3. Create UDPClient class with:
   - Handshake functionality
   - Power on/off commands
   - Basic heartbeat mechanism
4. Implement minimal LightEntity with on/off support
5. Test with Home Assistant Developer Tools

### Phase 2: Brightness & Color Temperature
1. Add brightness control to UDPClient
   - Map HA's 0-255 to light's 0-100 scale
   - Implement checksum calculation
2. Add color temperature control
   - Map HA's mired scale to light's 2900K-7000K
   - Handle temperature command format
3. Update LightEntity with brightness/color_temp properties
4. Add configuration flow for IP address entry

### Phase 3: RGB Color Support
1. Research RGB command format (may need packet capture)
2. Implement RGB command in UDPClient
3. Add rgb_color and hs_color support to LightEntity
4. Test color wheel integration in Home Assistant

### Phase 4: Advanced Features
1. Add support for effects/scenes (if command format discovered)
2. Implement GM (Green/Magenta) adjustment as custom service
3. Add configuration options for:
   - Heartbeat interval
   - Connection timeout
   - Default transition time

### Phase 5: Polish & Error Handling
1. Add proper error handling for network issues
2. Implement automatic reconnection on failure
3. Add debug logging for troubleshooting
4. Create comprehensive documentation
5. Add config flow for easier setup

## Configuration

### Configuration Flow
The integration should support UI configuration with these fields:
- **Name**: Friendly name for the light (default: "Neewer GL25C")
- **Host**: IP address of the light (required)
- **Port**: UDP port (default: 5052)

### YAML Configuration (Optional)
```yaml
light:
  - platform: neewer_gl25c
    name: "Studio Light"
    host: 192.168.1.100
    port: 5052  # optional, defaults to 5052
```

## Testing Requirements

### Unit Tests
1. Test UDP client commands generation
2. Test checksum calculation
3. Test value conversions (brightness, color temp, RGB)

### Integration Tests
1. Test entity appears in Home Assistant
2. Test on/off commands work
3. Test brightness slider functionality
4. Test color temperature slider
5. Test RGB color picker
6. Test that heartbeat maintains connection

### Manual Testing Checklist
- [ ] Light responds to on/off commands
- [ ] Brightness changes smoothly
- [ ] Color temperature adjusts correctly
- [ ] RGB colors display accurately
- [ ] Light stays responsive over time (heartbeat working)
- [ ] Recovery after network interruption
- [ ] Multiple lights can be controlled independently

## Potential Challenges & Solutions

### Challenge 1: Unknown Command Formats
**Issue**: RGB and effects commands not documented
**Solution**: 
- Start with basic features (on/off, brightness, CCT)
- Use Wireshark to capture traffic from official app
- Add features incrementally as protocols are discovered

### Challenge 2: No Status Feedback
**Issue**: Can't query light state
**Solution**: 
- Assume state based on last command sent
- Mark entity as "assumed_state" in HA
- Add "sync" service to reset assumed state

### Challenge 3: Network Reliability
**Issue**: UDP is unreliable, commands might be lost
**Solution**: 
- Send each command twice with small delay
- Implement connection monitoring
- Auto-reconnect on failure

### Challenge 4: Discovery
**Issue**: Lights don't advertise themselves
**Solution**: 
- Manual IP configuration initially
- Later: Add optional mDNS/broadcast discovery

## Future Enhancements

1. **Auto-discovery**: Implement network scanning to find lights
2. **Effects Support**: Add scene/effect selection once protocol known
3. **Transition Support**: Smooth transitions between states
4. **Group Control**: Control multiple lights as one entity
5. **Energy Monitoring**: Calculate power usage based on brightness/color
6. **Bluetooth Fallback**: Use Bluetooth when WiFi unavailable

## Reference Resources

### Code to Reuse/Adapt

1. **GL1 UDP Communication Code**: https://github.com/braintapper/neewer-gl1
   - Already has working UDP protocol implementation
   - Copy/adapt the command structure and checksum calculation
   - Use the heartbeat timing logic

2. **Home Assistant Example Light Component**: https://github.com/home-assistant/example-custom-config/tree/master/custom_components/example_light
   - Use as template for basic structure
   - Shows proper way to inherit from LightEntity
   - Has correct manifest.json format

3. **DMX Integration (UDP Example)**: https://github.com/jnimmo/hass-dmx
   - Shows how to implement UDP communication in HA
   - Good example of one-way communication (like our lights)
   - Has reconnection logic we can adapt

4. **WiZ Light Integration**: https://github.com/agguro/homeassistant-wizlight
   - Another UDP-based light control
   - Shows config flow implementation
   - Has discovery mechanisms (for future enhancement)

### Built-in Code We'll Use (No Need to Write)

1. **Home Assistant Light Platform**
   - `from homeassistant.components.light import LightEntity, ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, ATTR_RGB_COLOR`
   - All the base functionality is provided by HA

2. **Python Standard Library**
   - `socket` for UDP communication
   - `asyncio` for async operations
   - `struct` for packing binary data
   - `threading` for heartbeat timer

3. **Home Assistant Helpers**
   - `from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT`
   - `from homeassistant.core import HomeAssistant`
   - `from homeassistant.helpers.entity_platform import AddEntitiesCallback`

### What We Actually Need to Write

1. **UDP Client Adapter** (~50 lines)
   - Adapt GL1's JavaScript UDP code to Python
   - Implement heartbeat mechanism
   - Add checksum calculation

2. **Command Mapping** (~30 lines)
   - Map HA's brightness scale (0-255) to light's scale (0-100)
   - Convert HA's mired color temp to Kelvin (2900-7000)
   - Implement RGB command format (once discovered)

3. **Integration Glue** (~20 lines)
   - Connect UDP client to HA's LightEntity
   - Handle configuration
   - Error handling and logging

**Total new code: ~100 lines** (everything else is reused!)

## Success Criteria

The integration is considered complete when:
1. Light can be controlled via Home Assistant UI
2. All basic functions work (power, brightness, color temp)
3. Integration is stable over 24+ hour period
4. Installation is simple via HACS or manual install
5. Clear documentation exists for end users

## Notes for Implementation

1. **Don't overcomplicate** - We're mostly gluing existing code together
2. Start simple - get on/off working first  
3. The light won't provide feedback, so use "assumed_state"
4. Heartbeat is critical - without it, light stops responding
5. Test on same network segment as light (no VLAN routing initially)
6. Include debug logging that can be enabled via HA logger configuration
7. Consider making heartbeat interval configurable for different network conditions
8. **Copy liberally** from the referenced repositories - they've solved these problems already

## Code Reuse Strategy

### From GL1 Repository (JavaScript → Python)
Copy and convert these specific parts:
```javascript
// Command structures to copy:
const POWER_ON = Buffer.from('800502010189', 'hex')
const POWER_OFF = Buffer.from('800502010088', 'hex')
// Handshake format: 80 02 10 00 00 0d [IP_IN_HEX] 2e
// Brightness/Temp: 80 05 03 02 [BRIGHTNESS] [TEMP] [CHECKSUM]
```

### From Home Assistant Example Light
Use this entire file as starting template:
- Copy `example_light/light.py` structure
- Copy `example_light/manifest.json` format
- Copy `example_light/__init__.py` pattern

### From hass-dmx Integration
Borrow these specific patterns:
- UDP socket setup and error handling
- Async update loop pattern
- Connection retry logic
- One-way communication handling

### From Python Standard Library
```python
import socket
import struct
import asyncio
import threading
from typing import Any, Dict, Optional
```

No need to install any external dependencies!

## Minimal Code Example

Here's what the core functionality looks like (simplified):

```python
# In light.py - Most is boilerplate from example_light
class NeewerGL25CLight(LightEntity):
    def turn_on(self, **kwargs):
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]  # 0-255 from HA
            light_brightness = int(brightness * 100 / 255)  # Convert to 0-100
            # TODO: Send brightness command via UDP
        
        self._udp_client.send_command("800502010189")  # Power on
        self._is_on = True

    def turn_off(self, **kwargs):
        """Turn the light off."""
        self._udp_client.send_command("800502010088")  # Power off
        self._is_on = False

# In udp_client.py - Adapted from GL1
class NeewerUDPClient:
    def send_command(self, hex_command):
        """Send a hex command to the light."""
        data = bytes.fromhex(hex_command)
        self.sock.sendto(data, (self.host, self.port))
```

That's essentially it! Everything else is configuration and error handling.

## Deliverables

1. Working custom component (folder structure as specified)
2. README.md with installation and usage instructions
3. Example configuration snippets
4. Troubleshooting guide
5. HACS-compatible repository structure (optional)

## Quick Reference Links

- **GL1 Protocol (COPY THIS)**: https://github.com/braintapper/neewer-gl1
- **HA Example Light (USE AS TEMPLATE)**: https://github.com/home-assistant/example-custom-config/tree/master/custom_components/example_light
- **DMX Integration (UDP EXAMPLE)**: https://github.com/jnimmo/hass-dmx
- **HA Light Docs**: https://developers.home-assistant.io/docs/core/entity/light

## Minimal Code Example

Here's what the core functionality looks like (simplified):

```python
# In light.py - Most is boilerplate from example_light
class NeewerGL25CLight(LightEntity):
    def turn_on(self, **kwargs):
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]  # 0-255 from HA
            light_brightness = int(brightness * 100 / 255)  # Convert to 0-100
            # TODO: Send brightness command via UDP
        
        self._udp_client.send_command("800502010189")  # Power on
        self._is_on = True

    def turn_off(self, **kwargs):
        """Turn the light off."""
        self._udp_client.send_command("800502010088")  # Power off
        self._is_on = False

# In udp_client.py - Adapted from GL1
class NeewerUDPClient:
    def send_command(self, hex_command):
        """Send a hex command to the light."""
        data = bytes.fromhex(hex_command)
        self.sock.sendto(data, (self.host, self.port))
```

That's essentially it! Everything else is configuration and error handling.