from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from otium.db import db

bp = Blueprint('stuff', __name__)

@bp.route('/')
def index():
    return render_template('stock/hello_world.html')