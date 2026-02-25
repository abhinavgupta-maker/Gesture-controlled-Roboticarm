#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVO_MIN 150
#define SERVO_MAX 600
#define SERVO_FREQ 50

#define SDA_PIN 19
#define SCL_PIN 18

uint8_t buffer[6];
uint8_t indexPos = 0;
int lastClaw = -1;

int angleToPulse(int angle) {
  return map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
}
void setup() {
  Serial.begin(115200);

  Wire.begin(SDA_PIN, SCL_PIN);

  pwm.begin();
  pwm.setPWMFreq(SERVO_FREQ);

  delay(1000);
  Serial.println("READY");
}

void loop() {

  while (Serial.available()) {

    uint8_t byteIn = Serial.read();

    // ---- WAIT FOR HEADER ----
    if (indexPos == 0) {
      if (byteIn == 0xAA) {
        buffer[indexPos++] = byteIn;
      }
      continue;
    }

    // ---- COLLECT PACKET ----
    buffer[indexPos++] = byteIn;

    // ---- FULL PACKET ----
    if (indexPos == 6) {

      uint8_t a1 = buffer[1];
      uint8_t a2 = buffer[2];
      uint8_t a3 = buffer[3];
      uint8_t claw = buffer[4];
      uint8_t receivedChecksum = buffer[5];

      if ((a1 + a2 + a3 + claw) % 256 == receivedChecksum) {

        pwm.setPWM(0, 0, angleToPulse(a1));
        pwm.setPWM(1, 0, angleToPulse(a2));
        pwm.setPWM(2, 0, angleToPulse(a3));

        if (claw != lastClaw) {
          if (claw == 1)
            pwm.setPWM(3, 0, angleToPulse(20));
          else
            pwm.setPWM(3, 0, angleToPulse(50));

          lastClaw = claw;
        }

        Serial.println("OK");
      } 
      else {
        Serial.println("ERR");
      }

      // 🔥 CRITICAL RESET
      indexPos = 0;
    }
  }
}