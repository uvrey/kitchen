from tokenize import String
import manim as m
import os
from kitchen import SOUND_ERROR, SUCCESS, display_helper
# Import the required module for text 
# to speech conversion
from gtts import gTTS

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
    YAY,
    OOF,
    POP
) = range(13)

id = 0
config = NARR

def set_config(config_option):
    config = config_option
    return config

def _get_narration_path() -> String:
    global id
    id = id + 1
    return os.getcwd() + r'\assets\narration\narr_' + str(id) + '.mp3'

def _get_narration(script) -> String:
    """_summary_

    Args:
        script (str): Script for the lesson to play

    Returns:
        Path: Path of the narration file
    """    
    language = 'en'
    myobj = gTTS(text=script, lang=language, slow=False)
    path = _get_narration_path() 
    myobj.save(path)
    return path

def narrate(script, scene) -> int:
    if config == NARR:
        _new_narration = _get_narration(script)
        if not os.path.isfile(_new_narration):
            return SOUND_ERROR
        scene.add_sound(_new_narration)
    return SUCCESS

def add_sound_to_scene(scene, sound_spec):
    """Adds a sound to a scene based on some specification.

    Args:
        scene (Scene): Manim Scene object
        sound_spec (Enum): Some sound type as described in __init__.py

    Returns:
        int: Status code
    """    
    base_path = os.getcwd() + r'\assets\sounds'

    if not os.path.isdir(base_path):
        return SOUND_ERROR

    try:
        if sound_spec == CLICK:
            scene.add_sound(os.getcwd() + r'\assets\sounds\click.wav')
        elif sound_spec == FLASH:
            pass
        elif sound_spec == WAVE:
            pass
        elif sound_spec == CLANG:
            scene.add_sound(os.getcwd() + r'\assets\sounds\clang.wav')
        elif sound_spec == TWINKLE:
            scene.add_sound(os.getcwd() + r'\assets\sounds\twinkle.wav') 
        elif sound_spec == FAIL:
            scene.add_sound(os.getcwd() + r'\assets\sounds\fail.wav')
        elif sound_spec == YAY:
            scene.add_sound(os.getcwd() + r'\assets\sounds\yay.wav')
        elif sound_spec == OOF:
            scene.add_sound(os.getcwd() + r'\assets\sounds\oof.wav')   
        elif sound_spec == POP:
            scene.add_sound(os.getcwd() + r'\assets\sounds\pop.wav') 
    except OSError:
        display_helper.fail_secho("Sound not found - please check your assets folder.")
        return SOUND_ERROR

    return SUCCESS