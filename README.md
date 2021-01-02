# Home Assistant PDF File Sensor

The `pdf` sensor enables the parsing and searching of text content from local PDF files using [PyPDF2](https://pypi.org/project/PyPDF2/).


## Installation

Clone this repo into the `custom_components` directory:

```sh
cd [HA_HOME]/custom_components
git clone https://github.com/emcniece/ha_pdf.git
```

## Configuration

Home Assistant must first be allowed to access the directory with the target PDF file. Add the [allowlist_external_dirs](https://www.home-assistant.io/docs/configuration/basic/#allowlist_external_dirs) to `configuration.yaml`. In this example, the PDF exists at `/config/my.pdf`:

```yaml
homeassistant:
  allowlist_external_dirs:
    - /config
```

Next add the sensor definition:

```yaml
sensor:
  - platform: pdf
    name: My PDF Sensor
    file_path: /config/my.pdf
```

By default this configuration will extract all text content found in the first page of the PDF.

### Configuration Variables

#### file_path (required)

Path to a local PDF file

<hr />

#### unit_of_measurement (optional)

Measurement unit to associate with the rendered value

<hr />

#### pdf_page (optional)

Numeric value of the PDF Page to search. Default: `0`

<hr />

#### regex_search (optional)

Regular expression with capture groups used to search the PDF text.

<hr />

#### regex_match_index (optional)

Regular expression capture group index to render as the value. Default: `0`

Index `0` returns the whole matched string. Indexes >= `1` return valid capture groups.

<hr />

#### value_template (optional)

Post-regex template rendering of the value.

- `{{ value }}`: parsed text

<hr />

## Full Configuration Example

The PDF in this example contains a line of text reading the following:

```
Water Consumption Charge     15  x  $  2.2159             33.24 --------------Balance
```

Three sensors can be used with different `regex_match_index` capture groups to extract each numeric value:

```yaml
# Example configuration.yaml entry
homeassistant:
  allowlist_external_dirs:
    - /config

sensor:
  - platform: pdf
    name: Water Usage Volume
    file_path: /config/water-bill.pdf
    unit_of_measurement: m3
    pdf_page: 0
    regex_search: 'Water Consumption Charge\s+([\d.]+)\s+x\s+\$\s+([\d.]+)\s+([\d.]+)\s-+'
    regex_match_index: 1

  - platform: pdf
    name: Water Usage Billing Rate
    file_path: /config/water-bill.pdf
    unit_of_measurement: $
    pdf_page: 0
    regex_search: 'Water Consumption Charge\s+([\d.]+)\s+x\s+\$\s+([\d.]+)\s+([\d.]+)\s-+'
    regex_match_index: 2

  - platform: pdf
    name: Water Usage Total Cost
    file_path: /config/water-bill.pdf
    unit_of_measurement: $
    pdf_page: 0
    regex_search: 'Water Consumption Charge\s+([\d.]+)\s+x\s+\$\s+([\d.]+)\s+([\d.]+)\s-+'
    regex_match_index: 3
```
