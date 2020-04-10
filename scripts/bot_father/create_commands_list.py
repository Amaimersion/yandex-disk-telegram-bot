from pathlib import Path
import json


def main():
    file_path = Path("info/info.json")
    data = json.loads(file_path.read_text())

    for command in data["commands"]:
        print(f"{command['command']} - {command['description']}")


if (__name__ == "__main__"):
    main()
