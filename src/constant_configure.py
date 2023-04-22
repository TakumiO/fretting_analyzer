import os
import sys
import json
import PySimpleGUI as sg

app_name = "graph_maker"
config_filename = "config.json"

if sys.platform.startswith("win"):
    app_data_folder = os.getenv("APPDATA")
    config_folder = os.path.join(app_data_folder, app_name)
elif sys.platform.startswith("darwin"):
    app_support_folder = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    config_folder = os.path.join(app_support_folder, app_name)
else:
    raise RuntimeError("Unsupported platform")

if not os.path.exists(config_folder):
    os.makedirs(config_folder)

config_file_path = os.path.join(config_folder, config_filename)


def load_config():
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as f:
            config = json.load(f)
    else:
        config = {}
    return config


def save_config(config):
    with open(config_file_path, "w") as f:
        json.dump(config, f, indent=2)


def main():
    config = load_config()

    layout = [
        [sg.Text("摩擦力公正係数"), sg.InputText(config.get("friction_scale", ""), key="friction_scale")],
        [sg.Text("振幅公正係数"), sg.InputText(config.get("amp_scale", ""), key="amp_scale")],
        [sg.Text("", size=(40, 1), key="status")],
        [sg.Button("保存"), sg.Button("キャンセル")],
    ]

    window = sg.Window("設定管理", layout)

    while True:
        event, values = window.read()

        if event == "保存":
            config["friction_scale"] = float(values["friction_scale"])
            config["amp_scale"] = float(values["amp_scale"])
            save_config(config)
            window["status"].update(f"設定を保存しました。摩擦力公正係数: {config['friction_scale']}, 振幅公正係数: {config['amp_scale']}")
        elif event in (sg.WIN_CLOSED, "キャンセル"):
            break

    window.close()


if __name__ == "__main__":
    main()
