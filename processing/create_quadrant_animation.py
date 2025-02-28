import numpy as np
import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters
import cv2
import os
from PyQt6 import QtCore, QtWidgets

class QuadrantAnimation(QtWidgets.QMainWindow):
    def __init__(self, input_csv, output_video, image_folder="quadrant_frames"):
        super().__init__()

        self.setWindowTitle("Quadrant Circle Animation")
        self.resize(800, 800)

        self.plot_widget = pg.PlotWidget(title="Quadrants")
        self.plot_widget.setBackground("black")
        self.plot_widget.setAspectLocked()
        self.plot_widget.setXRange(-0.1, 0.1)  # set scale of graph
        self.plot_widget.setYRange(-0.1, 0.1)
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
        self.image_folder = image_folder
        self.output_video = output_video
        os.makedirs(self.image_folder, exist_ok=True)

        self.load_csv(input_csv)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

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

            self.save_plot(self.current_index)
            self.current_index += 1
        else:
            self.timer.stop()
            self.generate_video()
            self.cleanup_images()
            QtWidgets.QApplication.quit()

    def save_plot(self, index):
        exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
        exporter.parameters()["width"] = 800
        exporter.export(f"{self.image_folder}/quadrant_plot_{index:04d}.png")

    def generate_video(self):
        images = sorted([img for img in os.listdir(self.image_folder) if img.endswith(".png")])
        if not images:
            print("... no images found for video generation")
            return

        frame = cv2.imread(os.path.join(self.image_folder, images[0]))
        height, width, layers = frame.shape
        video = cv2.VideoWriter(self.output_video, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))

        for image in images:
            video.write(cv2.imread(os.path.join(self.image_folder, image)))

        video.release()
        print(f"... video saved as {self.output_video}")

    def cleanup_images(self):
        for img_file in os.listdir(self.image_folder):
            file_path = os.path.join(self.image_folder, img_file)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        print("... all images deleted from quadrant_frames")

def run_quadrant_animation(input_csv, output_video):
    print('run_quadrant_animation start')
    app = QtWidgets.QApplication([])
    quadrant_window = QuadrantAnimation(input_csv, output_video)
    quadrant_window.show()
    app.exec()
    print('run_quadrant_animation end')

