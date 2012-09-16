# -*- coding: utf-8 -*-
execfile("./config")
import sys
import paramiko
from PyQt4 import QtCore, QtGui,uic
from PyQt4.QtCore import QSettings,QVariant

config = all_config

settings = QSettings("HKEY_CURRENT_USER//Software//lymonitor",QSettings.NativeFormat);  

clients = {}

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType('monitor.ui')

def _decode_str(data):
    try:
        return data.decode("gbk")
    except:
        return data.decode('utf-8')


class MainWin(QtGui.QMainWindow,form_class):
    def __init__(self, *args):
        super(MainWin, self).__init__(*args)
        self.setupUi(self)
        self.init_ui()
        self.init_data()

    def init_ui(self):
        self.port_text.setValidator(QtGui.QIntValidator(1,65535))

    def init_data(self):
        self.host_list.clear()
        for host in config['hosts']:
            item = QtGui.QListWidgetItem(host[0]) 
            item.hostdata = host
            self.host_list.addItem(item)

        for desc,cmd in  config['commands'].items():
            self.command_select.addItem(desc,QVariant(cmd))

        self.host_list.setCurrentRow(0) 
        self.set_host()

    def set_host(self):

        citem = self.host_list.currentItem()
        hostdata = citem.hostdata
        self.host_text.setText(hostdata[0])
        self.port_text.setText(str(hostdata[1]))
        passwd = settings.value("%s_pw"%hostdata[0],'lingya')
        self.passwd_text.setText(passwd.toString())
        self.hostdesc_view.setText(hostdata[2])
        self.current_host = hostdata


    @QtCore.pyqtSlot()
    def on_reloadall_clicked(self):
        citem = self.host_list.currentItem()
        QtGui.QMessageBox.about(self,'info',citem.text())  

    @QtCore.pyqtSlot()
    def on_host_list_itemSelectionChanged(self):
        self.set_host()

    @QtCore.pyqtSlot()
    def on_command_cmd_clicked(self):
        cmdata = self.command_select.itemData(self.command_select.currentIndex())
        cmd = cmdata.toString()
        host,port = self.current_host[0],int(self.current_host[1])
        passwd = settings.value("%s_pw"%host,'lingya').toString()
        timeout = self.timeout_val.value()
        sshc = clients.get(host)    
        if not sshc:  
            try:
                self.statusbar.showMessage(u"正在连接主机.....",timeout*1000)
                sshc = paramiko.SSHClient()
                sshc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print host,port,passwd
                sshc.connect(host,port,"root",passwd,timeout=timeout)
                clients[host] = sshc
            except Exception as e:
                self.statusbar.showMessage(u"连接主机失败.....",5000)
                self.result_view.append(str(e))
                return
        self.statusbar.showMessage(u"正在执行命令: %s"%cmd,9000)
        stdin, stdout, stderr = sshc.exec_command(cmd)
        self.result_view.clear()
        for line in  stdout.readlines():
            self.result_view.append(_decode_str(line))
        self.statusbar.clearMessage()



    def closeEvent(self, event):
        if True:
            settings.sync()
            event.accept()
        else:
            event.ignore()        
            

if __name__ == "__main__":
    form = MainWin()
    form.show()
    sys.exit(app.exec_())