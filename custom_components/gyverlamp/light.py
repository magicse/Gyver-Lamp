import logging
import socket

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    LightEntityFeature,
    PLATFORM_SCHEMA,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
#from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import DeviceInfo

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_EFFECTS = "effects"

EFFECTS = [
	"Nexus",
	"Акварель",
	"Басейн",
	"Біле світло",
	"Веселка",
	"Веселка 3D",
	"Вино",
	"Вихори полум'я",
	"Вихори різнокольорові",
	"Вогонь",
	"Вогонь 2012",
	"Вогонь 2018",
	"Вогонь 2020",
	"Вогонь 2021",
	"Вогонь верховий",
	"Вогонь що літає",
	"Водоспад",
	"Водоспад 4 в 1",
	"Годинник",
	"Гроза в банці",
	"Джерело",
	"Дим",
	"Дим різнокольоровий",
	"Димові шашки",
	"ДНК",
	"Завиток",
	"Завірюха",
	"Зграя",
	"Зграя та хижак",
	"Зебра",
	"Змійка",
	"Зміна кольору",
	"Квітка лотоса",
	"Кипіння",
	"Кодовий замок",
	"Колір",
	"Кольорові драже",
	"Кольорові кучері",
	"Комета",
	"Комета однокольорова",
	"Комета подвійна",
	"Комета потрійна",
	"Контакти",
	"Конфетті",
	"Краплі на склі",
	"Кубик Рубика",
	"Кулі",
	"Лава",
	"Лавова лампа",
	"Лампа з метеликами",
	"Ліс",
	"Люменьєр",
	"М'ячики",
	"М'ячики без кордонів",
	"Магма",
	"Матриця",
	"Мерехтіння",
	"Метаболз",
	"Метелики",
	"Мозайка",
	"Мрія дизайнера",
	"Новорічна ялинка",
	"Океан",
	"Олійні фарби",
	"Опади",
	"Осцилятор",
	"Павич",
	"Пейнтбол",
	"Північне сяйво",
	"Пікассо",
	"Пісочний годинник",
	"Плазма",
	"Плазмова лампа",
	"Побічний ефект",
	"Полум'я",
	"Попкорн",
	"Призмата",
	"Притягнення",
	"Пульс",
	"Пульс білий",
	"Пульс райдужний",
	"Радіальна хвиля",
	"Райдужний змій",
	"Рідка лампа",
	"Рідка лампа авто",
	"Різнобарвний дощ",
	"Річки Ботсвани",
	"Рядок що біжить",
	"Світлячки",
	"Світлячки зі шлейфом",
	"Свічка",
	"Синусоїд",
	"Снігопад",
	"Спектрум",
	"Спірали",
	"Стрибуни",
	"Строб.Хаос.Дифузія",
	"Тихий океан",
	"Тіні",
	"Україна",
	"Феєрверк",
	"Феєрверк 2",
	"Фея",
	"Хвилі",
	"Хмари",
	"Хмарка в банці",
	"Шаленство",
]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_EFFECTS): cv.ensure_list,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([GyverLamp(config)], True)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    entity = GyverLamp(entry.options, entry.entry_id)
    async_add_entities([entity], True)

    hass.data[DOMAIN][entry.entry_id] = entity


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data[DOMAIN].pop(entry.entry_id)
    return True


class GyverLamp(LightEntity):
    def __init__(self, config: dict, unique_id=None):
        self._attr_effect_list = config.get(CONF_EFFECTS, EFFECTS)
        self._attr_name = config.get(CONF_NAME, "Gyver Lamp")
        self._attr_should_poll = True
        self._attr_supported_color_modes = {ColorMode.HS}
        self._attr_supported_features = LightEntityFeature.EFFECT
        self._attr_unique_id = unique_id
        self._attr_color_mode = ColorMode.HS  # Default color mode

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="@AlexGyver",
            model="GyverLamp",
        )

        self.host = config[CONF_HOST]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)

    @property
    def address(self) -> tuple:
        return self.host, 8888

    @property
    def color_mode(self):
        """Return the current color mode."""
        return self._attr_color_mode

    def debug(self, message):
        _LOGGER.debug(f"{self.host} | {message}")

    def turn_on(
        self,
        brightness: int = None,
        effect: str = None,
        hs_color: tuple = None,
        **kwargs,
    ):
        payload = []
        if brightness:
            payload.append("BRI%d" % brightness)

        if effect:
            try:
                payload.append("EFF%d" % self._attr_effect_list.index(effect))
            except ValueError:
                payload.append(effect)

        if hs_color:
            scale = round(hs_color[0] / 360.0 * 100.0)
            payload.append("SCA%d" % scale)
            speed = hs_color[1] / 100.0 * 255.0
            payload.append("SPD%d" % speed)
            self._attr_color_mode = ColorMode.HS  # Set the color mode to HS

        if not self._attr_is_on:
            payload.append("P_ON")

        self.debug(f"SEND {payload}")

        for data in payload:
            self.sock.sendto(data.encode(), self.address)
            resp = self.sock.recv(1024)
            self.debug(f"RESP {resp}")

    def turn_off(self, **kwargs):
        self.sock.sendto(b"P_OFF", self.address)
        resp = self.sock.recv(1024)
        self.debug(f"RESP {resp}")

    def update(self):
        try:
            self.sock.sendto(b"GET", self.address)
            data = self.sock.recv(1024).decode().split(" ")
            self.debug(f"UPDATE {data}")
            # bri eff spd sca pow
            i = int(data[1])
            self._attr_effect = (
                self._attr_effect_list[i] if i < len(self._attr_effect_list) else None
            )
            self._attr_brightness = int(data[2])
            self._attr_hs_color = (
                float(data[4]) / 100.0 * 360.0,
                float(data[3]) / 255.0 * 100.0,
            )
            self._attr_is_on = data[5] == "1"
            self._attr_available = True
            self._attr_color_mode = ColorMode.HS  # Ensure color mode is set

        except Exception as e:
            self.debug(f"Can't update: {e}")
            self._attr_available = False

