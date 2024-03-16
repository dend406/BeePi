import RPi.GPIO as GPIO
import dht11
import time
import datetime
import BlynkLib
from hx711 import HX711

# Ініціалізація GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Ініціалізація піну для звуку та датчика DHT11
sound = 16
instance = dht11.DHT11(pin=12)
GPIO.setup(sound, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Ініціалізація вагового датчика HX711
hx = HX711(dout_pin=25, pd_sck_pin=24)

# Функція зворотного виклику для обробки подій звуку
def callback(channel):
    if GPIO.input(sound):
        print("Sound Detected!")
    else:
        print("Sound Detected!")
# Додавання обробника подій для звуку
GPIO.add_event_detect(sound, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(sound, callback)

# Ініціалізація Blynk
blynk = BlynkLib.Blynk('lHbvlZnxALJUzrrp_JMCyolPPnf6Wv03')

# Функція для відображення ваги в додатку Blynk
@blynk.VIRTUAL_READ(0)
def my_weight():
    blynk.virtual_write(0, int((hx.get_raw_data_mean() - 537995) / 119))

# Функція для відображення температури в додатку Blynk
@blynk.VIRTUAL_READ(1)
def my_temperature():
    while True:
        result = instance.read()
        if result.is_valid():
            blynk.virtual_write(1, result.temperature)
        return ()

# Функція для відображення вологості в додатку Blynk
@blynk.VIRTUAL_READ(2)
def my_humidity():
    while True:
        result = instance.read()
        if result.is_valid():
            blynk.virtual_write(2, result.humidity)
        return ()

# Функція для відображення звуку в додатку Blynk
@blynk.VIRTUAL_READ(3)
def my_sound():
    blynk.virtual_write(0, GPIO.add_event_callback)

try:
    while True:
        result = instance.read()
        weight = (hx.get_raw_data_mean() - 537995) / 119
        blynk.run()
        my_weight()
        my_temperature()
        my_humidity()

        if result.is_valid():
            print("Last valid input: " + str(datetime.datetime.now()))
            print("Temperature: %-3.1f C" % result.temperature)
            print("Humidity: %-3.1f %%" % result.humidity)
            print("Weight: %-3.1f g" % weight)

        time.sleep(3)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()
