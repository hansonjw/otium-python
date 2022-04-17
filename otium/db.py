import sqlite3

import click
from flask import Flask, current_app, g, flash
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    db.create_all(app=app)

# models, helper functions, etc.