# -*- coding: utf-8 -*-
# This is a sample Python script for MQTT with TX62-W(B).
# scripted by jefflee@ocube.co.kr

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from serial.tools.list_ports import comports
import serial.tools.list_ports

import serial
import time
import sys
import getpass
import os.path
import os
ComPort = "";
port = "COM27" # 시리얼 포트 넘버설정 

baud = 115200 # 시리얼 포트 속도 설정 

nodes = comports()
count = 0;



for node in nodes:

    if "Cinterion" in node.description:
        if "Com Port" in node.description:
            ComPort = node.device
            

    count += 1        
    #print("[{0}]".format(count))
    #print("         device: ", node.device)
    #print("    description: ", node.description)
    #print("   manufacturer: ", node.manufacturer)
    #print("           hwid: ", node.hwid)
    #print("      interface: ", node.interface)
    #print("       location: ", node.location)
    #print("           name: ", node.name)

if count > 0 and ComPort != "" :
    print(" Cinterion Modem found in "+ComPort)
    port = ComPort
    
else:    
    print("No Port was founded ,named Cinterion ")
    exit()

    


seri_port = ComPort # serial port redefine
SVR_ADDR="mqtt://mqtt.eclipseprojects.io" #137.135.83.217" #
SVR_PORT = "1883" 


serialPort = serial.Serial(seri_port, baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)


def dp_result():
    time.sleep(0.3)
    retStr = serialPort.read(serialPort.inWaiting()).decode('utf-8')
    print(retStr)
    return retStr


def send_modem(str):
    serialPort.write(str.encode()+"\r\n".encode())


def save_service(svc_num):
    send_msg = 'AT^SIPS=service,save,' + str(svc_num)
    send_modem(send_msg)
    dp_result()


def load_service(svc_num):
    send_msg = 'AT^SIPS=service,load,' + str(svc_num)
    send_modem(send_msg)
    return dp_result()

def set_ipsystem():
    send_modem('AT+CGDCONT=1,"IP",""')

def init_modem():
    print('>--- Initialize Modem : start --- ')
    
    if False:
        print(" - Time sync -")
        send_modem('AT+CTZU=1')
        dp_result()
        
    print(' - SIM card check -')
    send_modem('AT+CPIN?')
    dp_result()
    

    print(" - Internet Service Activation -")
    send_modem('AT^SICA=1,1')
    dp_result()
    time.sleep(2)
    
    print(" - IP address -")
    send_modem('AT+CGPADDR')
    
    if dp_result().find('0.0.0.0') == 0 :
        # error case
        print (" IP v4 address is not set by ISP")
        
        if False :
            set_ipsystem()
        
            time.sleep(5)
            print("  - Registering LTE(M2M) Networks - ")
            send_modem('AT+CGATT=1')
            dp_result()
    else :
        print ("  - IP v4 address is Valid - ")
        
    print('>--- Initialize Modem : done --- ')

def get_i_svc_status(svc_num):
    send_modem('AT^SISI=' + str(svc_num))
    retStr = dp_result()
    retNum = retStr.find(',') + 1
    return retStr[retNum]


def set_tcp_sock():
    print('>---  MQTT Service Setting : start --- ')
    send_modem('AT^SISC=1')
    send_modem('AT+CGDCONT=1,IP,""')
    dp_result()
    send_modem('AT^SICS=1,dns1,164.124.101.2')
    dp_result()
    send_modem('AT^SICS=1,dns2,203.248.252.2')
    dp_result()
    
    send_modem('AT^SICA=1,1')
    dp_result()
    
    #send_modem(AT+CGPADDR=1) # another telit case (LE910 series)
    send_modem('AT+CGPADDR')
    dp_result()

    send_modem('AT^SISS=1,srvType,Mqtt')
    dp_result()
    print('AT^SISS=1,srvType,Mqtt')
    time.sleep(1)
    
    send_modem('AT^SISS=1,conId,1')
    dp_result()
    print('AT^SISS=1,conId,1')
    time.sleep(1)
    
    send_modem('at^siss=1,address,'+SVR_ADDR+':'+SVR_PORT)
    dp_result()
    time.sleep(1)

    send_modem('at^siss=1,clientId,4100214231500720313137')
    dp_result()
    print('at^siss=1,clientId,4100214231500720313137')
    time.sleep(1)
    
    send_modem('at^siss=1,retain,1') # cleanSession for init process
    dp_result()
    print('at^siss=1,cleanSession,1')
    time.sleep(1)
    
    send_modem('at^siss=1,ipVer,4')
    dp_result()
    print('at^siss=1,ipVer,4')
    time.sleep(1)

    send_modem('at^siss=1,cmd,unsubscribe')
    dp_result()
    print('at^siss=1,cmd,unsubscribe')
    time.sleep(1)
    
    send_modem('at^siss=1,TopicFilter,reqserver4100214231500720313137cmdjson')
    dp_result()
    
    print('at^siss=1,TopicFilter,reqserver4100214231500720313137cmdjson')
    time.sleep(1)
    
    send_modem('at^sica=1,1')
    dp_result()
    print('at^sica=1,1')

    time.sleep(3)
    print('at^siso=1,2')

    send_modem('at^siso=1,2')
    time.sleep(3)
    dp_result()
    
    time.sleep(3)
    
    print('>--- TCP Socket Initialize : done --- ')

def reconnect_socket():
    print(" --- Connect to tcp Server --- ")
    send_modem('AT^SISC=1')  # close previous service
    dp_result()
    send_modem('AT^SISO=1')  # open service
    dp_result()
    time.sleep(3)


def publish():
    print('-- publish -- ')
    send_modem('AT^SISU=1,"publish","0:MQTTDemo:1:100:36"')
    dp_result()

    send_modem('at^sisw=1,36')
    
    dp_result()
    send_modem('')
    send_modem('testSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS') 
                #testSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
    send_modem('')
    
    #time.sleep(1)
    dp_result()

def subsribe():
    print('-- subscribe --')
    send_modem('AT^SISU=1,"subscribe","MQTTDemo"')
    time.sleep(5.5)
    dp_result()
    
def read_return():
    send_modem('AT^SISR=1,150')
    dp_result()
    send_modem('AT^SISR=1,150')
    dp_result()
    
    

###############
#    main    #
##############

print(" v 1.0 test mqtt ")
init_modem()
send_modem('AT')
dp_result()
#svc_num = 0

print('-- set tcp socket : start --')
set_tcp_sock()

print('-- set tcp socket : done --')
# save_service(svc_num)
# print('save service')
# reconnect_socket()
time.sleep(5)
send_modem('AT^SISD=1,"cleanParam"')
time.sleep(2)

subsribe()
publish()


### main loop for test mqtt send/recv
while 1:
       
    read_return()

    time.sleep(3.5)

    publish()

