from cx_Freeze import setup, Executable

executables = [
    Executable(
        script="main.py",
        target_name="RSA Paper Backup Utility.exe",
        base="gui",
        icon="assets/app.ico"
    )
]

setup(
    name="RSA Paper Backup Utility",
    version="1.0",
    executables=executables
)