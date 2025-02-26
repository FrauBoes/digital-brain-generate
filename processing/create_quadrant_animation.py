import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore, QtGui
import imageio

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

        # Draw static circle
        theta = np.linspace(0, 2 * np.pi, 500)
        x_circle = np.cos(theta)
        y_circle = np.sin(theta)
        self.plot_widget.plot(x_circle, y_circle, pen=pg.mkPen(color='white', width=2))

        # Quadrant lines
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
        self.frames = []  # List to store frames for animation

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

            # Capture frame
            self.capture_frame()

            self.current_index += 1
        else:
            self.timer.stop()
            self.save_animation()

    def capture_frame(self):
        """Capture the current frame and store it as an image."""
        pixmap = self.plot_widget.grab()  # Take a snapshot of the plot
        img = pixmap.toImage()
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.OpenModeFlag.WriteOnly)
        img.save(buffer, "PNG")
        self.frames.append(buffer.data())

    def save_animation(self):
        """Save the stored frames as a GIF or MP4."""
        if not self.frames:
            print("No frames captured.")
            return

        # Convert frames to images
        images = [QtGui.QImage.fromData(frame) for frame in self.frames]
        images = [QtGui.QPixmap.fromImage(img).toImage() for img in images]

        # Save as GIF
        gif_filename = "quadrant_animation.gif"
        imageio.mimsave(gif_filename, [self.qimage_to_numpy(img) for img in images], fps=1)
        print(f"Saved animation as {gif_filename}")

    def qimage_to_numpy(self, img):
        """Convert QImage to a NumPy array."""
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.WriteOnly)
        img.save(buffer, "PNG")
        np_img = np.frombuffer(buffer.data(), np.uint8)
        return imageio.imread(np_img)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    quadrant_window = QuadrantAnimation()
    quadrant_window.show()
    sys.exit(app.exec())
