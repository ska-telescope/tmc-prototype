import sys
import os
from PyQt4 import QtCore, QtGui
from PyQt4 import Qwt5
from taurus.qt.qtgui.plot import TaurusPlot
from taurus.qt.qtgui.util.ui import UILoadable
import PyTango
import taurus
@UILoadable

class poc(QtGui.QMainWindow):
    def __init__(self):
        super(poc,self).__init__()
        self.loadUi(path=os.path.abspath(os.path.dirname(__file__)))
        
        self.panel1 = TaurusPlot()
        self.panel2 = TaurusPlot()
        self.panel3 = TaurusPlot()
        self.panel4 = TaurusPlot()
        
        model1 = ['ska_mid/subarray_node/1/desiredPoint', 'ska_mid/subarray_node/1/achievedPoint']
        model2 = ['ska_mid/subarray_node/2/desiredPoint', 'ska_mid/subarray_node/2/achievedPoint']
        model3 = ['ska_mid/subarray_node/3/desiredPoint', 'ska_mid/subarray_node/3/achievedPoint']
        # model4 = ['ska_mid/subarray_node/4/desiredPoint', 'ska_mid/subarray_node/4/achievedPoint']
        
        self.panel1.setModel(model1)
        self.panel2.setModel(model2)
        self.panel3.setModel(model3)
        
        self.panel1.setTitle('Dish1')
        
        self.verticalLayout1.addWidget(self.panel1)
        self.verticalLayout2.addWidget(self.panel2)
        self.verticalLayout3.addWidget(self.panel3)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myWindow = poc()
    myWindow.show()
    sys.exit(app.exec_())        
        
