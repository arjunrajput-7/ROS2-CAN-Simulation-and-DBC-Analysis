# ROS 2 CAN Simulation & DBC Analysis
This project demonstrates how to simulate a CAN bus environment on Ubuntu using Virtual CAN (vcan), SavvyCAN for visual analysis, and Python for programmatic data generation—all while running within a Docker container.  
1. PrerequisitesUbuntu (Host)  Docker installed  X11 Server (for GUI passthrough)  2. Host Setup: Virtual CANBefore starting Docker, you must create a virtual CAN interface on your physical machine.  Bash# Load the kernel module
sudo modprobe vcan

# Create and activate vcan0
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Verify the interface is active
ip addr show vcan0
3. Docker Environment Setup3.1 X11 Permissions (Host)To allow the GUI (SavvyCAN) to open from inside the container, run this on your host:  Bashxhost +local:docker
3.2 Running the ContainerLaunch your ROS 2 container with the necessary flags for network and display access:  Bashdocker run -it \
    --privileged \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    [YOUR_IMAGE_NAME]
3.3 Dependencies (Inside Docker)Install the libraries required for Qt-based GUIs and CAN utilities:  Bashsudo apt update && sudo apt install -y \
    can-utils libfuse2 libdbus-1-3 libxkbcommon-x11-0 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-xinput0 libxcb-shape0 libxcb-xfixes0
4. SavvyCAN Installation & Usage4.1 SetupDownload the SavvyCAN AppImage into your container.  Extract to bypass FUSE requirements:  Bash./SavvyCAN-x86_64.AppImage --appimage-extract
cd squashfs-root
./AppRun
Connect to Bus: Go to Connection > Add New Device Connection. Select QT SerialBus Devices, set the type to socketcan, and choose vcan0.  Load DBC: Go to File > DBC File Manager and load your .dbc file.  4.2 InterpretationTo see signal names instead of raw hex logs:  Check the Interpret Frames box on the right sidebar.  Click Expand All Rows to view decoded signal values (e.g., Velocity, Fault Codes).  5. Simulation ScriptUse the following Python script to generate traffic based on the provided robot_control.dbc.  Requirements: pip install cantools python-can.  Pythonimport can
import cantools
import time

db = cantools.database.load_file('robot_control.dbc')
bus = can.interface.Bus('vcan0', bustype='socketcan')

try:
    while True:
        # Example: Simulate Nav_Msg_0x611
        data = db.encode_message('Nav_Msg_0x611', {'LinearVelocity': 2, 'AngularVelocity': 0})
        msg = can.Message(arbitration_id=0x611, data=data, is_extended_id=False)
        bus.send(msg)
        time.sleep(0.02) # 20ms cycle
except KeyboardInterrupt:
    print("Simulation stopped.")
6. Saving Your ProgressIf you have installed many libraries inside your container, save them to a new image so they persist:  Bash# From Host
docker ps -a
docker commit [CONTAINER_ID] ros2_can_sim_image
