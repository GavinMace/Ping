import time
import mindwave

# Replace 'COM3' with your actual Bluetooth COM port
print("Initializing headset connection...")
headset = mindwave.Headset('COM5')  # Change to your Bluetooth COM port

# Add handler for attention only
def on_attention(headset, value):
    print(f"Attention value: {value}")

def on_connected(headset):
    print(f"DEBUG: Headset connected successfully with ID: {headset.headset_id}")

def on_disconnected(headset, id):
    print(f"DEBUG: Headset disconnected, ID: {id}")

# Register the attention handler, removing others
headset.attention_handlers.append(on_attention)
headset.headset_connected_handlers.append(on_connected)
headset.headset_disconnected_handlers.append(on_disconnected)

print("Connecting...")

# Increase timeout to allow for Bluetooth connection time
timeout = 60  # 60 second timeout for Bluetooth connection
start_time = time.time()

# Try to connect and check the status
while headset.status != 'connected' and time.time() - start_time < timeout:
    time.sleep(1)
    print(f"Status: {headset.status}")
    if headset.status == 'standby':
        print("Trying to connect...")
        headset.connect()

if headset.status == 'connected':
    print("Connected successfully!")
    
    # Check the signal quality
    print("\nChecking signal quality...")
    print(f"Current signal quality: {headset.poor_signal} (0-200, lower is better)")
    if headset.poor_signal > 100:
        print("Poor signal detected. Please ensure the headset is properly positioned: ")
        print("- Sensor pad should be touching your forehead")
        print("- Ear clip should be attached to your earlobe")
        print("- Headset should be powered on (check for LED indicator)")
    
    # Ensure attention is greater than zero
    last_attention = -1  # Initially no attention value
    print("\nStarting attentiveness monitoring. Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(0.5)
            
            # Only print when attention changes and the signal is good (low poor signal value)
            if headset.poor_signal < 100:  # Only process when signal quality is good
                if headset.attention != last_attention:
                    print(f"Attention: {headset.attention}")
                    last_attention = headset.attention
            else:
                print("Signal quality too poor, waiting for a better connection.")
                
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        headset.disconnect()
        headset.serial_close()
        print("Disconnected.")
else:
    print("Failed to connect within timeout period.")
    print("Please check the following:")
    print("- Ensure the headset is powered on and in pairing mode.")
    print("- Ensure Bluetooth is properly connected and the COM port is correct.")
    headset.serial_close()
