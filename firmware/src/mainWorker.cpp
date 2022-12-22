#include <Arduino.h>
#include <ad7768.h> 
#include <command.h>
#include <stdio.h>
#include <cmath>
#include <SPI.h>
#include <Vector.h>
#include <string>
#include <elapsedMillis.h>



#define RS485Serial Serial3

int Mode = 9; // high = send = D2 led off, low = listen = D2 led high
command receivedCommand; 
int ODR;
int numberOfByte = 32;
int duration;
int samplingRate;
bool mustSendStatus = false;
bool mustSendData = false;
bool readyToTrig = false;
int workerStatus = IDLE;
int workerID = 1;
int chipSelectPin = 10;
ad7768_chip _default = {
		/* Configuration */
		.chipSelectPin = chipSelectPin,
		.power_mode = AD7768_ECO,
		.mclk_div = AD7768_MCLK_DIV_32,
		.dclk_div = AD7768_DCLK_DIV_8,
		.dec_rate = AD7768_DEC_X1024,
		.filt_type = AD7768_FILTER_SINC,

	};
ad7768_chip _seismic = {
		/* Configuration */
		.chipSelectPin = chipSelectPin,
		.power_mode = AD7768_ECO,
		.mclk_div = AD7768_MCLK_DIV_32,
		.dclk_div = AD7768_DCLK_DIV_8,
		.dec_rate = AD7768_DEC_X32,
		.filt_type = AD7768_FILTER_SINC,

	};
ad7768_chip configType = _seismic;

// pin declaration
int dout0 = 2;
int dout1 = 3;
int dout2 = 4;
int clck = 6;
int drdy = 18;
#define encoderA 20
#define encoderB 19
int cs = 16;
int IN1 = 7;
int IN2 = 8;

volatile long countA = 0.0;
float nbrpoles = 12.0;
float nbrToursMoteur;
float nbrToursArbre; 
float division_factor = 0.00322 * 837.76; 
elapsedMillis taskTimer = 0;
unsigned int taskDelay = 100; //ms
volatile int current = 0;
volatile int current_limit = 760; //mA
volatile int current_average_factor = 1000;
volatile int number_of_averaging_loop = current_average_factor / 20;
volatile int current_number_of_averaging_loop = 0;
volatile int avg = 0;
int pwm = 240;
int direction = 0; // 0 == IDLE, 1 == FORWARD, -1 == BACKWARD
int coastingTime = 500; //ms


void pulseA();     
void coast(int time);
void currentSense();


// ISR functions
void read_ISR();
void drdy_ISR();

// binary_data-ready flags and counter
volatile bool data_packet_ready = false;
volatile int acquisition_initial_time;
volatile int data_packet_counter = 0; 


// trigger state
volatile bool init_trig_detected = false;
volatile bool triggered_state = false;

// clock count for each binary_data packet
volatile int clck_count = 0;

// binary_data buffer and precalculated 2s power
volatile int expo [32] = {0,0,0,0,0,0,0,0,pow(2,23),pow(2,22),pow(2,21),pow(2,20),
pow(2,19),pow(2,18),pow(2,17),pow(2,16),pow(2,15),pow(2,14),
pow(2,13),pow(2,12),pow(2,11),pow(2,10),pow(2,9),pow(2,8),pow(2,7),pow(2,6),pow(2,5),
pow(2,4),pow(2,3),pow(2,2),pow(2,1),pow(2,0)};
volatile int binary_data0[32];
volatile double integer_data0 = 0;

volatile int binary_data1[32];
volatile double integer_data1 = 0;

volatile int binary_data2[32];
volatile double integer_data2 = 0;




int number_of_data_packet =1600;

// vector that holds a complete acquisition
int storage_arrayD0[16000]; //TODO: This maximum array size is 0.5 sec for 32 khz ODR
int storage_arrayT0[16000];
Vector<int> data0(storage_arrayD0);
Vector<int> time(storage_arrayT0);

int storage_arrayD1[16000]; //TODO: This maximum array size is 0.5 sec for 32 khz ODR
// int storage_arrayT1[32000];
Vector<int> data1(storage_arrayD1);
// Vector<int> time0(storage_arrayT1);

int storage_arrayD2[16000]; //TODO: This maximum array size is 0.5 sec for 32 khz ODR
// int storage_arrayT2[32000];
Vector<int> data2(storage_arrayD2);
// Vector<int> time(storage_arrayT2);

// When the lenght of the array is 32k the memory is overflowing.

