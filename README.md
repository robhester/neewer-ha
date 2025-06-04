# Neewer GL25C Home Assistant Integration

Control your Neewer GL25C LED RGB streaming lights from Home Assistant.

## Features

- Power on/off control
- Brightness adjustment (0-100%)
- Color temperature control (2900K-7000K)
- Seamless integration with Home Assistant's light platform

## Requirements

- Home Assistant 2023.1 or newer
- Neewer GL25C light connected to your WiFi network
- Home Assistant and the light must be on the same network

## Installation

### Manual Installation

1. Copy the `custom_components/neewer_gl25c` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration to your `configuration.yaml` (see Configuration section)
4. Restart Home Assistant again

### HACS Installation (Coming Soon)

This integration will be available through HACS in the future.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
light:
  - platform: neewer_gl25c
    name: "Studio Light"
    host: 192.168.1.100  # Replace with your light's IP address
    port: 5052           # Optional, defaults to 5052
```

### Configuration Variables

- **host** (Required): The IP address of your Neewer GL25C light
- **name** (Optional): Friendly name for the light (default: "Neewer GL25C")
- **port** (Optional): UDP port for communication (default: 5052)

## Finding Your Light's IP Address

1. Connect your Neewer GL25C to your WiFi network using the manufacturer's app
2. Check your router's connected devices list
3. Look for a device named "Neewer" or similar
4. Note the IP address

## Usage

Once configured, your Neewer GL25C will appear as a light entity in Home Assistant. You can:

- Turn it on/off using the toggle
- Adjust brightness with the slider
- Change color temperature using the color temperature slider
- Include it in automations and scripts

## Troubleshooting

### Light not responding

1. Verify the light is connected to your WiFi network
2. Ensure the IP address in your configuration is correct
3. Check that Home Assistant and the light are on the same network segment
4. Try pinging the light's IP address from your Home Assistant host

### Connection drops after a while

The integration maintains a heartbeat to keep the connection alive. If you experience drops, check your network for any firewall rules blocking UDP traffic on port 5052.

## Known Limitations

- The light doesn't provide status feedback, so the state shown in Home Assistant is assumed based on the last command sent
- RGB color control is not yet implemented (coming in a future update)
- Special effects and scenes are not yet supported

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

This integration is based on the protocol reverse-engineered from the Neewer GL1, with adaptations for the GL25C model.

## License

This project is licensed under the MIT License.