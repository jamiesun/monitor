# -*- coding: utf-8 -*-
execfile("./config")
import sys,os,re
import paramiko
import binascii
import copy
from PyQt4 import QtCore, QtGui,uic
from PyQt4.QtCore import QSettings,QVariant
from Crypto.Cipher import AES

config = all_config

_key = '___a_b_c_d_e_f__'


bad_cmd = re.compile(r'(rm||mv||init||shutdown||halt||password)').match

settings = QSettings("HKEY_CURRENT_USER\Software\lymonitor",QSettings.NativeFormat);  

clients = {}

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType('monitor.ui')

def _decode_str(data):
    try:
        return data.decode("gbk")
    except:
        return data.decode('utf-8')

def _encrypt(x):
    if not x:return ''
    x = str(x)
    result =  AES.new(_key, AES.MODE_CBC).encrypt(x.ljust(len(x)+(16-len(x)%16)))
    return binascii.hexlify(result)

def _decrypt(x):
    if not x or len(x)%16 > 0 :return ''
    x = binascii.unhexlify(str(x))
    return AES.new(_key, AES.MODE_CBC).decrypt(x).strip()

class CheckServThread(QtCore.QThread):

    onConnect = QtCore.pyqtSignal(int,bool)

    def __init__(self, row,hostdata,parent=None):
        super(CheckServThread, self).__init__(parent)
        self.row = row
        self.hostdata = hostdata
        self.mutex = QtCore.QMutex()
        self.done = False
        self.start()

    def run(self):
        host = self.hostdata['addr']
        port = int(self.hostdata['port'])
        keyfile = self.hostdata['keyfile']
        passwd = self.hostdata['passwd']
        timeout = self.hostdata['timeout']
        try:
            sshc = paramiko.SSHClient()
            sshc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if keyfile and os.path.exists(keyfile):
                sshc.connect(host,port,"root",key_filename=keyfile,timeout=timeout)
            else:
                sshc.connect(host,port,"root",passwd,timeout=timeout)
            self.onConnect.emit(self.row,True)
            sshc.close()
        except:
            self.onConnect.emit(self.row,False)
        self.mutex.lock()
        self.done = True
        self.mutex.unlock()



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
        for addr in sorted(config['hosts'].keys()):
            host = config['hosts'][addr]
            item = QtGui.QListWidgetItem("%s-%s.."%(addr,host['desc'][:9])) 
            item.setToolTip(host['desc'])
            host['addr'] = addr
            item.hostdata = host
            self.host_list.addItem(item)

        for desc in  sorted(config['commands'].keys()):
            self.command_select.addItem(desc,QVariant(config['commands'][desc]))

        self.host_list.setCurrentRow(0) 
        self.set_host()

    def set_host(self):
        citem = self.host_list.currentItem()
        hostdata = citem.hostdata
        self.host_text.setText(hostdata['addr'])
        self.port_text.setText(str(hostdata['port']))
        passwd = settings.value("%s_pw"%hostdata['addr'],'')
        self.passwd_text.setText(_decrypt(passwd.toString()))
        self.hostdesc_view.setText(hostdata['desc'])
        self.current_host = hostdata

    @QtCore.pyqtSlot(int,bool)
    def on_chksrv_done(self,row,isSucc):
        try:
            item = self.host_list.item(row)
            color =  isSucc and QtCore.Qt.darkGreen or QtCore.Qt.red
            item.setForeground(QtGui.QBrush(color))
        except:pass

    @QtCore.pyqtSlot()
    def on_reloadall_clicked(self):
        self.reloadall.setEnabled(False) 
        __threads = []
        for row in range(self.host_list.count ()):
            item = self.host_list.item(row)
            item.setForeground(QtGui.QBrush(QtCore.Qt.gray))
            hostdata = copy.deepcopy(item.hostdata)
            hostdata['passwd'] = self.passwd_text.text()
            hostdata['timeout'] = self.timeout_val.value()

            thread = CheckServThread(row,hostdata)
            thread.onConnect.connect(self.on_chksrv_done)
            __threads.append(thread)

        while [td for td in __threads if not td.done]:
            app.processEvents()
        self.reloadall.setEnabled(True) 
        
        

    @QtCore.pyqtSlot()
    def on_passwd_text_editingFinished(self):
        pwd = self.passwd_text.text()
        if not pwd:
            return
        host = self.current_host['addr']
        settings.setValue("%s_pw"%host,QVariant(_encrypt(pwd)))
        settings.sync()

    @QtCore.pyqtSlot()
    def on_host_list_itemSelectionChanged(self):
        self.set_host()

    @QtCore.pyqtSlot()
    def on_command_cmd_clicked(self):
        cmdata = self.command_select.itemData(self.command_select.currentIndex())
        cmd = cmdata.toString()
        if not self._filter_cmd(cmd):
            return
        host,port = self.current_host['addr'],int(self.current_host['port'])
        keyfile = self.current_host['keyfile']
        passwd = self.passwd_text.text()
        timeout = self.timeout_val.value()
        sshc = clients.get(host)    
        if not sshc:  
            try:
                self.statusbar.showMessage(u"正在连接主机.....",timeout*1000)
                sshc = paramiko.SSHClient()
                sshc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                if keyfile and os.path.exists(keyfile):
                    sshc.connect(host,port,"root",key_filename=keyfile,timeout=timeout)
                else:
                    sshc.connect(host,port,"root",passwd,timeout=timeout)
                clients[host] = sshc
            except Exception as e:
                self.statusbar.showMessage(u"连接主机失败：%s"%str(e),20000)
                return
        self.statusbar.showMessage(u"正在执行命令: %s"%cmd,9000)
        try:
            stdin, stdout, stderr = sshc.exec_command(cmd)
            self.result_view.clear()
            for line in  stdout.readlines():
                self.result_view.append(_decode_str(line))
        except Exception as e:
            self.statusbar.showMessage(u"命令执行失败：%s"%str(e),20000)
            return
        self.statusbar.clearMessage()

    def _filter_cmd(self,cmd):
        _b = bad_cmd(cmd).group(1)
        if _b:
            ret = QtGui.QMessageBox.warning(self, u'警告',
                        u'命令[%s]包含危险字符(%s),是否继续执行'%(cmd,_b),
                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            return ret == QtGui.QMessageBox.Ok 
        return False

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
    