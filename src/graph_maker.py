# -*- coding: utf-8 -*-

import PySimpleGUI as sg
#GUI
layout = [
    [
        sg.Text("参照フォルダ:", size=(15, 1)),
        sg.InputText(size=(50, 1), key='ref'),
        sg.FolderBrowse(initial_folder='$HOME', button_text="フォルダ選択")
    ],
    [
        sg.Text("保存フォルダ:", size=(15, 1)),
        sg.InputText(size=(50, 1), key='save'),
        sg.FolderBrowse(initial_folder='$HOME', button_text="フォルダ選択")
    ],
    [
        sg.Text("荷重:", size=(15, 1)),
        sg.InputText(key='load', size=(20, 1))
    ],
    [
        sg.Text("", size=(65, 1), key="status")
    ],
    [
        sg.Button("実行", key="Submit"),
        sg.Button("キャンセル", key="Cancel")
    ]
]

window = sg.Window("graph_maker", layout, margins=(20, 20))

event, values = window.read()

import sys
# キャンセルボタンで終了
if event == "Cancel":
    sys.exit()


window["status"].update("準備中")
window.refresh()

import matplotlib
import matplotlib.backends.backend_pdf
matplotlib.use('pdf')

import glob
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from scipy.signal import firwin, filtfilt
import os
import json

# フォントの指定
if sys.platform.startswith('win'):
    matplotlib.rc('font', family='Yu Gothic')
elif sys.platform.startswith('darwin'):
    matplotlib.rc('font', family='BIZ UDGothic')
else:
    raise RuntimeError("Unsupported platform")

# 関数
## ファイル名のソート関数
def sort_key(file):
    num = int(re.search(r'auto\$(\d+).csv', file).group(1))
    return num

## 設定ファイルの読み込み
def load_config():
    # 設定ファイルのフォルダと名前を決定する
    app_name = "graph_maker"
    config_filename = "config.json"

    # Windows か Mac かを判定する
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

    # 設定ファイルのパスを決定する
    config_file_path = os.path.join(config_folder, config_filename)
    
    # 設定ファイルを読み込む
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
    else:
        # 設定ファイルがない場合はデフォルト値を使う
        config = {
            'friction_scale': 1.0,
            'amp_scale': 1.0,
            'load': 9.8,
        }
    return config

# 設定を読み込む

config = load_config()
friction_scale = float(config['friction_scale'])
amp_scale = float(config['amp_scale'])
# load の値が空の文字列であるかどうかをチェック
if values['load'] == '':
    load = 9.8
else:
    load = float(values['load'])
save_path = values['save']
window["status"].update("準備完了")
window.refresh()

# 実行部分
if event == "Submit":
    # ファイルの検索
    path = values['ref'] + '/*.csv'
    files = glob.glob(path)
    files.sort(key=sort_key)
    number_of_files = len(files)
    # データ・摩擦力・振幅の初期化
    data = dict()
    # 試験結果読み込み
    for i, file_path in enumerate(files):
        window["status"].update(f"読み込み中: auto${i}.csv/auto${number_of_files}.csv")
        data[i] = pd.read_csv(file_path, header=41, skipfooter=3, encoding='shift-jis', engine='python', usecols=['日時(μs)','(1)HA-V01','(1)HA-V02','(1)HA-V04','(1)HA-V06'])
        window.refresh()
    window["status"].update("読み込み完了")
    window.refresh()
    # 試験条件の取得
    ## モーター振動数を取得
    window['status'].update('モーター振動数を取得中')
    window.refresh()
    motor_freq = round(np.mean(data[round(number_of_files/2)]['(1)HA-V04'])*10)
    window['status'].update(f'モーター振動数取得完了: {motor_freq}[Hz]')
    window.refresh()
    ## サンプリングレートを取得
    window['status'].update('サンプリングレートを取得中')
    window.refresh()
    sampling_rate = round((int(data[1]['日時(μs)'][3]) - int(data[1]['日時(μs)'][2])))*1e-6
    window['status'].update(f'サンプリングレート取得完了: {sampling_rate*1e6}[μs]')
    window.refresh()
    # せん断力係数と相対振幅を算出
    ## 摩擦力と振幅の平滑化
    number_of_data = len(data[0])
    t = np.arange(0, number_of_data*sampling_rate, sampling_rate)
    ### ローパスフィルターの設計
    cutoff_freq = motor_freq
    nyquist_rate = 1 / (2 * t[1])
    num_taps = 101  # タップ数（フィルターの長さ）
    lpf = firwin(num_taps, cutoff_freq, window="hamming", fs=nyquist_rate * 2)
    # せん断力係数と相対振幅・相対湿度の初期化
    CoF = []
    Amp = []
    Humidity = []
    for i in range(number_of_files):
        # force, ampのFFT
        # force_fft, amp_fftの初期化、
        window['status'].update(f'せん断力係数と相対振幅を算出中: auto${i}.csv/auto${number_of_files}.csv')
        force = []
        amp = []
        window.refresh()
        force.extend(data[i]['(1)HA-V01'])
        amp.extend(data[i]['(1)HA-V02'])
        force = filtfilt(lpf, 1, force)
        amp = filtfilt(lpf, 1, amp)
        CoF.append((max(force) - min(force)) * friction_scale / load)
        Amp.append((max(amp) - min(amp)) * amp_scale)
        Humidity.append(np.mean(data[i]['(1)HA-V06'])*10)
    window.refresh()
        
    # 経時変化のグラフを作成(x軸: 摺動回数, y軸: 摩擦力, 振幅, 湿度)
    
    window['status'].update(f'グラフを作成中: auto${i}.csv')
    x = np.arange(0, number_of_files*10, 10)
    fig = plt.figure(figsize=(5, 3), dpi=300)
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    ax1.set_xlim(0, number_of_files*10)
    ax1.set_ylim(0, 2.0)
    ax2.set_ylim(0, 100)
    ax1.grid(True, which='major', axis='y', color='gray', linestyle='--', linewidth=0.5)
    ax1.set_xlabel("繰り返し数")
    ax1.set_ylabel("せん断力係数[-]")
    ax2.set_ylabel(r"相対振幅[$\mu$m], 湿度[%]")
    ax1.scatter(x, CoF, s=0.1, label='せん断力係数' , c="#B84644")
    ax2.scatter(x, Amp, s=0.1, label='相対振幅', c="#90B34F")
    ax2.scatter(x, Humidity, s=0.1, label='相対湿度' , c="#4676B5")
    ax1.legend(markerscale = 5, frameon = False, loc = "upper right")
    ax2.legend(markerscale = 5, frameon = False, loc = "upper right", bbox_to_anchor = (1 ,0.9))
    window['status'].update(f'グラフ作成完了')
    window.refresh()
    # グラフの保存
    window['status'].update(f'グラフを保存中')
    window.refresh()
    fig.savefig(f'{values["save"]}/result.pdf', bbox_inches='tight')
    window['status'].update(f'グラフを保存完了')
    window.refresh()
    # csvファイルの出力
    ## データフレームの作成
    window['status'].update(f'csvファイルを保存中')
    window.refresh()
    df_result = pd.DataFrame({'繰り返し数': x, 'せん断力係数': CoF, '相対振幅': Amp, '相対湿度': Humidity})
    ## csvファイルの保存
    df_result.to_csv(f'{values["save"]}/result.csv', index=False)
    window['status'].update(f'csvファイルを保存完了')
event, values = window.read()
window.close()