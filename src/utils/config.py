"""
GUI Configuration Constants
"""

# Window Configuration
WINDOW_TITLE = "PNG Compression Comparison System"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
WINDOW_GEOMETRY = "1400x900"

# Colors (Light Mode, Dark Mode)
BG_PRIMARY = ("#f3f3f3", "#1e1e1e")
BG_SECONDARY = ("#eaeaea", "#252526")
BG_ACCENT = ("#ffffff", "#2d2d30")
TEXT_PRIMARY = ("#1e1e1e", "#ffffff")
TEXT_SECONDARY = ("#606060", "#aaaaaa")
BUTTON_BG = ("#0078d4", "#1f77b4")
BUTTON_FG = "#ffffff"
BUTTON_HOVER = ("#1084d8", "#2c89c7")
PROGRESS_COLOR = ("#0078d4", "#1f77b4")
SUCCESS_COLOR = ("#107c10", "#2ea44f")
ERROR_COLOR = ("#d83b01", "#da3637")

# Fonts
FONT_TITLE = ("Segoe UI", 12, "bold")
FONT_HEADING = ("Segoe UI", 11, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO = ("Courier New", 9)

# Padding & Spacing
PADDING_LARGE = 15
PADDING_NORMAL = 10
PADDING_SMALL = 5
BORDER_RADIUS = 5

# Section Heights
SECTION_HEADER_HEIGHT = 50
SECTION_PADDING = 10

# Algorithm timeouts (seconds)
DEFLATE_TIMEOUT = None       # unlimited
OXIPNG_TIMEOUT = 120
ZOPFLI_TIMEOUT = 60

# Algorithm tuning
ZOPFLI_MAX_ITERATIONS = 15

# Preview
PREVIEW_WIDTH = 350
PREVIEW_HEIGHT = 350

# Comparison ETA window (number of recent files to average)
COMPARISON_ETA_WINDOW = 5
