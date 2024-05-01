from osgeo import gdal

def create_tiles(input_file, tile_width, tile_height):
    ds = gdal.Open(input_file)
    band = ds.GetRasterBand(1)
    xsize = band.XSize
    ysize = band.YSize
    
    for i in range(0, xsize, tile_width):
        for j in range(0, ysize, tile_height):
            ulx = ds.GetGeoTransform()[0] + i * ds.GetGeoTransform()[1]
            uly = ds.GetGeoTransform()[3] + j * ds.GetGeoTransform()[5]
            lrx = ulx + tile_width * ds.GetGeoTransform()[1]
            lry = uly + tile_height * ds.GetGeoTransform()[5]
            output_filename = f"tile_{i}_{j}.tif"
            gdal.Translate(output_filename, ds, format='GTiff', projWin=[ulx, uly, lrx, lry])
            print(f"Created {output_filename}")

create_tiles(r"C:\Users\USER\AppData\Local\Temp\tmp36jdqt1p.tif", 1024, 1024)  # Example: tile size 1024x1024 pixels
