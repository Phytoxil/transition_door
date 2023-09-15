/*
 * Water
 * Fab March 2022
 */

int pin = 6; // pin D6

void setup() {

  pinMode( pin , OUTPUT);
  pinMode( 13 , OUTPUT); // led
  Serial.begin(115200 );
  Serial.setTimeout( 10 );
  Serial.println("init pump...");
  Serial.println("ready");
}

void loop() {

  delay(10);
  if (Serial.available() > 0) {    
    String s = Serial.readString();
    //String s = Serial.readStringUntil('\r\n');
    s.trim();

    if( s.indexOf("pump") != -1)    
    {
      //Serial.println( "pump found" );
      
      char buffer[20];
      int ind1 = s.indexOf(',');
      if ( ind1 == -1 )
      {
        Serial.println( "Error: argument missing(pos1). should be: pump,pwm (0-255),duration (ms) example: pump,255,1000" );
        return;
      }
      String txt = s.substring(0, ind1);
      int ind2 = s.indexOf(',', ind1+1 );
      if ( ind1 == -1 )
      {
        Serial.println( "Error: argument missing(pos2). should be: pump,pwm (0-255),duration (ms) example: pump,255,1000" );
        return;
      }
      s.substring(ind1+1, ind2).toCharArray( buffer, 20 );
      int pwm = atoi( buffer );
      s.substring(ind2+1).toCharArray( buffer, 20 );
      int duration = atoi( buffer );

      //Serial.println( pwm );
      //Serial.println( duration );
      Serial.println( s );
      digitalWrite( 13, HIGH );
      analogWrite( pin , pwm );  // 80
      delay(duration);
      digitalWrite( pin, LOW );
      digitalWrite( 13, LOW );
      
      
    }
    /*
    if ( s.equals("drop" ) )
    {
      Serial.println("drop");
      analogWrite( pin , 255 );  // 80
      delay(100); // 17 microlitres
      digitalWrite( pin, LOW );
    }

    
    if ( s.equals("prime" ) )
    {
      Serial.println("prime");
      analogWrite( pin , 255 ); // 80
      delay(10000); // 100 * 17 microlitres
      digitalWrite( pin, LOW );
      Serial.println("prime done");
    
    }
    */
    
  }
  /*
  delay(1000);
  
    // set the LED with the ledState of the variable:
  //digitalWrite( pin, HIGH );
  //analogWrite( pin , 80 );
  delay(100);
  
  digitalWrite( pin, LOW );


  //delay(1000);
  */
  
  
}
