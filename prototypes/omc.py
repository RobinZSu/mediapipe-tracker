# toy tracker with VSeeFace head tracking data over OMC/VMC

from pythonosc import dispatcher
from pythonosc import osc_server
from scipy.spatial.transform import Rotation
from utils.filters import EMAFilter

# socket
import socket, struct

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
buf = bytearray(8 * 6) # UDP data buffer

f = EMAFilter()

def default_handler(address, *args):
    pass

def osc_handler(address, *args):
    if (len(args) < 1):
        return
    if (args[0] != 'Head'):
        return
    
    x, y, z = args[1:4]
    quat = args[4:]
    euler = Rotation.from_quat(quat).as_euler('yxz', degrees=True)

    rp, rr, ry = round(euler[0], 3), round(euler[1],3), round(euler[2],3)

    # Format the data 
    x *= 80 
    y *= 80
    z *= 80
    data = [x, y, z, rp, rr, ry] 
    # print(print(len(args), rp))

    # Send the data over UDP
    struct.pack_into('dddddd', buf, 0, *data)
    sock.sendto(buf, ('127.0.0.1', 4242))

def main():
    # Define the IP address and port for OSC server
    ip = "127.0.0.1"  # Localhost (or change to your specific IP)
    port = 39539      # Replace with your desired port number

    # Create dispatcher to handle incoming OSC messages
    disp = dispatcher.Dispatcher()
    disp.map("/VMC/Ext/Tra/Pos", osc_handler) # Map the OSC address "/head/6dof" to handler
    disp.set_default_handler(default_handler)
    
    # Create OSC server
    server = osc_server.BlockingOSCUDPServer((ip, port), disp)
    print(f"Listening for OSC messages on {ip}:{port}...")
    try:
        # Start the server
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()

if __name__ == "__main__":
    main()