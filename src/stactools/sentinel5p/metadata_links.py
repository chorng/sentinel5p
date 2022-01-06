import json
import os
from hashlib import md5  # type: ignore

import netCDF4 as nc  # type: ignore
import pystac

from .constants import SAFE_MANIFEST_ASSET_KEY


class ManifestError(Exception):
    pass


class MetadataLinks:

    def __init__(self, file_path: str):
        self.file_path = file_path
        if file_path.endswith(".nc"):
            self._root = nc.Dataset(file_path)
        elif file_path.endswith(".json"):
            self._root = json.load(open(file_path))
        else:
            raise ManifestError(
                f"Source file format is not supported: .{file_path.split('.')[-1]}"
            )

    def create_manifest_asset(self):
        if self.file_path.endswith(".nc"):
            asset = pystac.Asset(
                href=self.file_path,
                media_type="application/x-netcdf",
                roles=["metadata"],
            )
        else:
            asset = pystac.Asset(
                href=self.file_path,
                media_type=pystac.MediaType.JSON,
                roles=["metadata"],
            )
        return SAFE_MANIFEST_ASSET_KEY, asset

    def create_band_asset(self):
        asset_id = self.file_path.split("/")[-1].split(".")[0]
        asset_key = "data"
        media_type = "application/x-netcdf"
        roles = ["data"]
        if self.file_path.endswith(".nc"):
            data_href = self.file_path
            description = self._root.title
            asset_size = os.path.getsize(self.file_path)
            with open(self.file_path, 'rb') as f:
                asset_checksum = md5(f.read()).hexdigest()
            extra_fields = {
                "file:checksum": asset_checksum,
                "file:size": asset_size,
                "file:local_path": f"{asset_id}/{asset_id}.nc"
            }

        else:
            data_href = self.file_path.replace(".json", ".nc")
            description = self._root["title"]
            extra_fields = {}

        asset = pystac.Asset(href=data_href,
                             media_type=media_type,
                             description=description,
                             roles=roles,
                             extra_fields=extra_fields)
        return asset_key, asset
