from setuptools import setup

APP = ['arduino_reader_final.py']  # Your main script
DATA_FILES = ['app.icns',]  # Include necessary files
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5', 'flask', 'serial'],
    'resources': [],  # Ensure fonts are included
    'iconfile': 'app.icns',  # Set the macOS app icon
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
