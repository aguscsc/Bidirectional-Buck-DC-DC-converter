// ADC math corrections.
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
// handles the immediate reading mode
#include "esp_adc/adc_oneshot.h"
// handles the wifi events
#include "esp_event.h"
#include "esp_wifi.h"
// for printing
#include "esp_log.h"
// to pause processes
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"
// UNIX sockets
#include "lwip/sockets.h"
// saves the wifi calibratio data in flash memory
#include "nvs_flash.h"
// system on chips capabilities for curve and line fitting
#include "soc/soc_caps.h"
#include <string.h>

const static char *TAG = "WIFI_SENSOR";

// --- USER CONFIGURATION ---
#define WIFI_SSID "Agus"
#define WIFI_PASS "28062125"
#define PC_IP_ADDR "10.130.219.29" // <--- PC's IP
#define PORT 3333                  // <--- Port used

// ADC Config
#define ADC_BUCK ADC_CHANNEL_6  // GPIO 34
#define ADC_BOOST ADC_CHANNEL_7 // GPIO 35
#define BUCK_RATIO 5.1279f
#define BOOST_RATIO 11.5184f

// --- Wi-Fi Boilerplate globals ---
static EventGroupHandle_t
    s_wifi_event_group; // takes values depending on the state of the
                        // connection, points to a dashboard with events
#define WIFI_CONNECTED_BIT                                                     \
  BIT0 // binary signal to read the event thats taking place

// Declare global function to use later
static bool adc_calibration_init(adc_unit_t unit, adc_channel_t channel,
                                 adc_atten_t atten,
                                 adc_cali_handle_t *out_handle);
void wifi_init_sta(void);

// --- MAIN APPLICATION ---
void app_main(void) {
  // Initialize NVS (non-voltaile storage) (Required for Wi-Fi)
  esp_err_t ret = nvs_flash_init(); // Initialize memory
  // checks if there's space, if not, it wipes the junk and tries again
  if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
      ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
  }
  ESP_ERROR_CHECK(ret); // checks for corruption

  // Start Wi-Fi
  ESP_LOGI(TAG, "Starting Wi-Fi...");
  wifi_init_sta();

  // Setup UDP Socket
  int sock = socket(AF_INET, SOCK_DGRAM,
                    IPPROTO_UDP); // addr family, datagram, protocol
  // structure
  struct sockaddr_in dest_addr;
  dest_addr.sin_addr.s_addr = inet_addr(PC_IP_ADDR);
  dest_addr.sin_family = AF_INET;
  dest_addr.sin_port = htons(PORT);

  // Setup ADC
  adc_oneshot_unit_handle_t
      adc1_handle; // declares pointer to heap with adc rules
  adc_oneshot_unit_init_cfg_t init_config = {
      .unit_id = ADC_UNIT_1}; // sets the adc unit to use
  ESP_ERROR_CHECK(
      adc_oneshot_new_unit(&init_config, &adc1_handle)); // check for errors

  adc_oneshot_chan_cfg_t config = {
      .bitwidth = ADC_BITWIDTH_DEFAULT,
      .atten = ADC_ATTEN_DB_12}; // 12 bit, atten = 3, max ~2.45 V with and
                                 // errror up to 60mV
  // config GPIO 35 & 34
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, ADC_BUCK, &config));
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, ADC_BOOST, &config));

  // hanles for calibration
  adc_cali_handle_t cali_handle_buck = NULL;
  adc_cali_handle_t cali_handle_boost = NULL;
  bool do_calib_buck = adc_calibration_init(ADC_UNIT_1, ADC_BUCK,
                                            ADC_ATTEN_DB_12, &cali_handle_buck);
  bool do_calib_boost = adc_calibration_init(
      ADC_UNIT_1, ADC_BOOST, ADC_ATTEN_DB_12, &cali_handle_boost);

  // MAIN LOOP
  while (1) {
    // --- READ SENSORS ---
    uint32_t sum_buck = 0, sum_boost = 0;
    int raw_buck = 0, raw_boost = 0;
    // number of samples
    int samples = 64;

    for (int i = 0; i < samples; i++) {
      // read raw value and store the total sum
      ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, ADC_BUCK, &raw_buck));
      sum_buck += raw_buck;
      ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, ADC_BOOST, &raw_boost));
      sum_boost += raw_boost;
    }

    // calculate the avg
    int avg_buck = sum_buck / samples;
    int avg_boost = sum_boost / samples;
    int mv_buck = 0, mv_boost = 0;

    // scale results to real values
    if (do_calib_buck)
      adc_cali_raw_to_voltage(cali_handle_buck, avg_buck, &mv_buck);
    else
      mv_buck = avg_buck * 2450 / 4095;

    if (do_calib_boost)
      adc_cali_raw_to_voltage(cali_handle_boost, avg_boost, &mv_boost);
    else
      mv_boost = avg_boost * 2450 / 4095;

    float v_buck = (mv_buck * BUCK_RATIO) / 1000.0f;
    float v_boost = (mv_boost * BOOST_RATIO) / 1000.0f;

    // --- SEND VIA WI-FI ---
    // Format the string "Buck: 12.50, Boost: 24.00"
    char payload[64];
    snprintf(payload, sizeof(payload), "Buck: %.2f V, Boost: %.2f V\n", v_buck,
             v_boost);

    // Send the packet
    int err =
        sendto(sock, payload, strlen(payload), 0, (struct sockaddr *)&dest_addr,
               sizeof(dest_addr)); // socket, buffer, lenght, udp, ip and port
    if (err < 0) {
      ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
    } else {
      ESP_LOGI(TAG, "Sent: %s", payload);
    }

    vTaskDelay(pdMS_TO_TICKS(500));
  }
}

