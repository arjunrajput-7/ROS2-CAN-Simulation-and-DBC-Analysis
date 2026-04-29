import can
import cantools
import time

# 1. Load the DBC
db = cantools.database.load_file('robot_control.dbc')
# 2. Connect to the virtual bus
bus = can.interface.Bus('vcan0', bustype='socketcan')

print("Starting Simulation... Press Ctrl+C to stop.")

try:
    velocity = 0.0
    while True:
        # Simulate Nav_Msg_0x611 (ID: 0x611)
        # Scale velocity back and forth
        velocity = (velocity + 0.1) if velocity < 5.0 else 0.0
        
        data_611 = db.encode_message('Nav_Msg_0x611', {
            'LinearVelocity': int(velocity), 
            'AngularVelocity': 0
        })
        msg_611 = can.Message(arbitration_id=0x611, data=data_611, is_extended_id=False)
        bus.send(msg_611)

        # Simulate IC_Msg_0x663 (ID: 0x663) - Faults and Triggers
        data_663 = db.encode_message('IC_Msg_0x663', {
            'TriggerStatus': 1, 
            'FaultCode': 0
        })
        msg_663 = can.Message(arbitration_id=0x663, data=data_663, is_extended_id=False)
        bus.send(msg_663)

        time.sleep(0.02) # 20ms cycle time
except KeyboardInterrupt:
    print("Simulation stopped.")
