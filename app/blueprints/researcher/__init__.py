from flask import Blueprint

researcher = Blueprint(
    "researcher", 
    __name__, 
    template_folder="templates"
)

from . import routes
