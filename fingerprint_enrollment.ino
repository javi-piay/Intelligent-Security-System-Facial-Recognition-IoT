#include <Adafruit_Fingerprint.h>
#include <HardwareSerial.h>
#include <RCSwitch.h>

RCSwitch mySwitch = RCSwitch();
#define PIN_DATA 17  // Pin digital para el pin DATA (o DAT) del módulo RF
// Definir los pines para el sensor
#define RX_PIN 26
#define TX_PIN 27

HardwareSerial mySerial(2); // UART2: RX2=GPIO 26, TX2=GPIO 27

Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);
uint8_t id = 0; // ID para la huella dactilar

void setup() {
  // put your setup code here, to run once: 
  Serial.begin(57600);
  while (!Serial) { // Espera a que se inicie el puerto serie
    delay(10);
  }
  Serial.println("Iniciando...");
  mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN); // Configura UART2 con los nuevos pines
   // Aquí se incluye el argumento de velocidad en baudios
  finger.begin(57600);
  if (finger.verifyPassword()) {
    Serial.println("Sensor de huella dactilar encontrado!");
  } else {
    Serial.println("No se pudo encontrar el sensor de huella dactilar :(");
    while (1);
  }
  Serial.println("Esperando para registrar huellas dactilares...");
  //pinMode(TCH_PIN, INPUT); // Configurar el pin TCH como entrada, si se utiliza
  mySwitch.enableTransmit(PIN_DATA); // Pin de transmisión
} 
  

void loop() {  
// put your main code here, to run repeatedly:
  Serial.print("Ingrese un ID para la nueva huella dactilar: ");
  while (Serial.available() == 0); // Espera a que se ingrese un ID
  id = Serial.parseInt();
  Serial.print("Registrando ID ");
  Serial.println(id); 
  enrollFingerprint(id); 
}  
void enrollFingerprint(uint8_t id) {
  int p = -1;
  Serial.println("Coloque su dedo en el sensor...");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Imagen tomada");
        break;
      case FINGERPRINT_NOFINGER:
        Serial.println("No hay dedo detectado");
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Error de comunicación");
        break;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Error en la imagen");
        break;
      default:
        Serial.println("Error desconocido");
        break;
    }
  }

  // Convertir imagen a modelo
  p = finger.image2Tz(1);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Imagen convertida");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Imagen desordenada");
      return;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Error de comunicación");
      return;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("No se encontraron características");
      return;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Imagen no válida");
      return;
    default:
      Serial.println("Error desconocido");
      return;
  }
  Serial.println("Quite su dedo");
  delay(2000);
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }
  Serial.println("Coloque el mismo dedo nuevamente");

  p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Imagen tomada");
        break;
      case FINGERPRINT_NOFINGER:
        Serial.println("No hay dedo detectado");
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Error de comunicación");
        break;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Error en la imagen");
        break;
      default:
        Serial.println("Error desconocido");
        break;
    }
  }
  // Convertir segunda imagen a modelo
  p = finger.image2Tz(2);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Imagen convertida");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Imagen desordenada");
      return;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Error de comunicación");
      return;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("No se encontraron características");
      return;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Imagen no válida");
      return;
    default:
      Serial.println("Error desconocido");
      return;
  }
  // Crear modelo
  p = finger.createModel();
  if (p == FINGERPRINT_OK) {
    Serial.println("Modelo creado");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Error de comunicación");
    return;
  } else if (p == FINGERPRINT_ENROLLMISMATCH) {
    Serial.println("Las huellas no coinciden");
    return;
  } else {
    Serial.println("Error desconocido");
    return;
  }
  // Guardar modelo
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.println("Huella dactilar registrada exitosamente!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Error de comunicación");
    return;
  } else if (p == FINGERPRINT_BADLOCATION) {
    Serial.println("ID de almacenamiento no válido");
    return;
  } else if (p == FINGERPRINT_FLASHERR) {
    Serial.println("Error al escribir en la memoria flash");
    return;
  } else {
    Serial.println("Error desconocido");
    return;
  }
}
