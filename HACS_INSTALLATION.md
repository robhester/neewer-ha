# Installing Neewer GL25C Integration via HACS

## Prerequisites
- HACS must be installed in your Home Assistant
- Your Home Assistant instance must have internet access

## Installation Steps

### 1. Add as Custom Repository

1. **Open HACS in Home Assistant**
   - Navigate to HACS in your sidebar
   - Click on "Integrations"

2. **Add Custom Repository**
   - Click the 3 dots menu (⋮) in the top right
   - Select "Custom repositories"
   - In the dialog that appears:
     - **Repository**: `https://github.com/robhester/neewer-ha`
     - **Category**: Select "Integration"
   - Click "ADD"

3. **Install the Integration**
   - The repository should now appear in your HACS integrations list
   - Search for "Neewer GL25C" in HACS
   - Click on it and then click "DOWNLOAD"
   - Select the latest version
   - Click "DOWNLOAD" again
   - **RESTART Home Assistant** (Required!)

### 2. Configure the Integration

After restart, add to your `configuration.yaml`:

```yaml
light:
  - platform: neewer_gl25c
    name: "Studio Light"
    host: 192.168.1.100  # Replace with your light's IP address
```

### 3. Restart Again
- Restart Home Assistant one more time to load the light entity

### 4. Verify Installation
- Go to Developer Tools → States
- Search for `light.studio_light` (or whatever name you used)
- You should see your light entity

## Alternative: Manual Installation (if HACS doesn't work)

1. **Download the repository**
   ```bash
   cd /config  # or wherever your HA config is
   mkdir -p custom_components
   cd custom_components
   git clone https://github.com/robhester/neewer-ha
   mv neewer-ha/custom_components/neewer_gl25c .
   rm -rf neewer-ha
   ```

2. **Or download ZIP**
   - Go to https://github.com/robhester/neewer-ha
   - Click "Code" → "Download ZIP"
   - Extract and copy `custom_components/neewer_gl25c` to your HA's `custom_components` folder

3. **Configure and restart** (same as steps 2-4 above)

## Troubleshooting

### Light not appearing
- Check Home Assistant logs: Settings → System → Logs
- Look for any errors mentioning "neewer_gl25c"
- Verify the light's IP address is correct
- Ensure light is on same network as Home Assistant

### Can't connect to light
- Test with the standalone script first:
  ```bash
  python test_light.py 192.168.1.100
  ```
- Make sure no firewall is blocking UDP port 5052
- Try pinging the light's IP from your HA host

### HACS can't find repository
- Make sure you selected "Integration" as the category
- Check that the repository is public on GitHub
- Try refreshing HACS (3 dots menu → "Reload repositories")

## Finding Your Light's IP Address

1. **From your router**
   - Log into your router's admin panel
   - Look for connected devices
   - Find device named "Neewer" or similar

2. **From the Neewer app**
   - Some versions show the IP in device info

3. **Network scanner**
   - Use an app like Fing to scan your network
   - Look for unknown devices, test each IP