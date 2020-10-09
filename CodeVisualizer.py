# Manim
from manimlib.imports import *
import argparse
import manimlib.config
import manimlib.constants
import manimlib.extract_scene


file = 'pruebas/caquitadelavaquita.py'
omit_dunder = False

RESOLUTION = 20     # [pixels / mm]

PAPER_WIDTH  = 210  # A4 [mm]
PAPER_HEIGHT = 297  # A4 [mm]

PAPER_TOP_MARGIN    = 25    # [mm]
PAPER_BOTTOM_MARGIN = 25    # [mm]
PAPER_RIGHT_MARGIN  = 30    # [mm]
PAPER_LEFT_MARGIN   = 30    # [mm]

HORIZONTAL_RESOLUTION = PAPER_WIDTH * RESOLUTION    # [pixels]
VERTICAL_RESOLUTION = PAPER_HEIGHT * RESOLUTION     # [pixels]


scene_file = 'create_diagram.py'
scene = 'FlowDiagram'
if __name__ == '__main__':
    # python -m manim main.py FlowDiagram -ps -r 2970,2100
    args = argparse.Namespace(
        file=scene_file,
        scene_names=[scene],
        preview=True,
        write_to_movie=False,
        save_last_frame=True,
        low_quality=False,
        medium_quality=False,
        high_quality=False,
        save_pngs=False,
        save_as_gif=False,
        show_file_in_finder=False,
        transparent=False,
        quiet=False,
        write_all=False,
        file_name=None,
        start_at_animation_number=None,
        resolution=f'{VERTICAL_RESOLUTION},{HORIZONTAL_RESOLUTION}',
        color=None,
        sound=False,
        leave_progress_bars=False,
        media_dir=None,
        video_dir=None,
        video_output_dir=None,
        tex_dir=None
    )
    config = manimlib.config.get_configuration(args)
    manimlib.constants.initialize_directories(config)
    manimlib.extract_scene.main(config)
