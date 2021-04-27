# Copyright (c) 2020 Hewlett Packard Enterprise Development LP

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# __author__ = "@netwookie"
# __credits__ = ["Rick Kauffman"]
# __license__ = "MIT"
# __maintainer__ = "Rick Kauffman"
# __email__ = "rick.a.kauffman@hpe.com"
from mongoengine import signals
from flask import url_for
import os

from application import db
from utilities.common import utc_now_ts as now


class Networks(db.Document):
    fwip = db.StringField(db_field="f", required=True)
    maskbits = db.StringField(db_field="m", required=True)
    gateway = db.StringField(db_field="g", required=True)
    tag = db.StringField(db_field="t", required=True)
    comment = db.StringField(db_field="c", required=True)
    zone = db.StringField(db_field="z", required=True)

class FireWalls(db.Document):
    firewall_ip = db.StringField(db_field="f", required=True, unique=True)
    ha_pair_id = db.StringField(db_field="h", required=True)
    created = db.IntField(db_field="c", default=now())

class Creds(db.Document):
    fwip = db.StringField(db_field="f", required=True, unique=True)
    username = db.StringField(db_field="u", required=True)
    password = db.StringField(db_field="p", required=True)
