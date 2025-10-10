from typing import Iterable, cast
import weakref

from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from ..text import XivString
from ..imaging import ImageFile, ImageConverter

from PIL import Image, ImageChops

from pysaintcoinach import imaging


@xivrow
class Map(XivRow):
    """
    Class representing a map.
    """

    __medium_image = None  # type: weakref.ReferenceType
    __small_image = None  # type: weakref.ReferenceType
    __aetheryte_image = None
    __aetherytes = None

    @property
    def index(self) -> int:
        return self.as_int32("MapIndex")

    @property
    def id(self) -> XivString:
        """
        Gets the identifier string of the current map.
        :return: The identifier string of the current map.
        """
        return self.as_string("Id")

    @property
    def aetherytes(self) -> Iterable["MapMarker"]:
        if self.__aetherytes is not None:
            return self.__aetherytes
        self.__aetherytes = list(
            filter(
                lambda x: x.parent_row.key == self.map_marker_range
                and x["DataType"] == 3,
                self.sheet.collection.get_sheet("MapMarker"),
            )
        )
        return self.__aetherytes

    @property
    def hierarchy(self) -> int:
        """
        Gets the hierarchy level of the current map.
        :return: The hierarchy level of the current map.
        """
        return self.as_int32("Hierarchy")

    @property
    def map_marker_range(self) -> int:
        """
        Gets the MapMarker parent key range of the current map.
        :return: The MapMarker parent key range of the current map.
        """
        return self.as_int32("MapMarkerRange")

    @property
    def size_factor(self) -> int:
        """
        Gets the size factor of the current map.

        Base map size 41 units, the value of SizeFactor indicates by how much
        to divide this to get the size of the current map.
        :return: The size of the current map.
        """
        return self.as_int32("SizeFactor")

    @property
    def offset_x(self) -> int:
        """
        Gets the X value offset of the current map.
        """
        return self.as_int32("OffsetX")

    @property
    def offset_y(self) -> int:
        """
        Gets the Y value offset of the current map.
        """
        return self.as_int32("OffsetY")

    @property
    def region_place_name(self) -> "PlaceName":
        from .placename import PlaceName

        return self.as_T(PlaceName, "PlaceNameRegion")

    @property
    def place_name(self) -> "PlaceName":
        from .placename import PlaceName

        return self.as_T(PlaceName)

    @property
    def location_place_name(self) -> "PlaceName":
        from .placename import PlaceName

        return self.as_T(PlaceName, "PlaceNameSub")

    @property
    def territory_type(self) -> "TerritoryType":
        from .territory_type import TerritoryType

        return self.as_T(TerritoryType)

    @property
    def aetheryte_image(self) -> Image.Image:
        image = self.__aetheryte_image if self.__aetheryte_image is not None else None
        if image is not None:
            return image
        IMAGE_SCALE_FACTOR = 3  # Scale for aetheryte images
        m = self.medium_image.copy()
        for a in self.aetherytes:
            ae_icon = cast(imaging.ImageFile, a.as_image("Icon")).get_image().copy()
            ae_enlarged = ae_icon.resize(
                (
                    ae_icon.size[0] * IMAGE_SCALE_FACTOR,
                    ae_icon.size[1] * IMAGE_SCALE_FACTOR,
                )
            )
            m.paste(
                ae_enlarged,
                box=(
                    int(a.as_int32("X") - ae_enlarged.size[0] / 2),
                    int(a.as_int32("Y") - ae_enlarged.size[1] / 2),
                ),
                mask=ae_enlarged,
            )
        self.__aetheryte_image = m
        return m

    @property
    def medium_image(self) -> Image.Image:
        image = self.__medium_image() if self.__medium_image is not None else None
        if image is not None:
            return image
        image = self.__build_image("m")
        self.__medium_image = weakref.ref(image)
        return image

    @property
    def small_image(self) -> Image.Image:
        image = self.__small_image() if self.__small_image is not None else None
        if image is not None:
            return image
        image = self.__build_image("m")
        image.resize((1024, 1024), Image.Resampling.BICUBIC)
        self.__small_image = weakref.ref(image)
        return image

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(Map, self).__init__(sheet, source_row)

    def __build_image(self, size: str) -> Image.Image:
        MAP_FILE_FORMAT = "ui/map/{0}/{1}{2}_{3}.tex"

        if self.id is None or str(self.id) == "":
            return None

        file_name = str(self.id).replace("/", "")
        pack = self.sheet.collection.pack_collection

        file_path = MAP_FILE_FORMAT.format(str(self.id), file_name, "", size)
        file = pack.get_file(file_path)
        if file is None:
            return None

        image_file = ImageFile(file.pack, file.common_header)

        mask_path = MAP_FILE_FORMAT.format(str(self.id), file_name, "m", size)
        mask = pack.get_file(mask_path)
        if mask is not None:
            mask_file = ImageFile(mask.pack, mask.common_header)
            return self.__multiply_blend(image_file, mask_file)

        return image_file.get_image()

    @staticmethod
    def __multiply_blend(image: ImageFile, mask: ImageFile) -> Image.Image:
        if image.width != mask.width or image.height != mask.height:
            raise ValueError

        a_argb = ImageConverter.convert(image)
        b_argb = ImageConverter.convert(mask)

        return ImageChops.multiply(a_argb, b_argb)

    def to_map_coordinate_2d(self, value: int, offset: int) -> float:
        c = self.size_factor / 100.0
        offset_value = value + offset
        return (41.0 / c) * (offset_value / 2048.0) + 1

    def to_map_coordinate_3d(self, value: float, offset: int) -> float:
        c = self.size_factor / 100.0
        offset_value = (value + offset) * c
        return ((41.0 / c) * ((offset_value + 1024.0) / 2048.0)) + 1

    def __str__(self):
        return str(self.id)
