#include <HTTP_Method.h>
#include <Uri.h>
#include <WebServer.h>
#include <WiFi.h>
#include <WiFiAP.h>
#include <WiFiClient.h>
#include <WiFiGeneric.h>
#include <WiFiMulti.h>
#include <WiFiSTA.h>
#include <WiFiScan.h>
#include <WiFiServer.h>
#include <WiFiType.h>
#include <WiFiUdp.h>
#include <Adafruit_Fingerprint.h>
#include <HardwareSerial.h>
#include <RCSwitch.h>

#define PIN_DATA 17  // Pin digital para el pin DATA (o DAT) del módulo RF
// Definir los pines para el sensor
#define RX_PIN 26
#define TX_PIN 27

RCSwitch mySwitch = RCSwitch();
HardwareSerial mySerial(2); // UART2: RX2=GPIO 26, TX2=GPIO 27
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

// WiFi credentials
const char* ssid = "Xiaomi 11T";
const char* password = "javiguapo";

WebServer server(80);

void handleRoot() {
    const char* html = R"rawliteral(
    <!DOCTYPE HTML>
    <html>
    <head>
      <title>ESP32 Fingerprint Scanner</title>
      <script>
        function loadFingerprintStatus() {
          var xhr = new XMLHttpRequest();
          xhr.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
              document.getElementById("status").innerHTML = this.responseText;
            }
          };
          xhr.open("GET", "/fingerprint", true);
          xhr.send();
        }
        setInterval(loadFingerprintStatus, 1000); // Solicitar cada 1 segundo
      </script>
    </head>
    <body>
      <h1>ESP32 Fingerprint Scanner</h1>
      <div id="status">Waiting for fingerprint...</div>
    </body>
    </html>
  )rawliteral";

  server.send(200, "text/html", html);
}

void handleFingerprint() {
  int result = finger.getImage();
  if (result == FINGERPRINT_OK) {
    result = finger.image2Tz();
    if (result == FINGERPRINT_OK) {
      result = finger.fingerFastSearch();
      if (result == FINGERPRINT_OK) {
        String message = "Fingerprint recognized! ID: ";
        message += finger.fingerID;
        server.send(200, "text/plain", message);
        // Enviar número dependiendo del ID de la huella
        int numero = finger.fingerID == 0 ? 1 : (finger.fingerID == 1 ? 2 : 0);
        if (numero > 0) {
          mySwitch.send(numero, 24);
          message += ". Number sent: " + String(numero);
        } else {
          message += ". ID not recognized.";
        }
        server.send(200, "text/plain", message);
      } else {
        server.send(200, "text/plain", "Fingerprint not recognized");
      }
    } else {
      server.send(200, "text/plain", "Error converting fingerprint");
    }
  } else if (result== FINGERPRINT_NOFINGER) {
    server.send(200, "text/plain", "Error reading fingerprint");
  } else {
  server.send(200, "text/plain", "No finger detected");
  } 
}




void setup() {
  // put your setup code here, to run once: 
  Serial.begin(9600);
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
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to Wi-Fi");
  // Print the IP address
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  // Start the server
  server.on("/", handleRoot);
  server.on("/fingerprint", handleFingerprint);
  server.begin();
  Serial.println("HTTP server started");
} 
void loop() {
  server.handleClient();
}
