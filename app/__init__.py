#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 16:40:48 2017

@author: Pavan Akula
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, instance_path=os.path.join(basedir, 'instance'))
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models

