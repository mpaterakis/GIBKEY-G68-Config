import usb.core
import usb.util
import time
import argparse
import json
if True:
    from tkinter import *

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

KEY_CODES_SORTED = {
    'escape': 0x29,
    'tilde': 0x35,
    'tab': 0x2B,
    'capslock': 0x39,
    'lshift': 0xE1,
    'lctrl': 0xE0,
    'f1': 0x3A,
    '1': 0x1E,
    'q': 0x14,
    'a': 0x04,
    'z': 0x1D,
    'lwin': 0xE3,
    'f2': 0x3B,
    '2': 0x1F,
    'w': 0x1A,
    's': 0x16,
    'x': 0x1B,
    'lalt': 0xE2,
    'f3': 0x3C,
    '3': 0x20,
    'e': 0x08,
    'd': 0x07,
    'c': 0x06,
    'unknown1': 0x00,
    'f4': 0x3D,
    '4': 0x21,
    'r': 0x15,
    'f': 0x09,
    'v': 0x19,
    'unknown2': 0x00,
    'f5': 0x3E,
    '5': 0x22,
    't': 0x17,
    'g': 0x0A,
    'b': 0x05,
    'space': 0x2C,
    'f6': 0x3F,
    '6': 0x23,
    'y': 0x1C,
    'h': 0x0B,
    'n': 0x11,
    'unknown3': 0x00,
    'f7': 0x40,
    '7': 0x24,
    'u': 0x18,
    'j': 0x0D,
    'm': 0x10,
    'unknown4': 0x00,
    'f8': 0x41,
    '8': 0x25,
    'i': 0x0C,
    'k': 0x0E,
    'comma': 0x36,
    'unknown5': 0x00,
    'f9': 0x42,
    '9': 0x26,
    'o': 0x12,
    'l': 0x0F,
    'period': 0x37,
    'unknown6': 0x00,
    'f10': 0x43,
    '0': 0x27,
    'p': 0x13,
    'semicolon': 0x33,
    'slash': 0x38,
    'ralt': 0xE6,
    'f11': 0x44,
    'dash': 0x2D,
    'lbracket': 0x2F,
    'quote': 0x34,
    'unknown7': 0x00,
    'unknown8': 0x00,
    'f12': 0x45,
    'equals': 0x2E,
    'rbracket': 0x30,
    'unknown9': 0x00,
    'rshift': 0xE5,
    'fn': 0x00,
    'unknown10': 0x00,
    'backspace': 0x2A,
    'backslash': 0x31,
    'enter': 0x28,
    'unknown11': 0x00,
    'rctrl': 0xE4,
    'unknown12': 0x00,
    'unknown13': 0x00,
    'delete': 0x4C,
    'unknown14': 0x00,
    'unknown15': 0x00,
    'left': 0x50,
    'unknown16': 0x00,
    'print_screen': 0x46,
    'pause': 0x48,
    'scroll_lock': 0x47,
    'up': 0x52,
    'down': 0x51,
    'insert': 0x49,
    'pageup': 0x4B,
    'pagedown': 0x4E,
    'home': 0x4A,
    'end': 0x4D,
    'right': 0x4F,
    'function_toggle_rgb': 0xf03c00,
    'function_swap_wasd': 0xF00300,
    'function_change_keyboard_index': 0xF05200,
    'function_change_rgb_color': 0xf02b00,
    'function_change_rgb_pattern': 0xf01000,
    'function_increase_rgb_brightness': 0xf02500,
    'function_decrease_rgb_brightness': 0xf02600,
    'function_make_rgb_faster': 0xf02700,
    'function_make_rgb_slower': 0xf01800,
    'function_toggle_charging_light': 0xf05100,
    'function_bt_matching_2': 0xf04002,
    'function_bt_matching_3': 0xf04003,
    'function_reset_settings': 0xf02c00,
    'function_bt_matching_1': 0xf04001,
    'function_mac_mode': 0xf00500,
    'function_windows_mode': 0xf00600,
    'function_enter_wired_mode': 0xf04004,
    'function_enter_wireless_mode': 0xf04000,
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
    parser = argparse.ArgumentParser(description="Fully configure your GIBKEY G68")
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
        "-kc", "--key-color", type=str, nargs='+', metavar="[key=color]",
        help="Set inidividual key rgb (key=color). For example '-kc a=ffffff b=000000 enter=010101'"
    )
    parser.add_argument(
        "-km", "--key-map", type=str, nargs='+', metavar="[key=mapped_key]",
        help="Set inidividual key map (key=mapped_key). For FN mappings, append _fn to the key name. For example '-km a=up b=escape x=u pageup_fn=home'."
    )
    parser.add_argument(
        "--list-keys", action='store_true', help="List all usable key names."
    )
    parser.add_argument(
        "--list-patterns", action='store_true', help="List all usable pattern names."
    )
    parser.add_argument(
        "-o", "--config-output", type=str, metavar="<filepath>", help="Save the given config in a JSON file."
    )
    parser.add_argument(
        "-i", "--config-input", type=str, metavar="<filepath>", help="Load the config from a JSON file."
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

    # Process key_color
    key_color = {}
    if (args.key_color != None):
        try:
            key_color = dict(pair.split('=') for pair in args.key_color)
        except:
            ValueError(f"Error: key_color is not valid.")

    # Process key_map
    key_map = {}
    if (args.key_map != None):
        try:
            if "default" in args.key_map:
                key_map = {"default"}
            else:
                key_map = dict(pair.split('=') for pair in args.key_map)
        except:
            ValueError(f"Error: key_map is not valid.")

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

    # Process config
    config_output = args.config_output
    config_input = args.config_input

    return (pattern, brightness, color, direction, speed, key_color, key_map, config_output, config_input)

# List usable keys
def list_keys():
    for index, key in enumerate(KEY_CODES_SORTED):
        if "unknown" not in key and "function" not in key: 
            print(key)
    print("all [RGB ONLY] Fallback color for all unspecified keys")
    print("default [REMAP ONLY] Reset all keys to default")

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
    timeout = 1500
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

# Split the string into different packets
def split_data_into_packets(data, header):
    packets = []
    current_data_length = 0

    # Split data into parts
    parts = [data[i:i + 112] for i in range(0, len(data), 112)]
    if len(parts[-1]) < 112:
        parts[-1] = parts[-1].ljust(112, '0')  # Pad with '0' if less than 112

    # Generate the packets using the header, signature, size and data parts
    for part in parts:
        first_index_byte = int(current_data_length/0x100)
        second_index_byte = (current_data_length % 0x100)
        packet_data = f"38{second_index_byte:02x}{first_index_byte:02x}00{part}"

        verification = generate_verification(packet_data)
        packet = f"{header}{verification}{packet_data}"
        packets.append(packet)
        current_data_length = current_data_length + 0x38
    
    return packets

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
def generate_key_rgb_packets(key_color):
    current_data_length = 0

    # Create hex string with RGB values for each key
    data = ""
    for index, key in enumerate(KEY_CODES_SORTED):
        color = "000000"
        if key in key_color:
            color = key_color[key]
        elif 'all' in key_color:
            color = key_color['all']
        data += color
    
    packets = split_data_into_packets(data, "550b00")

    return packets

# Generate the packets for indivual key remaps
def generate_key_map_packets(key_map):

    # Create hex string with keymap values for each key
    data = ""
    for index, key in enumerate(KEY_CODES_SORTED):
        data += "1000"
        mapped_key = key

        # Ignore functions
        if "function" in key:
            mapped_key = "unknown1"
            
        if "default" not in key_map and key in key_map:
            mapped_key = key_map[key] # Set remap value
        data += f"{KEY_CODES_SORTED[mapped_key]:02X}"

        divider = "1000"

        # Apply default FN layer values
        if key in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            mapped_key = "f" + key
        elif key == "0":
            mapped_key = "f10"
        elif key == "dash":
            mapped_key = "f11"
        elif key == "equals":
            mapped_key = "f12"
        elif key == "rbracket":
            mapped_key = "end"
        elif key == "lbracket":
            mapped_key = "home"
        elif key == "delete":
            mapped_key = "insert"
        elif key == "pageup":
            mapped_key = "pause"
        elif key == "pagedown":
            mapped_key = "scroll_lock"
        elif key == "tilde":
            mapped_key = "print_screen"
        elif key == "p":
            mapped_key = "function_toggle_rgb"
            divider = ""
        elif key == "left":
            mapped_key = "function_make_rgb_slower"
            divider = ""
        elif key == "right":
            mapped_key = "function_make_rgb_faster"
            divider = ""
        elif key == "up":
            mapped_key = "function_increase_rgb_brightness"
            divider = ""
        elif key == "down":
            mapped_key = "function_decrease_rgb_brightness"
            divider = ""
        elif key == "backslash":
            mapped_key = "function_change_rgb_pattern"
            divider = ""
        elif key == "tab":
            mapped_key = "function_change_rgb_color"
            divider = ""
        elif key == "w":
            mapped_key = "function_swap_wasd"
            divider = ""
        elif key == "space":
            mapped_key = "function_change_keyboard_index"
            divider = ""
        elif key == "l":
            mapped_key = "function_toggle_charging_light"
            divider = ""
        elif key == "e":
            mapped_key = "function_bt_matching_1"
            divider = ""
        elif key == "r":
            mapped_key = "function_bt_matching_2"
            divider = ""
        elif key == "t":
            mapped_key = "function_bt_matching_3"
            divider = ""
        elif key == "escape":
            mapped_key = "function_reset_settings"
            divider = ""
        elif key == "period":
            mapped_key = "function_mac_mode"
            divider = ""
        elif key == "comma":
            mapped_key = "function_windows_mode"
            divider = ""
        elif key == "y":
            mapped_key = "function_enter_wired_mode"
            divider = ""
        elif key == "q":
            mapped_key = "function_enter_wireless_mode"
            divider = ""
        
        # Set FN layer value
        if "default" not in key_map and f"{key}_fn" in key_map:
            mapped_key = key_map[f"{key}_fn"]
            divider = "1000"
        data += divider + f"{KEY_CODES_SORTED[mapped_key]:02X}"

    packets = split_data_into_packets(data, "550900")

    return packets

# Set light pattern
def set_pattern(pattern_val, brightness_val, speed_val, direction_val, color = "000000"):
    send_data(bytes.fromhex(generate_pattern_packet(RGB_PATTERNS[pattern_val], brightness_val, speed_val, direction_val, color)))

# Set individual key RGB
def set_keys_color(key_color):
    for packet_data in generate_key_rgb_packets(key_color):
        send_data(bytes.fromhex(packet_data))
        time.sleep(0.2)

# Set inidividual key mappings
def set_key_map(key_map):
    for packet_data in generate_key_map_packets(key_map):
        send_data(bytes.fromhex(packet_data))
        time.sleep(0.2)

# Load config from JSON file
def load_config(pattern, brightness, color, direction, speed, key_map, key_color, config_input):
    with open(config_input, "r") as input_file:
        json_file = json.load(input_file)
        
        # Add the stored values to the given key_map and key_color object.
        # Config values don't override ones already in key_map and key_color.
        if "key_map" in json_file:
            for index, key in enumerate(json_file["key_map"]):
                if key not in key_map:
                    key_map[key] = json_file["key_map"][key]
        if "key_color" in json_file:
            for index, key in enumerate(json_file["key_color"]):
                if key not in key_color:
                    key_color[key] = json_file["key_color"][key]
        if "pattern" in json_file and pattern is None:
            pattern = json_file["pattern"]
        
        return (pattern, brightness, color, direction, speed, key_map, key_color)

# Save config to JSON file
def save_config(pattern, brightness, color, direction, speed, key_map, key_color, config_output):
    out_key_map = {}
    if "default" not in key_map: # Ignore key_map if default value is used
        out_key_map = key_map
    config = {"key_color": key_color, "key_map": out_key_map, "brightness": brightness, "color": color, "direction": direction, "speed": speed}
    
    if pattern != None:
        config["pattern"] = pattern

    with open(config_output, "w") as json_file:
        json.dump(config, json_file, indent=2)

# Show the GUI
def load_gui():
    import tkinter as tk
    from tkinter import ttk

    # Create main window
    root = Tk()

    # Create fields
    root.title("GIBKEY G68 Config")
    root.configure(bg="#2E2E2E")  # Set a dark background

    # Create styles
    label_style = {"bg": "#2E2E2E", "fg": "#FFFFFF", "font": ("Arial", 12)}
    entry_style = {"bg": "#3C3C3C", "fg": "#FFFFFF", "insertbackground": "#FFFFFF", "highlightbackground": "#5A5A5A", "relief": "flat"}
    style = ttk.Style()
    style.theme_use("clam")  # Use a modern theme
    style.configure(
        "TButton",
        background="#4CAF50",
        foreground="#FFFFFF",
        font=("Arial", 12),
        padding=0,
        borderwidth=0
    )
    style.map(
        "TButton",
        background=[("active", "#45A049"), ("pressed", "#3E8E41")],
        foreground=[("disabled", "#808080")],
    )

    # Frame for fields on the left
    fields_frame = tk.Frame(root, bg="#2E2E2E")
    fields_frame.pack(side="left", padx=20, pady=20, fill="y")

    # Add labels and fields
    fields = []
    for i in range(5):
        row_frame = tk.Frame(fields_frame, bg="#2E2E2E")
        row_frame.pack(fill="x", pady=5)

        label = tk.Label(row_frame, text=f"Field {i+1}:", **label_style)
        label.pack(side="left", padx=5)

        entry = tk.Entry(row_frame, **entry_style)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        fields.append(entry)

    # Add config buttons
    buttons_frame = tk.Frame(fields_frame, bg="#2E2E2E")
    buttons_frame.pack(pady=10)
    load_button = ttk.Button(buttons_frame, text="Load Config", padding=5)
    load_button.pack(side="left", padx=20)
    save_button = ttk.Button(buttons_frame, text="Save Config", padding=5)
    save_button.pack(side="left", padx=20)

    # Keyboard layout
    keyboard_frame = tk.Frame(root, bg="#2E2E2E")
    keyboard_frame.pack(side="left", padx=20, pady=20)
    keyboard_buttons = [
        ["Esc", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace", "~"],
        ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\", "Del"],
        ["CapsLock", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter", "PU"],
        ["LShift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "RShift", "Up", "PD"],
        ["LCtrl", "LWin", "LAlt", "Space", "RAlt", "Fn", "RCtrl", "Left", "Down", "Right"]
    ]

    # Button sizes
    key_width = 5
    key_spacing = 5
    special_keys = {
        "Backspace": 2 * (key_width) - 1,
        "Tab": 1.5 * (key_width),
        "\\": 1.5 * (key_width),
        "CapsLock": 1.75 * (key_width),
        "LShift": 2 * (key_width),
        "Space": 7 * (key_width) + 1,
        "Enter": 2.5 * (key_width),
        "RShift": 1.75 * (key_width) + 2,
        "LCtrl": 1.25 * (key_width),
        "LWin": 1.25 * (key_width),
        "LAlt": 1.25 * (key_width) + 1
    }

    # Add buttons to frame
    for row in keyboard_buttons:
        row_frame = tk.Frame(keyboard_frame, bg="#2E2E2E")
        for key in row:
            width = special_keys.get(key, key_width)
            button = ttk.Button(row_frame, text=key, width=int(width), style="TButton")
            button.pack(side="left", padx=key_spacing, ipady=12, pady=5)
        row_frame.pack()

    # Run the gui
    root.mainloop()

# Run the program
def run_program():
    # Load USB device and arguments
    setup_device()
    pattern, brightness, color, direction, speed, key_color, key_map, config_output, config_input = parse_args()

    # If no usable parameters are given, load the GUI
    if (len(key_map) < 1 and len(key_color) < 1 and pattern == None):
        load_gui()
    else:
        # CLI functionality
        # Load config
        if (config_input != None):
            pattern, brightness, color, direction, speed, key_map, key_color = load_config(pattern, brightness, color, direction, speed, key_map, key_color, config_input)
        
        # Load key maps
        if (len(key_map) > 0):
            set_key_map(key_map)

        # Load key RGB or pattern
        if (len(key_color) > 0):
            set_pattern('custom', brightness, speed, direction)
            set_keys_color(key_color)
        elif (pattern != None):
            set_pattern(pattern, brightness, speed, direction, color)

        # Save config
        if (config_output != None):
            save_config(pattern, brightness, color, direction, speed, key_map, key_color, config_output)


# Run the main functionality
run_program()