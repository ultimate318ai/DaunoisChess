from cx_Freeze import setup, Executable

base = None
# Remplacer "monprogramme.py" par le nom du script qui lance votre programme
executables = [Executable("main.py", base=base)]
# Renseignez ici la liste complète des packages utilisés par votre application
packages = [
    "pygame",
    "chess",
    "pygame_menu",
    "sys",
    "pygame_widgets",
    "chess.variant",
    "svglib",
    "svglib.svglib",
]
include_files = ["IA/Fairy-Stockfish", "pictures"]
options = {"build_exe": {"packages": packages, "include_files": include_files}}
# Adaptez les valeurs des variables "name", "version", "description" à votre programme.
setup(
    name="Test",
    options=options,
    version="0.1",
    description="Voici mon programme",
    executables=executables,
)
