"""
Main GUI Application
PNG Compression Comparison System
Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI

MILESTONE 1: GUI FOUNDATION COMPLETE
Entry Point - Run GUI Application
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.app import CompressionApp


def main():
    """Main application entry point."""
    print("=" * 60)
    print("PNG Compression Comparison System")
    print("MILESTONE 1: GUI Foundation - Starting...")
    print("=" * 60)
    
    app = CompressionApp()
    app.run()


if __name__ == "__main__":
    main()
