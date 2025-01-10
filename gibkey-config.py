import usb.core
import usb.util
import time
import argparse
import json

RGB_PATTERNS = {
    'custom': 0,
    'runner_light': 1,
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
DEFAULT_GUI_RGB = "000000"

device = None
out_endpoint = None
parser = None
silent = False
gui_objects = []

###################
## GUI functions ##
###################

# Show the GUI
def load_gui(error_message):
    import os, sys
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

    # If there was any error, show a message and exit
    if error_message != None:
        messagebox.showerror(title="GIBKEY G68 Config", message=error_message)
        return False

    # Create main window
    root = tk.Tk()
    root.title("GIBKEY G68 Config")

    # Load icon
    try:
        if getattr(sys, 'frozen', False):
            # If running as PyInstaller executable
            root.iconbitmap(os.path.join(sys._MEIPASS, "icon.ico"))
        else:
            # If running as a script
            root.iconbitmap(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    except:
        pass

    # Set style
    label_style, entry_style = set_gui_style(root)

    # Create validation entries
    validate_color_hex = root.register(validate_color)
    

    # Create top section
    fields_frame = tk.Frame(root, bg="#2E2E2E")
    fields_frame.pack(side="top", padx=5, pady=5, fill="y")

    pattern_values = []
    for index, pattern in enumerate(RGB_PATTERNS):
        pattern_values.append(pattern.replace("_"," ").title())

    pattern_frame = tk.Frame(fields_frame, bg="#2E2E2E")
    pattern_frame.pack(side="left", padx=5)
    pattern_label = tk.Label(pattern_frame, text="Pattern", **label_style)
    pattern_label.pack(side="left", padx=5)
    pattern_dropdown = ttk.Combobox(pattern_frame, values=pattern_values, style="TCombobox", state="readonly", width=15, name="pattern")
    pattern_dropdown.bind("<<ComboboxSelected>>", lambda event: adjust_key_fields())
    pattern_dropdown.current(1)
    pattern_dropdown.pack(side="right", pady=(1,0))

    color_frame = tk.Frame(fields_frame, bg="#2E2E2E")
    color_frame.pack(side="left", padx=5)
    color_label = tk.Label(color_frame, text="Color", **label_style)
    color_label.pack(side="left", padx=5)
    color_field = tk.Entry(color_frame, **entry_style, width=10, validate="key", validatecommand=(validate_color_hex, "%P"), name="color")
    color_field.insert(0, "Default")
    color_field.pack(side="left")
    color_field.bind("<Button-1>", lambda event: open_color_picker(event, True))
    color_field.bind("<Return>", lambda event: open_color_picker(event, True))
    default_color_button = ttk.Button(color_frame, text="↺", style="Custom.TButton", width=2, command=lambda: set_default_color_gui("Color"))
    default_color_button.pack(side="right", padx=(5,0))
        
    direction_frame = tk.Frame(fields_frame, bg="#2E2E2E")
    direction_frame.pack(side="left", padx=5)
    direction_label = tk.Label(direction_frame, text="Direction", **label_style)
    direction_label.pack(side="left", padx=5)
    direction_dropdown = ttk.Combobox(direction_frame, values=["Normal", "Reverse"], style="TCombobox", state="readonly", width=10, name="direction")
    direction_dropdown.current(0)
    direction_dropdown.pack(side="right", pady=(1,0))

    brightness_frame = tk.Frame(fields_frame, bg="#2E2E2E")
    brightness_frame.pack(side="left", padx=5)
    brightness_label = tk.Label(brightness_frame, text="Brightness (50)", **label_style, width=13)
    brightness_label.pack(side="left", padx=5)
    brightness_slider = ttk.Scale(brightness_frame, from_=0, to=100, orient="horizontal", name="brightness", value=50, command=lambda value: snap_slider(value, brightness_slider, brightness_label))
    brightness_slider.set(50)
    brightness_slider.pack(side="right", pady=(1,0))

    speed_frame = tk.Frame(fields_frame, bg="#2E2E2E")
    speed_frame.pack(side="left", padx=5)
    speed_label = tk.Label(speed_frame, text="Speed (2)", **label_style)
    speed_label.pack(side="left", padx=5)
    speed_slider = ttk.Scale(speed_frame, from_=1, to=5, orient="horizontal", name="speed", value=2, command=lambda value: snap_slider(value, speed_slider, speed_label))
    speed_slider.pack(side="right", pady=(1,0))

    # Keyboard layout
    keyboard_frame = tk.Frame(root, bg="#2E2E2E")
    keyboard_frame.pack(side="top", padx=20, pady=10, fill="x"),
    keyboard_keys_buttons = [
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
        "CapsLock": 1.75 * (key_width) + 1,
        "LShift": 2 * (key_width) + 1,
        "Space": 8 * (key_width) + 2,
        "Enter": 2.5 * (key_width),
        "RShift": 1.75 * (key_width) + 2,
        "LCtrl": 1.25 * (key_width),
        "LWin": 1.25 * (key_width),
        "LAlt": 1.25 * (key_width) + 1
    }

    # Add keyboard buttons
    buttons_collection = []
    for row in keyboard_keys_buttons:
        row_frame = tk.Frame(keyboard_frame, bg="#2E2E2E")
        for key in row:
            width = special_keys.get(key, key_width)
            key_button = tk.Button(row_frame, text=key, width=int(width), height=1, command=lambda k=key: select_key_button(k), name=f"key_button_{get_key_id(key)}")
            key_button.pack(side="left", padx=key_spacing, ipady=11, pady=5)
            key_button.config(background=f"#{DEFAULT_GUI_RGB}", foreground="white", font=("Arial", 11), borderwidth=0, activebackground="#202020", activeforeground="white", highlightthickness=4, relief="flat")
            
            # Add key button attributes
            key_button.key_id = get_key_id(key)
            key_button.map = key_button.key_id
            key_button.fn_map = get_default_fn_id(key_button.key_id)
            if key_button.fn_map == "forbidden":
                key_button.fn_map = None
            key_button.rgb = DEFAULT_GUI_RGB
            key_button.selected = False

            buttons_collection.append(key_button)
        row_frame.pack()

    # Add bottom buttons
    bottom_buttons_frame = tk.Frame(root, bg="#2E2E2E")
    bottom_buttons_frame.pack(pady=(5,12), side="right")
    load_config_button = ttk.Button(bottom_buttons_frame, text="Load Config", padding=5, command=lambda: load_config_gui(), style="Custom.TButton")
    load_config_button.pack(side="left", ipadx=15, padx=10)
    save_config_button = ttk.Button(bottom_buttons_frame, text="Save Config", padding=5, command=lambda: save_config_gui(), style="Custom.TButton")
    save_config_button.pack(side="left", ipadx=15, padx=10)
    apply_changes_button = ttk.Button(bottom_buttons_frame, text="Apply", padding=5, command=lambda: apply_changes(), style="Custom.TButton")
    apply_changes_button.pack(side="right", ipadx=15, padx=(10,25))

    # Add per-key config buttons
    key_buttons_frame = tk.Frame(root, bg="#2E2E2E", name="key_options")
    key_buttons_frame.pack(pady=(0,10), side="bottom")

    key_button_values = []
    for index, key in enumerate(KEY_CODES_SORTED):
        if "function" not in key and "unknown" not in key:
            key_button_values.append(key)
    key_button_values = sorted(key_button_values, key=lambda key_id: (len(key_id) > 1, key_id))
    
    key_map_frame = tk.Frame(key_buttons_frame, bg="#2E2E2E")
    key_map_frame.pack(side="left", fill="x", pady=5)
    key_map_label = tk.Label(key_map_frame, text="Mapping", **label_style)
    key_map_label.pack(side="left", padx=5)
    key_map_dropdown = ttk.Combobox(key_map_frame, values=key_button_values, style="TCombobox", state="readonly", width=15, name="map")
    key_map_dropdown.bind("<<ComboboxSelected>>", lambda event: set_key_map_gui())
    key_map_dropdown.pack(side="right", ipadx=5)
    
    key_fn_map_frame = tk.Frame(key_buttons_frame, bg="#2E2E2E")
    key_fn_map_frame.pack(side="left", fill="x", pady=5)
    key_fn_map_label = tk.Label(key_fn_map_frame, text="FN Mapping", **label_style)
    key_fn_map_label.pack(side="left", padx=5)
    key_fn_map_dropdown = ttk.Combobox(key_fn_map_frame, values=key_button_values, style="TCombobox", state="readonly", width=15, name="fn_map")
    key_fn_map_dropdown.bind("<<ComboboxSelected>>", lambda event: set_key_fn_map_gui())
    key_fn_map_dropdown.pack(side="right", ipadx=5)

    key_rgb_frame = tk.Frame(key_buttons_frame, bg="#2E2E2E", name="key_rgb_frame")
    # key_rgb_frame.pack(side="left", fill="x", pady=5) | Disabled so it's only loaded when Custom pattern is selected
    key_rgb_label = tk.Label(key_rgb_frame, text="RGB", **label_style)
    key_rgb_label.pack(side="left", padx=5)
    key_rgb_field = tk.Entry(key_rgb_frame, **entry_style, width=10, validate="key", validatecommand=(validate_color_hex, "%P"), name="rgb")
    key_rgb_field.pack(side="left")
    key_rgb_field.bind("<Button-1>", lambda event: open_color_picker(event))
    key_rgb_field.bind("<Return>", lambda event: open_color_picker(event))
    key_rgb_field.bind("<KeyRelease>", lambda event: set_key_rgb_gui(get_selected_key()))

    # Create a list that will hold all the gui objects
    global gui_objects
    gui_objects.append(pattern_dropdown)
    gui_objects.append(direction_dropdown)
    gui_objects.append(color_field)
    gui_objects.append(speed_slider)
    gui_objects.append(brightness_slider)
    gui_objects.append(key_map_dropdown)
    gui_objects.append(key_fn_map_dropdown)
    gui_objects.append(key_rgb_field)
    gui_objects.append(key_rgb_frame)
    gui_objects.extend(buttons_collection)
    
    # Run the gui
    root.mainloop()
        
# Select a button and show its details on the GUI
def select_key_button(key):
    key_id = get_key_id(key)
    default_fn_key_id = get_default_fn_id(key_id)

    # Get elements and values
    map_field = get_gui_object("map")
    fn_map_field = get_gui_object("fn_map")
    rgb_field = get_gui_object("rgb")
    key_button = get_gui_object(f"key_button_{key_id}")
    map_value = key_id
    rgb_value = "Default"
    fn_map_value = default_fn_key_id

    # Unset the previously selected key
    for key_object in get_all_keys():
        key_object.selected = False
        key_object.config(font=("Arial", 11))

    # Set the selected key and BOLDIFY it
    key_button.selected = True
    key_button.config(font=("Arial", 11, "bold"))

    # Get the button's values
    if key_button.map != None:
        map_value = key_button.map
    if key_button.fn_map != None:
        fn_map_value = key_button.fn_map
    if key_button.rgb != None:
        rgb_value = key_button.rgb
    
    # Load the button values into the fields
    if fn_map_value != "forbidden":              # Not all keys should have an FN remap. Default options need to be preserved.
        fn_map_field.current(fn_map_field["values"].index(fn_map_value))
        fn_map_field.config(state="readonly")
    else:
        fn_map_field.config(state="disabled")
        fn_map_field.set("")

    if key_id != "fn":                           # FN key must not be remapped
        map_field.current(map_field["values"].index(map_value))
        map_field.config(state="readonly")
    else:
        map_field.config(state="disabled")
        map_field.set("")
    rgb_field.delete(0, "end")
    rgb_field.insert(0, rgb_value)

# Set specific key's RGB. Using the "all" value as key will apply the color to all keys.
def set_key_rgb_gui(key = None, rgb_code = None):
    keys = [key]

    # Get elements and values
    if (rgb_code == None):
        rgb_code = get_gui_object("rgb").get()
    if rgb_code == "default":
        rgb_code = DEFAULT_GUI_RGB
    if key == "all":
        keys = get_all_keys()
    
    # Set key rgb
    for key_object in keys:
        key_object.config(background=f"#{rgb_code}")
        key_object.rgb = rgb_code

        # Darken text if key is too light
        r, g, b = int(rgb_code[0:2], 16), int(rgb_code[2:4], 16), int(rgb_code[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        if luminance > 186:
            key_object.config(foreground="black")
        else:
            key_object.config(foreground="white")

# Set specific key's FN mapping
def set_key_fn_map_gui(key = None, fn_map = None):

    # Get elements and values
    if (fn_map == None):
        fn_map = get_gui_object("fn_map").get()
    if key == None:
        key = get_selected_key()
    
    # Set key fn_map
    key.fn_map = fn_map

    # Adjust key text
    adjust_key_text(key)

# Set specific key's mapping
def set_key_map_gui(key = None, map = None):

    # Get elements and values
    if (map is None):
        map = get_gui_object("map").get()
    if key is None:
        key = get_selected_key()
    
    # Set key map
    key.map = map

    # Adjust key text
    adjust_key_text(key)

# Adjust key text. When a custom mapping or FN layer mapping is set, use a custom character.
def adjust_key_text(key):
    key_base = key.config("text")[-1].split("\n")[0]
    key_map = ""
    key_fn_map = ""
    default_fn_map = get_default_fn_id(key.key_id)
    button_size = int(key.config("width")[-1])

    if key.map != key.key_id:
        label = key.map.capitalize()
        mapped_key = get_gui_object(f"key_button_{key.map}")
        if mapped_key != None:
            label = mapped_key.config("text")[-1].split("\n")[0]
        key_map = truncate_text(f"\n\u2937 {label}", round(button_size * 1.5))
    if "forbidden" != default_fn_map and key.fn_map != default_fn_map:
        label = key.fn_map.capitalize()
        mapped_key = get_gui_object(f"key_button_{key.fn_map}")
        if mapped_key != None:
            label = mapped_key.config("text")[-1].split("\n")[0]
        if button_size == 9:
            button_size = 8
        key_fn_map = truncate_text(f"\nFn: {label}", round(button_size * 1.5))
    
    name = f"{key_base}{key_map}{key_fn_map}"
    key.config(text=name)


# Adjust key fields and selected key based on currently selected pattern
def adjust_key_fields():

    # Get elements and values
    pattern = get_gui_object("pattern")
    key_rgb_frame = get_gui_object("key_rgb_frame")

    # If the pattern is not custom, hide the per-key RGB field
    selected_pattern = pattern.get().lower().replace(" ", "_")
    if selected_pattern == "custom":
        key_rgb_frame.pack(side="left", fill="x", pady=5)
    else:
        key_rgb_frame.pack_forget()

# Truncate text to a given length
def truncate_text(text, max_length):
    if len(text) <= max_length:
        return text
    return text[:max_length - 1] + "."

# Generate current key map and RGB from GUI
def generate_key_map_and_rgb():
    key_map_collection = {}
    keys_color_collection = {}

    # Get all attributes of each button, and load them into the collections
    for key in get_all_keys():
        key_id = key.key_id
        key_map = key.map
        key_fn_map = key.fn_map
        key_rgb = key.rgb
        if key_map != None:
            key_map_collection[key_id] = key_map
        if key_fn_map != None:
            key_map_collection[f"{key_id}_fn"] = key_fn_map
        if key_rgb != None and  key_rgb != None:
            keys_color_collection[key_id] = key_rgb
    
    return (key_map_collection, keys_color_collection)

# Apply values from GUI to device
def apply_changes():

    # Get values
    pattern = get_gui_object("pattern").get().lower().replace(" ", "_")
    brightness = int(get_gui_object("brightness").get())
    speed = 5 - int(get_gui_object("speed").get())
    direction = get_gui_object("direction").get().lower()
    color = f"{get_gui_object("color").get().lower():0<6}"

    # Get key map and RGB collections
    key_map_collection, keys_color_collection = generate_key_map_and_rgb()

    # Apply all changes, as necessary. Similar to the CLI functionality, adding some pauses just to be safe.
    if len(key_map_collection) > 0:
        set_key_map(key_map_collection)
        time.sleep(0.1)
    if len(keys_color_collection) >0:
        set_keys_color(keys_color_collection)
        time.sleep(0.1)
    set_pattern(pattern, brightness, speed, direction, color)

# Load config from JSON file to GUI
def load_config_gui():
    from tkinter import filedialog as fd

    # Open file dialog
    filename = fd.askopenfilename(title='Select a config file to load from', initialdir='./', filetypes=(('All files', '*.*'),))
    if len(filename) < 1:
        return
    
    # Load config
    pattern, brightness, color, direction, speed, key_map, key_color = load_config(None, None, None, None, None, {}, {}, filename)

    # Apply all loaded values into the GUI
    if pattern != None:
        get_gui_object("pattern").current(list(RGB_PATTERNS).index(pattern))
        adjust_key_fields()

    if brightness != None:
        get_gui_object("brightness").set(brightness)

    if speed != None:
        get_gui_object("speed").set(5 - speed)
    
    if direction != None:
        direction_object = get_gui_object("direction")
        direction_object.delete(0, "end")
        if str(direction).isdigit():
            direction_object.current(direction)
        elif direction.lower() == "normal":
            direction_object.current(0)
        elif direction.lower() == "reverse":
            direction_object.current(1)

    if color != None:
        if color == "default": color = color.capitalize()
        color_object = get_gui_object("color")
        color_object.delete(0, "end")
        color_object.insert(0, color)
        set_key_rgb_gui("all", color.lower())
        
    # Apply per-key RGB after the global color has been set
    for key in get_all_keys():
        if key_map != None and key.key_id in key_map and key_map[key.key_id] in KEY_CODES_SORTED:
            set_key_map_gui(key, key_map[key.key_id])
        if key_map != None and f"{key.key_id}_fn" in key_map and key_map[f"{key.key_id}_fn"] in KEY_CODES_SORTED:
            set_key_fn_map_gui(key, key_map[f"{key.key_id}_fn"])
        if key_color != None and key.key_id in key_color and validate_color(key_color[key.key_id]):
            set_key_rgb_gui(key, key_color[key.key_id])

# Save config to JSON file to GUI
def save_config_gui():
    from tkinter import filedialog as fd

    # Get key map and RGB collections
    key_map_collection, keys_color_collection = generate_key_map_and_rgb()

    # Open file dialog
    filename = fd.asksaveasfilename(title='Select a config file to save to', initialdir='./', filetypes=(('JSON', '*.json'),), initialfile="config.json")
    if len(filename) < 1:
        return
    
    # Get values from GUI
    pattern = get_gui_object("pattern").get().lower().replace(" ", "_")
    brightness = int(get_gui_object("brightness").get())
    if brightness > 100:
        brightness = 100
    speed = 5 - int(get_gui_object("speed").get())
    direction = get_gui_object("direction").get().lower()
    color = f"{get_gui_object("color").get().lower():0<6}"
    
    # Save config file
    save_config(pattern, brightness, color, direction, speed, key_map_collection, keys_color_collection, filename)

# Set default color value on GUI
def set_default_color_gui(target, default = "Default", only_if_empty = False):

    # Get target
    target = get_gui_object(target.lower(), True)

    # Return if the target already has a value and only_if_empty is set
    if only_if_empty and len(object.get()) > 0:
        return
    
    # Set the value
    target.delete(0, "end")
    target.insert(0, default)
    
    # Set all keys to default color as well
    set_key_rgb_gui("all", DEFAULT_GUI_RGB)

# Open color picker and select a color
def open_color_picker(event, apply_to_all = False):

    # Skip if this widget has been disabled
    if "disabled" in event.widget.config("state"):
        return
    
    from tkinter import colorchooser
    color_value = colorchooser.askcolor(title ="Choose color")

    # Update field value
    if color_value[1] != None:
        color_code = color_value[1].replace("#","").lower()
        event.widget.delete(0, "end")
        event.widget.insert(0, color_code)
    else:
        return  # Skip if the user cancelled
    
    # Apply the color on the key button(s) as well
    if apply_to_all:
        # Apply to all keys
        set_key_rgb_gui("all", color_code)
    else:
        # Apply to selected key only
        set_key_rgb_gui(get_selected_key(), color_code)
        

# Get selected key button
def get_selected_key():
    global gui_objects

    for object in gui_objects:
        if "key_button_" in str(object) and hasattr(object, "selected") and object.selected:
            return object

    return None

# Get a GUI object by name
def get_gui_object(name, partial_match = False):
    global gui_objects

    for object in gui_objects:
        object_name = str(object).lower().rsplit(".", 1)[-1].replace(":", "")
        if name == object_name:
            return object
        elif partial_match and name in object_name:
            return object

    return None

# Get all keys
def get_all_keys():
    global gui_objects

    keys = []
    for object in gui_objects:
        if "key_button_" in str(object) and hasattr(object, "selected"):
            keys.append(object)

    return keys

# Validate color value
def validate_color(value):
    if value == "" or value.lower() == "default":  # Hack for backspace/delete
        return True
    return all(c in "0123456789abcdefABCDEF" for c in value) and len(value) <= 6

# Set GUI's styling. I apologize but I'm not going to explain myself here. I kind of hate ttk now because of this shit.
def set_gui_style(root):
    import tkinter as tk
    from tkinter import ttk

    root.configure(bg="#2E2E2E")
    root.resizable(False,False)
    label_style = {"bg": "#2E2E2E", "fg": "#FFFFFF", "font": ("Arial", 12)}
    entry_style = {"bg": "#3C3C3C", "fg": "#FFFFFF", "insertbackground": "#FFFFFF", "highlightbackground": "#5A5A5A", "relief": "flat", "disabledbackground": "#3C3C3C"}
    style = ttk.Style()
    style.theme_use("clam")
    
    # Tk (and not Ttk) ended up working better for buttons btw. Ttk wants to take control away from me when I do weird things.
    style.configure("TButton", background="#4CAF50", foreground="#FFFFFF", font=("Arial", 12), padding=0, borderwidth=0)
    style.configure("Custom.TButton", background="#e32d52", foreground="#FFFFFF", font=("Arial", 12), padding=0, borderwidth=0)
    style.configure("TCombobox", fieldbackground="#3C3C3C", background="#3C3C3C", foreground="white", relief="flat", selectbackground=None, selectforeground=None)
    style.configure("TScale", background="#2E2E2E", troughcolor="#444444", sliderrelief="flat", sliderlength=15, sliderthickness=10)
    style.map("TButton", background=[("active", "#45A049"), ("pressed", "#3E8E41")], foreground=[("disabled", "#808080")])
    style.map("Custom.TButton", background=[("active", "#e33659"), ("pressed", "#e33659")], foreground=[("disabled", "#808080")])
    style.map("TCombobox", bordercolor="#3C3C3C", highlightbackground="#3C3C3C", fieldbackground="#3C3C3C")

    # Preload the bold font to prevent issues later
    dummy_label = tk.Label(root, text="⤷", font=("Arial", 11, "bold"))
    dummy_label.pack_forget()

    return (label_style, entry_style)

# Snap the slider to the nearest integer
def snap_slider(value, slider, label):
    import math

    # Get old value from label
    old_value = int(label.config("text")[-1].split(" ")[1].replace("(","").replace(")",""))
    float_value = float(value)
    int_value = int(math.floor(float_value)) # Ceiling works better than round in this case

    # Only set the value if there's an actual change. WARNING: Removing this check causes recurse errors.
    if float_value != float(old_value):
        label_text = label.config("text")[-1].split(" ")[0]
        label_text = f"{label_text} ({int_value})"
        label_text = label.config(text=label_text)
        slider.set(int_value)

# Get a key id from its name
def get_key_id(key_name):
    key_name = key_name.lower()
    if key_name == "esc": key_name = "escape"
    if key_name == "\\": key_name = "backslash"
    if key_name == "/": key_name = "slash"
    if key_name == "~": key_name = "tilde"
    if key_name == "pu": key_name = "pageup"
    if key_name == "pd": key_name = "pagedown"
    if key_name == ",": key_name = "comma"
    if key_name == ".": key_name = "period"
    if key_name == "[": key_name = "lbracket"
    if key_name == "]": key_name = "rbracket"
    if key_name == "-": key_name = "dash"
    if key_name == "=": key_name = "equals"
    if key_name == ";": key_name = "semicolon"
    if key_name == "del": key_name = "delete"
    if key_name == "'": key_name = "quote"

    return key_name

###################
## CLI functions ##
###################

# Parse arguments
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

# Load libusb from a local file
def load_libusb():
    import os, sys
    from ctypes import CDLL

    # Load the DLL from the base path where the script/exe is located
    if getattr(sys, 'frozen', False):  # Check if running from PyInstaller's bundle
        base_path = os.path.dirname(sys.executable)  # Path to the executable
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))  # Path to the script
    
    # Define the DLL path in the original directory
    dll_path = os.path.join(base_path, 'libusb-1.0.dll')

    # Try loading the DLL from the original directory (where the .exe/.py is located)
    if os.path.isfile(dll_path):
        try:
            # Load the DLL and reurn without error
            CDLL(dll_path)
            return None
        except OSError as e:
            return f"Error loading DLL from : {e}"
    else:
        return "libusb-1.0.dll not found."

# Find and set up USB device
def setup_device():
    global device, out_endpoint
    error_message = load_libusb()
    if error_message != None:
        return error_message
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if device is None:
        return "ERROR: Device not found.\n\nMake sure that the keyboard is connected via a USB cable and is set to wired mode."
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
        return "MI_02 interface not found"

    # Select the OUT endpoint of the MI_02 interface
    out_endpoint = None
    for ep in mi_02_interface:
        ep_address = ep.bEndpointAddress
        if usb.util.endpoint_direction(ep_address) == usb.util.ENDPOINT_OUT:
            out_endpoint = ep
            break

    # Ensure we found the OUT endpoint
    if out_endpoint is None:
        return "OUT endpoint for MI_02 not found"
    
    return None

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
def generate_pattern_packet(pattern_int, brightness_int, speed_int, direction_val, color):
    brightness = f"{brightness_int:02x}"
    pattern = f"{pattern_int:02x}"

    # Add up the RGB values
    use_default_color = f"{int(color == 'default'):02x}" # Keep the different quotes to avoid breaking older Pythons
    if (color == "default"):
        color = "ffffff"

    if (len(color) != 6):
        raise ValueError("Color value is invalid")

    # Set direction value
    direction = None
    if direction_val == "normal":
        direction_val = 0
    elif direction_val == "reverse":
        direction_val = 1
    direction = f"{direction_val:02x}"
    
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

# Get the default FN layer key for this key_id. Function keys should NOT be remapped in the FN layer.
def get_default_fn_id(key_id, return_functions = False):
        fn_key_id = key_id
        if key_id in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            fn_key_id = "f" + fn_key_id
        elif key_id == "0":
            fn_key_id = "f10"
        elif key_id == "dash":
            fn_key_id = "f11"
        elif key_id == "equals":
            fn_key_id = "f12"
        elif key_id == "rbracket":
            fn_key_id = "end"
        elif key_id == "lbracket":
            fn_key_id = "home"
        elif key_id == "delete":
            fn_key_id = "insert"
        elif key_id == "pageup":
            fn_key_id = "pause"
        elif key_id == "pagedown":
            fn_key_id = "scroll_lock"
        elif key_id == "tilde":
            fn_key_id = "print_screen"
        elif key_id == "p":
            fn_key_id = "function_toggle_rgb"
        elif key_id == "left":
            fn_key_id = "function_make_rgb_slower"
        elif key_id == "right":
            fn_key_id = "function_make_rgb_faster"
        elif key_id == "up":
            fn_key_id = "function_increase_rgb_brightness"
        elif key_id == "down":
            fn_key_id = "function_decrease_rgb_brightness"
        elif key_id == "backslash":
            fn_key_id = "function_change_rgb_pattern"
        elif key_id == "tab":
            fn_key_id = "function_change_rgb_color"
        elif key_id == "w":
            fn_key_id = "function_swap_wasd"
        elif key_id == "space":
            fn_key_id = "function_change_keyboard_index"
        elif key_id == "l":
            fn_key_id = "function_toggle_charging_light"
        elif key_id == "e":
            fn_key_id = "function_bt_matching_1"
        elif key_id == "r":
            fn_key_id = "function_bt_matching_2"
        elif key_id == "t":
            fn_key_id = "function_bt_matching_3"
        elif key_id == "escape":
            fn_key_id = "function_reset_settings"
        elif key_id == "period":
            fn_key_id = "function_mac_mode"
        elif key_id == "comma":
            fn_key_id = "function_windows_mode"
        elif key_id == "y":
            fn_key_id = "function_enter_wired_mode"
        elif key_id == "q":
            fn_key_id = "function_enter_wireless_mode"

        if ("function" in fn_key_id or "fn" == fn_key_id) and not return_functions:
            fn_key_id = "forbidden"
        
        return fn_key_id

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
        mapped_key = get_default_fn_id(key, True)
        if "function" in mapped_key:
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
        time.sleep(0.1)

# Set inidividual key mappings
def set_key_map(key_map):
    for packet_data in generate_key_map_packets(key_map):
        send_data(bytes.fromhex(packet_data))
        time.sleep(0.1)

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
        if "brightness" in json_file and brightness is None:
            brightness = json_file["brightness"]
        if "color" in json_file and color is None:
            color = json_file["color"]
        if "direction" in json_file and direction is None:
            direction = json_file["direction"]
        if "speed" in json_file and speed is None:
            speed = json_file["speed"]
        
        return (pattern, brightness, color, direction, speed, key_map, key_color)

# Save config to JSON file
def save_config(pattern, brightness, color, direction, speed, key_map, key_color, config_output):
    out_key_map = {}
    if "default" not in key_map: # Ignore key_map if default value is used
        out_key_map = key_map
    config = {"key_color": key_color, "key_map": out_key_map, "brightness": brightness, "color": color, "direction": direction, "speed": speed}
    
    if pattern != None:
        config["pattern"] = pattern
    elif len(key_map) > 0:
        config["pattern"] = "custom"

    with open(config_output, "w") as json_file:
        json.dump(config, json_file, indent=2)

# Run the program
def run_program():
    # Load USB device and arguments
    error_message = setup_device()
    pattern, brightness, color, direction, speed, key_color, key_map, config_output, config_input = parse_args()

    # If no usable parameters are given, load the GUI
    if (len(key_map) < 1 and len(key_color) < 1 and pattern == None):
        load_gui(error_message)
    else:
        # CLI functionality

        # Throw error if device didn't connect
        if error_message != None:
            raise ValueError(error_message)

        # Load config
        if (config_input != None):
            pattern, brightness, color, direction, speed, key_map, key_color = load_config(pattern, brightness, color, direction, speed, key_map, key_color, config_input)
        
        # Load key maps
        if (len(key_map) > 0):
            set_key_map(key_map)

        # Load key RGB or pattern. Adding some pauses here just to be extra safe.
        if (len(key_color) > 0):
            time.sleep(0.1)
            set_pattern('custom', brightness, speed, direction)
            time.sleep(0.1)
            set_keys_color(key_color)
        elif (pattern != None):
            time.sleep(0.1)
            set_pattern(pattern, brightness, speed, direction, color)

        # Save config
        if (config_output != None):
            save_config(pattern, brightness, color, direction, speed, key_map, key_color, config_output)


# Run the main functionality
run_program()