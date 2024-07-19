import queue
import rtmidi
import serial
import serial.tools.list_ports
import threading
import logging
import time
import customtkinter
# 2021-03-26 Ruud Mulder
# Gui version of the Serial MIDI Bridge script from https://github.com/raspy135/serialmidi.
# The functionality is the serialmidi script, I just added the Gui.
#
# N.B. midiin = MIDI to Serial; midiout = Serial to MIDI

bridgeActive = False # set to True when bridge is active
logging.basicConfig(level = logging.DEBUG) # output all messages
midi_ready = False
midiin_message_queue = queue.Queue()
midiout_message_queue = queue.Queue()
serialPort  = ''
midiin      = rtmidi.MidiIn()
midiout     = rtmidi.MidiOut()
midiinPort  = ''
midioutPort = ''
enabled = True

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

app = customtkinter.CTk()


font = customtkinter.CTkFont(size=20, weight="normal")


def popupError(s):
    dialog = customtkinter.CTkToplevel()
    dialog.title("Error")

    dialog.columnconfigure(0, weight = 1)
    dialog.rowconfigure(0, weight = 1)

    label = customtkinter.CTkLabel(dialog, text=s)
    label.grid(row=0, column=0, padx=20, pady=20)



def get_midi_length(message):
    if len(message) == 0:
        return 100
    opcode = message[0]
    if opcode >= 0xf4:
        return 1
    if opcode in [ 0xf1, 0xf3 ]:
        return 2
    if opcode == 0xf2:
        return 3
    if opcode == 0xf0:
        if message[-1] == 0xf7:
            return len(message)

    opcode = opcode & 0xf0
    if opcode in [ 0x80, 0x90, 0xa0, 0xb0, 0xe0 ]:
        return 3
    if opcode in [ 0xc0, 0xd0 ]:
        return 2

    return 100

def serial_writer():
    global midi_ready, bridgeActive
    while midi_ready == False:
        time.sleep(0.1)
    while bridgeActive:
        try:
            message = midiin_message_queue.get(timeout=0.4)
        except queue.Empty:
            continue
        logging.debug(message)
        value = bytearray(message)
        serialPort.write(value)

def serial_watcher():
    global midi_ready, bridgeActive
    receiving_message = []
    running_status = 0

    while midi_ready == False:
        time.sleep(0.1)

    while bridgeActive:
        data = serialPort.read()
        if data:
            for elem in data:
                receiving_message.append(elem)
            #Running status
            if len(receiving_message) == 1:
                if (receiving_message[0]&0xf0) != 0:
                    running_status = receiving_message[0]
                else:
                    receiving_message = [ running_status, receiving_message[0] ]

            message_length = get_midi_length(receiving_message)
            if message_length <= len(receiving_message):
                logging.debug(receiving_message)
                midiout_message_queue.put(receiving_message)
                receiving_message = []

class midi_input_handler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        #logging.debug("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        midiin_message_queue.put(message)

def midi_watcher():
    global bridgeActive

    while bridgeActive:
        try:
            message = midiout_message_queue.get(timeout = 0.4)
        except queue.Empty:
            continue
        midiout.send_message(message)

def startSerialMidiServer(serial_port_name, serial_baud, portIn, portOut):
    global serialPort, midiinPort, midioutPort, midi_ready, bridgeActive
    ok = True
    bridgeActive = True
    try:
        serialPort  = serial.Serial(serial_port_name,serial_baud)
        midiinPort  = midiin.open_port(portIn)
        midioutPort = midiout.open_port(portOut)
        midi_ready  = True
        midiin.ignore_types(sysex = False, timing = False, active_sense = False)
        midiin.set_callback(midi_input_handler(midiinPort))
    except serial.serialutil.SerialException as se:
        popupError("Serial port opening error." + se)
        ok = False

    if ok:
        serialPort.timeout = 0.4
        # By default the program waits for threads to finish before exiting
        s_watcher = threading.Thread(target = serial_watcher)
        s_writer  = threading.Thread(target = serial_writer)
        m_watcher = threading.Thread(target = midi_watcher)
        s_watcher.start()
        s_writer.start()
        m_watcher.start()
    return ok

