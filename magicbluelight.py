import logging

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, Light, PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv

# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['magicblue==0.2.3']

CONF_NAME = 'name'
CONF_ADDRESS = 'address'
CONF_VERSION = 'version'

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_ADDRESS): cv.string,
    vol.Optional(CONF_VERSION, default=3): cv.positive_int
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the MagicBlue platform."""
    from magicblue import MagicBlue

    # Assign configuration variables. The configuration check takes care they are
    # present.
    bulb_name = config.get(CONF_NAME)
    bulb_mac_address = config.get(CONF_ADDRESS)
    bulb_version = config.get(CONF_VERSION)

    bulb = MagicBlue(bulb_mac_address, bulb_version)

    try:
        bulb.connect()
    except Exception as e:
        _LOGGER.error('Could not connect to the MagicBlue %s', bulb_mac_address)

    # # Verify that passed in configuration works
    # if not bulb.is_connected():
    #     _LOGGER.error('Could not connect to the MagicBlue %s', bulb_mac_address)
    #     return False

    # Add devices
    add_devices([MagicBlueLight(bulb, bulb_name)])


class MagicBlueLight(Light):
    """Representation of an MagicBlue Light."""

    def __init__(self, light, name):
        """Initialize an MagicBlueLight."""
        self._light = light
        self._name = name
        self._state = None
        self._brightness = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Brightness of the light (an integer in the range 1-255).

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        if not self._light.is_connected():
            try:
                self._light.connect()
            except Exception as e:
                _LOGGER.error('Could not connect to the MagicBlue %s', bulb_mac_address)
                self._state = True
                return

        # self._light.brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        self._light.turn_on()
        self._state = True

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        if not self._light.is_connected():
            try:
                self._light.connect()
            except Exception as e:
                _LOGGER.error('Could not connect to the MagicBlue %s', bulb_mac_address)
                self._state = False
                return

        self._light.turn_off()
        self._state = False

    # def update(self):
    #     """Fetch new state data for this light.
    #
    #     This is the only method that should fetch new data for Home Assistant.
    #     """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
