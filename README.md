# EWSDemodulator
緊急警報放送復調器

# これはなに？
緊急警報放送(EWS)とは、災害時にEWS検知機能付き機器(ラジオなど)を自動起動するためのピロピロ音です。
このスクリプトは音声入力(または音声ファイル)からEWSの信号を取り出し、0と1に復調します。

# インストール
事前に pyaudio と numpy モジュールをインストールするだけで動くはずです。

# 調整
EWSDemodulatorのクラス変数は調整用のパラメータです。
- audio_args と stream_args は音声入力に応じて書き換える必要があります。pyaudioのマニュアルも参照しましょう。
```
    # Args for pyaudio
    audio_args =  {'format':   pyaudio.paInt16,
                   'rate':     44100,
                   'channels': 1,
                   #'input_device_index': 2,
                   'input':    True,
                   'frames_per_buffer': 4096,}
    stream_args = (4096, False)
```
- carrier_freq_margin, signale_freq_margin は音声入力のサンプリングレートが低い場合は、これらの値を大きくする必要があるかもしれません。
```
    # Carrier Frequency Hi/Low [Hz]
    carrier_freq        = 640
    carrier_freq_margin = 30
    # Signal Frequency Hi/Low [Hz]
    signal_freq        = 1024
    signal_freq_margin = 30
```

# 使い方
コマンドとして実行するか、モジュールとしてインポートして EWSDemodulator クラスのインスタンスを生成し、 start メソッドを実行してください。
```
demod = EWSDemodulator()
demod.start()
```

start メソッドにはコールバック関数を渡すことができます。start メソッドは復調した信号をリストに詰めてコールバック関数に渡して実行します。コールバック関数がデフォルトの場合は print 関数が呼ばれます。
```
print([0, 0, 1, 1, ...])
```
