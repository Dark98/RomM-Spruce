import os
from typing import Optional

import platform_maps
from models import Rom


class Filesystem:
    _instance: Optional["Filesystem"] = None

    # Storage paths for ROMs
    _sd1_roms_storage_path: str
    _sd2_roms_storage_path: str | None

    # Resources path: Use current working directory + "resources"
    resources_path = os.path.join(os.getcwd(), "resources")

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Filesystem, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Optionally ensure resources directory exists (not required for roms dir)
        if not os.path.exists(self.resources_path):
            os.makedirs(self.resources_path, exist_ok=True)

        # ROMs storage path
        self._sd1_roms_storage_path = "/mnt/SDCARD/Roms"
        self._sd2_roms_storage_path = None

        # Ensure the ROMs storage path exists
        if self._sd2_roms_storage_path and not os.path.exists(
            self._sd2_roms_storage_path
        ):
            os.mkdir(self._sd2_roms_storage_path)

        # Set the default SD card based on the existence of the storage path
        self._current_sd = int(
            os.getenv(
                "DEFAULT_SD_CARD",
                1 if os.path.exists(self._sd1_roms_storage_path) else 2,
            )
        )

    ###
    # PRIVATE METHODS
    ###
    def _get_sd1_roms_storage_path(self) -> str:
        """Return the base ROMs storage path."""
        return self._sd1_roms_storage_path

    def _get_sd2_roms_storage_path(self) -> Optional[str]:
        """Return the secondary ROMs storage path if available."""
        return self._sd2_roms_storage_path

    def _get_platform_storage_dir_from_mapping(self, platform: str) -> str:
        """Return the platform-specific storage path."""
        platform_dir = platform_maps.SUPPORTED_PLATFORMS_FS_MAP.get(platform)
        if platform_dir is None:
            raise ValueError(f"[RomM] Unsupported platform slug '{platform}' — please add it to SUPPORTED_PLATFORMS_FS_MAP")
        return platform_dir



    def _get_sd1_platforms_storage_path(self, platform: str) -> str:
        platforms_dir = self._get_platform_storage_dir_from_mapping(platform)
        return os.path.join(self._sd1_roms_storage_path, platforms_dir)

    def _get_sd2_platforms_storage_path(self, platform: str) -> Optional[str]:
        if self._sd2_roms_storage_path:
            platforms_dir = self._get_platform_storage_dir_from_mapping(platform)
            return os.path.join(self._sd2_roms_storage_path, platforms_dir)
        return None

    ###
    # PUBLIC METHODS
    ###

    def switch_sd_storage(self) -> None:
        """Switch the current SD storage path."""
        if self._current_sd == 1:
            self._current_sd = 2
        else:
            self._current_sd = 1

    def get_roms_storage_path(self) -> str:
        """Return the current SD storage path."""
        if self._current_sd == 2 and self._sd2_roms_storage_path:
            return self._sd2_roms_storage_path

        return self._sd1_roms_storage_path

    def get_platforms_storage_path(self, platform: str) -> str:
        """Return the storage path for a specific platform."""
        if self._current_sd == 2:
            storage_path = self._get_sd2_platforms_storage_path(platform)
            if storage_path:
                return storage_path

        return self._get_sd1_platforms_storage_path(platform)

    def is_rom_in_device(self, rom: Rom) -> bool:
        """Check if a ROM exists in the storage path."""
        rom_path = os.path.join(
            self.get_platforms_storage_path(rom.platform_slug),
            rom.fs_name if not rom.multi else f"{rom.fs_name}.m3u",
        )
        return os.path.exists(rom_path)
