#include <Wire.h>
#include <Adafruit_Sensor.h> //inclusao da biblioteca geral de sensores adafruit
#include <Adafruit_BME280.h> //inclusao da biblioteca especifica do sensor BMP280
#include <max6675.h>

Adafruit_BME280 bme; //cria objeto tipo Adafruit_BME280 (I2C)

// variables to serial communication in the reading function
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
String Comm;

void setup()
{
  Serial.begin(9600);
  bme.begin(0x76);
  delay(50);
}

void loop()
{
  reading();
  command();
}

void reading()
{
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false)
  {
    rc = Serial.read();
    delay(1);
    
    if (rc == startMarker)
    {
      recvInProgress = true;
    }

    else if (recvInProgress == true)
    {
      if (rc != endMarker)
      {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars)
        {
          ndx = numChars - 1;
        }
      }
      else
      {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }
  }
}

void command()
{
  if (newData == true)
  {
    if (receivedChars[0] == 'S')
    {
      if (receivedChars[1] == 'T')
      {
        Serial.println(bme.readTemperature());
        newData = false;
      }
      
      else if (receivedChars[1] == 'P')
      {
        Serial.println(bme.readPressure());
        newData = false;
      }
      
      else if (receivedChars[1] == 'H')
      {
        Serial.println(bme.readHumidity());
        newData = false;
      }
    }
  }
}

