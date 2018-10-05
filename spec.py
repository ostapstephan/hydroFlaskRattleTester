from scipy import signal
import matplotlib.pyplot as plt
from scipy.io import wavfile

sample_rate, samples = wavfile.read('./Audacity/BadBottleBoth.wav')
print(sample_rate)
freq, times, spectrogram = signal.spectrogram(samples, sample_rate)



plt.pcolormesh(times,freq,spectrogram)
plt.imshow(spectrogram)
plt.xlabel('time')
plt.ylabel('freq')
plt.show()