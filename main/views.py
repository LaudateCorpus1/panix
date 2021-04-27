#!/usr/bin/env python
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

# http://pandevice.readthedocs.io/en/latest/reference.html

"""
bulk_subinterfaces.py
=====================

Use bulk operations to create / delete hundreds of firewall interfaces.

NOTE: Please update the hostname and auth credentials variables
      before running.

The purpose of this script is to use and explain both the bulk operations
as it relates to subinterfaces as well as the new function that organizes
objects into vsys.  This script will show how the new bulk operations
correctly handle when subinterface objects are in separate vsys trees.

"""
from flask import Blueprint, render_template, request, redirect, session, url_for, abort
import uuid
import os
from main.models import Networks, FireWalls, Creds
from werkzeug.utils import secure_filename
import datetime
import random
import sys
# Copyright (c) 2017, Palo Alto Networks
from pandevice import device
from pandevice import firewall
from pandevice import network

ALLOWED_EXTENSIONS = set(['csv'])

main_app = Blueprint('main_app', __name__)

@main_app.route('/return_to', methods=('GET', 'POST'))
def return_to():
    for i in Creds.objects:
        fwip=i.fwip
        banner = 'You authenticated using %s credentials' % (fwip)

    return render_template('main/mainx.html', banner=banner)

@main_app.route('/', methods=('GET', 'POST'))
def main():
    '''
    display the login screen
    '''

    return render_template('main/new_main.html')

@main_app.route('/mainx', methods=('GET', 'POST'))
def mainx():
    '''
    capture login info
    '''
    # Get the credentials from the user
    username = request.form.get('username')
    password = request.form.get('password')
    fwip= request.form.get('fwip')

    # Clear creds for storing
    Creds.objects().delete()
    creds = Creds(fwip=fwip,username=username,password=password)
    try:
        creds.save()
    except:
        error = 'ERR002-Failed to save creds to the database'
        return render_template('main/dberror.html')


    # First, let's create the firewall object that we want to modify.
    fw = firewall.Firewall(fwip, username, password)
    banner = 'You authenticated using %s credentials' % (fwip)

    return render_template('main/mainx.html', banner=banner)



# Bulk import from file selector
@main_app.route('/sub_deploy', methods = ['GET', 'POST'])
def sub_deploy():
    firewalls = []
    # get current items
    for i in Networks.objects:
        fwip = i.fwip
        if fwip not in firewalls:
            firewalls.append(fwip)

    return render_template('main/fw_chooser.html', firewalls=firewalls)

# Bulk import from file selector
@main_app.route('/deploy_interface', methods = ['GET', 'POST'])
def deploy_interface():
    fw_deploy= request.form.get('firewall')
    for i in Creds.objects:
        fwip=i.fwip.encode('utf-8')
        username=i.username.encode('utf-8')
        password=i.password.encode('utf-8')
    if fwip == None:
        error = 'ERR2222-No creds in the Creds DB. Log out and login again'
        return render_template('main/dberror.html')

    ints=[]

    # get info from firewall...must have active interfaces
    fw = firewall.Firewall(fwip, username, password)
    interfaces = network.EthernetInterface.refreshall(fw, add=False)
    for eth in interfaces:
        ints.append(eth)

    return render_template('main/interface_chooser.html', interfaces=ints, fwip=fwip)

