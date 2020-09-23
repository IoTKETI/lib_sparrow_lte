#!/usr/bin/python3
import json, sys, serial, threading
import paho.mqtt.client as mqtt
from time import sleep

argv = sys.argv

# my_lib_name = 'lib_sparrow_lte'

global lib_topic
global lib_mqtt_client

global missionPort
global lteQ


def on_connect(client,userdata,flags, rc):
    if rc == 0:
        print('[msw_mqtt_connect] connect to ', broker_ip)
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
	print(str(rc))


def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)


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


def missionPortOpening(missionPort, missionPortNum, missionBaudrate, missionLTE):
    global lteQ
    global lib
    
    if (missionPort == None):
        try:
            missionPort = serial.Serial(missionPortNum, missionBaudrate, timeout = 2)
            print ('missionPort open. ' + missionPortNum + ' Data rate: ' + missionBaudrate)
            mission_thread = threading.Thread(
                target=missionPortData, args=(missionPort, missionLTE)
            )
            mission_thread.start()

            return missionPort

        except serial.SerialException as e:
            missionPortError(e)
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


def missionPortData(missionPort, missionLTE):
    global lteQ
    lteQ = dict()
    while True:
        lteReqGetRssi(missionPort)
        missionStr = missionPort.readlines()

        arrLTEQ = missionStr[1].decode("utf-8").split(", ")
        
        if (missionLTE == 'KT'):
	    lte!['type'] = missionLTE
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

        elif (missionLTE == 'SKT'):
	    lte!['type'] = missionLTE
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
                    lteQ['sinr'] = float(arrQValue_1_data[1])
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

        elif (missionLTE == 'LG'):
	    lte!['type'] = missionLTE
            for idx in range(len(arrLTEQ)):
                arrQValue = arrLTEQ[idx].split(':')
                if (arrQValue[0] == '@DBG'):
                    lteQ['frequency'] = int(arrQValue[2])
                elif (arrQValue[0] == 'Band'):
                    lteQ['band'] = int(arrQValue[1])
                elif (arrQValue[0] == 'BW'):
                    lteQ['bandwidth'] = int(arrQValue[1][:-3])
                elif (arrQValue[0] == 'Cell ID'):
                    lteQ['cell_id'] = arrQValue[1]
                elif (arrQValue[0] == 'RSRP'):
                    lteQ['rsrp'] = float(arrQValue[1][:-3])
                elif (arrQValue[0] == 'RSSI'):
                    lteQ['rssi'] = float(arrQValue[1][:-3])
                elif (arrQValue[0] == 'RSRQ'):
                    lteQ['rsrq'] = float(arrQValue[1][:-2])
                elif (arrQValue[0] == 'BLER'):
                    lteQ['bler'] = float(arrQValue[1][:-2])
                elif (arrQValue[0] == 'Tx Power'):
                    lteQ['tx_power'] = int(arrQValue[1])
                elif (arrQValue[0] == 'PLMN'):
                    lteQ['plmn'] = arrQValue[1]
                elif (arrQValue[0] == 'TAC'):
                    lteQ['tac'] = int(arrQValue[1])
                elif (arrQValue[0] == 'DRX cycle length'):
                    lteQ['drx'] = int(arrQValue[1])
                elif (arrQValue[0] == 'EMM state'):
                    lteQ['emm_state'] = arrQValue[1]
                elif (arrQValue[0] == 'RRC state'):
                    lteQ['rrc_state'] = arrQValue[1]
                elif (arrQValue[0] == 'Net OP Mode'):
                    lteQ['net_op_mode'] = arrQValue[1]
                elif (arrQValue[0] == 'EMM Cause'):
                    lteQ['emm_cause'] = int(arrQValue[1])
                elif (arrQValue[0] == 'ESM Cause'):
                    lteQ['esm_cause'] = arrQValue[1].split(",")[0]

        # print ('lteQ: \n', lteQ)

        container_name = lib["data"][0]
        data_topic = '/MUV/data/' + lib["name"] + '/' + container_name
        lteQ = json.dumps(lteQ)

        send_data_to_msw(data_topic, lteQ)

        lteQ = dict()
        # print(lteQ)


if __name__ == '__main__':
    my_lib_name = 'lib_sparrow_lte'

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
    lib['lteType'] = argv[3]

    broker_ip = 'localhost'
    port = 1883

    msw_mqtt_connect(broker_ip, port)

    missionPort = None
    missionPortNum = lib["serialPortNum"]
    missionBaudrate = lib["serialBaudrate"]
    missionLTE = lib['lteType']
    missionPortOpening(missionPort, missionPortNum, missionBaudrate, missionLTE)
