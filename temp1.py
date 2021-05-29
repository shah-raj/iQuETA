import os, secrets, json ,sys
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, Flask, session, make_response
from flask_app import app, db, bcrypt, mail, google, REDIRECT_URI, currentUserType
from flask_app.forms import *
from flask_app.models import Teacher, Student, Questions, Test, Marks
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from urllib.request import Request, urlopen, URLError
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from flask_app.objective import ObjectiveTest
import random
from datetime import date, datetime
from sqlalchemy import desc

import string
from flask_app.models import Test,Questions


objective_generator = ObjectiveTest('dbms.txt')
print(objective_generator.generate_test())