idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES esp_adc driver esp_wifi nvs_flash esp_event esp_netif lwip)

