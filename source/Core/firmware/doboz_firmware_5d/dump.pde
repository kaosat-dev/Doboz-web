  /*
  then=micros();
  for(int i=0;i<500;i++)
  {
     digitalWrite(13,HIGH); 
     digitalWrite(13,LOW);
  }
  now=micros();
  Serial.print("digitalread/write: ");
  Serial.print(now-then);
  Serial.println(" us");
  
  then=micros();
  for(int i=0;i<500;i++)
  {
    BIT_SET(PORTB,0);
    BIT_CLR(PORTB,0);
  }
  now=micros();
  Serial.print("direct: ");
  Serial.print(now-then);
  Serial.println(" us");
  
  then=micros();
  for(int i=0;i<500;i++)
  {
    digWrite(8,HIGH);
    digWrite(8,LOW);
   
  }
  now=micros();
  Serial.print("helper: ");
  Serial.print(now-then);
  Serial.println(" us");
delay(3000);
  */