def stopSerialMidiServer():
    global serialPort, midiinPort, midioutPort, midi_ready, bridgeActive
    bridgeActive = False
    midi_ready   = False
    del serialPort
    midiinPort.close_port()
    midioutPort.close_port()

spStrings   = []
spPortnames = []
# set serial portnames and 'port - desc' for Combo
def setSerialPortnames():
    global spStrings, spPortnames
    spStrings   = []
    spPortnames = []
    for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
        spStrings.append(u'{} - {}'.format(portname, desc))
        spPortnames.append(portname)

bdValues = []
def setBaudrates():
    global bdValues
    bdValues = serial.Serial.BAUDRATES

midiinPorts  = []
midioutPorts = []
def getMidiPorts():
    global midiinPorts, midioutPorts
    midiinPorts  = midiin.get_ports()
    midioutPorts = midiout.get_ports()

setSerialPortnames()
setBaudrates()
getMidiPorts()

#TODO: start/stopSerialMidiServer working: no messages yet.
#TODO: add message OutputElement
# make components for Gui


wc = font.measure(max(spStrings+midiinPorts+midioutPorts,key=len))# length of longest combo box string.
scbString = 'ScanPorts'
stbString = 'Start'
exbString = 'Exit'
wb = font.measure(max([scbString, stbString, exbString],key=len)) # length of longest button string.
spText  = 'Serial port' # text of labels
bdText  = 'Baudrate'
s2mText = 'Serial to MIDI'
m2sText = 'MIDI to Serial'
lb = font.measure(max([spText,bdText,s2mText,m2sText],key=len)) # length of longest label.
csize = (wc,1) # will be set correctly on create
bsize = (wb,1)
tsize = (lb,1)
spSettings  = 'SerialPortName' # names for UserSettings
bdSettings  = 'Baudrate'
s2mSettings = 'Serial2MidiName'
m2sSettings = 'Midi2SerialName'

spCombo_var = customtkinter.StringVar(value=spStrings[0])
spCombo  = customtkinter.CTkOptionMenu(app, values=spStrings, variable=spCombo_var, width=wc)

bdCombo_var = customtkinter.StringVar(value=bdValues[0])
bdValuesStr = [str(num) for num in bdValues]
bdCombo  = customtkinter.CTkOptionMenu(app, values=bdValuesStr, variable=bdCombo_var, width=wc)

s2mCombo_var = customtkinter.StringVar(value=midiinPorts[0])
s2mCombo = customtkinter.CTkOptionMenu(app, values=midiinPorts, variable=s2mCombo_var, width=wc)

m2sCombo_var = customtkinter.StringVar(value=midioutPorts[0])
m2sCombo = customtkinter.CTkOptionMenu(app, values=midioutPorts, variable=m2sCombo_var, width=wc)
scKey = '-SCAN-'
stKey = '-START-'
exKey = '-EXIT-'

# scan serial and midi ports and try to set the one already selected
def scanports():
    setSerialPortnames()
    getMidiPorts()
    # set new values and make sure the Combos have equal widths
    wc = font.measure(max(spStrings+midiinPorts+midioutPorts,key=len)) # length of longest combo box string.
    sel = spCombo.get()
    spCombo.configure(values=spStrings, width=wc)
    spCombo.set(sel)
    bdCombo.configure(width=wc)
    sel = s2mCombo.get()
    s2mCombo.configure(values=midiinPorts, width=wc)
    s2mCombo.set(sel)
    sel = m2sCombo.get()
    m2sCombo.configure(values=midioutPorts, width=wc)
    m2sCombo.set(sel)

def exKey():
    global bridgeActive  # Declare 'bridgeActive' as a global variable
    bridgeActive = False # stop the server
    app.destroy()

