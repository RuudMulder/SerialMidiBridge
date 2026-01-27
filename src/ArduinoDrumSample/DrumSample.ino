// ============================
// CONFIGURAÇÃO GERAL
// ============================
#define PIEZO_PIN A0
#define THRESHOLD 60
#define RETRIGGER_DELAY 50

#define MIDI_CHANNEL 0   // Canal 1
#define MIDI_NOTE 38     // Snare
#define VELOCITY_MIN 20
#define VELOCITY_MAX 127

unsigned long lastTriggerTime = 0;

// ============================
// SETUP
// ============================
void setup() {
  Serial.begin(31250); // MIDI padrão (UNO e MEGA)
}

// ============================
// LOOP
// ============================
void loop() {
  int piezoValue = analogRead(PIEZO_PIN);

  if (piezoValue > THRESHOLD) {
    unsigned long now = millis();

    if (now - lastTriggerTime > RETRIGGER_DELAY) {
      int velocity = map(
        piezoValue,
        THRESHOLD,
        1023,
        VELOCITY_MIN,
        VELOCITY_MAX
      );

      velocity = constrain(velocity, VELOCITY_MIN, VELOCITY_MAX);

      sendNoteOn(MIDI_NOTE, velocity, MIDI_CHANNEL);
      delay(10);
      sendNoteOff(MIDI_NOTE, 0, MIDI_CHANNEL);

      lastTriggerTime = now;
    }
  }
}

// ============================
// FUNÇÕES MIDI
// ============================
void sendNoteOn(byte note, byte velocity, byte channel) {
  Serial.write(0x90 | channel);
  Serial.write(note);
  Serial.write(velocity);
}

void sendNoteOff(byte note, byte velocity, byte channel) {
  Serial.write(0x80 | channel);
  Serial.write(note);
  Serial.write(velocity);
}
