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

KEY_INDEXES = {
    'esc': 0,
    'tilde': 1,
    'tab': 2,
    'capslock': 3,
    'lshift': 4,
    'lctrl': 5,
    'unknown': 6,
    '1': 7,
    'q': 8,
    'a': 9,
    'z': 10,
    'lwin': 11,
    'unknown2': 12,
    '2': 13
}

# Constants for vendor and product IDs
VENDOR_ID = 0x258A
PRODUCT_ID = 0x0049

device = None
out_endpoint = None

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
    global device, out_endpoint
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

# Send the data to the USB device
def send_data(data):
    global device, out_endpoint
    retries = 5
    timeout = 1000
    for attempt in range(retries):
        try:
            device.write(out_endpoint.bEndpointAddress, data, timeout=timeout)
            print(f"Packet sent: {data.hex()}")
            break
        except usb.core.USBError as e:
            print(f"Error during data transfer: {e}")
            if attempt < retries - 1:
                print(f"Retrying...")
                time.sleep(1)
            else:
                print("Max retries reached. Failed to send chunk.")

# Generate packet verificationgenerate_verification
def generate_verification(packet_data):
    verification = 0x00
    packet_bytes = bytearray.fromhex(packet_data)
    packet_bytes.reverse()
    for byte in packet_bytes:
        verification = (verification + byte)
    verification = f"{(verification % 0x100):02x}"

    return verification

# Generate the pattern packet
def generate_pattern_packet(pattern_int, brightness_int, speed_int, direction_int, color):
    brightness = f"{brightness_int:02x}"
    pattern = f"{pattern_int:02x}"

    # Add up the RGB values
    use_default_color = f"{int(color == "default"):02x}"
    color_total = "0"
    if (color == "default"):
        color = "ffffff"

    if (len(color) != 6):
        raise ValueError("Color value is invalid")

    # Set direction value
    direction = f"{direction_int:02x}"
    
    # Set speed value
    speed = f"{speed_int:02x}"

    # Create the packet data
    packet_data = f"2000000002aa{pattern}{brightness}{speed}{direction}{use_default_color}00{color}0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000"
    
    # Generate verificationgenerate_verification
    verification = generate_verification(packet_data)
    packet = f"550600{verification}{packet_data}"

    return packet

# Generate the packets for indivual key RGB
def generate_key_rgb_packets():
    packets = []
    current_data_length = 0

    line1 = ""

    color = "ff0000"
    for index, key in enumerate(KEY_INDEXES):
        color = "ff0000"
        if index % 5 == 0:
            color = "ff0000"
        elif index % 5 == 1:
            color = "00ff00" 
        elif index % 5 == 2:
            color = "0000ff" 
        elif index % 5 == 3:
            color = "ffffff"
        elif index % 5 == 4:
            color = "000000" 
            
        # if (index < 2): color = "000000" 
        print(index % 5, key, " -> ", color)
        line1 += color
    
    print(line1)


    for i in range(1,2):
        first_index_byte = int(current_data_length/0x100)
        second_index_byte = (current_data_length % 0x100)
        packet_data = f"38{second_index_byte:02x}{first_index_byte:02x}00{line1}0000000000000000000000000000"

        verification = generate_verification(packet_data)
        packet = f"550b00{verification}{packet_data}"
        packets.append(packet)
        current_data_length = current_data_length + 0x38

    return packets

# Set light pattern
def set_pattern(pattern_val, brightness_val, speed_val, direction_val, color = "000000"):
    send_data(bytes.fromhex(generate_pattern_packet(LIGHT_PATTERNS[pattern_val], brightness_val, speed_val, direction_val, color)))

# Set key RGB
def set_keys_rgb():
    for packet_data in generate_key_rgb_packets():
        send_data(bytes.fromhex(packet_data))
        time.sleep(0.1)

# Run the program
def run_program():
    pattern, brightness, color, direction, speed = parse_args()
    setup_device()
    set_keys_rgb()
    

run_program()

# 550600 {verification} 2000000002aa {pattern}{brightness} {speed}{direction}{use_default_color}00 {color} 0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 f0             2000000002aa 001e                  01000100                                38e3ed  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 32             2000000002aa 1664                  01000000                                f0fe01  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 34             2000000002aa 065c                  01000100                                38e3ed  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 35             2000000002aa 065c                  01010100                                38e3ed  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 2f             2000000002aa 0664                  00000000                                ffffff  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000
# 550600 35             2000000002aa 0664                  04010100                                ffffff  0000ff00000400000100000000ffffffffffffffff000000000000000000000000000000000000000000000000

# Single key LED commands
# 550b00 56             38 000000 ffffff{rgb1}{rgb1}{rgb1}{rgb1}{rgb2}000000{rgb1}{rgb1}{rgb1}{rgb1}{rgb2}000000{rgb1}{rgb1}{rgb1}{rgb1}{rgb2}0000
# 550b00 47             38 380000 00{rgb1}{rgb1}{rgb1}{rgb1}000000000000{rgb1}{rgb1}{rgb1}{rgb1}000000000000{rgb1}{rgb1}{rgb1}{rgb1}{rgb1}0000007e
# 550b00 83             38 700000 00ff{rgb1}{rgb1}{rgb1}000000000000{rgb1}{rgb1}{rgb1}{rgb1}000000000000{rgb1}{rgb1}{rgb1}{rgb1}000000000000{rgb1}
# 550b00 3a             38 a80000 {rgb1}{rgb1}{rgb1}000000000000{rgb1}{rgb1}{rgb1}{rgb1}{rgb1}000000{rgb1}{rgb1}{rgb1}000000000000000000{rgb1}7e00
# 550b00 33             38 e00000 ff000000{rgb1}{rgb1}000000{rgb1}{rgb1}{rgb1}000000{rgb2}000000000000{rgb1}000000000000{rgb2}00000000000000000000
# 550b00 0e             38 180100 0000{rgb2}{rgb2}000000ff00fc{rgb1}000000000000{rgb2}000000000000000000000000000000000000000000000000000000000000
# 550b00 81             30 500100 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 <= might be unused, or it could be the end call
# 550b00 29             38 000000 ff000000ff000000ffffffff000000ff000000ff000000ffffffff000000ff000000ff000000ff000000000000000000000000000000000000