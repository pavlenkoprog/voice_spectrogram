import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram

# путь к вашему файлу
path = "voice_examples/Девушка1 WAV .wav"

# загрузка аудио
sample_rate, data = wavfile.read(path)

# если стерео – берём один канал
if len(data.shape) > 1:
    data = data[:, 0]

# вычисление спектрограммы
f, t, Sxx = spectrogram(
    data,
    fs=sample_rate,
    window='hann',
    nperseg=1024,   # длина окна
    noverlap=512,  # перекрытие
    scaling='density',
    mode='magnitude'
)

# визуализация
plt.figure(figsize=(12, 6))
plt.pcolormesh(t, f, Sxx, shading='gouraud')
plt.ylabel("Частота (Гц)")
plt.xlabel("Время (с)")
plt.title("Спектрограмма (анализатор спектра)")
plt.colorbar(label="Амплитуда")
plt.show()
