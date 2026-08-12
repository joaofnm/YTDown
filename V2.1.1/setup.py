# Instale a versão corrigida do py2app
pip install git+https://github.com/ronaldoussoren/py2app.git@master

# Crie/modifique o setup.py
cat > setup.py << 'ENDSCRIPT'
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['yt_dlp', 'tkinter'],
    'includes': ['yt_dlp', 'threading', 'tkinter', 'json', 'time', 'os', 'sys'],
    'excludes': ['PyQt5', 'PySide2', 'matplotlib', 'numpy', 'scipy'],
    'iconfile': None,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
ENDSCRIPT

# Construa
rm -rf build dist
python setup.py py2app
