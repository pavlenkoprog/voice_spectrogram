import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram

# путь к файлу
path = "voice_examples/Запись_речи_с_петличного_микрофона_WAV_.wav"

# загружаем весь WAV
sample_rate, data = wavfile.read(path)
if len(data.shape) > 1:
    data = data[:, 0]

# ---- ВЫБОР ВРЕМЕННОГО ПЕРИОДА ----
t_start = 0  # сек
t_end = 0.5    # сек

start_idx = int(t_start * sample_rate)
end_idx = int(t_end * sample_rate)

data_segment = data[start_idx:end_idx]
# ---------------------------------

# параметры спектрограммы
nperseg = 1024
noverlap = int(nperseg * 0.9)
freq_limit = 20000

# спектрограмма только выбранного фрагмента
f, t, Sxx = spectrogram(
    data_segment,
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
Sxx_dB = np.clip(Sxx_dB, -50, 0)

# график
plt.figure(figsize=(14, 7))
plt.pcolormesh(t + t_start, f, Sxx_dB, shading='gouraud', cmap='inferno')
#           ^ добавили смещение по времени

plt.ylabel("Частота (Гц)")
plt.xlabel("Время (с)")
plt.title("Спектрограмма выбранного временного участка (dB)")
plt.colorbar(label="Амплитуда (dB)")
plt.ylim(0, freq_limit)
plt.tight_layout()
plt.show()
