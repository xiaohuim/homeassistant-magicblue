import logging

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_RGB_COLOR, SUPPORT_RGB_COLOR, SUPPORT_BRIGHTNESS, Light, PLATFORM_SCHEMA

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
    vol.Optional(CONF_VERSION, default=9): cv.positive_int
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

    # try:
    #     bulb.connect()
    # except Exception as e:
    #     _LOGGER.error('Could not connect to the MagicBlue %s', bulb_mac_address)

    # Add devices
    add_devices([MagicBlueLight(bulb, bulb_name)])


class MagicBlueLight(Light):
    """Representation of an MagicBlue Light."""

    def __init__(self, light, name):
        """Initialize an MagicBlueLight."""
        self._light = light
        self._name = name
        self._state = False
        self._rgb = (255, 255, 255)
        self._brightness = 255
        self._available = False

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def rgb_color(self):
        """Return the RBG color value."""
        return self._rgb

    @property
    def brightness(self):
        """Return the brightness of the light (an integer in the range 1-255)."""
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def supported_features(self):
        """Return the supported features."""
        return SUPPORT_BRIGHTNESS | SUPPORT_RGB_COLOR

    @property
    def available(self):
        return self._available

    def update(self):
        _LOGGER.debug("{}: MagicBlueLight.update()".format(self))
        try:
            if not self._light.test_connection():
                self._light.connect()

            device_info = self._light.get_device_info()

            self._state = device_info['on']
            self._rgb = (device_info['r'], device_info['g'], device_info['b'])
            self._brightness = device_info['brightness']
            self._available = True
        except Exception as ex:
            _LOGGER.debug("Exception during update status: %s", ex)
            self._available = False

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        _LOGGER.debug("{}: MagicBlueLight.turn_on()".format(self))
        if not self._light.test_connection():
            try:
                self._light.connect()
            except Exception as e:
                _LOGGER.error('Could not connect to the MagicBlue %s', self._light)
                return

        if not self._state:
            self._light.turn_on()

        if ATTR_RGB_COLOR in kwargs:
            self._rgb = kwargs[ATTR_RGB_COLOR]
            self._brightness = 255
            self._light.set_color(self._rgb)

        if ATTR_BRIGHTNESS in kwargs:
            self._rgb = (255, 255, 255)
            self._brightness = kwargs[ATTR_BRIGHTNESS]
            self._light.set_warm_light(self._brightness / 255)

        self._state = True

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        _LOGGER.debug("{}: MagicBlueLight.turn_off()".format(self))
        if not self._light.test_connection():
            try:
                self._light.connect()
            except Exception as e:
                _LOGGER.error('Could not connect to the MagicBlue %s', self._light)
                return

        self._light.turn_off()
        self._state = False

    def __str__(self):
        return "<MagicBlueLight('{}', '{}')>".format(self._light, self._name)

    def __repr__(self):
        return "<MagicBlueLight('{}', '{}')>".format(self._light, self._name)
