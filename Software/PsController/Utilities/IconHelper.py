import pkgutil
import base64
import PsController.Utilities.OsHelper as osHelper


def getIconData(iconName):
    if osHelper.getCurrentOs() == osHelper.WINDOWS:
        separator = '\\'
    else:
        separator = '/'
    imageData = pkgutil.get_data('PsController', 'Icons' + separator + iconName)
    return base64.b64encode(imageData, altchars=None)  # Python image only create gifs from base64-encoded strings