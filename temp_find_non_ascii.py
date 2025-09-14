import os

for root, dirs, files in os.walk("backend"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            print(f"Checking file: {path}")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    f.read()
            except UnicodeDecodeError:
                print(f"****************************************")
                print(f"Non-UTF-8 file found: {path}")
                print(f"****************************************")