import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
from matplotlib.animation import FuncAnimation

class RadarAnimation:
    def __init__(self, file_path, channels, buffer_size=3):
        self.file_path = file_path
        self.channels = channels
        self.data = self.read_data(file_path, channels)
        self.buffer_size = buffer_size

    def read_data(self, file_path, channels):
        channel_data = {channel: [] for channel in channels}
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  
            for row in reader:
                for i, channel in enumerate(channels):
                    channel_data[channel].append(float(row[i]))
        return channel_data

    def update(self, frame, ax, lines, fills, buffer):
        values = [self.data[channel][frame] for channel in self.channels]
        theta = np.linspace(0, 2 * np.pi, len(self.channels) + 1)
        values = np.append(values, values[0])  

        buffer.append(values)  # Maintain only last `buffer_size` frames

        for i, vals in enumerate(buffer):
            lines[i].set_data(theta, vals)
            fills[i].remove()
            fills[i] = ax.fill(theta, vals, alpha=0.2 * (i + 1), color=f"C{i}")[0]

        return lines + fills

    def create_radar_animation(self):
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'polar': True})
        ax.set_xticks(np.linspace(0, 2 * np.pi, len(self.channels), endpoint=False))
        ax.set_xticklabels(self.channels, fontsize=10)

        lines = [ax.plot([], [], marker='o', lw=2)[0] for _ in range(self.buffer_size)]
        fills = [ax.fill([], [], alpha=0.2)[0] for _ in range(self.buffer_size)]
        buffer = deque(maxlen=self.buffer_size)

        frames = len(next(iter(self.data.values())))
        return FuncAnimation(fig, self.update, frames=frames, fargs=(ax, lines, fills, buffer), interval=600, blit=False)

def run_radar_animation(input_file, output_file):
    print('run_radar_animation start')
    channels = [f'Col{i}' for i in range(16)]
    radar_animation = RadarAnimation(input_file, channels)
    anim = radar_animation.create_radar_animation()
    anim.save(output_file, writer='ffmpeg', fps=10)
    print('run_radar_animation end')

