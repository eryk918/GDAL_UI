import os
import shutil
import sys
from optparse import OptionParser

from PyQt5.QtWidgets import QApplication

from utils import create_progress_bar

if os.path.exists(os.path.join(os.path.dirname(sys.executable), 'Scripts')):
    sys.path.append(os.path.join(os.path.dirname(sys.executable), 'Scripts'))
import gdal2tiles


class SimpleGdal2Tiles:
    def execute_gdal2tiles(self, input_file, output_file,
                           options_dict) -> bool:
        progress = create_progress_bar()
        progress.show()
        QApplication.processEvents()
        options = OptionParser()
        options.defaults = options_dict
        ret_code = self.single_threaded_tiling(
            input_file,
            output_file,
            options.get_default_values()
        )
        progress.close()
        return ret_code

    def single_threaded_tiling(self, input_file: str, output_folder: str,
                               options: OptionParser) -> bool:
        if options.verbose:
            print("Begin tiles details calc")
        conf, tile_details = gdal2tiles.worker_tile_details(
            input_file, output_folder, options)

        if not conf or not tile_details:
            return True

        if options.verbose:
            print("Tiles details calc complete.")

        if not options.verbose and not options.quiet:
            progress_bar = gdal2tiles.ProgressBar(len(tile_details))
            progress_bar.start()

        for tile_detail in tile_details:
            gdal2tiles.create_base_tile(conf, tile_detail)

            if not options.verbose and not options.quiet:
                progress_bar.log_progress()

        if getattr(gdal2tiles.threadLocal, 'cached_ds', None):
            del gdal2tiles.threadLocal.cached_ds

        gdal2tiles.create_overview_tiles(conf, output_folder, options)

        shutil.rmtree(os.path.dirname(conf.src_file))
        return False
