#include <Wire.h>
#include <Adafruit_Sensor.h> //inclusao da biblioteca geral de sensores adafruit
#include <Adafruit_BME280.h> //inclusao da biblioteca especifica do sensor BMP280
#include <max6675.h>

// ON-OFF warnings:
int green_led = 1;
int yellow_led = 2;
int red_led = 3
int relay_1 = 4;
int relay_2 = 5;

Adafruit_BME280 bme; //cria objeto tipo Adafruit_BME280 (I2C)

int MICS5524 = A6;

int thermoSO = 12; // SO = Serial Out
int thermoCS = 10; // CS = chip select CS pin
int thermoCLK = 13; // SCK = Serial Clock pin

MAX6675 thermocouple(thermoCLK, thermoCS, thermoSO);

// variables to serial communication in the reading function
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
String Comm;

void setup()
{
  Serial.begin(9600);
  bme.begin(0x76);
  pinMode(green_led, OUTPUT);
  pinMode(yellow_led, OUTPUT);
  pinMode(red_led, OUTPUT);
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
    //Digital Port control
    if (receivedChars[0] == 'D')
    {
      if (receivedChars[1] == '1')
      {
        if (receivedChars[2] == 'H')
        {
          digitalWrite(green_led, HIGH);
          newData = false;
        }
        else if (receivedChars[2] == 'L')
        {
          digitalWrite(green_led, LOW);
          newData = false;
        }
      }
      else if (receivedChars[1] == '2')
      {
        if (receivedChars[2] == 'H')
        {
          digitalWrite(yellow_led, HIGH);
          newData = false;
        }
        else if (receivedChars[2] == 'L')
        {
          digitalWrite(yellow_led, LOW);
          newData = false;
        }
      }
      else if (receivedChars[1] == '3')
      {
        if (receivedChars[2] == 'H')
        {
          digitalWrite(red_led, HIGH);
          newData = false;
        }
        else if (receivedChars[2] == 'L')
        {
          digitalWrite(red_led, LOW);
          newData = false;
        }
      }
      else if (receivedChars[1] == '4')
      {
        if (receivedChars[2] == 'H')
        {
          digitalWrite(relay_1, HIGH);
          newData = false;
        }
        else if (receivedChars[2] == 'L')
        {
          digitalWrite(relay_1, LOW);
          newData = false;
        }
      }
    }

    //Sensor communication - BME280 and MICS5524
    else if (receivedChars[0] == 'S')
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

      else if(receivedChars[1] == 'M')
      {
        Serial.println(analogRead(MICS5524));
        newData = false;
      }
    }
    
    //thermocouple communication
    else if (receivedChars[0] == 'T')
    {
      if (receivedChars[1] == '1')
      {
        float temperature = thermocouple.readCelsius();
        delay(50);
        Serial.println(temperature);
        newData = false;
      }
      
    }
  }
}
