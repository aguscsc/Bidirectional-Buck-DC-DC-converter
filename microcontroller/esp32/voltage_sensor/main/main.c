// contains the calibration APIs to correct the readings using factory data burned into the chip
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
// Driver for one shot mode, it allows the CPU to trigger a single conversion and wait for the result, instead of continnously reading
#include "esp_adc/adc_oneshot.h"
// allows to print output to the terminal
#include "esp_log.h"
// OS headers to call vTaskDelay 
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
//System on chip capabilities, this tells the compiler which features the specific chip has
#include "soc/soc_caps.h"
// Standard libs
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const static char *TAG = "VOLT_SENSOR";

// We need to declare this helper function so the compiler knows it exists
static bool adc_calibration_init(adc_unit_t unit, adc_channel_t channel,
                                 adc_atten_t atten,
                                 adc_cali_handle_t *out_handle);

// --- configuration ---
#define ADC_BUCK ADC_CHANNEL_6 // GPIO 34
#define ADC_BOOST ADC_CHANNEL_7 // GPIO 35

// Resistor divider ratios
#define BUCK_RATIO 5.71f
#define BOOST_RATIO 11.0f

void app_main(void) {
  // --- SETUP ADC UNIT ---
  adc_oneshot_unit_handle_t adc1_handle; //pointer that points to a configuration structure in RAM
  // adc unit to use, is has to be 1, adc 2 shares circuitry with the wifi module
  adc_oneshot_unit_init_cfg_t init_config = {
      .unit_id = ADC_UNIT_1,
  };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config, &adc1_handle)); //Erro check is a macro provided by ESP idf to report errors

  // --- CONFIGURE PINS ---
  adc_oneshot_chan_cfg_t config = {
      .bitwidth = ADC_BITWIDTH_DEFAULT, //12 bit resolution
      .atten = ADC_ATTEN_DB_12, // Allows measuring up to ~2.45V with up to 60mV of error
  };
  // Config check
  ESP_ERROR_CHECK(
      adc_oneshot_config_channel(adc1_handle, ADC_BUCK, &config)); 

  ESP_ERROR_CHECK(
      adc_oneshot_config_channel(adc1_handle, ADC_BOOST, &config)); 

  // --- SETUP CALIBRATION ---
  adc_cali_handle_t cali_handle_buck = NULL;
  adc_cali_handle_t cali_handle_boost = NULL;
  // We check if calibration was successful (returns true/false)
  bool do_calibration1 = adc_calibration_init(ADC_UNIT_1, ADC_BUCK,
                                             ADC_ATTEN_DB_12, &cali_handle_buck);
  bool do_calibration2 = adc_calibration_init(ADC_UNIT_1, ADC_BOOST,
                                             ADC_ATTEN_DB_12, &cali_handle_boost);

  // --- 4. MAIN LOOP ---
  while (1) {
    // unsigned integer to store the sum
    uint32_t adc_sum_buck = 0;
    uint32_t adc_sum_boost = 0;
    // raw value
    int raw_buck = 0;
    int raw_boost = 0;
    // number of samples taken
    int samples = 64;


    for (int i = 0; i < samples; i++){
      // Read the raw raw_value (0 to 4095)
      ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, ADC_BUCK, &raw_buck));
      adc_sum_buck += raw_buck;
      ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, ADC_BOOST, &raw_boost));
      adc_sum_boost += raw_boost;
    }

    int raw_avg_buck = adc_sum_buck / samples;
    int raw_avg_boost = adc_sum_boost / samples;
    int voltage_buck_mv = 0;
    int voltage_boost_mv = 0;

    // Convert to Voltage in mV
    if (do_calibration1 && do_calibration2) {
      ESP_ERROR_CHECK(
          adc_cali_raw_to_voltage(cali_handle_buck, raw_avg_buck, &voltage_buck_mv)); // voltage = (raw*gain) + offset 
      ESP_ERROR_CHECK(
          adc_cali_raw_to_voltage(cali_handle_boost, raw_avg_boost, &voltage_boost_mv)); // voltage = (raw*gain) + offset 
      
      ESP_LOGI(TAG, "Buck: %d mV |  Boost: %d mV", voltage_buck_mv, voltage_boost_mv);
    } else {
      // Fallback if calibration failed (rough estimate)
      ESP_LOGW(TAG, "Calibration missing! Using rough math.");
      voltage_buck_mv = raw_avg_buck * 2450 /4095;
      voltage_boost_mv = raw_avg_boost * 2450 /4095;
      ESP_LOGI(TAG, "Buck: %d mV |  Boost: %d mV", voltage_buck_mv, voltage_boost_mv);
    }

    //scaled readings
    float real_buck = (voltage_buck_mv*BUCK_RATIO)/1000.0;
    float real_boost = (voltage_boost_mv*BOOST_RATIO)/1000.0;

    ESP_LOGI(TAG, "Voltage readings: BUCK: %.2f V | BOOST: %.2f V", real_buck, real_boost);
    vTaskDelay(pdMS_TO_TICKS(500)); // Delay 1 second
  }
}

// --- HELPER FUNCTION: This handles the complicated calibration setup ---
static bool adc_calibration_init(adc_unit_t unit, adc_channel_t channel,
                                 adc_atten_t atten,
                                 adc_cali_handle_t *out_handle) {
  adc_cali_handle_t handle = NULL;
  esp_err_t ret = ESP_FAIL;
  bool calibrated = false;

  // Check for "Curve Fitting" (Newer Chips: S3, C3, etc.), y = ax^2 + bx + c
#if ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
  if (!calibrated) {
    adc_cali_curve_fitting_config_t cali_config = {
        .unit_id = unit,
        .chan = channel,
        .atten = atten,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    ret = adc_cali_create_scheme_curve_fitting(&cali_config, &handle);
    if (ret == ESP_OK) {
      calibrated = true;
    }
  }
#endif


  // Check for "Line Fitting" (Older Chips: Original ESP32), y = mx + c
#if ADC_CALI_SCHEME_LINE_FITTING_SUPPORTED
  if (!calibrated) {
    adc_cali_line_fitting_config_t cali_config = {
        .unit_id = unit,
        .atten = atten,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    ret = adc_cali_create_scheme_line_fitting(&cali_config, &handle);
    if (ret == ESP_OK) {
      calibrated = true;
    }
  }
#endif

  *out_handle = handle;
  if (ret == ESP_OK) {
    ESP_LOGI(TAG, "Calibration Success");
  } else {
    ESP_LOGW(TAG, "eFuse not burnt or invalid, skipping calibration");
  }

  return calibrated;
}
