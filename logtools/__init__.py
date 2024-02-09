from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = '<<unknown>>'

version_string = f'logtools version {__version__}'

del metadata
