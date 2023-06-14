#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// LCD nesnesi oluşturma
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Pin tanımları
const int buzzerPin = 8; // Buzzer'ın bağlı olduğu pin numarası
const int buttonPin = 2; // Button'un bağlı olduğu pin numarası
const int ledPin1 = 9;
const int ledPin2 = 10;
const int ledPin3 = 11;
const int ledPin4 = 12;

// Zamanlama değişkenleri
unsigned long timerStart = 0;
bool timerStarted = false;

// Button durum değişkenleri
volatile bool buttonPressed = false;
unsigned long buttonPressTime = 0;
unsigned long temp_time = 0;

void setup() {
  // Seri bağlantı hızını 9600 baud olarak ayarla
  Serial.begin(9600);

  // Pin modlarını ayarlama
  pinMode(buzzerPin, OUTPUT); // Buzzer pinini çıkış olarak ayarla
  pinMode(buttonPin, INPUT_PULLUP); // Button pinini giriş olarak ayarla ve pullup direncini etkinleştir

  // External interrupt
  attachInterrupt(digitalPinToInterrupt(buttonPin), buttonPressInterrupt, RISING);

  // LED pinleri için pin modlarını ayarlama
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  pinMode(ledPin4, OUTPUT);

  // LCD başlatma
  lcd.begin(16, 2);
  lcd.backlight();
  lcd.clear();
}

void loop() {
  // Button'a basıldıysa ve 5 saniye geçtiyse
  if (buttonPressed && (millis() - buttonPressTime > 5000)) {
    lcd.clear();
    lcd.print("Program stopped");
    temp_time = millis();

    // Eğer 2 saniyeden fazla süre geçtiyse
    if (temp_time > 2000) {
      lcd.noBacklight();
    }

    Serial.println("STOP py");

    while (true) {
      lcd.noBacklight();
    }; // Programı durdurmak için sonsuz döngü
  }

  // Seri bağlantı üzerinden veri geldiyse
  if (Serial.available()) {
    // Seri bağlantıdan gelen veriyi oku
    String message = Serial.readStringUntil('\n');

    // Button'a basıldıysa ve 5 saniye geçtiyse
    if (buttonPressed && (millis() - buttonPressTime > 5000)) {
      lcd.clear();
      lcd.print("Program stopped");
      temp_time = millis();

      // Eğer 2 saniyeden fazla süre geçtiyse
      if (temp_time > 2000) {
        lcd.noBacklight();
      }

      Serial.println("STOP py");

      while (true) {
        Serial.println("STOP py");
        lcd.noBacklight();
      }; // Programı durdurmak için sonsuz döngü
    }

    // Can ve zırh değerlerini ayrıştır
    int can = message.substring(message.indexOf("Can:") + 5, message.indexOf("Zirh:")).toInt();
    int zirh = message.substring(message.indexOf("Zirh:") + 5, message.indexOf("Spike:")).toInt();
    int spike = message.substring(message.indexOf("Spike") + 6).toInt();

    // LCD'ye değerleri yazdır
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Can :");
    lcd.setCursor(0, 1);
    lcd.print("Zirh:");
    lcd.setCursor(9, 0);
    lcd.print("Spike");
    lcd.setCursor(5, 0);
    lcd.print(can);
    lcd.setCursor(5, 1);
    lcd.print(zirh);
    lcd.setCursor(11, 1);
    lcd.print(spike);

    // Spike değerine göre buzzer kontrolü
    if (spike > 6 && spike <= 29) {
      digitalWrite(buzzerPin, HIGH);
      delay(125);
      digitalWrite(buzzerPin, LOW);
    } else if (spike > 1 && spike <= 5) {
      digitalWrite(buzzerPin, HIGH);
    } else if (spike == 0) {
      digitalWrite(buzzerPin, LOW);
    };

    // Can değerine göre LED kontrolü
    if (can > 75 && can <= 100) {
      digitalWrite(ledPin1, HIGH);
      digitalWrite(ledPin2, HIGH);
      digitalWrite(ledPin3, HIGH);
      digitalWrite(ledPin4, HIGH);
    } else if (can > 50 && can <= 75) {
      digitalWrite(ledPin1, HIGH);
      digitalWrite(ledPin2, HIGH);
      digitalWrite(ledPin3, LOW);
      digitalWrite(ledPin4, HIGH);
    } else if (can > 25 && can <= 50) {
      digitalWrite(ledPin1, HIGH);
      digitalWrite(ledPin2, HIGH);
      digitalWrite(ledPin3, LOW);
      digitalWrite(ledPin4, LOW);
    } else if (can > 0 && can <= 25) {
      digitalWrite(ledPin1, LOW);
      digitalWrite(ledPin2, HIGH);
      digitalWrite(ledPin3, LOW);
      digitalWrite(ledPin4, LOW);
    } else {
      digitalWrite(ledPin1, LOW);
      digitalWrite(ledPin2, LOW);
      digitalWrite(ledPin3, LOW);
      digitalWrite(ledPin4, LOW);
    }
  }
}

void buttonPressInterrupt() {
  // Button basma kesme fonksiyonu
  buttonPressed = true;
  buttonPressTime = millis();
}
