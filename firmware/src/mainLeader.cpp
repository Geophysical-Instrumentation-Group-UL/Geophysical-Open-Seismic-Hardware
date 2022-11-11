#include <Arduino.h>
#include <ad7768.h>
#include <command.h>

#define RS485Serial Serial3

//TODO: Print instructions

int Mode = 9; // high = send = D2 led off, low = listen = D2 led high
int trig = 22;
String instruction;
bool waitingForworkerResponse = false;
bool waitForData = false;
int number_of_data_packet;
String duration = "50";
String sampling_rate = "32";

void trig_ISR();

volatile bool init_trig_detected = false;
volatile bool triggered_state = false;

void setup() {
  RS485Serial.begin(115200);
  Serial.begin(115200);
  pinMode(Mode,OUTPUT);
  digitalWrite(Mode,LOW);
  pinMode(trig,INPUT_PULLDOWN);
}

void loop() {

if (Serial.available() ) 
  {
    instruction = Serial.readStringUntil('\n');
    instruction.trim();
     // I always want the status of the worker after a command
    String temp;
    temp = instruction.substring(instruction.length() - 1);
    int workerid = temp.toInt();

	if (instruction.equals("arm")) {
    digitalWrite(Mode,HIGH);
    delay(5);
    arm(&RS485Serial);
    delay(5);
    digitalWrite(Mode,LOW);
    Serial.println("arming...");
    Serial.flush();
    attachInterrupt(digitalPinToInterrupt(trig),trig_ISR,LOW);
    // waitingForworkerResponse = true;

  }
  if (instruction.startsWith("get status")) {
    digitalWrite(Mode,HIGH);
    delay(5);
    getWorkerStatus(&RS485Serial,workerid);
    delay(5);
    digitalWrite(Mode,LOW);
  }
  if (instruction.startsWith("config acq")) {
    Serial.print("Configuration in process to : ");Serial.println(workerid);
    sampling_rate = Serial.readStringUntil('\n');
    duration = Serial.readStringUntil('\n');
    // Serial.println(sampling_rate);
    // Serial.println(duration);
    digitalWrite(Mode,HIGH);
    delay(5);
    sendConfigToADC(&RS485Serial,DEFAULT, sampling_rate + "T" + duration,workerid);
    delay(5);
    digitalWrite(Mode,LOW);
    delay(5);
    digitalWrite(Mode,HIGH);
    delay(5);
    getWorkerStatus(&RS485Serial,workerid);
    delay(5);
    digitalWrite(Mode,LOW);
    waitingForworkerResponse = true;
  }
  if (instruction.startsWith("config default")) {
    Serial.print("Configuration in process to : ");Serial.println(workerid);
    digitalWrite(Mode,HIGH);
    delay(5);
    sendConfigToADC(&RS485Serial,DEFAULT, duration,workerid);
    delay(5);
    digitalWrite(Mode,LOW);
    delay(5);
    // digitalWrite(Mode,HIGH);
    // delay(5);
    // getWorkerStatus(&RS485Serial,workerid);
    // delay(5);
    // digitalWrite(Mode,LOW);
    waitingForworkerResponse = true;
  }
  if (instruction.startsWith("config seismic")) {
    Serial.print("Configuration in process to : ");Serial.println(workerid);
    digitalWrite(Mode,HIGH);
    delay(5);
    sendConfigToADC(&RS485Serial,SEISMIC, duration,workerid); 
    delay(5);
    digitalWrite(Mode,LOW);
    delay(5);
    // digitalWrite(Mode,HIGH);
    // delay(5);
    // getWorkerStatus(&RS485Serial,workerid);
    // delay(5);
    // digitalWrite(Mode,LOW);
    waitingForworkerResponse = true;
  }
  if (instruction.startsWith("harvest")) {
    digitalWrite(Mode,HIGH);
    delay(5);
    HarvestData(&RS485Serial,workerid);
    delay(5);
    digitalWrite(Mode,LOW);
    Serial.print(workerid);Serial.println("harvesting");
    waitForData = true;
    waitingForworkerResponse = false; //I dont want the status, i want the data, the status is allready asked at 
    // the end of the triggered state
  }
  }
if (waitingForworkerResponse == true) 
{ 
  command receivedStatus; 
  receivedStatus = readCommand(&RS485Serial);
      if (receivedStatus.status == IDLE)
      {
        Serial.print("Status : ");Serial.println("IDLE");
        // Serial.print("Status : ");Serial.println("CONFIGURED");
      }
      else if (receivedStatus.status == ARMED)
      {
       Serial.print("Status : ");Serial.println("ARMED");
       attachInterrupt(digitalPinToInterrupt(trig), trig_ISR,RISING);
      }
      else if (receivedStatus.status == DATAREADY)
      {
       Serial.print("Status : ");Serial.println("DATAREADY");
      }
      else if (receivedStatus.status == CONFIGURED)
      {
        String conf;
        conf = RS485Serial.readStringUntil('f');
        delay(5);
        // Serial.println("ADC parameters : ");
        // Serial.println("-----------------");
        // Serial.println(conf);
        // Serial.println("-----------------");
        Serial.print("Status : ");Serial.println("CONFIGURED");
        Serial.flush();
      }

    waitingForworkerResponse = false;
}
if (waitForData == true)
{
    String data;
    int workeridData;
    
    
    workeridData = RS485Serial.readStringUntil('w').toInt();
    Serial.print("worker # "),Serial.println(workeridData);

    Serial.println("-----------------");

    number_of_data_packet = RS485Serial.readStringUntil(':').toInt();
    Serial.print("Number of data packets : "),Serial.println(number_of_data_packet);
    // number_of_data_packet = 1600;
    delay(2);
    for (int i = 0; i < number_of_data_packet; i++)
    {
        data = RS485Serial.readStringUntil(':');
        Serial.println(data);
    }
    Serial.println("-----------------");
    waitForData = false;
    
}

noInterrupts();
if (triggered_state == true)
{
 
  digitalWrite(Mode,HIGH);
  sendTrigger(&RS485Serial);
  digitalWrite(Mode,LOW);
  detachInterrupt(digitalPinToInterrupt(trig));
  delay(5);
  Serial.println("trigged");
  delay(5); 
  


  // send trigger command to worker
  triggered_state = false;
  // waitingForworkerResponse = true;
}
interrupts();

}




 void trig_ISR() {
		init_trig_detected = true;
		triggered_state = true;
}
