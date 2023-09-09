import os.path
import sys
import subprocess
import getopt



def main():
    try:
        import ui
    except FileNotFoundError:
        print("OAuth Client ID not found.")
        if sys.platform == "win32":
            if not os.path.exists(os.getenv("APPDATA") + r"\gspread"):
                os.mkdir(os.getenv("APPDATA") + r"\gspread")
            subprocess.run(f"explorer.exe {os.getenv('APPDATA')}\gspread")
            import webbrowser
            webbrowser.open("https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id")
    else:
        ui.event_loop()


args = sys.argv[1:]
options = "hs"
long_options = ["Help", "Skip_venv"]


try:
    arguments, _ = getopt.getopt(args, options, long_options)
except getopt.error as err:
    print(str(err))
else:
    arguments = [x[0] for x in arguments]
    if "-h" in arguments or "--Help" in arguments:
        print("-h --Help, Displays this message \n"
              "-s --Skip_venv, Skips creation of virtual environment and installation of required packages")
    elif "-s" in arguments or "--Skip_venv" in arguments:
        main()
    else:
        path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(path + r"\venv"):
            subprocess.run(f"cd {path} && python -m venv venv", shell=True)
        subprocess.run(f"{path}\\venv\\Scripts\\python.exe -m pip install --upgrade pip")
        subprocess.run(f"{path}\\venv\\Scripts\\python.exe -m pip install --upgrade -r {path}\\requirements.txt")
        subprocess.run(f"{path}\\venv\\Scripts\\python.exe {path}\\main.py -s")