def stKey():
    global enabled  # Declare 'enabled' as a global variable

    if enabled:
        stButton.configure(text='Start')
        enabled = False
        scButton.configure(state="normal")
        spCombo.configure(state="normal")
        bdCombo.configure(state="normal")
        s2mCombo.configure(state="normal")
        m2sCombo.configure(state="normal")
        spi  = spCombo.get()
        bdi  = bdCombo.get()
        s2mi = s2mCombo.get()
        m2si = m2sCombo.get()
        stopSerialMidiServer()
    else:
        try:
            # check if all values are chosen
            spi  = spStrings.index(spCombo.get())
            bdi  = bdValues.index(int(bdCombo.get()))
            s2mi = midiinPorts.index(s2mCombo.get())
            m2si = midioutPorts.index(m2sCombo.get())
            # all values chosen, now start server
            print('Starting: "'+spPortnames[spi]+'" "'+str(bdValues[bdi])+'" "'+midiinPorts[s2mi]+'" "'+midioutPorts[m2si]+'"')
            ok = startSerialMidiServer(spPortnames[spi], bdValues[bdi], s2mi, m2si)
            if ok:
                stButton.configure(text='Stop')
                enabled = True
                scButton.configure(state="disable")
                spCombo.configure(state="disable")
                bdCombo.configure(state="disable")
                s2mCombo.configure(state="disable")
                m2sCombo.configure(state="disable")
        except Exception as e:
            popupError('Select all values\n'+str(e))

scButton = customtkinter.CTkButton(app, text=scbString, width=wb, height=1)
scButton.configure(command=scanports)
stButton = customtkinter.CTkButton(app, text=stbString, width=wb, height=1, command=stKey)
exButton = customtkinter.CTkButton(app, text=exbString, width=wb, height=1, command=exKey)

app.title('Serial-MIDI bridge')
app.columnconfigure((0,1,2), weight = 1)
app.rowconfigure((0,1,2,3,4), weight = 1)

#Serial Ports
label_sp = customtkinter.CTkLabel(app, text=spText)
label_sp.grid(row=0, column=0, padx=20, pady=20, sticky='w')
label_spn = customtkinter.CTkLabel(app, text=':')
label_spn.grid(row=0, column=1)
spCombo.grid(row=0, column=2, padx=20, pady=20)

#Baud Rate
label_bd = customtkinter.CTkLabel(app, text=bdText)
label_bd.grid(row=1, column=0, padx=20, pady=20, sticky='w')
label_bdn = customtkinter.CTkLabel(app, text=':')
label_bdn.grid(row=1, column=1)
bdCombo.grid(row=1, column=2, padx=20, pady=20)

#Serial To Midi
label_s2m = customtkinter.CTkLabel(app, text=s2mText)
label_s2m.grid(row=2, column=0, padx=20, pady=20, sticky='w')
label_s2mn = customtkinter.CTkLabel(app, text=':')
label_s2mn.grid(row=2, column=1)
s2mCombo.grid(row=2, column=2, padx=20, pady=20)

#Midi to Serial
label_m2s = customtkinter.CTkLabel(app, text=m2sText)
label_m2s.grid(row=3, column=0, padx=20, pady=20, sticky='w')
label_m2sn = customtkinter.CTkLabel(app, text=':')
label_m2sn.grid(row=3, column=1)
m2sCombo.grid(row=3, column=2, padx=20, pady=20)

#Buttons
scButton.grid(row=4, column=0, padx=20, pady=20)
stButton.grid(row=4, column=1, padx=20, pady=20)
exButton.grid(row=4, column=2, padx=20, pady=20)


# Main event loop
enabled = False
app.mainloop()


# Save selected values for next time
#sg.user_settings_set_entry(spSettings,  spCombo.get())
#sg.user_settings_set_entry(bdSettings,  bdCombo.get())
#sg.user_settings_set_entry(s2mSettings, s2mCombo.get())
#sg.user_settings_set_entry(m2sSettings, m2sCombo.get())