// --- WI-FI HELPERS  ---
static void event_handler(void *arg, esp_event_base_t event_base,
                          int32_t event_id, void *event_data) {
  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
    esp_wifi_connect();
  } else if (event_base == WIFI_EVENT &&
             event_id == WIFI_EVENT_STA_DISCONNECTED) {
    esp_wifi_connect(); // Auto-reconnect
    ESP_LOGI(TAG, "Retrying to connect...");
  } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
    ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
    ESP_LOGI(TAG, "Got IP:" IPSTR, IP2STR(&event->ip_info.ip));
    xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
  }
}

void wifi_init_sta(void) {
  // creates a global dashboard for wifi vetns
  s_wifi_event_group = xEventGroupCreate();
  // initialize lightweight ip to handle traffic
  ESP_ERROR_CHECK(esp_netif_init());
  // handles wifi notifications to the code
  ESP_ERROR_CHECK(esp_event_loop_create_default());
  // creates a virtual network interface, station
  esp_netif_create_default_wifi_sta();

  // wifi config
  wifi_init_config_t cfg =
      WIFI_INIT_CONFIG_DEFAULT(); // initialize deafult wifi config
  // check the config for errors
  ESP_ERROR_CHECK(esp_wifi_init(&cfg));

  // create handler for any id and ip instances
  esp_event_handler_instance_t instance_any_id;
  esp_event_handler_instance_t instance_got_ip;
  ESP_ERROR_CHECK(esp_event_handler_instance_register(
      WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, &instance_any_id));
  ESP_ERROR_CHECK(esp_event_handler_instance_register(
      IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, &instance_got_ip));

  // wifi object
  wifi_config_t wifi_config = {
      .sta =
          {
              .ssid = WIFI_SSID,
              .password = WIFI_PASS,
          },
  };
  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
  ESP_ERROR_CHECK(esp_wifi_start());

  // Block until we are connected
  ESP_LOGI(TAG, "Waiting for Wi-Fi...");
  xEventGroupWaitBits(s_wifi_event_group, WIFI_CONNECTED_BIT, pdFALSE, pdFALSE,
                      portMAX_DELAY); // read the event until it is connected,
                                      // do not change it, use max delay
  ESP_LOGI(TAG, "Connected!");
}

// --- ADC ---
static bool adc_calibration_init(adc_unit_t unit, adc_channel_t channel,
                                 adc_atten_t atten,
                                 adc_cali_handle_t *out_handle) {
  adc_cali_handle_t handle = NULL;
  esp_err_t ret = ESP_FAIL;
  bool calibrated = false;
#if ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
  if (!calibrated) {
    adc_cali_curve_fitting_config_t cali_config = {.unit_id = unit,
                                                   .chan = channel,
                                                   .atten = atten,
                                                   .bitwidth =
                                                       ADC_BITWIDTH_DEFAULT};
    ret = adc_cali_create_scheme_curve_fitting(&cali_config, &handle);
    if (ret == ESP_OK)
      calibrated = true;
  }
#endif
#if ADC_CALI_SCHEME_LINE_FITTING_SUPPORTED
  if (!calibrated) {
    adc_cali_line_fitting_config_t cali_config = {
        .unit_id = unit, .atten = atten, .bitwidth = ADC_BITWIDTH_DEFAULT};
    ret = adc_cali_create_scheme_line_fitting(&cali_config, &handle);
    if (ret == ESP_OK)
      calibrated = true;
  }
#endif
  *out_handle = handle;
  return calibrated;
}
