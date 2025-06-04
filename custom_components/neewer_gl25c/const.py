"""Constants for the Neewer GL25C Light integration."""

DOMAIN = "neewer_gl25c"

# Default values
DEFAULT_NAME = "Neewer GL25C"
DEFAULT_PORT = 5052

# Commands from GL1 protocol
COMMAND_POWER_ON = "800502010189"
COMMAND_POWER_OFF = "800502010088"
COMMAND_QUERY_POWER = "8004020106"

# Temperature range
MIN_KELVIN = 2900
MAX_KELVIN = 7000

# Brightness range
MIN_BRIGHTNESS = 0
MAX_BRIGHTNESS = 100