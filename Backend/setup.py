import cx_Freeze
import sys
import matplotlib

base = None

if sys.platform == 'Win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("app.py", base=base)]

cx_Freeze.setup(
    name = "Data monitoring App",
    options = {"build_exe": {"packages":["flask","flask_cors","serial","webui","time","sys","json","jinja2.ext","os","random","csv","threading",
    "struct","datetime","fpdf","xlsxwriter","signal"]}}, 
    version = "0.01",
    description = "Meter data Monitoring App",
    executables = executables
    )
