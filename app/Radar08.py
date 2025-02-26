import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyqtgraph as pg
from matplotlib.animation import FuncAnimation
from PyQt6 import QtCore, QtWidgets

class RadarAnimation:
    def __init__(self, file_path, channels):
        self.file_path = file_path
        self.channels = channels
        self.data = self.read_data(file_path, channels)
        self.buffer_size = 3

    def read_data(self, file_path, channels):
        """Reads data from a CSV file and returns a dictionary of channel values."""
        channel_data = {channel: [] for channel in channels}
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  
            for row in reader:
                for i, channel in enumerate(channels):
                    channel_data[channel].append(float(row[i]))
        return channel_data

    def update(self, frame, ax, lines, fills):
        """Update the radar chart for each frame."""
        start = max(0, frame - self.buffer_size + 1)
        frames_to_show = range(start, frame + 1)

        while len(lines) > len(frames_to_show):
            lines.pop(0).remove()
            fills.pop(0)[0].remove()

        for i, f in enumerate(frames_to_show):
            values = [self.data[channel][f] for channel in self.channels]
            theta = np.linspace(0, 2 * np.pi, len(self.channels) + 1)
            values = np.append(values, values[0])  

            if i < len(lines):
                lines[i].set_data(theta, values)
                fills[i][0].remove()
                fills[i][0] = ax.fill(theta, values, alpha=0.2 * (i + 1), color=f"C{i}")[0]
            else:
                line, = ax.plot(theta, values, marker='o', alpha=0.6, lw=2, label=f"Frame {f}")
                fill = [ax.fill(theta, values, alpha=0.2 * (i + 1), color=f"C{i}")[0]]
                lines.append(line)
                fills.append(fill)

        return lines + [f[0] for f in fills]

    def animate_radar(self):
        """Creates an animated radar chart."""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'polar': True})
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(np.linspace(0, 2 * np.pi, len(self.channels), endpoint=False))
        ax.set_xticklabels(self.channels, fontsize=10)
        ax.set_title("Animated Radar Chart", fontsize=16, weight="bold", pad=20)

        ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.7)

        lines = []
        fills = []

        frames = len(next(iter(self.data.values())))
        anim = FuncAnimation(fig, self.update, frames=frames, fargs=(ax, lines, fills), interval=600, blit=False)
        plt.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1), fontsize=10)
        plt.tight_layout()
        plt.show()
        anim.save("radar_animation.mp4", writer="ffmpeg", fps=10)



class QuadrantAnimation(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quadrant Circle Animation")
        self.resize(800, 600)

        self.plot_widget = pg.PlotWidget(title="Quadrants")
        self.plot_widget.setBackground("black")
        self.plot_widget.setAspectLocked()
        self.plot_widget.setXRange(-1.5, 1.5)
        self.plot_widget.setYRange(-1.5, 1.5)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.setCentralWidget(self.plot_widget)

        theta = np.linspace(0, 2 * np.pi, 500)
        x_circle = np.cos(theta)
        y_circle = np.sin(theta)
        self.plot_widget.plot(x_circle, y_circle, pen=pg.mkPen(color='white', width=2))

        self.quadrant_lines = {
            "Q1": [pg.PlotDataItem(pen=pg.mkPen(color='red', width=2)) for _ in range(4)],
            "Q2": [pg.PlotDataItem(pen=pg.mkPen(color='green', width=2)) for _ in range(4)],
            "Q3": [pg.PlotDataItem(pen=pg.mkPen(color='blue', width=2)) for _ in range(4)],
            "Q4": [pg.PlotDataItem(pen=pg.mkPen(color='magenta', width=2)) for _ in range(4)]
        }
        for quadrant in self.quadrant_lines.values():
            for line in quadrant:
                self.plot_widget.addItem(line)

        self.data = []
        self.current_index = 0
        self.buffer_size = 4

        self.load_csv('data/data-interpolated.csv')

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(800)

    def load_csv(self, file_name):
        try:
            df = pd.read_csv(file_name, header=0)
            self.data = df.to_numpy()
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            self.data = []

    def update_plot(self):
        if self.current_index < len(self.data):
            row = self.data[self.current_index]

            quadrant_data = {
                "Q1": row[:len(row)//4],
                "Q2": row[len(row)//4:len(row)//2],
                "Q3": row[len(row)//2:3*len(row)//4],
                "Q4": row[3*len(row)//4:]
            }

            for quadrant, lines in self.quadrant_lines.items():
                values = quadrant_data[quadrant]
                for i, line in enumerate(lines):
                    if self.current_index - i >= 0:
                        angles = np.linspace(i * (np.pi / 2), (i + 1) * (np.pi / 2), len(values), endpoint=False)
                        angles = np.append(angles, angles[0])
                        values = np.append(values, values[0])
                        x = values * np.cos(angles)
                        y = values * np.sin(angles)
                        line.setData(x, y)
                    else:
                        line.clear()

            self.current_index += 1
        else:
            self.timer.stop()


if __name__ == "__main__":
    channels = [f'Col{i}' for i in range(16)]
    radar_animation = RadarAnimation('data/data-interpolated.csv', channels)
    radar_animation.animate_radar()

    app = QtWidgets.QApplication([])
    quadrant_window = QuadrantAnimation()
    quadrant_window.show()
    app.exec()
