#!/usr/bin/python
# GoogleMapDownloader.py
# Created by Hayden Eskriett [http://eskriett.com]
# Edited by Abdurrahman Aydın   @aoaydin
#
# A script which, when given a longitude, latitude, zoom level, map layer, and image filename, downloads a
# high-resolution Google Map

from PIL import Image
import math
import shutil
import requests
import os

class GoogleMapsLayers:
    ROADMAP = "v"
    TERRAIN = "p"
    ALTERED_ROADMAP = "r"
    SATELLITE = "s"
    TERRAIN_ONLY = "t"
    HYBRID = "y"


class GoogleMapDownloader:
    """
    A class which generates high-resolution Google Maps images given
    a latitude, longitude, zoom level, and map layer
    """

    def __init__(self, lat, lng, zoom=12, layer=GoogleMapsLayers.ROADMAP):
        """
        GoogleMapDownloader Constructor
        Args:
            lat:    The latitude of the location required
            lng:    The longitude of the location required
            zoom:   The zoom level of the location required, ranging from 3 to 21
                    defaults to 12
            layer:  The map layer type, defaults to GoogleMapsLayers.ROADMAP
        """
        self._lat = lat
        self._lng = lng
        self._zoom = zoom
        self._layer = layer

    def getXY(self):
        """
        Generates an X, Y tile coordinate based on the latitude, longitude,
        and zoom level
        Returns:
            An X, Y tile coordinate
        """

        tile_size = 256

        # Use a left shift to get the power of 2
        # i.e., a zoom level of 2 will have 2^2 = 4 tiles
        numTiles = 1 << self._zoom

        # Find the x_point given the longitude
        point_x = (tile_size / 2 + self._lng * tile_size / 360.0) * numTiles // tile_size

        # Convert the latitude to radians and take the sine
        sin_y = math.sin(self._lat * (math.pi / 180.0))

        # Calculate the y coordinate
        point_y = (
            (tile_size / 2) + 0.5 * math.log((1 + sin_y) / (1 - sin_y)) * -(tile_size / (2 * math.pi))
        ) * numTiles // tile_size

        return int(point_x), int(point_y)

    def generateImage(self, **kwargs):
        """
        Generates an image by stitching a number of Google Map tiles together.
        Args:
            start_x:        The top-left x-tile coordinate
            start_y:        The top-left y-tile coordinate
            tile_width:     The number of tiles wide the image should be -
                            defaults to 5
            tile_height:    The number of tiles high the image should be -
                            defaults to 5
        Returns:
            A high-resolution Google Map image.
        """

        start_x = kwargs.get('start_x', None)
        start_y = kwargs.get('start_y', None)
        tile_width = kwargs.get('tile_width', 8)
        tile_height = kwargs.get('tile_height', 8)

        # Check if x and y
        if start_x is None or start_y is None:
            start_x, start_y = self.getXY()

        # Determine the size of the image
        width, height = 256 * tile_width, 256 * tile_height

        # Create a new image of the required size
        map_img = Image.new('RGB', (width, height))

        for x in range(-tile_width // 2, tile_width // 2):
            for y in range(-tile_height // 2, tile_height // 2):
                url = f'https://mt0.google.com/vt?lyrs={self._layer}&x=' + str(start_x + x) + \
                      '&y=' + str(start_y + y) + '&z=' + str(self._zoom)
                current_tile = str(x) + '-' + str(y)
                response = requests.get(url, stream=True)
                with open(current_tile, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                im = Image.open(current_tile)
                map_img.paste(im, ((x + tile_width // 2) * 256, (y + tile_height // 2) * 256))
                os.remove(current_tile)

        print('Image size (pixels):', map_img.size)
        return map_img


def main():
    # Get user input for latitude, longitude, zoom level, map layer, and image filename
    lat = float(input("Enter latitude: "))
    lng = float(input("Enter longitude: "))
    zoom = int(input("Enter zoom level (0-23): "))
    layer = input("Enter map layer (e.g., 'r' for altered roadmap): ")
    filename = input("Enter image filename (e.g., high_resolution_image.png): ")

    # Create a new instance of GoogleMapDownloader
    gmd = GoogleMapDownloader(lat, lng, zoom, layer)

    print("The tile coordinates are:", gmd.getXY())

    try:
        # Get the high-resolution image
        img = gmd.generateImage()
    except IOError:
        print("Could not generate the image - try adjusting the zoom level and checking your coordinates")
    else:
        # Save the image to disk
        img.save(filename+".png")
        print("The map has been successfully created and saved as", filename)


if __name__ == '__main__':
    main()
