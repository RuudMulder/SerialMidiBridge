import time
import queue
import rtmidi
import serial
import serial.tools.list_ports
import threading
import logging
import sys
import time
import PySimpleGUI as sg
# 2021-03-26 Ruud Mulder
# Gui version of the Serial MIDI Bridge script from https://github.com/raspy135/serialmidi.
# The functionality is the serialmidi script, I just added the Gui.
#
# N.B. midiin = MIDI to Serial; midiout = Serial to MIDI
bridgeActive = False # set to True when bridge is active
logging.basicConfig(level = logging.DEBUG) # output all messages
myfont = 'Any 12'
midi_ready = False
midiin_message_queue = queue.Queue()
midiout_message_queue = queue.Queue()
serialPort  = ''
midiin      = rtmidi.MidiIn()
midiout     = rtmidi.MidiOut()
midiinPort  = ''
midioutPort = ''

def popupError(s):
    sg.popup_error(s, font=myfont)

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
    except serial.serialutil.SerialException:
        popupError("Serial port opening error.")
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
wc = len(max(spStrings+midiinPorts+midioutPorts,key=len)) # length of longest combo box string.
scbString = 'ScanPorts'
stbString = 'Start'
exbString = 'Exit'
wb = len(max([scbString, stbString, exbString],key=len)) # length of longest button string.
spText  = 'Serial port' # text of labels
bdText  = 'baudrate'
s2mText = 'Serial to MIDI'
m2sText = 'MIDI to Serial'
lb = len(max([spText,bdText,s2mText,m2sText],key=len)) # length of longest label.
csize = (wc,1) # will be set correctly on create
bsize = (wb,1)
tsize = (lb,1)
spSettings  = 'SerialPortName' # names for UserSettings
bdSettings  = 'Baudrate'
s2mSettings = 'Serial2MidiName'
m2sSettings = 'Midi2SerialName'
spCombo  = sg.Combo(spStrings,    size=csize, default_value=sg.UserSettings().get(spSettings,''))
bdCombo  = sg.Combo(bdValues,     size=csize, default_value=sg.UserSettings().get(bdSettings,''))
s2mCombo = sg.Combo(midiinPorts,  size=csize, default_value=sg.UserSettings().get(s2mSettings,''))
m2sCombo = sg.Combo(midioutPorts, size=csize, default_value=sg.UserSettings().get(m2sSettings,''))
scKey = '-SCAN-'
stKey = '-START-'
exKey = '-EXIT-'
scButton = sg.Button(scbString, size=bsize, key=scKey, tooltip='Scan for Serial and MIDI ports')
stButton = sg.Button(stbString, size=bsize, key=stKey, tooltip='Start/stop the Serial-MIDI bridging')
exButton = sg.Button(exbString, size=bsize, key=exKey)
# scan serial and midi ports and try to set the one already selected
def scanports():
    setSerialPortnames()
    getMidiPorts()
    # set new values and make sure the Combos have equal widths
    wc = len(max(spStrings+midiinPorts+midioutPorts,key=len)) # length of longest combo box string.
    wcsize = (wc, None)
    sel = spCombo.get()
    spCombo.Update(values=spStrings, value=sel, size=wcsize)
    bdCombo.Update(size=(wc, None))
    sel = s2mCombo.get()
    s2mCombo.Update(values=midiinPorts, value=sel, size=wcsize)
    sel = m2sCombo.get()
    m2sCombo.Update(values=midioutPorts, value=sel, size=wcsize)

layout = [[sg.Text(spText,  size=tsize), sg.Text(':'), spCombo],
          [sg.Text(bdText,  size=tsize), sg.Text(':'), bdCombo],
          [sg.Text(s2mText, size=tsize), sg.Text(':'), s2mCombo],
          [sg.Text(m2sText, size=tsize), sg.Text(':'), m2sCombo],
          [scButton, stButton, exButton]
         ]
enabled = False
window  = sg.Window('Serial-MIDI bridge', layout, font=myfont) # make font a little bigger
# Main event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == exKey:
        bridgeActive = False # stop the server
        break
    elif event == scKey:
        scanports()
    elif event == stKey:
        if enabled:
            stButton.update(text='Start')
            enabled = False
            scButton.update(disabled = False)
            spCombo.update(disabled = False)
            bdCombo.update(disabled = False)
            s2mCombo.update(disabled = False)
            m2sCombo.update(disabled = False)
            spi  = spStrings.index(spCombo.get())
            bdi  = bdValues.index(bdCombo.get())
            s2mi = midiinPorts.index(s2mCombo.get())
            m2si = midioutPorts.index(m2sCombo.get())
            stopSerialMidiServer()
        else:
            try:
                # check if all values are chosen
                spi  = spStrings.index(spCombo.get())
                bdi  = bdValues.index(bdCombo.get())
                s2mi = midiinPorts.index(s2mCombo.get())
                m2si = midioutPorts.index(m2sCombo.get())
                # all values chosen, now start server
                print('Starting: "'+spPortnames[spi]+'" "'+str(bdValues[bdi])+'" "'+midiinPorts[s2mi]+'" "'+midioutPorts[m2si]+'"')
                ok = startSerialMidiServer(spPortnames[spi], bdValues[bdi], s2mi, m2si)
                if ok:
                    stButton.update(text='Stop')
                    enabled = True
                    scButton.update(disabled = True)
                    spCombo.update(disabled = True)
                    bdCombo.update(disabled = True)
                    s2mCombo.update(disabled = True)
                    m2sCombo.update(disabled = True)
            except Exception as e:
                popupError('Select all values\n'+str(e))

# Save selected values for next time
sg.user_settings_set_entry(spSettings,  spCombo.get())
sg.user_settings_set_entry(bdSettings,  bdCombo.get())
sg.user_settings_set_entry(s2mSettings, s2mCombo.get())
sg.user_settings_set_entry(m2sSettings, m2sCombo.get())
window.close()