void setup() {

  RS485Serial.begin(115200);
  Serial.begin(115200);   
  pinMode(Mode,OUTPUT);
  digitalWrite(Mode,LOW);
  SPI.begin();
  pinMode(dout0, INPUT);
  pinMode(drdy, INPUT_PULLDOWN);
  pinMode(clck, INPUT);
  pinMode(chipSelectPin, OUTPUT);
  pinMode(cs, INPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(encoderA, INPUT);
  pinMode(encoderB, INPUT);

  delay(100);
  ad7768_setup(configType);
}

void loop() {

if(RS485Serial.available () >0 and readyToTrig == false) 
{
  // String test;

  receivedCommand = readCommand(&RS485Serial);
  // Serial.println(receivedCommand.def);
  // Serial.println(receivedCommand.workerId);
  // test = RS485Serial.readStringUntil('\n');
  // Serial.println(test);
  if (receivedCommand.type == GLOBAL or receivedCommand.workerId == workerID)
  {
    // Serial.println("called");
    // Serial.println(receivedCommand.def);
    // Serial.println(receivedCommand.workerId);

  if (receivedCommand.def == ARM)
  {
    workerStatus = ARMED;
    Serial.println("armed");
    data_packet_counter = 0;
    readyToTrig = true;

    attachInterrupt(digitalPinToInterrupt(drdy), drdy_ISR, RISING);
    attachInterrupt(digitalPinToInterrupt(clck), read_ISR, FALLING);
  }
  else if (receivedCommand.def == STATUS)
  {
    digitalWrite(Mode,HIGH);
    delay(5);
    sendWorkerStatus(&RS485Serial,workerStatus,workerID);
    delay(5);
    digitalWrite(Mode,LOW);
    delay(5);
  }
  else if (receivedCommand.def == CONFIG)
   {
    //  Serial.print(receivedCommand.adcConfig);
     Serial.print("config");
     if (receivedCommand.adcConfig == DEFAULT)
     {configType = _default;}
     else if (receivedCommand.adcConfig == SEISMIC)
     {configType = _seismic;} 
     int index = receivedCommand.data.indexOf("T");   
     samplingRate = receivedCommand.data.substring(0,index).toInt();
     duration = receivedCommand.data.substring(index+1).toInt();
    if (samplingRate == 32)
     {
      configType.dec_rate = AD7768_DEC_X32;
      }
    else if (samplingRate == 16)
      {
      configType.dec_rate = AD7768_DEC_X64;
      }
    else if (samplingRate == 8)
      {
      configType.dec_rate = AD7768_DEC_X128;
      }
    else if (samplingRate == 4)
      {
      configType.dec_rate = AD7768_DEC_X256;
      }
    else if (samplingRate == 2)
      {
      configType.dec_rate = AD7768_DEC_X512;
      }
    else if (samplingRate == 1)
      {
      configType.dec_rate = AD7768_DEC_X1024;
      }

     ad7768_setup(configType);
     workerStatus = CONFIGURED;

    // delay(5);
    // digitalWrite(Mode,HIGH);
    // delay(5);
    // sendWorkerStatus(&RS485Serial,workerStatus,workerID);
    // delay(5);
    // digitalWrite(Mode,LOW);


    number_of_data_packet =  int(((duration/1000.0) * (samplingRate*1000.0)));
    // delay(5);
    // digitalWrite(Mode,HIGH);
    // delay(5);



    // RS485Serial.println(number_of_data_packet);

    // RS485Serial.println(receivedCommand.data);
    // RS485Serial.println(receivedCommand.data.substring(index+1).toInt());
    // ODR = print_config(configType, &RS485Serial);
    // RS485Serial.flush();
    // delay(5);
    // RS485Serial.print(duration);RS485Serial.println(samplingRate);
    //     delay(5);

    // RS485Serial.println('s');
    // digitalWrite(Mode,LOW);

 
    // Serial.println(number_of_data_packet);
    // workerStatus = IDLE;
    

   }
  else if (receivedCommand.def == HARVEST)
  {
    mustSendData = true;
    Serial.println("called for harvest");
  }
  else if (receivedCommand.def == MOTOR)
  {
    String direction = receivedCommand.data;
   if (direction == "forward")
   {
    current = 0;
    coast(coastingTime);
    analogWrite(IN1, pwm);
    analogWrite(IN2, 0);
    delay(1000);
    
    attachInterrupt(digitalPinToInterrupt(encoderA), pulseA, RISING);

    while (current < current_limit)
    {
    analogWrite(IN1, pwm);
    analogWrite(IN2, 0);
    
    nbrToursMoteur = countA/nbrpoles; //Diviser par le nombre de pole pour obtenir le vrai rpm du moteur
    nbrToursArbre = nbrToursMoteur/721.0 ;  // Appliquer le ratio du réducteur
    
    if (taskTimer > taskDelay )
  {
    digitalWrite(Mode,HIGH);
  
    RS485Serial.print(current);RS485Serial.print(",");
    
    RS485Serial.println(nbrToursArbre);
    digitalWrite(Mode,LOW);
    taskTimer = 0;

  }
  
  
    }
    coast(coastingTime);
        
    digitalWrite(Mode,HIGH);
    RS485Serial.println('w');
    RS485Serial.print('T');
    RS485Serial.println(nbrToursArbre);
    RS485Serial.print('S');RS485Serial.println(current);
    delay(5);
    digitalWrite(Mode,LOW);
  }
   
   if (direction == "backward")
   {
    current = 0;
    coast(coastingTime);
    analogWrite(IN1, 0);
    analogWrite(IN2, pwm);
    delay(1000);

    attachInterrupt(digitalPinToInterrupt(encoderA), pulseA, RISING);

    while (current < current_limit)
    {
    analogWrite(IN1, 0);
    analogWrite(IN2, pwm);
    
    nbrToursMoteur = countA/nbrpoles; //Diviser par le nombre de pole pour obtenir le vrai rpm du moteur
    nbrToursArbre = nbrToursMoteur/721.0 ;  // Appliquer le ratio du réducteur
    
    if (taskTimer > taskDelay )
  {
    digitalWrite(Mode,HIGH);
  
    RS485Serial.print(current);RS485Serial.print(",");
    
    RS485Serial.println(nbrToursArbre);
    digitalWrite(Mode,LOW);
    taskTimer = 0;

  }
  
  
    }
    coast(coastingTime);
        
    
    digitalWrite(Mode,HIGH);
    RS485Serial.println('w');
    RS485Serial.print('T');
    RS485Serial.println(nbrToursArbre);
    RS485Serial.print('S');RS485Serial.println(current);
    delay(5);
    digitalWrite(Mode,LOW);
   }
   
   if (direction == "stop")
   {
    coast(coastingTime);
   }
   }
   
  }
  
  }

   

  if (mustSendData == true)
  {
    digitalWrite(Mode,HIGH);
     delay(5);
    RS485Serial.print(workerID);RS485Serial.println('w');
    delay(5);
    RS485Serial.print(number_of_data_packet);RS485Serial.println(':');
    delay(5);
    for (int i = 0; i < number_of_data_packet; i++)
      {
        RS485Serial.print(time.at(i));RS485Serial.print(",");
        RS485Serial.print(data0.at(i));RS485Serial.print(",");
        RS485Serial.print(data1.at(i));RS485Serial.print(",");
        RS485Serial.print(data2.at(i));
        RS485Serial.print(':');
        delay(1);
      }
    RS485Serial.flush();
    digitalWrite(Mode,LOW);
    mustSendData = false;
    workerStatus = IDLE;
    time.clear();
    data0.clear();
    data1.clear();
    data2.clear();
  }


noInterrupts();
if (readyToTrig == true and triggered_state == false)
{
 if (RS485Serial.find('t'))
{
    acquisition_initial_time = micros();
    triggered_state = true;
  }
}
if (data_packet_ready == true and triggered_state == true)
{		

    data0.push_back(integer_data0);
    data1.push_back(integer_data1);
    data2.push_back(integer_data2);
    time.push_back(micros() - acquisition_initial_time);

		data_packet_ready = false;
		data_packet_counter += 1;

		if (data_packet_counter == number_of_data_packet)
		{
      workerStatus = DATAREADY;
      // mustSendStatus = true;
			triggered_state = false;
      readyToTrig = false;
      data_packet_counter = 0;
      detachInterrupt(digitalPinToInterrupt(drdy));
      detachInterrupt(digitalPinToInterrupt(clck));
		}

}
interrupts();
}

void read_ISR() {
if (clck_count < 32){ // because the output is 32 bit long
// delayNanoseconds(10);
binary_data0[clck_count] = digitalRead(dout0);
binary_data1[clck_count] = digitalReadFast(dout1);
binary_data2[clck_count] = digitalReadFast(dout2);
clck_count += 1;


}
else if (clck_count == 33){ // directly after the last bit
	data_packet_ready = true;
	for (int i = 8; i < 32; i++) { // data bit is from 8 to 32
      integer_data0 +=  expo[i] * binary_data0[i];
			integer_data1 +=  expo[i] * binary_data1[i];
      integer_data2 +=  expo[i] * binary_data2[i];

			}
	clck_count += 1;

}

else {
	clck_count += 1;
}
}

void drdy_ISR(){
	if (triggered_state == true)
	{
	clck_count = 0;
	integer_data0 = 0;	
  integer_data1 = 0;	
  integer_data2 = 0;	
	}
	

}

void currentSense () {
    current_number_of_averaging_loop += 1;
    int i = 0;
    
    for (i = 0; i < 20; i++) { //The value of 20 is choosen in order to minimize the time spent in this function
      avg += analogRead(cs);
    }
    
    if(current_number_of_averaging_loop > number_of_averaging_loop) {
      current_number_of_averaging_loop = 0;
      
      current = ((avg/(i * number_of_averaging_loop)) * division_factor )+22.71;
      avg = 0;
    
        if (current > current_limit) {
          coast(coastingTime);
          detachInterrupt(digitalPinToInterrupt(encoderA));
        }
    }

    

}

void checkDirection(){
  if(digitalRead(encoderB) ==  HIGH){                             
    direction = 1;  
  }
  else{
    direction = -1;
  }
}

void pulseA(){  
  checkDirection();
  currentSense();
  countA += direction;
}

void coast(int time) {
  analogWrite(IN1, 0);
  analogWrite(IN2, 0);
  delay(time);
  direction = 0;
}