# Deploy sub interfaces from the database
@main_app.route('/deploy', methods = ['GET', 'POST'])
def deploy():
    # Get the credentials from the user
    selected_fwip = request.form.get('firewall').encode('utf-8')
    interface = request.form.get('interface').encode('utf-8')
    router = request.form.get('router').encode('utf-8')

    if interface == 'none selected':
        error = "ERR2222-Go back you didn't select an interface"
        return render_template('main/gen_error.html', error=error)

    '''
    Handling HA

    # Don't assume either firewall is primary or active.
    # Just start by telling pandevice they are an HA pair
    # and how to connect to them.
    fw = Firewall('10.0.0.1', 'admin', 'password')
    fw.set_ha_peers(Firewall('10.0.0.2', 'admin', 'password'))
    fw.refresh_ha_active()
    # Now, verify the config is synced between the devices.
    # If it's not synced, force config synchronization from active to standby
    if not fw.config_synced():
        fw.synchronize_config()  # blocks until synced or error
    '''
    for i in Creds.objects:
        fwip=i.fwip.encode('utf-8')
        username=i.username.encode('utf-8')
        password=i.password.encode('utf-8')

        if fwip == None:
            error = 'ERR2222-No creds in the Creds DB. Log out and login again'
            return render_template('main/dberror.html')

    # First, let's create the firewall object that we want to modify.
    fw = firewall.Firewall(selected_fwip, username, password)
    # Get vsys
    vsys_list = device.Vsys.refreshall(fw, name_only=True)

    # This works...need to figure out a better way
    vsys = random.choice(vsys_list)

    # Let's make our base interface that we're going to make subinterfaces
    base = network.EthernetInterface(interface, "layer3")
    fw.add(base)
    base.create()
    # Now let's go ahead and make all of our subinterfaces.
    for i in Networks.objects:
        gateway=i.gateway.encode('utf-8')
        tag=i.tag.encode('utf-8')
        comment=i.comment.encode('utf-8')
        zone=i.zone.encode('utf-8')

        # Build subinterface
        name = "{0}.{1}".format(interface, tag)
        sub_intf = network.Layer3Subinterface(name,tag,gateway,comment)
        # Now add the subinterface to that randomly chosen vsys.
        vsys.add(sub_intf)
        vr = sub_intf.set_virtual_router(virtual_router_name=router)
        security_zone = sub_intf.set_zone(zone_name=zone)

    # Creat all subinterfaces at once
    sub_intf.create_similar()
    vsys.add(vr)
    vsys.add(security_zone)
    vr.create()
    security_zone.create()

    return render_template('main/deploy_success.html', fwip=selected_fwip)


# Bulk import from file selector
@main_app.route('/bulk_picker', methods = ['GET', 'POST'])
def bulk_picker():
    return render_template('main/chooser.html')

# Bulk import from file selector
@main_app.route('/bulk', methods = ['GET', 'POST'])
def bulk():
    if request.method == 'POST':
        file = request.files['file']
        # check if the post request has the file part
        if 'file' not in request.files:
            error = 'Missing File Part'
            return render_template('main/chooser.html', error=error)
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            error = 'No selected file'
            return render_template('main/chooser.html', error=error)

        file.save(os.path.join(file.filename))
        vars = []
        with open(os.path.join(file.filename)) as f:
            line = f.readline().strip('/t')
            check = 0
            while line:
                vars = line.split(',')
                fwip = vars[0]
                # Check to make sure that this firewall has not been uploaded.
                for i in Networks.objects:
                    fw_check=i.fwip
                    if fwip == fw_check and check == 0:
                        error = 'ERR00034, trying to upload duplicate CSV'
                        return render_template('main/dberror.html', error=error)
                # set the check flag
                check = 1
                gateway=vars[1][:-1]+'1'
                junk, maskbits=vars[3].split('/')
                tag=vars[4]
                comment=vars[5]
                zone=vars[6][:-1]

                # Write controller to database
                try:
                    out = Networks(fwip=fwip,gateway=gateway,maskbits=maskbits,tag=tag,comment=comment,zone=zone)
                    out.save()
                except:
                    error = 'ERR001-Failed to save network to the database'
                    return render_template('main/dberror.html')
                line = f.readline().strip('/t')

    return render_template('main/db_uploaded.html')

# Select record for editing
@main_app.route('/show_networks', methods = ['GET'])
def show_networks():
    error = None
    count = 0
    networks = []

    # get current items
    for i in Networks.objects:
        fwip = i.fwip
        maskbits = i.maskbits
        gateway = i.gateway
        tag = i.tag
        comment = i.comment
        zone = i.zone
        out = [fwip,maskbits,gateway,tag,comment,zone]
        networks.append(out)

    return render_template('main/show_networks.html', networks=networks)


@main_app.route('/ask_db_drop', methods=('GET', 'POST'))
def ask_db_drop():

    return render_template('main/ask_db_drop.html')

@main_app.route('/db_drop', methods=('GET', 'POST'))
def db_drop():
    Networks.objects().delete()
    return render_template('main/db_drop.html')


@main_app.route('/help', methods=('GET', 'POST'))
def help():

    return render_template('main/help.html')

@main_app.route('/logout', methods=('GET', 'POST'))
def logout():
    Creds.objects().delete()
    return render_template('main/new_main.html')
