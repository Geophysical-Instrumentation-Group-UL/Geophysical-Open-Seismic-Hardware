#include <Arduino.h>
#include <unity.h>
#include <ad7768.h> 

// void setUp(void) {
// // set stuff up here
// }

// void tearDown(void) {
// // clean stuff up here
// }

uint8_t i = 0;
uint8_t max_blinks = 5;


void test_set_power_mode(void) {
    int chipSelectPin = 10;
ad7768_chip teste = {
		/* Configuration */
		.chipSelectPin = chipSelectPin,
		.power_mode = AD7768_ECO,
		.mclk_div = AD7768_MCLK_DIV_32,
		.dclk_div = AD7768_DCLK_DIV_8,
		.dec_rate = AD7768_DEC_X1024,
		.filt_type = AD7768_FILTER_SINC,

	};
    uint16_t buf;
    teste.power_mode = AD7768_FAST;
    set_power_mode(teste);
    buf = read_spi(teste,AD7768_REG_PWR_MODE);
    TEST_ASSERT_EQUAL(0x8460, buf);
}

void test_led_state_high(void) {
    digitalWrite(LED_BUILTIN, HIGH);
    TEST_ASSERT_EQUAL(HIGH, digitalRead(LED_BUILTIN));
}

void test_led_state_low(void) {
    digitalWrite(LED_BUILTIN, LOW);
    TEST_ASSERT_EQUAL(LOW, digitalRead(LED_BUILTIN));
}

void setup() {
    // NOTE!!! Wait for >2 secs
    // if board doesn't support software reset via Serial.DTR/RTS
    delay(2000);

    UNITY_BEGIN();    // IMPORTANT LINE!
    

    pinMode(LED_BUILTIN, OUTPUT);
}



void loop() {
    // if (i < max_blinks)
    // {
    //     RUN_TEST(test_led_state_high);
    //     delay(500);
    //     RUN_TEST(test_led_state_low);
    //     delay(500);
    //     i++;
    // }
    // else if (i == max_blinks) {
    RUN_TEST(test_set_power_mode);
      UNITY_END(); // stop unit testing

}