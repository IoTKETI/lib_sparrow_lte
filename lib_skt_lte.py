#!/usr/bin/python3
import json, sys, serial, threading
import paho.mqtt.client as mqtt
import os, signal

i_pid = os.getpid()
argv = sys.argv

lteQ = {}

def lteQ_init():
    global lteQ
    
    lteQ['band'] = 0
    lteQ['bandwidth'] = 0
    lteQ['plmn'] = 0
    lteQ['tac'] = 0
    lteQ['cell_id'] = ""
    lteQ['esm_cause'] = 0
    lteQ['drx'] = 0
    lteQ['rsrp'] = 0.0
    lteQ['rsrq'] = 0.0
    lteQ['rssi'] = 0.0
    lteQ['l2w'] = ""
    lteQ['ri'] = 0
    lteQ['cqi'] = 0
    lteQ['status'] = ""
    lteQ['sub_status'] = ""
    lteQ['rrc'] = ""
    lteQ['svc'] = ""
    lteQ['sinr'] = 0.0
    lteQ['tx_pwr'] = 0
    lteQ['tmsi'] = ""
    lteQ['ip'] = ""
    lteQ['avg_rsrp'] = 0.0
    lteQ['antbar'] = 0
    lteQ['imsi'] = 0
    lteQ['missdn'] = 0
    
#---MQTT----------------------------------------------------------------
def on_connect(client,userdata,flags, rc):
    if rc == 0:
        print('[msw_mqtt_connect] connect to ', broker_ip)
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
	print(str(rc))

	
def on_message(client, userdata, msg):
    print(str(msg.payload.decode("utf-8")))


def msw_mqtt_connect(broker_ip, port):
    global lib_mqtt_client

    lib_mqtt_client = mqtt.Client()
    lib_mqtt_client.on_connect = on_connect
    lib_mqtt_client.on_disconnect = on_disconnect
    lib_mqtt_client.on_message = on_message
    lib_mqtt_client.connect(broker_ip, port)

    lib_mqtt_client.loop_start()
#-----------------------------------------------------------------------

def missionPortOpening(missionPortNum, missionBaudrate):
    global missionPort
    global lteQ
    global lib
    
    if (missionPort == None):
        try:
            missionPort = serial.Serial(missionPortNum, missionBaudrate, timeout = 2)
            print ('missionPort open. ' + missionPortNum + ' Data rate: ' + missionBaudrate)

        except TypeError as e:
            missionPortClose()
    else:
        if (missionPort.is_open == False):
            missionPortOpen()

            data_topic = '/MUV/data/' + lib["name"] + '/' + lib["data"][0]
            send_data_to_msw(data_topic, lteQ)

def missionPortOpen():
    global missionPort
    print('missionPort open!')
    missionPort.open()

def missionPortClose():
    global missionPort
    print('missionPort closed!')
    missionPort.close()


def missionPortError(err):
    print('[missionPort error]: ', err)
    os.kill(i_pid, signal.SIGKILL)

def lteReqGetRssi():
    global missionPort
    
    if missionPort is not None:
        if missionPort.is_open:
            atcmd = b'AT@DBG\r'
            missionPort.write(atcmd)

def send_data_to_msw (data_topic, obj_data):
    global lib_mqtt_client

    lib_mqtt_client.publish(data_topic, obj_data)


def missionPortData():
    global missionPort
    global lteQ

    try:
        lteReqGetRssi()
        missionStr = missionPort.readlines()

        arrLTEQ = missionStr[1].decode("utf-8").split(", ")
        # print(arrLTEQ)
        arrQValue_0 = arrLTEQ[0].split(':')
        if (arrQValue_0[0] == '@DBG'):
                lteQ['earfcn_dl'] = arrQValue_0[2].split(',')[0].split('/')[0]
                lteQ['earfcn_ul'] = arrQValue_0[2].split(',')[0].split('/')[1]
                lteQ['rf_state'] = arrQValue_0[3]
        arrQValue_1 = arrLTEQ[1].split(',')
        for idx in range(len(arrQValue_1)):
            arrQValue_1_data = arrQValue_1[idx].split(':')
            if (arrQValue_1_data[0] == 'BAND'):
                lteQ['band'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'BW'):
                lteQ['bandwidth'] = int(arrQValue_1_data[1][:-3])
            elif (arrQValue_1_data[0] == 'PLMN'):
                lteQ['plmn'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'TAC'):
                lteQ['tac'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'Cell(PCI)'):
                lteQ['cell_id'] = arrQValue_1_data[1]
            elif (arrQValue_1_data[0] == 'ESM CAUSE'):
                lteQ['esm_cause'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'DRX'):
                lteQ['drx'] = int(arrQValue_1_data[1][:-2])
            elif (arrQValue_1_data[0] == 'RSRP'):
                lteQ['rsrp'] = float(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'RSRQ'):
                lteQ['rsrq'] = float(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'RSSI'):
                lteQ['rssi'] = float(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'L2W'):
                lteQ['l2w'] = arrQValue_1_data[1]
            elif (arrQValue_1_data[0] == 'RI'):
                lteQ['ri'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'CQI'):
                lteQ['cqi'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'STATUS'):
                lteQ['status'] = arrQValue_1_data[1]
            elif (arrQValue_1_data[0] == 'SUB STATUS'):
                lteQ['sub_status'] = arrQValue_1_data[1]
            elif (arrQValue_1_data[0] == 'RRC'):
                lteQ['rrc'] = arrQValue_1_data[1]
            elif (arrQValue_1_data[0] == 'SVC'):
                lteQ['svc'] = arrQValue_1_data[1]
            elif (arrQValue_1_data[0] == 'SINR'):
                try:
                    lteQ['sinr'] = float(arrQValue_1_data[1])
                except ValueError:
                    lteQ['sinr'] = 0.0
            elif (arrQValue_1_data[0] == 'Tx Pwr'):
                lteQ['tx_pwr'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'TMSI'):
                lteQ['tmsi'] = arrQValue_1_data[1]
            elif (arrQValue_1_data[0] == 'IP'):
                lteQ['ip'] = arrQValue_1_data[1]
            elif (arrQValue_1_data[0] == 'AVG RSRP'):
                lteQ['avg_rsrp'] = float(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'ANTBAR'):
                lteQ['antbar'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'IMSI'):
                lteQ['imsi'] = int(arrQValue_1_data[1])
            elif (arrQValue_1_data[0] == 'MSISDN'):
                lteQ['missdn'] = int(arrQValue_1_data[1])

        data_topic = '/MUV/data/' + lib["name"] + '/' + lib["data"][0]
        lteQ = json.dumps(lteQ)

        send_data_to_msw(data_topic, lteQ)

        lteQ = json.loads(lteQ)

    except (TypeError, ValueError):
        lteQ_init()

    except serial.SerialException as e:
        missionPortError(e)


if __name__ == '__main__':
    global missionPort

    my_lib_name = 'lib_skt_lte'

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
    missionPortOpening(missionPortNum, missionBaudrate)

    while True:
        missionPortData()

# python -m PyInstaller lib_skt_lte.py