#!/usr/bin/env python3
"""
Standalone test script for Neewer GL25C light control.
Run this to test if your light responds to UDP commands before installing in Home Assistant.

Usage:
    python test_light.py <light_ip_address>
    
Example:
    python test_light.py 192.168.1.100
"""

import socket
import sys
import time
import threading
from typing import Optional

class NeewerTestClient:
    def __init__(self, host: str, port: int = 5052):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._heartbeat_active = False
        
    def send_command(self, hex_command: str):
        """Send a hex command to the light."""
        if not self.sock:
            print(f"❌ Socket not initialized")
            return
            
        data = bytes.fromhex(hex_command)
        self.sock.sendto(data, (self.host, self.port))
        print(f"📤 Sent: {hex_command}")
        
    def connect(self):
        """Connect to the light."""
        print(f"\n🔌 Connecting to {self.host}:{self.port}...")
        
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Send handshake
        ip_parts = self.host.split('.')
        ip_hex = ''.join([f'{int(part):02x}' for part in ip_parts])
        handshake = f"80021000000d{ip_hex}2e"
        
        print(f"🤝 Sending handshake...")
        self.send_command(handshake)
        
        # Start heartbeat
        self.start_heartbeat()
        print(f"✅ Connected!")
        
    def start_heartbeat(self):
        """Start heartbeat thread."""
        def heartbeat_loop():
            while self._heartbeat_active:
                self.send_command("8004020106")  # Query power status
                time.sleep(0.2)  # 200ms interval
                
        self._heartbeat_active = True
        self._heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        print(f"💓 Heartbeat started (every 200ms)")
        
    def stop_heartbeat(self):
        """Stop heartbeat thread."""
        self._heartbeat_active = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join()
        print(f"💔 Heartbeat stopped")
        
    def disconnect(self):
        """Disconnect from the light."""
        self.stop_heartbeat()
        if self.sock:
            self.sock.close()
            self.sock = None
        print(f"🔌 Disconnected")
        
    def calculate_checksum(self, data: bytes) -> int:
        """Calculate checksum for command data."""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
        
    def test_power_on(self):
        """Test power on command."""
        print(f"\n💡 Testing POWER ON...")
        self.send_command("800502010189")
        
    def test_power_off(self):
        """Test power off command."""
        print(f"\n🌑 Testing POWER OFF...")
        self.send_command("800502010088")
        
    def test_brightness(self, brightness: int):
        """Test brightness command (0-100)."""
        print(f"\n🔆 Testing brightness: {brightness}%")
        # Command format: 80 05 03 02 [BRIGHTNESS] [TEMP] [CHECKSUM]
        # Using default temp of 50 (middle value)
        cmd_data = bytes([0x80, 0x05, 0x03, 0x02, brightness, 50])
        checksum = self.calculate_checksum(cmd_data)
        command = cmd_data.hex() + f"{checksum:02x}"
        self.send_command(command)
        
    def test_color_temperature(self, kelvin: int):
        """Test color temperature (2900K-7000K)."""
        print(f"\n🌡️  Testing color temperature: {kelvin}K")
        # Convert Kelvin to 0-100 scale
        temp_value = int((kelvin - 2900) * 100 / (7000 - 2900))
        temp_value = max(0, min(100, temp_value))
        
        # Use current brightness of 50%
        cmd_data = bytes([0x80, 0x05, 0x03, 0x02, 50, temp_value])
        checksum = self.calculate_checksum(cmd_data)
        command = cmd_data.hex() + f"{checksum:02x}"
        self.send_command(command)


def main():
    if len(sys.argv) < 2:
        print("❌ Error: Please provide the light's IP address")
        print("Usage: python test_light.py <light_ip_address>")
        print("Example: python test_light.py 192.168.1.100")
        sys.exit(1)
        
    host = sys.argv[1]
    
    print(f"🎮 Neewer GL25C Light Test Tool")
    print(f"================================")
    print(f"Target: {host}")
    print(f"\nMake sure your light is:")
    print(f"  1. Powered on")
    print(f"  2. Connected to WiFi")
    print(f"  3. On the same network as this computer")
    
    client = NeewerTestClient(host)
    
    try:
        client.connect()
        
        while True:
            print(f"\n📋 Test Menu:")
            print(f"  1. Power ON")
            print(f"  2. Power OFF")
            print(f"  3. Set brightness (0-100%)")
            print(f"  4. Set color temperature (2900K-7000K)")
            print(f"  5. Quick test sequence")
            print(f"  q. Quit")
            
            choice = input("\nSelect option: ").strip().lower()
            
            if choice == '1':
                client.test_power_on()
                
            elif choice == '2':
                client.test_power_off()
                
            elif choice == '3':
                try:
                    brightness = int(input("Enter brightness (0-100): "))
                    if 0 <= brightness <= 100:
                        client.test_brightness(brightness)
                    else:
                        print("❌ Brightness must be between 0 and 100")
                except ValueError:
                    print("❌ Invalid number")
                    
            elif choice == '4':
                try:
                    kelvin = int(input("Enter color temperature (2900-7000): "))
                    if 2900 <= kelvin <= 7000:
                        client.test_color_temperature(kelvin)
                    else:
                        print("❌ Temperature must be between 2900K and 7000K")
                except ValueError:
                    print("❌ Invalid number")
                    
            elif choice == '5':
                print(f"\n🎬 Running test sequence...")
                
                print(f"\n1️⃣ Power ON")
                client.test_power_on()
                time.sleep(2)
                
                print(f"\n2️⃣ Brightness 100%")
                client.test_brightness(100)
                time.sleep(2)
                
                print(f"\n3️⃣ Brightness 50%")
                client.test_brightness(50)
                time.sleep(2)
                
                print(f"\n4️⃣ Cool white (6500K)")
                client.test_color_temperature(6500)
                time.sleep(2)
                
                print(f"\n5️⃣ Warm white (3000K)")
                client.test_color_temperature(3000)
                time.sleep(2)
                
                print(f"\n6️⃣ Power OFF")
                client.test_power_off()
                
                print(f"\n✅ Test sequence complete!")
                
            elif choice == 'q':
                print(f"\n👋 Goodbye!")
                break
                
            else:
                print(f"❌ Invalid option")
                
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()