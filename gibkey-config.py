import usb.core
import usb.util
import time
import argparse

LIGHT_PATTERNS = {
    'Custom': 0,
    'Runner\'s Light': 1,
    'Static': 3,
    'Breathe': 4,
    'Flower': 5,
    'Wave': 6,
    'Wave Vertical': 7,
    'Bubbler': 8,
    'Wave Light': 9,
    'Vortex': 10,
    'Wave Bar': 22,
    'Sea Wave': 12,
    'Ripple': 13,
    'Star': 20,
    'Single': 15,
    'Cell': 16
}

# Constants for vendor and product IDs (replace with your actual values)
VENDOR_ID = 0x258A  # Your vendor ID
PRODUCT_ID = 0x0049  # Your product ID

def parse_args():
    parser = argparse.ArgumentParser(description="Control lighting patterns and brightness.")
    parser.add_argument(
        "-p", "--pattern", type=str,
        help="Specify the lighting pattern (e.g., 'wave', 'static')."
    )
    parser.add_argument(
        "-b", "--brightness", type=int, choices=range(0, 101), metavar="[0-100]",
        help="Set brightness level (0-100)."
    )
    parser.add_argument(
        "-c", "--color", type=str, metavar="[000000-FFFFFF]",
        help="Set RGB color (000000-FFFFFF)."
    )
    parser.add_argument(
        "-d", "--direction", type=str, choices=["normal", "reverse"], metavar="[normal/reverse]",
        help="Set animation direction (normal/reverse)."
    )
    parser.add_argument(
        "-s", "--speed", type=int, choices=range(1, 6), metavar="[1-5]",
        help="Set animation speed (1-5)."
    )

    args = parser.parse_args()

    # Process pattern
    pattern = args.pattern
    if pattern is not None:
        matched_pattern = None
        for index, original_pattern in enumerate(LIGHT_PATTERNS):
            # Match formatted input against formatted version of the pattern list
            formatted_original = original_pattern.lower().replace(' ', '_').replace('\'', '')
            if pattern == formatted_original:
                matched_pattern = (index, original_pattern)
                break

        if matched_pattern:
            index, original_pattern = matched_pattern
            pattern = original_pattern
        else:
            print(f"Error: Pattern '{formatted_pattern}' is not valid.")
    else:
        print("No pattern selected.")

    # Process brightness
    brightness = args.brightness
    if brightness is None:
        brightness = 50

    # Process color
    color = args.color
    if color is None:
        color = "default"

    # Process direction
    direction = 0
    if direction is None or args.direction == "reverse":
        direction = 1

    # Process speed
    speed = args.speed
    if speed is None:
        speed = 2
    speed = 5 - speed
    
    return (pattern, brightness, color, direction, speed)

# Find and set up USB device
def setup_device():
    # Find the device
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if device is None:
        raise ValueError("Device not found")
    device.set_configuration()
    
    mi_02_interface = None
    for cfg in device:
        for intf in cfg:
            if intf.bInterfaceNumber == 2:  # MI_02 is interface number 2
                mi_02_interface = intf
                break
        if mi_02_interface:
            break

    # Ensure we found the MI_02 interface
    if mi_02_interface is None:
        raise ValueError("MI_02 interface not found")

    # Select the OUT endpoint of the MI_02 interface
    out_endpoint = None
    for ep in mi_02_interface:
        ep_address = ep.bEndpointAddress
        if usb.util.endpoint_direction(ep_address) == usb.util.ENDPOINT_OUT:
            out_endpoint = ep
            break

    # Ensure we found the OUT endpoint
    if out_endpoint is None:
        raise ValueError("OUT endpoint for MI_02 not found")
    
    return (device, out_endpoint)

# Function to generate the packet with dynamic verification and brightness
def generate_packet(pattern_int, brightness_int, speed_int, direction_int, color):

    # Convert integer brightness_int to a two-digit hex string
    brightness = f"{brightness_int:02x}"
    pattern = f"{pattern_int:02x}"

    # Add up the RGB values
    use_default_color = f"{int(color == "default"):02x}"
    color_total = "0"
    if (color == "default"):
        color = "ffffff"

    if (len(color) != 6):
        raise ValueError("Color value is invalid")
    color_byte1 = int(color[0:2], 16)
    color_byte2 = int(color[2:4], 16)
    color_byte3 = int(color[4:6], 16)
    color_total = f"{((color_byte1 + color_byte2 + color_byte3) % 0x100):02x}"  # Modulo 0x100 ensures roll over

    # Set direction value
    direction = f"{direction_int:02x}"
    
    # Set speed value
    speed = f"{speed_int:02x}"

    # Replace verification and brightness in the packet template
    packet_data = f"2000000002aa{pattern}{brightness}{speed}{direction}{use_default_color}00{color}0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000"
    
    # Generate verification bytes
    # Old version: 
    verification = 0x00
    packet_bytes = bytearray.fromhex(packet_data)
    packet_bytes.reverse()
    for byte in packet_bytes:
        verification = (verification + byte) % 0x100
    verification = f"{((brightness_int + pattern_int + speed_int + direction_int + int(color_total, 16) + int(use_default_color,16) + 0xC8) % 0x100):02x}"
    packet = f"550600{verification}{packet_data}"

    return packet


# Send the data in chunks
def send_data_in_chunks(device, out_endpoint, data):
    chunk_size = 64
    retries = 5
    timeout = 1000  # Timeout in milliseconds
    for start in range(0, len(data), chunk_size):
        chunk = data[start:start + chunk_size]
        print(f"Sending chunk: {chunk.hex()}")

        # Retry mechanism
        for attempt in range(retries):
            try:
                # Send chunk to the OUT endpoint
                device.write(out_endpoint.bEndpointAddress, chunk, timeout=timeout)
                print("Chunk sent successfully!")
                break
            except usb.core.USBError as e:
                print(f"Error during data transfer: {e}")
                if attempt < retries - 1:
                    print(f"Retrying in 1 second...")
                    time.sleep(1)
                else:
                    print("Max retries reached. Failed to send chunk.")

# Set light pattern
def set_pattern(device, out_endpoint, pattern_val, brightness_val, speed_val, direction_val, color = "000000"):
    send_data_in_chunks(device, out_endpoint, bytes.fromhex(generate_packet(LIGHT_PATTERNS[pattern_val], brightness_val, speed_val, direction_val, color)))

# Run the program
def run_program():
    pattern, brightness, color, direction, speed = parse_args()
    device, out_endpoint = setup_device()
    set_pattern(device, out_endpoint, pattern, brightness, speed, direction, color)

run_program()

# 550600 {verification} 2000000002aa {pattern}{brightness} {speed}{direction}{use_default_color}00 {color} 0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 f0             2000000002aa 001e                  01000100                                38e3ed  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 32             2000000002aa 1664                  01000000                                f0fe01  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 34             2000000002aa 065c                  01000100                                38e3ed  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 35             2000000002aa 065c                  01010100                                38e3ed  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 2f             2000000002aa 0664                  00000000                                ffffff  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 35             2000000002aa 0664                  04010100                                ffffff  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000