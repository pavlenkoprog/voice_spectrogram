import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# путь к файлу
path = "voice_examples/Девушка1 WAV .wav"

# загрузка WAV
sample_rate, data = wavfile.read(path)
if len(data.shape) > 1:
    data = data[:, 0]

# нормализация
data = data / np.max(np.abs(data))

# ---- ВЫБОР ВРЕМЕННОГО ПЕРИОДА ----
t_start = 1.2  # сек
t_end   = 1.6  # сек

start_idx = int(t_start * sample_rate)
end_idx   = int(t_end   * sample_rate)

segment = data[start_idx:end_idx]
# ----------------------------------

# мгновенная амплитуда |x(t)|
abs_signal = np.abs(segment)

# сглаживание: большое окно → плавная линия, но высокое разрешение сохраняется
window_size = int(0.005 * sample_rate)  # 5 мс
window = np.ones(window_size) / window_size

envelope = np.convolve(abs_signal, window, mode='same')

# шкала времени
time = np.linspace(t_start, t_end, len(envelope))

# график
plt.figure(figsize=(12, 5))
plt.plot(time, envelope)
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда (огибающая)")
plt.title("График громкости с максимальным разрешением")
plt.grid(True)
plt.show()
