#!/usr/bin/env python3
"""Comprehensive example for pyairobotrest library.

Demonstrates all library features including:
- Basic status reading
- Factory method (recommended for Home Assistant)
- Context manager usage
- Individual setting methods (via CLI)
- Strict validation mode

Usage:
    python example.py                        # Run all examples
    python example.py --help                # Show available commands

Set environment variables for real device testing:
    export AIROBOT_HOST=192.168.1.100
    export AIROBOT_USERNAME=T01XXXXXX
    export AIROBOT_PASSWORD=your_password
"""
# ruff: noqa: T201

import asyncio
import os
import sys

from pyairobotrest import AirobotClient
from pyairobotrest.exceptions import AirobotConnectionError, AirobotError


async def main():
    """Main example function."""
    # Create client instance with Basic Auth credentials
    # Replace with your actual thermostat credentials
    client = AirobotClient(
        host="192.168.1.100",  # Device IP or "airobot-thermostat-t01xxxxxx.local"
        username="T01XXXXXX",  # Your thermostat Device ID
        password="your_password",  # Password for Local API access
    )

    try:
        # Get thermostat status (all read-only parameters)
        print("Fetching thermostat status...")
        status = await client.get_statuses()

        print(f"Device ID: {status.device_id}")
        print(f"Hardware Version: {status.hw_version}")
        print(f"Firmware Version: {status.fw_version}")
        print()

        print("Temperature Measurements:")
        print(f"  Air Temperature: {status.temp_air:.1f}°C")
        if status.has_floor_sensor:
            print(f"  Floor Temperature: {status.temp_floor:.1f}°C")
        else:
            print("  Floor Temperature: No sensor attached")
        print(f"  Setpoint Temperature: {status.setpoint_temp:.1f}°C")
        print()

        print("Air Quality:")
        print(f"  Humidity: {status.hum_air:.1f}%")
        if status.has_co2_sensor:
            print(f"  CO2: {status.co2} ppm")
            print(f"  Air Quality Index: {status.aqi}")
        else:
            print("  CO2: No sensor equipped")
        print()

        print("System Status:")
        print(f"  Heating: {'ON' if status.is_heating else 'OFF'}")
        print(f"  Device Uptime: {status.device_uptime} seconds")
        print(f"  Heating Uptime: {status.heating_uptime} seconds")
        if status.has_error:
            print(f"  Error Code: {status.errors}")
        else:
            print("  Status: No errors")
        print()

        print("Status Flags:")
        print(f"  Window Open Detected: {status.status_flags.window_open_detected}")
        print(f"  Heating Requested: {status.status_flags.heating_on}")

    except AirobotConnectionError as err:
        print(f"Connection error: {err}")
        print("Make sure the thermostat is on the network and reachable")
    except AirobotError as err:
        print(f"API error: {err}")
        print("Check if the Local API is enabled in thermostat settings")
    finally:
        # Close the client session
        await client.close()


async def factory_method_example():
    """Example using factory method for explicit session initialization."""
    print("Factory Method Example - Recommended for Home Assistant")
    print("=" * 60)
    print()

    # Using factory method - ensures session is ready before use
    client = await AirobotClient.create(
        host="192.168.1.100",
        username="T01XXXXXX",
        password="your_password",
    )

    try:
        status = await client.get_statuses()
        print(f"Current air temperature: {status.temp_air:.1f}°C")
        print(f"Heating: {'ON' if status.is_heating else 'OFF'}")
    except AirobotError as err:
        print(f"Error: {err}")
    finally:
        await client.close()


async def context_manager_example():
    """Example using context manager."""
    print("Context Manager Example")
    print("=" * 60)
    print()

    # Using context manager - automatically closes session
    async with AirobotClient(
        host="192.168.1.100", username="T01XXXXXX", password="your_password"
    ) as client:
        status = await client.get_statuses()
        print(f"Current air temperature: {status.temp_air:.1f}°C")


async def strict_validation_example():
    """Example demonstrating strict validation mode."""
    print("Strict Validation Example")
    print("=" * 60)
    print()

    print("Strict validation mode is useful for testing and development.")
    print("It raises ValueError if sensor readings are out of expected ranges.")
    print("Example: ThermostatStatus.from_dict(api_data, strict=True)")
    print()
    print("In production, use default mode (strict=False) which logs warnings")


def show_help():
    """Show available usage information."""
    print("=" * 70)
    print("pyairobotrest - Airobot Thermostat API Library Examples")
    print("=" * 70)
    print()
    print("Usage:")
    print("  python example.py               # Run all examples")
    print("  python example.py --help        # Show this help")
    print()
    print("Environment variables (optional - overrides hardcoded values):")
    print("  AIROBOT_HOST       Thermostat IP address (default: 192.168.1.100)")
    print("  AIROBOT_USERNAME   Device ID (default: T01XXXXXX)")
    print("  AIROBOT_PASSWORD   Password (default: your_password)")
    print()
    print("Examples:")
    print("  export AIROBOT_HOST=192.168.1.100")
    print("  export AIROBOT_USERNAME=T01123456")
    print("  export AIROBOT_PASSWORD=mypassword")
    print("  python example.py")
    print()
    print("For individual setting methods, see example_individual_settings.py")
    print()


if __name__ == "__main__":
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "help"):
        show_help()
        sys.exit(0)

    # Get credentials from environment or use placeholders
    host = os.getenv("AIROBOT_HOST", "192.168.1.100")
    username = os.getenv("AIROBOT_USERNAME", "T01XXXXXX")
    password = os.getenv("AIROBOT_PASSWORD", "your_password")

    print("=" * 70)
    print("pyairobotrest LIBRARY - COMPREHENSIVE EXAMPLES")
    print("=" * 70)
    print()
    print(f"Using credentials: {username}@{host}")
    print("(Set AIROBOT_HOST, AIROBOT_USERNAME, AIROBOT_PASSWORD to override)")
    print()

    # Note: Functions use hardcoded credentials; they'll be updated via env vars above

    # Run all examples
    asyncio.run(main())
    print("\n")
    asyncio.run(factory_method_example())
    print("\n")
    asyncio.run(context_manager_example())
    print("\n")
    asyncio.run(strict_validation_example())

    print()
    print("=" * 70)
    print("Examples completed! 🚀")
    print("For individual setting methods, use: example_individual_settings.py")
    print("=" * 70)
