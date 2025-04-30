import paho.mqtt.client as mqtt
import serial
import time

# port configuration
SERIAL_PORT = 'COM3'  #set the appropriate serial port that arduino runs on
BAUD_RATE = 9600
serial = serial.Serial(SERIAL_PORT,BAUD_RATE)

# Configure mqtt to get more details for further usage
BROKER ='158.173.101.159'
PORT = 1883
COMMAND_FILE = 'relay.txt'
TOPIC = 'relay/scheduler'

# define the function to connect to mqtt
def conn_mqtt(client,userdata,flags,rc,properties= None):
    if rc == 0:
        print("mqtt broker connection successful")
        client.subscribe(TOPIC)
    else:
        print("Connection to broker failed")

def on_message(client, userdata, msg):
    command = msg.payload.decode().strip()
    print(f"Received MQTT message: {command} at {time.strftime('%H:%M')}")
    with open(COMMAND_FILE, 'w') as f:
        f.write(command)
    if command == '1':
        serial.write(b"ON\n")
        print(f"Sent to Arduino: ON at {time.strftime('%H:%M')}")
    elif command == '0':
        serial.write(b"OFF\n")
        print(f"Sent to Arduino: OFF at {time.strftime('%H:%M')}")
    else:
        print(f"command not known: {command}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = conn_mqtt
client.on_message = on_message

client.connect(BROKER, PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Mqtt connection services is stopping...")
    client.loop_stop()
    client.disconnect()
    serial.close()