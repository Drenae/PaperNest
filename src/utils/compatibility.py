import sys


MINIMUM_PYTHON_VERSION = (3, 10)


def check_python_version() -> None:
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        required_version = ".".join(
            str(part)
            for part in MINIMUM_PYTHON_VERSION
        )

        current_version = ".".join(
            str(part)
            for part in sys.version_info[:3]
        )

        raise RuntimeError(
            f"PaperNest nécessite Python {required_version} "
            f"ou une version plus récente. "
            f"Version actuelle : {current_version}."
        )