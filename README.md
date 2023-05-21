# 摩擦力・振幅・湿度データ解析アプリ

## TL;DR

このアプリケーションは、NR-500から出力された電圧から摩擦力・振幅・湿度データを解析して経時変化のグラフを作成するアプリケーションです。

## 必要なもの

- Python (3.10以上が望ましい)
- 後述するライブラリ
- VSCode (任意)

## ライブラリのインストール

このアプリケーションを実行するには、以下のライブラリが必要です。

- matplotlib
- numpy
- pandas
- PySimpleGUI
- scipy

素早くインストールするには、以下のコマンドを実行してください。

### condaを使う場合

```bash
conda env create -f macros_gui.yml
```

### condaを使わない場合

```bash
pip install -r pip_requirements.txt
```

## VS Codeの拡張機能

VS Codeを使う場合、以下の拡張機能をインストールすると便利です。

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python Environment Manager](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python-environment-manager)

## VS Codeで実行

VS Codeでこのアプリケーションを実行するには、以下の手順を実行してください。

1. VS Codeでフォルダを開く。
2. 実行したいPythonファイルを開く。
3. 「実行とデバッグ」パネルを開く。
4. 再生ボタンを押してコードを実行する。

### 公正係数の設定

このアプリケーションを初めて実行する場合、または新たに公正係数を設定する場合は'`constant_configure.py`'を実行してください。


