
#include <FED3.h>                                       //Include the FED3 library 
#include <Wire.h>
String sketch = "FR1";                                  //Unique identifier text for each sketch
FED3 fed3 (sketch);                                     //Start the FED3 object
Adafruit_SharpMem display(SHARP_SCK, SHARP_MOSI, SHARP_SS, 144, 168);

//Initialize value

int nbLeft = 0;
int nbRight = 0;


//Setup
void setup() {
  Serial.begin(57600);
  
  display.begin();
  display.setRotation(3); //Rotate 180°
  display.setTextSize(2);
  display.clearDisplay();
  pinMode(RIGHT_POKE, INPUT_PULLUP); //  RIGHT_POKE Pullup
  pinMode(LEFT_POKE, INPUT_PULLUP); //  RIGHT_POKE Pullup
  
  fed3.begin();
  //fed3.DisplayPokes = false;
  //fed3.DisplayPo
}

//Loop
void loop() {
 
  //fed3.run();

  // digitalWrite (MOTOR_ENABLE, LOW);
  
  //Clear mouse column on left side of screen
  display.fillRect(0, 0, 27, 168, WHITE);

  // Minor Jam
  // fed3.RotateDisk(100);  
  
  fed3.pixelsOn( 255 , 0 , 0 ,0 );
  delay( 200 );
  fed3.pixelsOn( 25 , 0 , 0 , 0 );
  delay( 200 );
  //fed3.Click();
  delay( 100 );
  fed3.leftPixel( 0 , 50 , 0 , 0 );
  delay( 200 );
  fed3.leftPokePixel( 0 , 20 , 20 , 0 );
  delay( 200 );
  fed3.leftPokePixel( 0 , 0 , 0 , 0 );
  delay( 200 );
  
    
  /* // vibrate Jam
  for (int i = 0; i < 30; i++) {
    if (RotateDisk(120)) {
      display.fillRect (5, 15, 120, 15, WHITE);  //erase the "Jam clear" text without clearing the entire screen by pasting a white box over it
      return true;
    }
    if (RotateDisk(-60)) {
      display.fillRect (5, 15, 120, 15, WHITE);  //erase the "Jam clear" text without clearing the entire screen by pasting a white box over it
      return true;
    }
  }
   */

/*
random(30, 100);
    tone(BUZZER, 3000, 200);
      delay(200);
      tone(BUZZER, 4000, 400);
*/
  int py = 100;
    //Draw Mouse
    display.fillRoundRect (5, py, 16, 12, 4, BLACK); //body
    if (nbLeft % 2 == 0) {
      display.fillRoundRect (14, py - 1, 11, 6, 2, BLACK); //head
      display.fillRoundRect (12, py - 3, 6, 3, 1, BLACK);  //ear
      display.fillRoundRect (18, py - 1, 2, 1, 1, WHITE);  //eye
      display.drawFastHLine(0, py + 1, 6, BLACK);      //tail
      display.drawFastHLine(0, py, 6, BLACK);      //tail
      display.fillRoundRect (18, py + 9, 4, 4, 1, BLACK); //front foot
      display.fillRoundRect (3, py + 9, 4, 4, 1, BLACK); //back foot
    }
    else {
      display.fillRoundRect (15, py - 2, 11, 7, 2, BLACK); //head
      display.fillRoundRect (13, py - 3, 6, 3, 1, BLACK);  //ear
      display.fillRoundRect (19, py - 1, 2, 1, 1, WHITE);  //eye
      display.drawFastHLine(0, py + 3, 6, BLACK);      //tail
      display.drawFastHLine(0, py + 2, 6, BLACK);    //tail
      display.fillRoundRect (16, py + 9, 4, 4, 1, BLACK); //front foot
      display.fillRoundRect (5, py + 9, 4, 4, 1, BLACK); //back foot
    }

    
  

  
  display.setTextColor(BLACK, WHITE);
  display.setCursor(3, 2);
  display.print(F("LEFT:"));
  display.println(nbLeft);
  //display.setCursor(80, 2);
  display.print(F("RIGHT:"));
  display.println(nbRight);

  display.setCursor(30, 40);
  display.print(F("GHFC"));

  //Check for poke
  if (digitalRead(RIGHT_POKE) == LOW)
  {
    nbRight ++;
    Serial.println("right");
    if ( nbRight%20 == 0)
    {
     // fed3.Feed();
    }
  }
  if (digitalRead(LEFT_POKE) == LOW)
  {
    nbLeft ++;
    Serial.println("left");
  }

/*
while (digitalRead (PELLET_WELL) == LOW) {            //Wait here while there's a pellet in the well
    delay (10);
  }
  */

  // display.clearDisplay();
  
  display.refresh();
}
