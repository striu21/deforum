import fall
import os

req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")

with open(req_file) as file:
    for lib in file:
        lib = lib.strip()
        if not fall.is_installed(lib):
            fall.run_pip(f"install {lib}", f"Deforum requirement: {lib}")
