import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram

# путь к файлу
path = "voice_examples/Девушка1 WAV .wav"

# загрузка
sample_rate, data = wavfile.read(path)
if len(data.shape) > 1:
    data = data[:, 0]

# Параметры для максимальной детализации
nperseg = 4096
noverlap = int(nperseg * 0.9)
freq_limit = 15000  # ограничение частоты

# вычисление спектрограммы
f, t, Sxx = spectrogram(
    data,
    fs=sample_rate,
    window='hann',
    nperseg=nperseg,
    noverlap=noverlap,
    scaling='density',
    mode='magnitude'
)

# ограничение частоты
mask = f <= freq_limit
f = f[mask]
Sxx = Sxx[mask, :]

# перевод в dB
Sxx_dB = 20 * np.log10(Sxx + 1e-10)

# ограничение динамического диапазона (например, -120…0 dB)
Sxx_dB = np.clip(Sxx_dB, -50, 0)

# визуализация
plt.figure(figsize=(14, 7))
plt.pcolormesh(t, f, Sxx_dB, shading='gouraud', cmap='inferno')
plt.ylabel("Частота (Гц)")
plt.xlabel("Время (с)")
plt.title("Максимально информативная спектрограмма (логарифмическая амплитуда)")
plt.colorbar(label="Амплитуда (dB)")
plt.ylim(0, freq_limit)
plt.tight_layout()
plt.show()
