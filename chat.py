import serial
from time import sleep
import binascii

ser = serial.Serial('/dev/ttyS0', 57600)  # open serial port
print(ser.name)         # check which port was really used

global message

def resetRadio():
    komennot = [
        'mac reset 868',
        'sys get ver',
        'sys get hweui',
        'mac pause',
        'radio set pwr 14'
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
            
def sendRadio():
    resetRadio()
    global message
    message = 'lol'
    start = '1234'
    end = 'end'
    msg = start.encode("utf-8").hex()+';'.encode("utf-8").hex()+message.encode("utf-8").hex()+';'.encode("utf-8").hex()+end.encode("utf-8").hex()  
    print(msg)
    send = 'radio tx '
    ser.write(send.encode('utf_8')+msg.encode('utf_8')+'\r\n'.encode('utf_8'))     # write a string
    sleep(.2)
    response = ser.readline().decode()
    print(response)
    sleep(2)

def receiveRadio():
    resetRadio()
    i=1
    global temp, humi, date
    while i==1:
        #print('start')
        sleep(.2)
        ser.write('radio rx 0'.encode())
        ser.write(b'\r\n')
        #if ser.readable():                
        response = ser.readline().decode()
        if response.startswith('radio_rx'):
            print(response)
            msg2 = response[10:][:-2]
            print(msg2)
            msg = binascii.unhexlify(msg2.encode()).decode()
            if (((msg.startswith('1234'))) and msg.endswith('end')):
                start, message, end = msg.split(';')               
                print(message)
            
            elif (((msg.startswith('1234'))) and not msg.endswith('end')):
                print('send again')
            else:
                print('not for us')
    else:
        print('loppu')
    
while True:
    sendRadio()
    sleep(1)
#receiveRadio()
