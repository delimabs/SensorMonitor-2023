#include <Wire.h>
#include <max6675.h>

int thermoSO = 12;// SO=Serial Out
int thermoCS = 10;// CS = chip select CS pin
int thermoCLK = 13;// SCK = Serial Clock pin

MAX6675 thermocouple(thermoCLK, thermoCS, thermoSO);

// variables to serial communication in the reading function
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
String Comm;

void setup()
{
  Serial.begin(9600);
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
    if (receivedChars[0] == 'T')
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

