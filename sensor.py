"""Support for reading text from local PDF files"""
import logging
import os
import re
from PyPDF2 import PdfReader
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_UNIT_OF_MEASUREMENT, CONF_VALUE_TEMPLATE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

CONF_FILE_PATH = "file_path"
CONF_PDF_PAGE = "pdf_page"
CONF_REGEX_SEARCH = "regex_search"
CONF_REGEX_MATCH_INDEX = "regex_match_index"

ATTR_VALUE = "value"

DEFAULT_NAME = "File"

ICON = "mdi:file-pdf"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_FILE_PATH): cv.isfile,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
        vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
        vol.Optional(CONF_PDF_PAGE, default=0): cv.string,
        vol.Optional(CONF_REGEX_SEARCH): cv.string,
        vol.Optional(CONF_REGEX_MATCH_INDEX, default=0): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the file sensor."""
    file_path = config.get(CONF_FILE_PATH)
    name = config.get(CONF_NAME)
    unit = config.get(CONF_UNIT_OF_MEASUREMENT)
    pdf_page = config.get(CONF_PDF_PAGE)
    value_template = config.get(CONF_VALUE_TEMPLATE)
    regex_search = config.get(CONF_REGEX_SEARCH)
    regex_match_index = config.get(CONF_REGEX_MATCH_INDEX)

    if value_template is not None:
        value_template.hass = hass

    if hass.config.is_allowed_path(file_path):
        async_add_entities([PDFFileSensor(
            name,
            file_path,
            unit,
            pdf_page,
            value_template,
            regex_search,
            regex_match_index
        )], True)
    else:
        _LOGGER.error("'%s' is not an allowed directory", file_path)


class PDFFileSensor(Entity):
    """Implementation of a file sensor."""

    def __init__(self,
            name,
            file_path,
            unit_of_measurement,
            pdf_page,
            value_template,
            regex_search,
            regex_match_index
    ):
        """Initialize the file sensor."""
        self._name = name
        self._file_path = file_path
        self._unit_of_measurement = unit_of_measurement
        self._pdf_page = pdf_page
        self._val_tpl = value_template
        self._regex_search = regex_search
        self._regex_match_index = regex_match_index
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return ICON

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Get the latest entry from a file and updates the state."""
        try:
            with open(self._file_path, 'rb') as file_data:
                pdf = PdfReader(file_data)
                try:
                    page = pdf.pages[int(self._pdf_page)]
                except IndexError:
                    _LOGGER.error("PDF Page %s does not exist in file: %s", self._pdf_page, self._file_path)
                text = page.extract_text()
        except (IndexError, FileNotFoundError, IsADirectoryError, UnboundLocalError):
            _LOGGER.warning(
                "File or data not present at the moment: %s",
                os.path.basename(self._file_path),
            )
            return

        state = ''
        match_index = int(self._regex_match_index)

        if self._regex_search is not None:
            matches = re.search(self._regex_search, text)
            matched_index = matches[match_index]
            state = matched_index
        else:
            state = text

        if self._val_tpl is not None:
            variables = {
                ATTR_VALUE: state
            }
            state = self._val_tpl.render(variables, parse_result=False)

        if len(state) > 255:
            _LOGGER.warning("PDF data exceeds 255 characters, truncating: %s", state)
            state = state[:255]

        self._state = state
