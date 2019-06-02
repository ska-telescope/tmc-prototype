from PyQt4 import QtCore
from PyQt4 import QtGui
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.util.ui import UILoadable
import os
import sys
import tango
from subprocess import Popen
from taurus.qt.qtgui.plot import TaurusPlot, CurveAppearanceProperties

@UILoadable
class mainWindow_SKA(QtGui.QMainWindow):
    def __init__(self):
        super(mainWindow_SKA, self).__init__()
        self.loadUi(path=os.path.abspath(os.path.dirname(__file__)))
        # self.setWindowIcon(QtGui.QIcon('path'))
        self.initialization()
        self.subscribeEvent()
        
    def initialization(self):
        
        # initializing containers and write click event of actions
        self.flag = True
        self.deviceVsprxoy = {}
        self.deivceVsCommand = {}
        self.dishProxy = {}
        self.generateProxy()
        self.generateCommandList()
        self.comboBoxNode.addItems(sorted(self.deviceVsprxoy.keys()))
        self.displayCommand()
        #self.attrDisplayTable(['TelescopeHealthState', 'Subarray1HealthState', 'Subarray2HealthState'], self.tableWidgetCentral, ['ska_mid/tm_central/central_node'])
        self.tableWidgetCentral.resizeRowsToContents()
        self.tableWidgetCentral.resizeColumnsToContents()
        self.attrDisplayTable(['ScanID', 'SbID', 'ReceptorIDList'], self.tableWidgetSubarray, ['ska_mid/tm_subarray_node/1', 'ska_mid/tm_subarray_node/2'])
        self.attrDisplayTable(['Capturing', 'WindSpeed', 'DesiredPointing', 'AchievedPointing'], self.tableWidgetDish, ['mid_d0001/elt/master', 'mid_d0002/elt/master', 'mid_d0003/elt/master', 'mid_d0004/elt/master'])
        
        # self.tableWidgetSubarray.horizontalHeaderItem(1).setBackgroundColor(QtCore.Qt.red)
        
        self.plotSpectrumAttr()
        
        self.comboBoxNode.currentIndexChanged.connect(self.displayCommand)
        self.comboBoxCommand.currentIndexChanged.connect(self.clearterminal)
        self.pushButtonExecute.clicked.connect(self.executeCommand)
        self.pushButtonLogViwer.clicked.connect(self.openLogViewer)
        self.pushButtonAlarmPanel.clicked.connect(self.openAlarmPanel)
        
    def plotSpectrumAttr(self):
        
        # plotting of spectrum attribute
        
        self.panel1 = TaurusPlot()
        self.panel2 = TaurusPlot()
        self.panel3 = TaurusPlot()
        self.panel4 = TaurusPlot()
        
        self.panel1.setTitle('Dish1')
        self.panel1.showLegend(False)
        # self.panel1.setStyleSheet("background-color: white;")
        # self.panel1.setCurveAppearanceProperties({'desiredPointing':CurveAppearanceProperties(sColor='red')})
        
        self.panel2.setTitle('Dish2')
        # self.panel2.setStyleSheet("background-color: white;")
        self.panel2.showLegend(False)
        
        self.panel3.setTitle('Dish3')
        self.panel3.showLegend(False)
        # self.panel3.setStyleSheet("background-color: white;")
        
        self.panel4.setTitle('Dish4')
        # self.panel4.setStyleSheet("background-color: white;")
        
        model1 = ['mid_d0001/elt/master/desiredPointing', 'mid_d0001/elt/master/achievedPointing']
        model2 = ['mid_d0002/elt/master/desiredPointing', 'mid_d0002/elt/master/achievedPointing']
        model3 = ['mid_d0003/elt/master/desiredPointing', 'mid_d0003/elt/master/achievedPointing']
        model4 = ['mid_d0004/elt/master/desiredPointing', 'mid_d0004/elt/master/achievedPointing']
        
        self.panel1.setModel(model1)
        self.panel2.setModel(model2)
        self.panel3.setModel(model3)
        self.panel4.setModel(model4)
        
        self.horizontalLayoutPlotting.addWidget(self.panel1)
        self.horizontalLayoutPlotting.addWidget(self.panel2)
        self.horizontalLayoutPlotting.addWidget(self.panel3)
        self.horizontalLayoutPlotting.addWidget(self.panel4)
        

    def generateProxy(self):
        
        try:
            # CentralNode proxy 
            
            self.deviceVsprxoy['CentralNode'] = tango.DeviceProxy('ska_mid/tm_central/central_node')
            
            # subarray node proxy
            
            self.deviceVsprxoy['Subarray1'] = tango.DeviceProxy('ska_mid/tm_subarray_node/1')
            self.deviceVsprxoy['Subarray2'] = tango.DeviceProxy('ska_mid/tm_subarray_node/2')
            
            # leaf Node proxy
            
            self.deviceVsprxoy['LeafNode1'] = tango.DeviceProxy('ska_mid/tm_leaf_node/d0001')
            self.deviceVsprxoy['LeafNode2'] = tango.DeviceProxy('ska_mid/tm_leaf_node/d0002')
            self.deviceVsprxoy['LeafNode3'] = tango.DeviceProxy('ska_mid/tm_leaf_node/d0003')
            self.deviceVsprxoy['LeafNode4'] = tango.DeviceProxy('ska_mid/tm_leaf_node/d0004')
            print 'self.dishProxy', self.dishProxy
            self.dishProxy['Dish1'] =  tango.DeviceProxy('mid_d0001/elt/master')
            self.dishProxy['Dish2'] =  tango.DeviceProxy('mid_d0002/elt/master')
            self.dishProxy['Dish3'] =  tango.DeviceProxy('mid_d0003/elt/master')
            self.dishProxy['Dish4'] =  tango.DeviceProxy('mid_d0004/elt/master')
            print 'self.dishProxy', self.dishProxy
        except Exception as e:
            self.plainTextEdit.appendPlainText('Unable to create device proxy')

    def generateCommandList(self):
        
        # generate command list from device proxy
        try:
            for device in self.deviceVsprxoy:
                self.deivceVsCommand[device] = self.deviceVsprxoy[device].get_command_list()
        except:
            self.plainTextEdit.appendPlainText('There is problem to fetch command list from device server '+device)

    def displayCommand(self):
        self.comboBoxCommand.clear()
        if self.comboBoxNode.currentText():
            self.comboBoxCommand.addItems(self.deivceVsCommand.get(str(self.comboBoxNode.currentText())))
        self.lineEditCommandTerminal.clear()
        
    def clearterminal(self):
        self.lineEditCommandTerminal.clear()

    def attrDisplayTable(self, l, tablewidget, nodelist):
    

        for row in range(len(l)):
            for column in range(len(nodelist)):
                tablewidget.setCellWidget(row+1, column+1, self.generateModel(nodelist[column]+'/'+l[row]))

        tablewidget.resizeRowsToContents()
        tablewidget.resizeColumnsToContents()

    def generateModel(self, modelName):
        valueLable = TaurusLabel()
        valueLable.setMinimumSize(QtCore.QSize(100, 0))
        valueLable.model = modelName
        valueLable.bgRole = 'None'
        valueLable.setAlignment(QtCore.Qt.AlignCenter)
        return valueLable
        
    def executeCommand(self):
        
        # execute command of node
        arg = str(self.lineEditCommandTerminal.text()).rstrip().lstrip().split()
        if arg:
            self.deviceVsprxoy.get(str(self.comboBoxNode.currentText())).command_inout(str(self.comboBoxCommand.currentText()), arg)
        else:
            self.deviceVsprxoy.get(str(self.comboBoxNode.currentText())).command_inout(str(self.comboBoxCommand.currentText()))   
            
    def openLogViewer(self):
        try:
            Popen('logviewer')    
        except:
            self.plainTextEdit.appendPlainText('Problem occurred opening logviewer')
    def openAlarmPanel(self):
        try:    
            Popen(['atkpanel', 'alarmhandler/1/1'])
        except:
            self.plainTextEdit.appendPlainText('Problem occurred while opening Alarm handler')
    
    def activityLogs(self, event):
        device = event.device.dev_name()
        if event.attr_value is not None:
            v = event.attr_value.value
            text = '[' + device + '] ' + v
            self.plainTextEdit.appendPlainText(text)
        
    def subarrayDishColor(self,event):
        try:
            try:
                receptorIDList = event.attr_value.value
		print "Start of the event: ", str(receptorIDList)
                #print "Printing value :-> ", type(receptorIDList)
                #print "Printing Attr value :-> ", event.attr_value
            except:
                print 'in dish color first try', event.attr_value
            device = str(event.device.dev_name())
            if receptorIDList is not None and len(receptorIDList)>0 and device[-1] == '1':
                for i in receptorIDList:
                    self.tableWidgetDish.item(0,i).setBackgroundColor(QtCore.Qt.blue) 
            elif receptorIDList is not None and len(receptorIDList)>0 and device[-1] == '2':
                for i in receptorIDList:
                    self.tableWidgetDish.item(0,i).setBackgroundColor(QtCore.Qt.magenta)
            
            id1 = self.deviceVsprxoy['Subarray1'].receptorIDList if self.deviceVsprxoy['Subarray1'].receptorIDList is not None else ()
            id2 = self.deviceVsprxoy['Subarray2'].receptorIDList if self.deviceVsprxoy['Subarray2'].receptorIDList is not None else ()
            notColored = set([1,2,3,4])^(set(id1)|set(id2))
            if len(notColored)>0:
                for j in notColored:
                   self.tableWidgetDish.item(0,j).setBackgroundColor(QtCore.Qt.white)       
        except Exception as e:
            print "In exception of the event: ", str(receptorIDList)
            #print "Printing Attr value :-> ", event.attr_value
            print 'in dishcolor error:', str(e)
        
        
    def updateval(self, eve):
        device = eve.device
        # print 'd', device
        attrv = eve.attr_value.name
        # print 'attrv',attrv
        # print 'device name', device.dev_name()
        # print 'value', device.telescopeHealthState.name
        if self.flag:
            self.flag = False
            if eve.attr_value.name.lower() == 'telescopeHealthState'.lower():
                item = QtGui.QTableWidgetItem(device.telescopeHealthState.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetCentral.setItem(0,1,item)
            elif eve.attr_value.name.lower() == 'Subarray1HealthState'.lower():
                item = QtGui.QTableWidgetItem(device.Subarray1HealthState.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetCentral.setItem(1,1,item)
            elif eve.attr_value.name.lower() == 'Subarray2HealthState'.lower():
                item = QtGui.QTableWidgetItem(device.Subarray2HealthState.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetCentral.setItem(2,1,item)
                
            elif eve.attr_value.name.lower() == 'HealthState'.lower() and device.dev_name()[:-1] == 'ska_mid/tm_subarray_node/':
                item = QtGui.QTableWidgetItem(device.HealthState.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetSubarray.setItem(4,int(device.dev_name()[-1]), item)    
            elif eve.attr_value.name.lower() == 'ObsMode'.lower():
                item = QtGui.QTableWidgetItem(device.ObsMode.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetSubarray.setItem(5,int(device.dev_name()[-1]),item)    
            elif eve.attr_value.name.lower() == 'ObsState'.lower():
                item = QtGui.QTableWidgetItem(device.ObsState.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetSubarray.setItem(6,int(device.dev_name()[-1]),item)
                
            elif eve.attr_value.name.lower() == 'HealthState'.lower():
                item = QtGui.QTableWidgetItem(device.HealthState.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetDish.setItem(5,int(device.dev_name()[8]),item)    
            elif eve.attr_value.name.lower() == 'dishMode'.lower():
                print 'dishmode', device.dev_name()
                item = QtGui.QTableWidgetItem(device.dishMode.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetDish.setItem(6,int(device.dev_name()[8]),item) 
            elif eve.attr_value.name.lower() == 'pointingState'.lower():
                item = QtGui.QTableWidgetItem(device.pointingState.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetDish.setItem(7,int(device.dev_name()[8]),item)     
            elif eve.attr_value.name.lower() == 'ConfiguredBand'.lower():
                item = QtGui.QTableWidgetItem(device.ConfiguredBand.name)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter| QtCore.Qt.AlignCenter)
                self.tableWidgetDish.setItem(8,int(device.dev_name()[8]),item) 
                
        self.flag = True
        
    
    def subscribeEvent(self):
        try:
            
	    self.deviceVsprxoy['CentralNode'].subscribe_event('TelescopeHealthState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.deviceVsprxoy['CentralNode'].subscribe_event('Subarray2HealthState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.deviceVsprxoy['CentralNode'].subscribe_event('Subarray1HealthState', tango.EventType.CHANGE_EVENT, self.updateval)

            self.deviceVsprxoy['Subarray1'].subscribe_event('HealthState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.deviceVsprxoy['Subarray1'].subscribe_event('ObsMode', tango.EventType.CHANGE_EVENT, self.updateval)
            self.deviceVsprxoy['Subarray1'].subscribe_event('ObsState', tango.EventType.CHANGE_EVENT, self.updateval)

            self.deviceVsprxoy['Subarray2'].subscribe_event('HealthState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.deviceVsprxoy['Subarray2'].subscribe_event('ObsMode', tango.EventType.CHANGE_EVENT, self.updateval)
            self.deviceVsprxoy['Subarray2'].subscribe_event('ObsState', tango.EventType.CHANGE_EVENT, self.updateval)

            self.dishProxy['Dish1'].subscribe_event('HealthState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish1'].subscribe_event('dishMode', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish1'].subscribe_event('pointingState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish1'].subscribe_event('ConfiguredBand', tango.EventType.CHANGE_EVENT, self.updateval)

            self.dishProxy['Dish2'].subscribe_event('HealthState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish2'].subscribe_event('dishMode', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish2'].subscribe_event('pointingState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish2'].subscribe_event('ConfiguredBand', tango.EventType.CHANGE_EVENT, self.updateval)

            self.dishProxy['Dish3'].subscribe_event('HealthState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish3'].subscribe_event('dishMode', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish3'].subscribe_event('pointingState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish3'].subscribe_event('ConfiguredBand', tango.EventType.CHANGE_EVENT, self.updateval)

            self.dishProxy['Dish4'].subscribe_event('HealthState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish4'].subscribe_event('dishMode', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish4'].subscribe_event('pointingState', tango.EventType.CHANGE_EVENT, self.updateval)
            self.dishProxy['Dish4'].subscribe_event('ConfiguredBand', tango.EventType.CHANGE_EVENT, self.updateval)

	    self.deviceVsprxoy['Subarray1'].subscribe_event('receptorIDList', tango.EventType.PERIODIC_EVENT, self.subarrayDishColor)
            self.deviceVsprxoy['Subarray2'].subscribe_event('receptorIDList', tango.EventType.PERIODIC_EVENT, self.subarrayDishColor)

            self.deviceVsprxoy['CentralNode'].subscribe_event('activityMessage', tango.EventType.CHANGE_EVENT, self.activityLogs)
            self.deviceVsprxoy['Subarray1'].subscribe_event('activityMessage', tango.EventType.CHANGE_EVENT, self.activityLogs)
            self.deviceVsprxoy['Subarray2'].subscribe_event('activityMessage', tango.EventType.CHANGE_EVENT, self.activityLogs)
            self.deviceVsprxoy['LeafNode1'].subscribe_event('activityMessage', tango.EventType.CHANGE_EVENT, self.activityLogs)
            self.deviceVsprxoy['LeafNode2'].subscribe_event('activityMessage', tango.EventType.CHANGE_EVENT, self.activityLogs)
            self.deviceVsprxoy['LeafNode3'].subscribe_event('activityMessage', tango.EventType.CHANGE_EVENT, self.activityLogs)
            self.deviceVsprxoy['LeafNode4'].subscribe_event('activityMessage', tango.EventType.CHANGE_EVENT, self.activityLogs)
        except Exception as e:
            raise
            print '[Error]: ', str(e)

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow = mainWindow_SKA()
    MainWindow.show()
    sys.exit(app.exec_())
