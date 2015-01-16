import sys, os, random

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from __builtin__ import enumerate

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

from core import *

class Worker(QThread):
    update_data = pyqtSignal(tuple)
    update_gencount = pyqtSignal(int)
    core = None

    def run(self):
        for i in range(self.core.config.trajanje_svijeta):
            grupiranje, centri = self.core.cycle()
            if i % 3 is 0:
                self.update_data.emit((grupiranje, centri))
            self.update_gencount.emit(i)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self._thread = Worker(self)

        self.setupMatplotlibWidget()
        self.setupUi(self.canvas)
        self._thread.update_gencount.connect(self.updateGenLabel)
        self._thread.update_data.connect(self.on_draw)
        self.setupActions()

        self.selectDataset('Iris')

    def selectDataset(self, dataset):
        ds = self.getNewConfig(dataset)
        self.core = Core(Config(ds))
        self.dimensions = self.core.config.n_dims
        self.colors = []
        self._thread.core = self.core
        self.dimensionLabel.setText(str(self.core.config.dataset.getColNum()) + 'x' + str(self.core.config.dataset.getRowNum()))
        self.on_draw_initial(self.core.config.dataset.data)

    def getNewConfig(self, dataset):
        if dataset == 'Iris': return Iris()
        elif dataset == 'Glass' : return Glass()
        elif dataset == 'Wine' : return Wine()
        elif dataset == 'Breast cancer' : return Cancer()

    def getColor(self, klasa):
        if klasa > len(self.colors) - 1:
            color = (random.random(), random.random(), random.random())
            self.colors.append(color)
            return color
        else:
            return self.colors[klasa]

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"

        path = unicode(QFileDialog.getSaveFileName(self,
                        'Save file', '',
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)

    def setup_axes(self):
        if (self.dimensions == 2):
            self.axes.clear()
            self.axes.set_xlim(-50, 150)
            self.axes.set_ylim(-50, 150)
        else:
            self.axes.clear()
            self.axes.set_zlim3d([-50, 150])
            self.axes.set_ylim3d([-50, 150])
            self.axes.set_xlim3d([-50, 150])

    def on_draw(self, data):

        # clear the axes and redraw the plot anew
        self.setup_axes()

        for iklasa, klasa in enumerate(data[0]):
            self.axes.plot([t[0] * 100 for t in klasa],
                           [t[1] * 100 for t in klasa],
                           [t[2] * 100 for t in klasa if self.dimensions > 2],
                           'o',
                           markersize=5,
                           color=(self.getColor(data[0].index(klasa))))
            self.axes.plot([data[1][iklasa][0] * 100 ],
                           [data[1][iklasa][1] * 100 ],
                           'x',
                           markersize=10,
                           color=(self.getColor(data[0].index(klasa))))

        self.canvas.draw()

    def on_draw_initial(self, data):
        if (self.dimensions > 2):
            self.axes = Axes3D(self.fig)

        # clear the axes and redraw the plot anew
        self.setup_axes()

        self.axes.plot([t[0] * 100 for t in data],
                       [t[1] * 100 for t in data],
                       [t[2] * 100 for t in data if self.dimensions > 2],
                       'o', markersize=5 ,
                       color=(self.getColor(data[0].index(data[0][0]))))
        self.generationLabel.setText('0/' + str(self.core.config.trajanje_svijeta))
        self.canvas.draw()

    def setupMatplotlibWidget(self):
        self.dpi = 120
        self.fig = Figure((10.0, 10.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.axes = self.fig.add_subplot(111)
        #self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def updateGenLabel(self, i):
        self.generationLabel.setText(str(i) + '/' + str(self.core.config.trajanje_svijeta))

    def setupUi(self, canvas):
        self.setObjectName("Evo-clustering")
        self.resize(600, 650)
        self.centralwidget = QtGui.QWidget()

        hbox = QtGui.QHBoxLayout()
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        for i in ['Iris', 'Wine', 'Glass', 'Breast cancer']:
            self.comboBox.addItem(i)
        self.label = QtGui.QLabel("Dataset")
        hbox.addWidget(self.label)
        hbox.addWidget(self.comboBox)

        hbox2 = QtGui.QHBoxLayout()
        self.label_2 = QtGui.QLabel("Dataset dimensions")
        self.dimensionLabel = QtGui.QLabel("None loaded")
        hbox2.addWidget(self.label_2)
        hbox2.addWidget(self.dimensionLabel)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)

        vbox1= QtGui.QVBoxLayout()
        self.startButton = QtGui.QPushButton("Start")

        hbox3 = QtGui.QHBoxLayout()
        hbox4 = QtGui.QHBoxLayout()
        self.label_3 = QtGui.QLabel("Current generation")
        self.label_4 = QtGui.QLabel("Number of clusters")
        self.generationLabel = QtGui.QLabel('0')
        self.clusterNumLabel = QtGui.QLabel('0')
        hbox3.addWidget(self.label_3)
        hbox3.addWidget(self.generationLabel)
        hbox4.addWidget(self.label_4)
        hbox4.addWidget(self.clusterNumLabel)

        vbox1.addWidget(self.startButton)
        vbox1.addLayout(hbox3)
        vbox1.addLayout(hbox4)

        hbox_master = QtGui.QHBoxLayout()
        hbox_master.addLayout(vbox)
        hbox_master.addLayout(vbox1)

        vbox_master = QtGui.QVBoxLayout()
        vbox_master.addWidget(canvas)
        vbox_master.addLayout(hbox_master)
        self.centralwidget.setLayout(vbox_master)

        self.setCentralWidget(self.centralwidget)


    def setupActions(self):
        QtCore.QObject.connect(self.comboBox, QtCore.SIGNAL("currentIndexChanged(QString)"), self.selectDataset)
        QtCore.QObject.connect(self.startButton, QtCore.SIGNAL("clicked()"), self._thread.run)


def main():
    app = QApplication(sys.argv)
    form = MainWindow(parent=None)
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()