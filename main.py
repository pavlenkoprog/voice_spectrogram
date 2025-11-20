import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# путь к вашему файлу
path = "voice_examples/Девушка1 WAV .wav"

# загрузка
sample_rate, data = wavfile.read(path)

# если стерео — берём один канал
if len(data.shape) > 1:
    data = data[:, 0]

# вычисление FFT
N = len(data)
spectrum = np.fft.fft(data)
freq = np.fft.fftfreq(N, d=1/sample_rate)

# берём только положительные частоты
idx = np.where(freq >= 0)
freq = freq[idx]
spectrum = np.abs(spectrum[idx])

# график
plt.figure(figsize=(12, 6))
plt.plot(freq, spectrum)
plt.xlabel("Частота (Гц)")
plt.ylabel("Амплитуда")
plt.title("Спектр WAV-сигнала")
plt.grid(True)
plt.show()
