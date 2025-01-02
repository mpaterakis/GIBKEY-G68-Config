import usb.core
import usb.util
import time
import argparse

RGB_PATTERNS = {
    'custom': 0,
    'runners_light': 1,
    'static': 3,
    'breathe': 4,
    'flower': 5,
    'wave': 6,
    'wave_vertical': 7,
    'bubbler': 8,
    'wave_light': 9,
    'vortex': 10,
    'wave_bar': 22,
    'sea_wave': 12,
    'ripple': 13,
    'star': 20,
    'single': 15,
    'cell': 16
}

KEY_INDEXES = {
    'esc': 0,
    'tilde': 1,
    'tab': 2,
    'capslock': 3,
    'lshift': 4,
    'lctrl': 5,
    'unknown1': 6,
    '1': 7,
    'q': 8,
    'a': 9,
    'z': 10,
    'lwin': 11,
    'unknown2': 12,
    '2': 13,
    'w': 14,
    's': 15,
    'x': 16,
    'lalt': 17, 
    'unknown3': 18,
    '3': 19,
    'e': 20,
    'd': 21,
    'c': 22,
    'unknown4': 23,
    'unknown5': 24,
    '4': 25,
    'r': 26,
    'f': 27,
    'v': 28,
    'unknown6': 29,
    'unknown7': 30,
    '5': 31,
    't': 32,
    'g': 33,
    'b': 34,
    'space': 35,
    'unknown9': 36,
    '6': 37,
    'y': 38,
    'h': 39,
    'n': 40,
    'unknown10': 41,
    'unknown11': 42,
    '7': 43,
    'u': 44,
    'j': 45,
    'm': 46,
    'unknown12': 47,
    'unknown13': 48,
    '8': 49,
    'i': 50,
    'k': 51,
    'comma': 52,
    'unknown14': 53,
    'unknown15': 54,
    '9': 55,
    'o': 56,
    'l': 57,
    'period': 58,
    'unknown16': 59,
    'unknown17': 60,
    '0': 61,
    'p': 62,
    'semicolon': 63,
    'slash': 64,
    'lalt': 65,
    'unknown18': 66,
    'unknown19': 67,
    'minus': 68,
    'lbracket': 69,
    'quote': 70,
    'unknown20': 71,
    'unknown21': 72,
    'unknown22': 73,
    'plus': 74,
    'rbracket': 75,
    'unknown23': 76,
    'rshift': 77,
    'fn': 78,
    'unknown24': 79,
    'backspace': 80,
    'backslash': 81,
    'enter': 82,
    'unknown25': 83,
    'rctrl': 84,
    'unknown26': 85,
    'unknown27': 86,
    'delete': 87,
    'unknown28': 88,
    'unknown29': 89,
    'left': 90,
    'unknown31': 91,
    'unknown32': 92,
    'unknown33': 93,
    'unknown34': 94,
    'up': 95,
    'down': 96,
    'unknown35': 97,
    'pageup': 98,
    'pagedown': 99,
    'unknown36': 100,
    'unknown37': 101,
    'right': 102
}

# Constants for vendor and product IDs
VENDOR_ID = 0x258A
PRODUCT_ID = 0x0049

device = None
out_endpoint = None
parser = None
silent = False

