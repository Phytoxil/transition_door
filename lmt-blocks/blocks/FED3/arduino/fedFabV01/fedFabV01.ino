// libs

#include <FED3.h>                                       //Include the FED3 library 
String sketch = "FAB";                                  //Unique identifier text for each sketch
FED3 fed3 (sketch);                                     //Start the FED3 object


#include <Wire.h>
#include <SPI.h>
#include "RTClib.h"
#include <Adafruit_SharpMem.h>
#include <Adafruit_GFX.h>
//#include <Fonts/FreeSans9pt7b.h>
#include <Adafruit_NeoPixel.h>



/********************************************************
  Setup Sharp Memory Display
********************************************************/
#define SHARP_SCK  12
#define SHARP_MOSI 11
#define SHARP_SS   10
#define BLACK 0
#define WHITE 1
Adafruit_SharpMem display(SHARP_SCK, SHARP_MOSI, SHARP_SS, 144, 168);
int minorHalfSize;

int counter = 0; // for tick display
int nbRight = 0;
int nbLeft = 0;

/********************************************************
  Setup RTC object
********************************************************/
RTC_PCF8523 rtc;
char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

/********************************************************
  Initialize NEOPIXEL strip
********************************************************/
#define NEOPIXEL A1
Adafruit_NeoPixel strip = Adafruit_NeoPixel(8, NEOPIXEL, NEO_GRBW + NEO_KHZ800);
#define ENABLE_RGB 13

/********************************************************
  // Fill the dots one after the other with a color
 ********************************************************/
void colorWipe(uint32_t c, uint8_t wait) {
  for (uint16_t i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, c);
    strip.show();
    delay(wait);
  }
}

void setup () {
  Serial.begin(57600);  //open serial monitor so you can see time output on computer via USB

  /********************************************************
    Start neopixel library
  ********************************************************/
  pinMode(ENABLE_RGB, OUTPUT);
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'

  /********************************************************
     Start, clear, and setup the display
   ********************************************************/
  display.begin();
  minorHalfSize = min(display.width(), display.height()) / 2;
  display.setRotation(3);
  display.setTextColor(BLACK);
  display.setFont(&FreeSans9pt7b);
  display.setTextSize(1);
  display.clearDisplay();
  display.refresh();

  pinMode(RIGHT_POKE, INPUT_PULLUP);
  pinMode(LEFT_POKE, INPUT_PULLUP);
}

void loop () {
  digitalWrite(ENABLE_RGB, LOW);
  display.clearDisplay();

  display.setCursor(1, 40);
  display.print ("GHFC FED3");
  //display.setCursor(1, 40);
  //display.print ("RTC set to:");

  tone(BUZZER, 3000, 200);
  delay(200);
  tone(BUZZER, 4000, 400);

  if (digitalRead(RIGHT_POKE) == LOW)
  {
    nbRight++;
  }
  if (digitalRead(LEFT_POKE) == LOW)
  {
    nbLeft++;
  }
  
  //display.fillRoundRect (0, 45, 400, 25, 1, WHITE);
  //display.refresh();
  /*
  display.setCursor(1, 60);
  if (now.month() < 10)
    display.print('0');      // Trick to add leading zero for formatting
  display.print(now.month(), DEC);
  display.print("/");
  if (now.day() < 10)
    display.print('0');      // Trick to add leading zero for formatting
  display.print(now.day(), DEC);
  display.print("/");
  display.print(now.year(), DEC);
  display.print(" ");
  display.print(now.hour(), DEC);
  display.print(":");
  if (now.minute() < 10)
    display.print('0');      // Trick to add leading zero for formatting
  display.print(now.minute(), DEC);
  display.print(":");
  if (now.second() < 10)
    display.print('0');      // Trick to add leading zero for formatting
  display.println(now.second(), DEC);
  */
  display.drawFastHLine(30, 80, 100, BLACK);

  display.setCursor(1, 90);
  display.print ( counter, DEC );
  counter++;
  display.setCursor(30, 90);
  display.print ( nbLeft, DEC );
  display.setCursor(60, 90);
  display.print ( nbRight, DEC );
  
  display.setCursor(1, 110);
  display.print ("Connected");
  display.setCursor(2, 110);
  display.print ("Connected");
  display.refresh();
  //delay (200);

  /********************************************************
       Print to Serial monitor as well
     ********************************************************/
  Serial.println ("GHFC TEST");

  //delay(500);

  /********************************************************
    // Randomly fill the neopixel bar with color
   ********************************************************/
  colorWipe(strip.Color(random(0, 5), random(0, 5), random(0, 5)), 100); // Color wipe
  
  colorWipe(strip.Color(0, 0, 0), 100); // OFF
  
}
