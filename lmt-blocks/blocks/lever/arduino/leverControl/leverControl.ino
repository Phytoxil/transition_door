
#include <Wire.h>

// Lever control / Fab

int LED_PIN = 13;
int LIDAR_PIN = 3;

int currentState = 10;

//Setup
void setup() {
  
  
  
  pinMode( LED_PIN, OUTPUT);
  pinMode( LIDAR_PIN, INPUT_PULLUP);
  
  Serial.begin(115200); // 57600
  Serial.setTimeout( 50 );
  
  digitalWrite( LED_PIN, LOW );
  Serial.println("Lever control started.");
}

//Loop
void loop() {

  int r = digitalRead(LIDAR_PIN);
  if ( currentState != r )
  {
    if ( r )
    {
      Serial.println("release");
    }else
    {
      Serial.println("press");
    }
    currentState = r;
  }

  if (Serial.available() > 0)  // read incoming orders
  { 

    String incomingString = Serial.readString();
    incomingString.trim();
    
    if ( incomingString.equals( "light" ) )
    {
        digitalWrite( LED_PIN, HIGH );
    }

    if ( incomingString.equals( "lightoff" ) )
    {
        digitalWrite( LED_PIN, LOW );
    }

    if ( incomingString.equals( "click" ) )
    {      
      //todo
    }

    if ( incomingString.equals( "ping" ) )
    {
      Serial.println("pong");
    }
  
  }
  

  
  // Serial.println("pellet picked");
    
  

}

/*
void manageFeeding()
{
  if ( !tryFeeding )
  {
    return;
  }
  
  digitalWrite (MOTOR_ENABLE, HIGH);  //Enable motor driver
  fed3.stepper.step(1);
  if ( checkPellet() )
  {
    fed3.ReleaseMotor ();
    tryFeeding = false;
  }

  if ( millis() - startFeedingMs > 60000 )
  {
    Serial.println("feed timeout");  
    fed3.ReleaseMotor ();
    tryFeeding = false;
  }
  
}

boolean checkPellet()
{
  for (int j = 0; j < 20; j++)
  {
    delayMicroseconds(100);   
    if (digitalRead (PELLET_WELL) == LOW)
    {
      delayMicroseconds(100);
      // Debounce
      if (digitalRead (PELLET_WELL) == LOW)
      {        
        return true;
      }
    }
  }
  return false;
}
*/
