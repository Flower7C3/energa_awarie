"""Binary sensor for active Energa outages (mapa bieżących, typ awaryjny)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_ATTRIBUTION,
    ATTR_DESCRIPTION,
    ATTR_END,
    ATTR_OUTAGES,
    ATTR_START,
    ATTRIBUTION,
    CONF_AREA,
    CONF_CITY,
    CONF_COUNTY,
    CONF_STREET,
    COUNTY_OPTIONS,
    DOMAIN,
    SHUTDOWN_TYPE,
)
from .coordinator import EnergaOutagesCoordinator
from .entity import EnergaAwarieEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up active-outage binary sensor."""
    coordinator: EnergaOutagesCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    county_id = entry.data[CONF_COUNTY]
    county_name = COUNTY_OPTIONS.get(county_id, str(county_id))
    async_add_entities(
        [
            EnergaActiveOutageBinarySensor(
                coordinator,
                entry.entry_id,
                county_id,
                county_name,
                entry.data.get(CONF_AREA, ""),
                entry.data.get(CONF_CITY, ""),
                entry.data.get(CONF_STREET, ""),
            )
        ]
    )


class EnergaActiveOutageBinarySensor(EnergaAwarieEntity, BinarySensorEntity):
    """ON gdy trwa awaria awaryjna (shutdownType 1) w skonfigurowanej lokalizacji."""

    _attr_translation_key = "active_outage"
    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_icon = "mdi:transmission-tower-off"

    def __init__(
        self,
        coordinator: EnergaOutagesCoordinator,
        entry_id: str,
        county_id: int,
        county_name: str,
        area: str,
        city: str,
        street: str,
    ) -> None:
        super().__init__(
            coordinator, entry_id, county_id, county_name, area, city, street
        )
        self._attr_unique_id = f"{self._slug}_active_outage"

    def _active_outages(self) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        current = self.coordinator.data.get("current", []) if self.coordinator.data else []
        active: list[dict[str, Any]] = []
        for outage in current:
            start = outage["start_date"]
            end = outage["end_date"]
            if start <= now <= end:
                active.append(outage)
        return active

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return bool(self._active_outages())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        active = self._active_outages()
        attrs: dict[str, Any] = {
            **self._location_attributes(),
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "active_count": len(active),
        }
        outage_list = [
            {
                "start": o["start_date"].isoformat(),
                "end": o["end_date"].isoformat(),
                "description": o.get("description", ""),
                "type": SHUTDOWN_TYPE.get(str(o.get("shutdownType", "1")), "Outage"),
            }
            for o in sorted(active, key=lambda x: x["start_date"])
        ]
        if outage_list:
            attrs[ATTR_OUTAGES] = outage_list
            first = outage_list[0]
            attrs[ATTR_START] = first["start"]
            attrs[ATTR_END] = first["end"]
            attrs[ATTR_DESCRIPTION] = first["description"]
        return attrs