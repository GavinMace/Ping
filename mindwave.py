import select, serial, threading

# Byte codes - ensure these are all bytes objects
CONNECT              = b'\xc0'
DISCONNECT           = b'\xc1'
AUTOCONNECT          = b'\xc2'
SYNC                 = b'\xaa'
EXCODE               = b'\x55'
POOR_SIGNAL          = b'\x02'
ATTENTION            = b'\x04'
MEDITATION           = b'\x05'
BLINK                = b'\x16'
HEADSET_CONNECTED    = b'\xd0'
HEADSET_NOT_FOUND    = b'\xd1'
HEADSET_DISCONNECTED = b'\xd2'
REQUEST_DENIED       = b'\xd3'
STANDBY_SCAN         = b'\xd4'
RAW_VALUE            = b'\x80'

# Status codes
STATUS_CONNECTED     = 'connected'
STATUS_SCANNING      = 'scanning'
STATUS_STANDBY       = 'standby'

class Headset(object):
    """
    A MindWave Headset
    """

    class DongleListener(threading.Thread):
        """
        Serial listener for dongle device.
        """
        def __init__(self, headset, *args, **kwargs):
            """Set up the listener device."""
            self.headset = headset
            super(Headset.DongleListener, self).__init__(*args, **kwargs)

        def run(self):
            """Run the listener thread."""
            s = self.headset.dongle

            # Re-apply settings to ensure packet stream
            s.write(DISCONNECT)
            try:
                d = s.get_settings()
                for i in range(2):
                    d['rtscts'] = not d['rtscts']
                    s.apply_settings(d)
            except AttributeError:
                # Fall back to older PySerial methods if needed
                d = s.getSettingsDict()
                for i in range(2):
                    d['rtscts'] = not d['rtscts']
                    s.applySettingsDict(d)

            while True:
                # Begin listening for packets
                try:
                    first_byte = s.read(1)
                    if first_byte == SYNC and s.read(1) == SYNC:
                        # Packet found, determine plength
                        while True:
                            plength_byte = s.read(1)
                            plength = int.from_bytes(plength_byte, byteorder='big')
                            if plength != 170:
                                break
                        if plength > 170:
                            continue

                        # Read in the payload
                        payload = s.read(plength)

                        # Verify its checksum
                        val = sum(b for b in payload[:-1])
                        val &= 0xff
                        val = ~val & 0xff
                        chksum = int.from_bytes(s.read(1), byteorder='big')

                        #if val == chksum:
                        if True: # ignore bad checksums
                            self.parse_payload(payload)
                except (select.error, OSError):
                    break
                except serial.SerialException:
                    s.close()
                    break

        def parse_payload(self, payload):
            """Parse the payload to determine an action."""
            index = 0
            while index < len(payload):
                # Parse data row
                excode = 0
                try:
                    code = payload[index]
                    index += 1
                except IndexError:
                    break
                    
                while code == ord(EXCODE):
                    # Count excode bytes
                    excode += 1
                    try:
                        code = payload[index]
                        index += 1
                    except IndexError:
                        break
                        
                if code < 0x80:
                    # This is a single-byte code
                    try:
                        value = payload[index]
                        index += 1
                    except IndexError:
                        break
                        
                    if code == ord(POOR_SIGNAL):
                        # Poor signal
                        old_poor_signal = self.headset.poor_signal
                        self.headset.poor_signal = value
                        if self.headset.poor_signal > 0:
                            if old_poor_signal == 0:
                                for handler in self.headset.poor_signal_handlers:
                                    handler(self.headset, self.headset.poor_signal)
                        else:
                            if old_poor_signal > 0:
                                for handler in self.headset.good_signal_handlers:
                                    handler(self.headset, self.headset.poor_signal)
                    elif code == ord(ATTENTION):
                        # Attention level
                        self.headset.attention = value
                        for handler in self.headset.attention_handlers:
                            handler(self.headset, self.headset.attention)
                    elif code == ord(MEDITATION):
                        # Meditation level
                        self.headset.meditation = value
                        for handler in self.headset.meditation_handlers:
                            handler(self.headset, self.headset.meditation)
                    elif code == ord(BLINK):
                        # Blink strength
                        self.headset.blink = value
                        for handler in self.headset.blink_handlers:
                            handler(self.headset, self.headset.blink)
                else:
                    # This is a multi-byte code
                    try:
                        vlength = payload[index]
                        index += 1
                    except IndexError:
                        break
                        
                    value = payload[index:index+vlength]
                    index += vlength
                    
                    # Multi-byte EEG and Raw Wave codes not included
                    # Raw Value added due to Mindset Communications Protocol
                    if code == ord(RAW_VALUE):
                        raw = value[0]*256 + value[1]
                        if (raw >= 32768):
                            raw = raw - 65536
                        self.headset.raw_value = raw
                        for handler in self.headset.raw_value_handlers:
                            handler(self.headset, self.headset.raw_value)
                    if code == ord(HEADSET_CONNECTED):
                        # Headset connect success
                        run_handlers = self.headset.status != STATUS_CONNECTED
                        self.headset.status = STATUS_CONNECTED
                        self.headset.headset_id = value.hex()
                        if run_handlers:
                            for handler in self.headset.headset_connected_handlers:
                                handler(self.headset)
                    elif code == ord(HEADSET_NOT_FOUND):
                        # Headset not found
                        if vlength > 0:
                            not_found_id = value.hex()
                            for handler in self.headset.headset_notfound_handlers:
                                handler(self.headset, not_found_id)
                        else:
                            for handler in self.headset.headset_notfound_handlers:
                                handler(self.headset, None)
                    elif code == ord(HEADSET_DISCONNECTED):
                        # Headset disconnected
                        headset_id = value.hex()
                        for handler in self.headset.headset_disconnected_handlers:
                            handler(self.headset, headset_id)
                    elif code == ord(REQUEST_DENIED):
                        # Request denied
                        for handler in self.headset.request_denied_handlers:
                            handler(self.headset)
                    elif code == ord(STANDBY_SCAN):
                        # Standby/Scan mode
                        try:
                            byte = value[0]
                        except IndexError:
                            byte = None
                        if byte:
                            run_handlers = (self.headset.status != STATUS_SCANNING)
                            self.headset.status = STATUS_SCANNING
                            if run_handlers:
                                for handler in self.headset.scanning_handlers:
                                    handler(self.headset)
                        else:
                            run_handlers = (self.headset.status != STATUS_STANDBY)
                            self.headset.status = STATUS_STANDBY
                            if run_handlers:
                                for handler in self.headset.standby_handlers:
                                    handler(self.headset)

    def __init__(self, device, headset_id=None, open_serial=True):
        """Initialize the headset."""
        # Initialize headset values
        self.dongle = None
        self.listener = None
        self.device = device
        self.headset_id = headset_id
        self.poor_signal = 255
        self.attention = 0
        self.meditation = 0
        self.blink = 0
        self.raw_value = 0
        self.status = None

        # Create event handler lists
        self.poor_signal_handlers = []
        self.good_signal_handlers = []
        self.attention_handlers = []
        self.meditation_handlers = []
        self.blink_handlers = []
        self.raw_value_handlers = []
        self.headset_connected_handlers = []
        self.headset_notfound_handlers = []
        self.headset_disconnected_handlers = []
        self.request_denied_handlers = []
        self.scanning_handlers = []
        self.standby_handlers = []

        # Open the socket
        if open_serial:
            self.serial_open()

    def connect(self, headset_id=None):
        """Connect to the specified headset id."""
        if headset_id:
            self.headset_id = headset_id
        else:
            headset_id = self.headset_id
            if not headset_id:
                self.autoconnect()
                return
        # Convert headset_id to bytes if it's not already
        if isinstance(headset_id, str):
            headset_id_bytes = bytes.fromhex(headset_id)  # Convert hex string to byte array
        else:
            headset_id_bytes = headset_id  # already a byte array, so leave it as is

        self.dongle.write(CONNECT + headset_id_bytes)  # Send the command as bytes

    def autoconnect(self):
        """Automatically connect device to headset."""
        self.dongle.write(AUTOCONNECT)  # No string to encode, so just send the byte command

    def disconnect(self):
        """Disconnect the device from the headset."""
        self.dongle.write(DISCONNECT)

    def serial_open(self):
        """Open the serial connection and begin listening for data."""
        # Establish serial connection to the dongle
        if not self.dongle or not self.dongle.isOpen():
            self.dongle = serial.Serial(self.device, 115200)

        # Begin listening to the serial device
        if not self.listener or not self.listener.isAlive():
            self.listener = self.DongleListener(self)
            self.listener.daemon = True
            self.listener.start()

    def serial_close(self):
        """Close the serial connection."""
        self.dongle.close()