def parse_args():
    global parser
    parser = argparse.ArgumentParser(description="Configure your GIBKEY G68 to your heart's desire")
    parser.add_argument(
        "-s", "--silent", action='store_true', help="Shoosh."
    )
    parser.add_argument(
        "-p", "--pattern", type=str,
        help="Specify the lighting pattern (e.g., 'wave', 'static')"
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
        "-sp", "--speed", type=int, choices=range(1, 6), metavar="[1-5]",
        help="Set animation speed (1-5)."
    )
    parser.add_argument(
        "-kc", "--keys_color", type=str, nargs='+', metavar="[key=color]",
        help="Set inidividual key rgb (key=color). For example '-kc a=ffffff b=000000 enter=010101'"
    )
    parser.add_argument(
        "--list_keys", action='store_true', help="List all usable key names."
    )
    parser.add_argument(
        "--list_patterns", action='store_true', help="List all usable pattern names."
    )

    args = parser.parse_args()

    # Process silent
    global silent, show_help
    silent = args.silent

    # Process list
    if (args.list_keys):
        list_keys()
    elif (args.list_patterns):
        list_patterns()

    # Process keys_color
    keys_color = {}
    if (args.keys_color != None):
        try:
            keys_color = dict(pair.split('=') for pair in args.keys_color)
        except:
            ValueError(f"Error: keys_color is not valid.")

    # Process pattern
    pattern = args.pattern
    if pattern is not None:
        if pattern not in RGB_PATTERNS:
            raise ValueError(f"Error: Given pattern is not valid.")

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

    return (pattern, brightness, color, direction, speed, keys_color)

# List usable keys
def list_keys():
    for index, key in enumerate(KEY_INDEXES):
        if ('unknown' not in key): 
            print(key)
    print("all (fallback color for all unspecified keys)")

# List usable patterns
def list_patterns():
    for index, key in enumerate(RGB_PATTERNS): 
        print(key)

# Find and set up USB device
def setup_device():
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
    global device, out_endpoint, silent
    retries = 5
    timeout = 1000
    for attempt in range(retries):
        try:
            device.write(out_endpoint.bEndpointAddress, data, timeout=timeout)
            if not silent:
                print(f"Packet sent: {data.hex()}")
            break
        except usb.core.USBError as e:
            if not silent:
                print(f"Error during data transfer: {e}")
            if attempt < retries - 1:
                if not silent:
                    print(f"Retrying...")
                time.sleep(1)
            else:
                raise RuntimeError("Max retries reached. Failed to send chunk.")

# Generate packet verification
def generate_verification(packet_data):
    verification = 0x00
    packet_bytes = bytearray.fromhex(packet_data)
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
def generate_key_rgb_packets(keys_color):
    packets = []
    current_data_length = 0

    # Create hex string with RGB values for each key
    data = ""
    for index, key in enumerate(KEY_INDEXES):
        color = "000000"
        if key in keys_color:
            color = keys_color[key]
        elif 'all' in keys_color:
            color = keys_color['all']
        data += color
    
    # Split the string into different packets
    parts = [data[i:i + 112] for i in range(0, len(data), 112)]
    if len(parts[-1]) < 112:
        parts[-1] = parts[-1].ljust(112, '0')  # Pad with '0' if less than 112

    for part in parts:
        first_index_byte = int(current_data_length/0x100)
        second_index_byte = (current_data_length % 0x100)
        packet_data = f"38{second_index_byte:02x}{first_index_byte:02x}00{part}"

        verification = generate_verification(packet_data)
        packet = f"550b00{verification}{packet_data}"
        packets.append(packet)
        current_data_length = current_data_length + 0x38

    return packets

# Set light pattern
def set_pattern(pattern_val, brightness_val, speed_val, direction_val, color = "000000"):
    send_data(bytes.fromhex(generate_pattern_packet(RGB_PATTERNS[pattern_val], brightness_val, speed_val, direction_val, color)))

# Set individual key RGB
def set_keys_color(keys_color):
    for packet_data in generate_key_rgb_packets(keys_color):
        send_data(bytes.fromhex(packet_data))
        time.sleep(0.1)

# HELP!
def show_help():
    global parser, show_help
    if (show_help):
        parser.print_help()

# Run the program
def run_program():
    pattern, brightness, color, direction, speed, keys_color = parse_args()
    setup_device()
    
    if (len(keys_color) > 0):
        set_pattern('custom', brightness, speed, direction)
        set_keys_color(keys_color)
    elif (pattern != None):
        set_pattern(pattern, brightness, speed, direction, color)

# Run the main functionality
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