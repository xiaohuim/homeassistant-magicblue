import functools
import logging
import threading

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_RGB_COLOR, SUPPORT_RGB_COLOR, SUPPORT_BRIGHTNESS, Light, PLATFORM_SCHEMA

import homeassistant.helpers.config_validation as cv

# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['magicblue==0.4.2']

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


# region Decorators
def comm_lock(blocking=True):
    """
    Lock method (per instance) such that the decorated method cannot be ran from multiple thread simulatinously.
    If blocking = True (default), the thread will wait for the lock to become available and then execute the method.
    If blocking = False, the thread will try to acquire the lock, fail and _not_ execute the method.
    """
    def ensure_lock(instance):
        if not hasattr(instance, '_comm_lock'):
            instance._comm_lock = threading.Lock()

        return instance._comm_lock

    def call_wrapper(func):
        """Call wrapper for decorator."""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            """Lock method (per instance) such that the decorated method cannot be ran from multiple thread simulatinously."""

            lock = ensure_lock(self)

            locked = lock.acquire(blocking)
            if locked:
                _LOGGER.debug('comm_lock(): %s.%s: entry', self, func.__name__)
                vals = func(self, *args, **kwargs)
                lock.release()
                _LOGGER.debug('comm_lock(): %s.%s: exit', self, func.__name__)
                return vals

            _LOGGER.debug('comm_lock(): %s.%s: lock not acquired, exiting', self, func.__name__)

        return wrapper

    return call_wrapper
# endregion


# region Home-Assistant
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the MagicBlue platform."""
    from magicblue import MagicBlue

    # Assign configuration variables. The configuration check takes care they are
    # present.
    bulb_name = config.get(CONF_NAME)
    bulb_mac_address = config.get(CONF_ADDRESS)
    bulb_version = config.get(CONF_VERSION)

    bulb = MagicBlue(bulb_mac_address, bulb_version)

    # Add devices
    add_devices([MagicBlueLight(hass, bulb, bulb_name)])


class MagicBlueLight(Light):
    """Representation of an MagicBlue Light."""

    def __init__(self, hass, light, name):
        """Initialize an MagicBlueLight."""
        self.hass = hass
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
        _LOGGER.debug("%s.update()", self)
        self.hass.add_job(self._update_blocking)

    @comm_lock(False)
    def _update_blocking(self):
        _LOGGER.debug("%s._update_blocking()", self)

        try:
            if not self._light.test_connection():
                self._light.connect()

            device_info = self._light.get_device_info()

            self._state = device_info['on']
            self._rgb = (device_info['r'], device_info['g'], device_info['b'])
            self._brightness = device_info['brightness']
            self._available = True
        except Exception as ex:
            _LOGGER.debug("%s._update_blocking(): Exception during update status: %s", self, ex)
            self._available = False

    @comm_lock()
    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        _LOGGER.debug("%s.turn_on()", self)
        if not self._light.test_connection():
            try:
                self._light.connect()
            except Exception as e:
                _LOGGER.error('%s.turn_on(): Could not connect to %s', self, self._light)
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

    @comm_lock()
    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        _LOGGER.debug("%s: MagicBlueLight.turn_off()", self)
        if not self._light.test_connection():
            try:
                self._light.connect()
            except Exception as e:
                _LOGGER.error('%s.turn_off(): Could not connect to %s', self, self._light)
                return

        self._light.turn_off()
        self._state = False

    def __str__(self):
        return "<MagicBlueLight('{}', '{}')>".format(self._light, self._name)

    def __repr__(self):
        return "<MagicBlueLight('{}', '{}')>".format(self._light, self._name)
# endregion
