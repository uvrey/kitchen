""" Displays and handles error messages. """
# kitchen/helpers/sounds.py

from gtts import gTTS
import manim as m
import os
from pathlib import Path
import shutil

from kitchen import SOUND_ERROR, SUCCESS
from kitchen.helpers import display

(
    SOUND,
    NO_SOUND,
    NARR, 
    NO_NARR,
    CLICK,
    CLANG,
    FLASH,
    WAVE,
    TWINKLE,
    FAIL,
    CLACK,
    YAY,
    POP,
    MOVE,
    TYPE
) = range(15)

id = 0
config = NARR

def get_config():
    """Retrieves current narration configuration setting.

    Returns:
        int: Configuration setting.
    """    
    return config

def set_config(config_option: int):
    """Sets the configuration option for narration.

    Args:
        config_option (int): NARR or NO_NARR.

    Returns:
        int: Status code.
    """    
    global config
    config = config_option
    return SUCCESS

def _get_narration_path() -> str:
    """Creates a unique path for the temporary narration file.

    Returns:
        str: Narration path.
    """    
    global id
    id = id + 1
    return os.getcwd() + r'\assets\narration\narr_' + str(id) + '.mp3'

def _get_narration(script: str) -> str:
    """Generates a gTTS narration .mp3 from a script and saves the file.

    Args:
        script (str): Script for the gTTS narration.

    Returns:
        Path: Path of the narration file.
    """    
    language = 'en'
    myobj = gTTS(text=script, lang=language, slow=False)
    path = _get_narration_path() 
    myobj.save(path)
    return path

def narrate(script, scene) -> int:
    """Creates a narration given a script and Manim Scene.

    Args:
        script (str): Script to be narrated.
        scene (Scene): Manim Scene to be narrated over.

    Returns:
        int: Status code.
    """    
    if config == NARR:
        _new_narration = _get_narration(script)
        if not os.path.isfile(_new_narration):
            return SOUND_ERROR
        scene.add_sound(_new_narration)
    return SUCCESS

def init_narr_dir() -> None:
    """Initialises the narration directory.
    """    
    narration_dir = os.getcwd() + r'\assets\narration'
    try:
        Path(narration_dir).mkdir(exist_ok=True)
    except OSError:
        display.fail_secho("There was an issue creating the narration " +
            "directory.")

def clear_narrs():
    """Clears and reinitialises the narration directory.
    """    
    if get_config() == NARR:
        clear_narr_dir()
        init_narr_dir()

def clear_narr_dir():
    """Cleans the narration directory after the animation is created.
    """    
    narration_dir = os.getcwd() + r'\assets\narration'
    shutil.rmtree(Path(narration_dir))
    return

def add_sound_to_scene(scene, sound_spec):
    """Adds a sound to a scene based on some specification.

    Args:
        scene (Scene): Manim Scene object.
        sound_spec (int): Some sound type as described in __init__.py.

    Returns:
        int: Status code.
    """    
    base_path = os.getcwd() + r'\assets\sounds'

    if not os.path.isdir(base_path):
        return SOUND_ERROR

    try:
        if sound_spec == CLICK:
            scene.add_sound(os.getcwd() + r'\assets\sounds\click.wav')
        elif sound_spec == FLASH:
            pass
        elif sound_spec == TYPE:
            scene.add_sound(os.getcwd() + r'\assets\sounds\type.wav')
        elif sound_spec == CLANG:
            scene.add_sound(os.getcwd() + r'\assets\sounds\clang.wav')
        elif sound_spec == TWINKLE:
            scene.add_sound(os.getcwd() + r'\assets\sounds\twinkle.wav') 
        elif sound_spec == FAIL:
            scene.add_sound(os.getcwd() + r'\assets\sounds\fail.wav')
        elif sound_spec == CLACK:
            scene.add_sound(os.getcwd() + r'\assets\sounds\clack.wav')
        elif sound_spec == YAY:
            scene.add_sound(os.getcwd() + r'\assets\sounds\yay.wav')   
        elif sound_spec == POP:
            scene.add_sound(os.getcwd() + r'\assets\sounds\pop.wav') 
        elif sound_spec==MOVE:
            scene.add_sound(os.getcwd() + r'\assets\sounds\move.wav')
    except OSError:
        display.fail_secho("Sound [" + str(sound_spec) + "] not found -\
            please check your assets/sounds folder.")
        return SOUND_ERROR

    return SUCCESS