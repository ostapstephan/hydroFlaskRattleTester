from scipy import signal
import matplotlib.pyplot as plt

sample_rate, samples = wavFile.read('./Audacity/BadBottleBoth.wav')
freq, times, spectrogram = signal.spectrogram(samples, sample_rate)

plt.pcolormesh(times,freq,spectrogram)
plt.imshow(spectrogram)
plt.xlabel('time')
plt.ylabel('freq')
plt.show()