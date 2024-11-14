"""The Backup integration."""

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.hassio import is_hassio
from homeassistant.helpers.typing import ConfigType

from .agent import BackupAgent, UploadedBackup
from .const import DOMAIN, LOGGER
from .http import async_register_http_views
from .manager import BackupManager
from .models import BackupUploadMetadata
from .websocket import async_register_websocket_handlers

__all__ = [
    "BackupAgent",
    "BackupUploadMetadata",
    "UploadedBackup",
]

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Backup integration."""
    hass.data[DOMAIN] = backup_manager = BackupManager(hass)

    with_hassio = is_hassio(hass)

    async_register_websocket_handlers(hass, with_hassio)

    if with_hassio:
        if DOMAIN in config:
            LOGGER.error(
                "The backup integration is not supported on this installation method, "
                "please remove it from your configuration"
            )
        return True

    async def async_handle_create_service(call: ServiceCall) -> None:
        """Service handler for creating backups."""
        await backup_manager.async_create_backup(
            addons_included=None,
            database_included=True,
            folders_included=None,
            name=None,
            on_progress=None,
        )
        if backup_task := backup_manager.backup_task:
            await backup_task

    hass.services.async_register(DOMAIN, "create", async_handle_create_service)

    async_register_http_views(hass)

    return True
