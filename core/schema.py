"""
PragyanAI EDA Solution - Data Contract
This schema defines the mandatory structure for the architecture_plan.json.
Any design failing this validation is rejected by the Design Critic node.
"""

ARCH_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "PragyanAI Architecture Plan",
    "type": "object",
    "properties": {
        "mcu": {
            "type": "object",
            "description": "The primary processing unit and its package variant.",
            "properties": {
                "family": {
                    "type": "string",
                    "description": "e.g., ESP32-S3, STM32F4, RP2040"
                },
                "package": {
                    "type": "string",
                    "description": "Specific physical variant, e.g., WROOM-1, QFN-48"
                }
            },
            "required": ["family"]
        },
        "power_tree": {
            "type": "array",
            "description": "Sequential voltage regulation path from input to logic.",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "description": "Type of regulator, e.g., Buck, LDO"
                    },
                    "input_v": {
                        "type": "number",
                        "description": "Voltage entering the component"
                    },
                    "output_v": {
                        "type": "number",
                        "description": "Voltage exiting the component"
                    }
                },
                "required": ["component", "input_v", "output_v"]
            }
        },
        "interfaces": {
            "type": "object",
            "description": "Mapping of peripheral components to communication protocols.",
            "additionalProperties": {
                "type": "string",
                "enum": ["I2C", "SPI", "UART", "ADC", "GPIO", "PWM", "USB"]
            }
        }
    },
    "required": ["mcu", "power_tree", "interfaces"],
    "additionalProperties": False
}

def get_schema():
    """Returns the master schema for validation purposes."""
    return ARCH_SCHEMA
  
