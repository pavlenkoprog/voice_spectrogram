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

# спектрограмма
f, t, Sxx = spectrogram(
    data,
    fs=sample_rate,
    window='hann',
    nperseg=2048,
    noverlap=1024,
    mode='magnitude'
)

# ограничение частоты до 10 kHz
freq_limit = 2000
mask = f <= freq_limit

f = f[mask]
Sxx = Sxx[mask, :]

# ограничение амплитуды до 150
Sxx = np.clip(Sxx, 0, 150)

# график
plt.figure(figsize=(12, 6))
plt.pcolormesh(t, f, Sxx, shading='gouraud')
plt.ylabel("Частота (Гц)")
plt.xlabel("Время (с)")
plt.title("Спектрограмма (0–2 kHz, амплитуда до 150)")
plt.colorbar(label="Амплитуда")
plt.ylim(0, freq_limit)
plt.show()
