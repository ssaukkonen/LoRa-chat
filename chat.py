import serial
from time import sleep
import binascii
from cryptography.fernet import Fernet
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)
from main_window_ui import Ui_MainWindow
from PyQt5.QtCore import *
ser = serial.Serial('/dev/ttyS0', 57600)  # open serial port
print(ser.name)         # check which port was really used
message = '' 

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.statusBar().showMessage('Ready to send message')
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.startWorker()

    def startWorker(self):
        worker = Worker()
        #worker.signals.current.connect(self.updateCurrent)
        worker.signals.messageToGUI.connect(self.writeToBrowser)
        self.threadpool.start(worker)        

    def connectSignalsSlots(self):
        #self.action_Exit.triggered.connect(self.close)
        self.sendButton.clicked.connect(self.receiveSendButton)
        
    @pyqtSlot(str)
    def writeToBrowser(self, message):
        self.textBrowser.append(message)

    @pyqtSlot()
    def receiveSendButton(self):
        self.statusBar().showMessage('clicked')    
            
class WorkerSignals(QObject):
    messageToGUI = pyqtSignal(str)

class Worker(QRunnable):
    '''
    Worker thread
    '''
    def __init__(self):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()

    def run(self):
        print("Thread start")
        objectCrypto = self.crypto()
        objectRadio = self.radio()
        objectRadio.receiveRadio()

    class crypto:
        def load_key(self):
            return open("secret.key", "rb").read()

        def encryption(self, message):
            key = self.load_key()
            message = message.encode()
            f = Fernet(key)
            return f.encrypt(message)
        
        def decryption(self, message):
            key = self.load_key()
            f = Fernet(key)
            try:
                decryptedMessage = f.decrypt(message)
                return decryptedMessage.decode('utf-8')
            except:
                print('error')

    class radio:
        def resetRadio(self):
            komennot = [
                'mac reset 868',
                'sys get ver',
                'sys get hweui',
                'mac pause',
                'radio set sf sf7',
                'radio set bw 250',
                'radio set pwr 5'
            ]

            for m in komennot:
                    ser.write(m.encode())
                    ser.write(b'\r\n')
                    r = ser.readline().decode()
                    if len(r):
                        print('{r}'.format(r=r[:-2]))
                    else:
                        print('\t<< no response')
            sleep(.2)           
                    
        def sendRadio(self):
            self.resetRadio()
            message
            #message = 'lol'
            start = '1234'
            end = 'end'
            
            object1 = crypto()
            encryptedMessage = object1.encryption(message)
            print(len(encryptedMessage))
            
            msg = start.encode("utf-8").hex()+';'.encode("utf-8").hex()+encryptedMessage.hex()+';'.encode("utf-8").hex()+end.encode("utf-8").hex()  
            print(msg)
            send = 'radio tx '
            ser.write(send.encode('utf_8')+msg.encode('utf_8')+'\r\n'.encode('utf_8'))     # write a string
            sleep(.2)
            response = ser.readline().decode()
            print(response)
            sleep(2)
            self.resetRadio()

        def sendReceived(self):
            sleep(2)
            self.resetRadio()
            msg = '4321'.encode("utf-8").hex()
            print(msg)
            send = 'radio tx '
            ser.write(send.encode('utf_8')+msg.encode('utf_8')+'\r\n'.encode('utf_8'))     # write a string
            sleep(.2)
            response = ser.readline().decode()
            print(response)
            sleep(2)
            self.resetRadio()
            
        def receiveRadio(self):
            self.resetRadio()
            while True:
                #print('start')
                sleep(.2)
                ser.write('radio rx 0'.encode())
                ser.write(b'\r\n')
                #if ser.readable():                
                response = ser.readline().decode()
                #print(response)
                if response.startswith('radio_rx'):
                    print(response)
                    msg2 = response[10:][:-2]
                    print(msg2)
                    if msg2.startswith('34333231'):
                        print('message received')
                    elif msg2.startswith('39393939'):
                        print('send message again')
                        self.sendRadio()
                    elif len(msg2) % 2 == 1 or msg2.endswith(('o', 'k')):
                        print('send again')
                    else:
                        if msg2.startswith('313233343') and msg2.endswith('656E64'):
                            msg = binascii.unhexlify(msg2.encode()).decode()
                            start, message, end = msg.split(';')                                       
                            print(len(message),message)
                            message = bytes(message, encoding= 'utf-8')
                            object2 = Worker
                            decryptedMessage = object2.crypto().decryption(message)
                            print(decryptedMessage)
                            object2.signals.messageToGUI.emit(decryptedMessage)
                            self.sendReceived()
                        elif (((msg2.startswith('313233343'))) and not msg2.endswith('656E64')):
                            print('send again')
                        else:
                            print('not for us')
            else:
                print('loppu')     

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

#while True:
#   message = 'lol'    
#   radio().sendRadio()
#   sleep(1)
#radio().receiveRadio()
