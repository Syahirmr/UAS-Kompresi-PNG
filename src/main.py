"""
Main GUI Application
PNG Compression Comparison System
Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI

Entry Point - Run GUI Application
"""

from src.ui.app import CompressionApp


def main():
    """Main application entry point."""
    app = CompressionApp()
    app.run()


if __name__ == "__main__":
    main()
