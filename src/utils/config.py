"""
GUI Configuration Constants
"""

# Window Configuration
WINDOW_TITLE = "PNG Compression Comparison System"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
WINDOW_GEOMETRY = "1400x900"

# Colors (Light Mode, Dark Mode)
BG_PRIMARY = ("#F8FAFC", "#0B1220")
BG_SECONDARY = ("#FFFFFF", "#111827")
BG_ACCENT = ("#FFFFFF", "#111827")
TEXT_PRIMARY = ("#111827", "#F9FAFB")
TEXT_SECONDARY = ("#64748B", "#94A3B8")
BUTTON_BG = ("#2563EB", "#2563EB")
BUTTON_FG = "#ffffff"
BUTTON_HOVER = ("#3B82F6", "#3B82F6")

SUCCESS_COLOR = (
    "#22C55E",
    "#22C55E"
)

ERROR_COLOR = (
    "#EF4444",
    "#EF4444"
)

WARNING_COLOR = (
    "#F59E0B",
    "#F59E0B"
)

PROGRESS_COLOR = (
    "#2563EB",
    "#2563EB"
)

PURPLE_COLOR = (
    "#8B5CF6",
    "#8B5CF6"
)

BORDER_COLOR = (
    "#E5E7EB",
    "#1F2937"
)

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
BORDER_RADIUS = 16
CONTROL_RADIUS = 8

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
