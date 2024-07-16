from PySide6 import QtGui 
import matplotlib
import matplotlib.pyplot as plt
import sys
import shutil
import os

matplotlib.use('Qt5Agg')
from PySide6.QtWidgets import QMainWindow, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from matplotlib import pyplot as plt
import numpy as np
from PySide6.QtWidgets import (QApplication, 
                               QWidget, 
                               QInputDialog, 
                               QLineEdit, 
                               QFileDialog, 
                               QPushButton, 
                               QVBoxLayout,
                               QHBoxLayout
                               )
import h5py

class FigurePlot(QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=200):
        super(FigurePlot, self).__init__(parent)
        
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.path = None
        self.curr_idx = 0
        self.all_patterns = None
        self.len = 0
        self.ui()
        
    def ui(self, *args, **kwargs):
        # initialize buttons
        self.button1 = QPushButton('Browse')
        self.button1.clicked.connect(self.open_file)
        self.button2 = QPushButton('Plot')
        self.button2.clicked.connect(self.init_graph)
        self.button3 = QPushButton('<-')
        self.button3.clicked.connect(lambda: self.next_graph(False))
        self.button4 = QPushButton('->')
        self.button4.clicked.connect(lambda: self.next_graph(True))
        self.button5 = QPushButton('Close App')
        self.button5.clicked.connect(self.close_mainwindow)
        self.button6 = QPushButton('Trash')
        self.button6.clicked.connect(self.delete_graph)
        
        # setup layout
        layout = QHBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addWidget(self.button4)
        layout.addWidget(self.button5)
        layout.addWidget(self.button6)
        
        self.setLayout(layout)
        
    def open_file(self, *args, **kwargs):
        opts = QFileDialog.Options()
        opts |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileName(self,
            "QFileDialog.getOpenFileName()", 
            "","All Files (*);;Python Files (*.py)", 
            options=opts)
        self.path = file
        version = 0

        split_path = self.path.split(".hp")[0]
        copy_path = split_path + "_copy_0.hp"

        while os.path.exists(copy_path):
            version += 1
            copy_path = split_path + f"_trash_{version}.hp"
            
        copy_path = split_path + f"_trash_{version}.hp"
        shutil.copy(file, copy_path)

    def init_graph(self, *args, **kwargs):
        if self.path:
            with h5py.File(self.path, 'a') as f:
                self.all_patterns = f['diffraction']['micrograph'][:]
                self.len = len(self.all_patterns)
                print(f"Number of files: {self.len}")
                self.plot_graph()
    
    def plot_graph(self, *args, **kwargs):
        if self.len > 0:
            self.curr_pattern = self.all_patterns[self.curr_idx]
            self.axes.clear()
            self.axes.imshow(self.curr_pattern, cmap='gray')
            self.axes.set_title(f"Electron Diffraction Pattern {self.curr_idx + 1} of {self.len}")
            self.canvas.draw()
    
    def next_graph(self, next: bool = None, *args, **kwargs):
        if next is not None:
            if next:
                self.curr_idx += 1
                if self.curr_idx == self.len:
                    self.curr_idx = 0
            else:
                self.curr_idx -= 1
                if self.curr_idx == -1:
                    self.curr_idx = self.len - 1
            self.plot_graph()
    
    def close_mainwindow(self):
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            main_window.close()
    
    def delete_graph(self, *args, **kwargs):
        if self.len > 0:
            with h5py.File(self.path, 'a') as f:
                patterns = f['diffraction']['micrograph'][:]
                new_data = np.delete(patterns, self.curr_idx, axis=0)
                del f['diffraction']['micrograph']
                f.create_dataset('diffraction/micrograph', data=new_data)
                self.all_patterns = new_data
                self.len = len(self.all_patterns)
                if self.curr_idx >= self.len:
                    self.curr_idx = 0
                self.plot_graph()

        
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.title = "Plot"
        self.setWindowTitle(self.title)
        self.plot = FigurePlot(self, width =5, height =5, dpi=200)
        self.setCentralWidget(self.plot)
        
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

w = MainWindow()
w.show()
app.exec()