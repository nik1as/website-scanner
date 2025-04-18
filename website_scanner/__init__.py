from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("website-scanner")
except PackageNotFoundError:
    __version__ = "unknown"
