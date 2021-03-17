import os
from typing import Union
import wave
import matplotlib.pyplot as plt
import librosa
import librosa.display
import scipy.io.wavfile as wav
import numpy as np
from keras.models import model_from_json, Sequential
from sklearn.externals import joblib
from sklearn.base import BaseEstimator

def load_model(
    checkpoint_path: str, checkpoint_name: str, model_name: str
) -> Union[Sequential, BaseEstimator]:
    """
    加载模型

    Args:
        checkpoint_path (str): checkpoint 路径
        checkpoint_name (str): checkpoint 文件名
        model_name (str): 模型名称

    Returns:
        model (Union[keras.Sequential, sklearn.base.BaseEstimator]): 加载好的模型
    """
    if model_name in ['lstm', 'cnn1d', 'cnn2d']:
        # 加载 json
        model_json_path = os.path.join(checkpoint_path, checkpoint_name + '.json')
        json_file = open(model_json_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)

        # 加载权重
        model_path = os.path.join(checkpoint_path, checkpoint_name + '.h5')
        model.load_weights(model_path)

    else:
        model_path = os.path.join(checkpoint_path, checkpoint_name + '.m')
        model = joblib.load(model_path)

    return model

def plotCurve(train: list, val: list, title: str, y_label: str) -> None:
    """
    绘制损失值和准确率曲线

    Args:
        train (list): 训练集损失值或准确率数组
        val (list): 测试集损失值或准确率数组
        title (str): 图像标题
        y_label (str): y 轴标题
    """
    plt.plot(train)
    plt.plot(val)
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

def play_audio(file_path: str) -> None:
    """
    播放语音

    Args:
        file_path (str): 要播放的音频路径
    """
    import pyaudio
    p = pyaudio.PyAudio()
    f = wave.open(file_path, 'rb')
    stream = p.open(
        format = p.get_format_from_width(f.getsampwidth()),
        channels = f.getnchannels(),
        rate = f.getframerate(),
        output = True
    )
    data = f.readframes(f.getparams()[3])
    stream.write(data)
    stream.stop_stream()
    stream.close()
    f.close()

def Radar(data_prob: np.ndarray, class_labels: list) -> None:
    """
    绘制置信概率雷达图

    Args:
        data_prob (np.ndarray): 概率数组
        class_labels (list): 情感标签
    """
    angles = np.linspace(0, 2 * np.pi, len(class_labels), endpoint = False)
    data = np.concatenate((data_prob, [data_prob[0]]))  # 闭合
    angles = np.concatenate((angles, [angles[0]]))  # 闭合

    fig = plt.figure()

    # polar参数
    ax = fig.add_subplot(111, polar = True)
    ax.plot(angles, data, 'bo-', linewidth=2)
    ax.fill(angles, data, facecolor='r', alpha=0.25)
    ax.set_thetagrids(angles * 180 / np.pi, class_labels)
    ax.set_title("Emotion Recognition", va = 'bottom')

    # 设置雷达图的数据最大值
    ax.set_rlim(0, 1)

    ax.grid(True)
    # plt.ion()
    plt.show()
    # plt.pause(4)
    # plt.close()

def Waveform(file_path: str) -> None:
    """
    绘制音频波形图

    Args:
        file_path (str): 音频路径
    """
    data, sampling_rate = librosa.load(file_path)
    plt.figure(figsize=(15, 5))
    librosa.display.waveplot(data, sr = sampling_rate)
    plt.show()

def Spectrogram(file_path: str) -> None:
    """
    绘制频谱图

    Args:
        file_path (str): 音频路径
    """

    # sr: 采样率
    # x: 音频数据的numpy数组
    sr, x = wav.read(file_path)

    # step: 10ms, window: 30ms
    nstep = int(sr * 0.01)
    nwin  = int(sr * 0.03)
    nfft = nwin
    window = np.hamming(nwin)

    nn = range(nwin, len(x), nstep)
    X = np.zeros( (len(nn), nfft//2) )

    for i,n in enumerate(nn):
        xseg = x[n-nwin:n]
        z = np.fft.fft(window * xseg, nfft)
        X[i,:] = np.log(np.abs(z[:nfft//2]))

    plt.imshow(X.T, interpolation = 'nearest', origin = 'lower', aspect = 'auto')
    plt.show()
