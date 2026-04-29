# ROS 2 CAN Simulation & DBC Analysis

This project demonstrates how to simulate a CAN bus environment on Ubuntu using:

- Virtual CAN (`vcan`)
- SavvyCAN for visual analysis
- Python for programmatic CAN traffic generation  
- Docker for isolated ROS 2 environment

---

## 📋 Prerequisites

Ensure the following are installed on your host system:

- Ubuntu (Host Machine)
- Docker
- X11 Server (for GUI passthrough)

---

## ⚙️ 1. Host Setup: Virtual CAN

```bash
# Load the kernel module
sudo modprobe vcan

# Create and activate vcan0
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Verify the interface
ip addr show vcan0
```

---

## 🐳 2. Docker Environment Setup

### 2.1 Enable X11 Permissions (Host)

```bash
xhost +local:docker
```

### 2.2 Run the Container

```bash
docker run -it \
    --privileged \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    [YOUR_IMAGE_NAME]
```

### 2.3 Install Dependencies (Inside Docker)

```bash
sudo apt update && sudo apt install -y \
    can-utils libfuse2 libdbus-1-3 libxkbcommon-x11-0 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-xinput0 libxcb-shape0 libxcb-xfixes0
```

---

## 📊 3. SavvyCAN Setup & Usage

### Installation

```bash
./SavvyCAN-x86_64.AppImage --appimage-extract
cd squashfs-root
./AppRun
```

### Connect to CAN Bus

- Go to: Connection → Add New Device Connection
- Select: QT SerialBus Devices
- Type: socketcan
- Interface: vcan0

### Load DBC File

- File → DBC File Manager → Load `.dbc`

### Frame Interpretation

- Enable Interpret Frames
- Click Expand All Rows

---

## 🧪 4. CAN Simulation Script

### Requirements

```bash
pip install cantools python-can
```

### Example Script

```python
import can
import cantools
import time

db = cantools.database.load_file('robot_control.dbc')
bus = can.interface.Bus('vcan0', bustype='socketcan')

try:
    while True:
        data = db.encode_message(
            'Nav_Msg_0x611',
            {
                'LinearVelocity': 2,
                'AngularVelocity': 0
            }
        )

        msg = can.Message(
            arbitration_id=0x611,
            data=data,
            is_extended_id=False
        )

        bus.send(msg)
        time.sleep(0.02)

except KeyboardInterrupt:
    print("Simulation stopped.")
```

---

## 💾 5. Save Docker State

```bash
docker ps -a
docker commit [CONTAINER_ID] ros2_can_sim_image
```

---

## ✅ Summary

- Simulate CAN traffic using `vcan`
- Visualize messages using SavvyCAN
- Generate CAN frames using Python + DBC
- Run everything inside Docker
