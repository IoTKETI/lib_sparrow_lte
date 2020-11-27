#!/usr/bin/python3
import json, sys, serial, threading
import paho.mqtt.client as mqtt
from time import sleep

argv = sys.argv

global lib_topic
global lib_mqtt_client

global missionPort
global lteQ

def lteQ_init():
    global lteQ

    lteQ = dict()
    lteQ['plmn'] = ""
    lteQ['band'] = 0
    lteQ['earfcn'] = 0
    lteQ['bandwidth'] = 0
    lteQ['pci'] = 0
    lteQ['cell_id'] = ""
    lteQ['guti'] = ""
    lteQ['tac'] = 0
    lteQ['rsrp'] = 0.0
    lteQ['rsrq'] = 0.0
    lteQ['rssi'] = 0.0
    lteQ['sinr'] = 0.0


def on_connect(client,userdata,flags, rc):
    if rc == 0:
        print('[msw_mqtt_connect] connect to ', broker_ip)
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
	print(str(rc))


def on_publish(client, userdata, mid):
    i = 1
    # print("In on_pub callback mid= ", mid)


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print(str(msg.payload.decode("utf-8")))


def msw_mqtt_connect(broker_ip, port):
    global lib_topic
    global lib_mqtt_client

    lib_topic = ''

    lib_mqtt_client = mqtt.Client()
    lib_mqtt_client.on_connect = on_connect
    lib_mqtt_client.on_disconnect = on_disconnect
    lib_mqtt_client.on_publish = on_publish
    lib_mqtt_client.on_message = on_message
    lib_mqtt_client.connect(broker_ip, port)
    # lib_mqtt_client.subscribe(lib_topic, 0)
    lib_mqtt_client.loop_start()
    return lib_mqtt_client


def missionPortOpening(missionPort, missionPortNum, missionBaudrate):
    global lteQ
    global lib

    if (missionPort == None):
        try:
            missionPort = serial.Serial(missionPortNum, missionBaudrate, timeout = 2)
            print ('missionPort open. ' + missionPortNum + ' Data rate: ' + missionBaudrate)
            mission_thread = threading.Thread(
                target=missionPortData, args=(missionPort,)
            )
            mission_thread.start()

            return missionPort

        except TypeError as e:
            missionPortClose()
    else:
        if (missionPort.is_open == False):
            missionPortOpen()

            # lteQ.rssi = -Math.random()*100;
            container_name = lib["name"]
            data_topic = '/MUV/data/' + lib["name"] + '/' + container_name
            send_data_to_msw(data_topic, lteQ)

def missionPortOpen():
    print('missionPort open!')
    missionPort.open()

def missionPortClose():
    global missionPort
    print('missionPort closed!')
    missionPort.close()


def missionPortError(err):
    print('[missionPort error]: ', err)


def lteReqGetRssi(missionPort):
    if missionPort is not None:
        if missionPort.is_open:
            atcmd = b'AT@DBG\r'
            missionPort.write(atcmd)

def send_data_to_msw (data_topic, obj_data):
    lib_mqtt_client.publish(data_topic, obj_data)


def missionPortData(missionPort):
    global lteQ

    lteQ = lteQ_init()

    while True:
        try:
            lteReqGetRssi(missionPort)
            missionStr = missionPort.readlines()

            arrLTEQ = missionStr[1].decode("utf-8").split(", ")

            for idx in range(len(arrLTEQ)):
                arrQValue = arrLTEQ[idx].split(':')
                if (arrQValue[0] == '@DBG'):
                    lteQ['plmn'] = arrQValue[2]
                elif (arrQValue[0] == 'Band'):
                    lteQ['band'] = int(arrQValue[1])
                elif (arrQValue[0] == 'EARFCN'):
                    lteQ['earfcn'] = int(arrQValue[1])
                elif (arrQValue[0] == 'Bandwidth'):
                    lteQ['bandwidth'] = int(arrQValue[1][:-3])
                elif (arrQValue[0] == 'PCI'):
                    lteQ['pci'] = int(arrQValue[1])
                elif (arrQValue[0] == 'Cell-ID'):
                    lteQ['cell_id'] = arrQValue[1]
                elif (arrQValue[0] == 'GUTI'):
                    lteQ['guti'] = arrQValue[1]
                elif (arrQValue[0] == 'TAC'):
                    lteQ['tac'] = int(arrQValue[1])
                elif (arrQValue[0] == 'RSRP'):
                    lteQ['rsrp'] = float(arrQValue[1][:-3])
                elif (arrQValue[0] == 'RSRQ'):
                    lteQ['rsrq'] = float(arrQValue[1][:-3])
                elif (arrQValue[0] == 'RSSI'):
                    lteQ['rssi'] = float(arrQValue[1][:-3])
                elif (arrQValue[0] == 'SINR'):
                    lteQ['sinr'] = float(arrQValue[1][:-2])

            # print ('lteQ: \n', lteQ)

            data_topic = '/MUV/data/' + lib["name"] + '/' + lib["data"][0]
            lteQ = json.dumps(lteQ)

            send_data_to_msw(data_topic, lteQ)

            lteQ = json.loads(lteQ)

        except (TypeError, ValueError):
            lteQ_init()
        except serial.SerialException as e:
            missionPortError(e)

if __name__ == '__main__':
    my_lib_name = 'lib_kt_lte'

    try:
        lib = dict()
        with open(my_lib_name + '.json', 'r') as f:
            lib = json.load(f)
            lib = json.loads(lib)

    except:
        lib = dict()
        lib["name"] = my_lib_name
        lib["target"] = 'armv6'
        lib["description"] = "[name] [portnum] [baudrate]"
        lib["scripts"] = './' + my_lib_name + ' /dev/ttyUSB1 115200'
        lib["data"] = ['LTE']
        lib["control"] = []
        lib = json.dumps(lib, indent=4)
        lib = json.loads(lib)

        with open('./' + my_lib_name + '.json', 'w', encoding='utf-8') as json_file:
            json.dump(lib, json_file, indent=4)


    lib['serialPortNum'] = argv[1]
    lib['serialBaudrate'] = argv[2]

    broker_ip = 'localhost'
    port = 1883

    msw_mqtt_connect(broker_ip, port)

    missionPort = None
    missionPortNum = lib["serialPortNum"]
    missionBaudrate = lib["serialBaudrate"]
    missionPortOpening(missionPort, missionPortNum, missionBaudrate)

# python -m PyInstaller lib_kt_lte.py 
