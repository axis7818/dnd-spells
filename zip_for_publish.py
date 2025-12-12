import shutil
from version import version

shutil.make_archive(f"spell-output-{version}", "zip", "spell-output")
