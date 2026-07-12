import argparse
import asyncio
import json
import logging
from typing import Any

import serial
import serial.tools.list_ports
import websockets

DEFAULT_SERIAL_PORT = "COM3"
DEFAULT_BAUD_RATE = 115200
DEFAULT_WS_URI = "ws://localhost:8000/ws"

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def list_serial_ports() -> list[str]:
    return [port.device for port in serial.tools.list_ports.comports()]


def parse_serial_line(line: str) -> dict[str, Any] | None:
    """Parse either JSON telemetry or CSV telemetry from the Arduino sketch."""
    line = line.strip()
    if not line:
        return None

    # Prefer JSON if the device sends it.
    if line.startswith("{") and line.endswith("}"):
        try:
            payload = json.loads(line)
            return payload
        except json.JSONDecodeError:
            logging.warning("Invalid JSON line received: %s", line)
            return None

    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 5:
        logging.warning("Unexpected CSV format, expected at least 5 values: %s", line)
        return None

    telemetry: dict[str, Any] = {}
    try:
        telemetry["water"] = float(parts[0])
        telemetry["rain"] = float(parts[1])
        telemetry["temp"] = float(parts[2])
        telemetry["humidity"] = float(parts[3])
        telemetry["light"] = float(parts[4])
    except ValueError as e:
        logging.warning("Failed to parse numeric sensor values: %s", e)
        return None

    telemetry["relay"] = parts[5] if len(parts) >= 6 else "off"
    telemetry["led_rgb"] = parts[6] if len(parts) >= 7 else "green"
    telemetry["buzzer"] = parts[7] if len(parts) >= 8 else "silent"

    # Add defaults for keys expected by the Fusion engine.
    telemetry.setdefault("phone", 0.0)
    telemetry.setdefault("movement", 0.0)
    telemetry.setdefault("health", "healthy")
    telemetry.setdefault("language", "english")
    telemetry.setdefault("pose", "vertical")
    telemetry.setdefault("confidence", 0.80)

    return telemetry


async def bridge_serial_to_ws(serial_port: str, baud_rate: int, ws_uri: str) -> None:
    logging.info("Opening serial port %s @ %d", serial_port, baud_rate)
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        while True:
            try:
                logging.info("Connecting to Fusion WebSocket at %s", ws_uri)
                async with websockets.connect(
                    ws_uri,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                    open_timeout=10,
                ) as websocket:
                    logging.info("Connected to Fusion backend. Forwarding telemetry...")
                    while True:
                        raw_line = ser.readline().decode(errors="replace")
                        if not raw_line:
                            await asyncio.sleep(0.05)
                            continue

                        logging.debug("Serial line: %s", raw_line.strip())
                        telemetry = parse_serial_line(raw_line)
                        if telemetry is None:
                            continue

                        try:
                            await websocket.send(json.dumps(telemetry))
                            logging.info("Sent telemetry: %s", telemetry)
                        except Exception as e:
                            logging.error("WebSocket send failed: %s", e)
                            break
                        await asyncio.sleep(0.1)
            except Exception as e:
                logging.error("WebSocket connection failed: %s", e)
                logging.info("Retrying WebSocket connect in 3 seconds...")
                await asyncio.sleep(3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Arduino UNO serial -> Fusion WS bridge")
    parser.add_argument("--port", default=DEFAULT_SERIAL_PORT, help="Serial port for Arduino UNO")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD_RATE, help="Serial baud rate")
    parser.add_argument("--ws", default=DEFAULT_WS_URI, help="Fusion WebSocket URI")
    parser.add_argument("--list", action="store_true", help="List available serial ports")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.list:
        ports = list_serial_ports()
        if ports:
            logging.info("Available serial ports: %s", ", ".join(ports))
        else:
            logging.info("No serial ports found.")
        return

    asyncio.run(bridge_serial_to_ws(args.port, args.baud, args.ws))


if __name__ == "__main__":
    main()
