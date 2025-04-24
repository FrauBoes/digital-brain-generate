import numpy as np
import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters
import time as tmee
import os
import subprocess
from PyQt6 import QtCore, QtWidgets


class VideoExportWorker(QtCore.QThread):
    def __init__(self, image_folder, output_video, parent=None):
        super().__init__(parent)
        self.image_folder = image_folder
        self.output_video = output_video

    def run(self):
        print("Background: Starting video export with ffmpeg...")

        cmd = [
            "ffmpeg",
            "-y",
            "-framerate", "10",
            "-i", os.path.join(self.image_folder, "quadrant_plot_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            self.output_video
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"Background: Video saved to {self.output_video}")
        except subprocess.CalledProcessError as e:
            print("FFmpeg failed:", e)

        # Cleanup
        for img in os.listdir(self.image_folder):
            try:
                os.remove(os.path.join(self.image_folder, img))
            except Exception as e:
                print(f"Error deleting image: {e}")
        print("Background: Image cleanup complete.")


class QuadrantAnimation(QtWidgets.QMainWindow):
    def __init__(self, input_csv, output_video, image_folder="quadrant_frames"):
        super().__init__()

        self.setWindowTitle("Quadrant Circle Animation")
        self.resize(800, 800)

        self.output_video = output_video
        self.image_folder = image_folder
        os.makedirs(self.image_folder, exist_ok=True)

        # Setup plot
        self.plot_widget = pg.PlotWidget(title="Quadrants")
        self.plot_widget.setBackground("black")
        self.plot_widget.setAspectLocked()
        self.plot_widget.setXRange(-0.03, 0.03)
        self.plot_widget.setYRange(-0.03, 0.03)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.setCentralWidget(self.plot_widget)

        # Circle
        theta = np.linspace(0, 2 * np.pi, 500)
        self.plot_widget.plot(np.cos(theta), np.sin(theta), pen=pg.mkPen("white", width=2))

        # Quadrants
        self.quadrant_lines = {
            q: [pg.PlotDataItem(pen=pg.mkPen(color=c, width=2)) for _ in range(4)]
            for q, c in zip(["Q1", "Q2", "Q3", "Q4"], ["red", "green", "blue", "magenta"])
        }
        for lines in self.quadrant_lines.values():
            for line in lines:
                self.plot_widget.addItem(line)

        # Load data
        self.data = self.load_csv(input_csv)
        self.num_rows = len(self.data)
        self.current_index = 0
        
        # Precompute
        total_cols = self.data.shape[1]
        self.buffer_size = 4
        self.quadrant_indices = np.array_split(np.arange(total_cols), 4)
        self.precomputed_angles = [
            np.linspace(i * np.pi / 2, (i + 1) * np.pi / 2, total_cols // 4, endpoint=False)
            for i in range(self.buffer_size)
        ]
        
        self.exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
        self.exporter.parameters()["width"] = 800

        self.worker = None
        self.start_time = tmee.time()

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

    def load_csv(self, path):
        try:
            return pd.read_csv(path).to_numpy()
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return np.empty((0, 0))

    def update_plot(self):
        if self.current_index >= self.num_rows:
            self.timer.stop()
            self.start_background_export()
            QtWidgets.QApplication.quit()
            return
        
        elapsed_time = tmee.time() - self.start_time
        if elapsed_time >= 35:
            self.close()

        row = self.data[self.current_index]
        for q_index, (q_name, lines) in enumerate(self.quadrant_lines.items()):
            values = row[self.quadrant_indices[q_index]]
            extended_values = np.append(values, values[0])
            for i, line in enumerate(lines):
                if self.current_index - i >= 0:
                    angles = self.precomputed_angles[i]
                    extended_angles = np.append(angles, angles[0])
                    x = extended_values * np.cos(extended_angles)
                    y = extended_values * np.sin(extended_angles)
                    line.setData(x, y)
                else:
                    line.clear()

        self.save_plot(self.current_index)
        self.current_index += 1

    def save_plot(self, index):
        filename = f"{self.image_folder}/quadrant_plot_{index:04d}.png"
        self.exporter.export(filename)
        print(f"Saved: {filename}")

    def start_background_export(self):
        self.worker = VideoExportWorker(self.image_folder, self.output_video)
        self.worker.start()

    def closeEvent(self, event):
        print("Window closed early. Running background export.")
        self.timer.stop()
        self.start_background_export()
        event.accept()


def run_quadrant_animation(input_csv, output_video):
    print("Starting animation...")
    app = QtWidgets.QApplication([])
    window = QuadrantAnimation(input_csv, output_video)
    window.show()
    app.exec()
    print("Animation finished.")
