# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import threading
import json
import urllib, urllib2
import sys, os, platform, time

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.switch_tasks_dialog import Ui_Dialog
from datetime import datetime, timedelta
from functools import partial

sg_engine = sgtk.platform.engine
path_from_engine = sg_engine

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables
# ----------------------------------------------------------------------------------------------------------------------

# Define system variables
osSystem = platform.system()

if osSystem == 'Windows':
    base = '//hal'
    env_user = 'USERNAME'
    computername = 'COMPUTERNAME'
else:
    base = '/Volumes'
    env_user = 'USER'
    computername = 'HOSTNAME'

# I need to learn how to use this logger info.  It currently doesn't work.
app_log = sgtk.platform.get_logger('T-Sheets TEST: engine: %s' % sg_engine)

# Get T-Sheets Authorization
auth_id = 3
auth_filters = [
    ['id', 'is', auth_id]
]
auth_fields = ['code']

user_params = {'per_page': '50', 'active': 'yes'}
jobs_params = {'active': 'yes'}

url = 'https://rest.tsheets.com/api/v1/'


def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 

    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("T-Sheets Connect", app_instance, AppDialog)


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """

    def __init__(self, timesheet_id=None, jobcode_id=None):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()

        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk

        auth_id = 3
        auth_filters = [
            ['id', 'is', auth_id]
        ]
        auth_fields = ['code']

        engine = self._app.engine
        self.sg = engine.sgtk

        auth_data = self.sg.shotgun.find_one('CustomNonProjectEntity06', auth_filters, auth_fields)
        authorization = auth_data['code']

        self.headers = {
            'Authorization': 'Bearer %s' % authorization
        }

        offset = (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone) / 3600
        self.timezone = '-%02d:00' % offset
        self._generator = None
        self._timerId = None

        # lastly, set up our very basic UI
        setup_user = self.confirm_user()
        context = self._app.context
        project_info = context.project
        self.ui.new_project.setText(project_info['name'])
        setup_name = context.user['name']
        self.ui.employee.setText(setup_name)
        task = context.task['name']
        self.ui.new_task.setText(task)
        shot_asset = context.entity['name']
        shot_asset_type = context.entity['type']
        self.ui.new_entity.setText(shot_asset)
        setup_email = setup_user['email']
        setup_timesheet = self.get_ts_user_timesheet(email=setup_email)
        self.ui.no_btn.clicked.connect(self.no)
        get_context = self.get_sg_current_context()
        if setup_timesheet:
            ts_id = setup_timesheet.keys()[0]
            setup_ts_data = setup_timesheet.values()[0]
            setup_username = setup_ts_data['username']
            setup_timecard = setup_ts_data['timecard']
            setup_user_id = setup_ts_data['user_id']
            setup_jobcode_id = setup_timecard['jobcode_id']
            get_jobcode_data = self.get_ts_jobcode(jobcode=setup_jobcode_id)
            ts_project_info = self.get_ts_project_from_sg(project_name=project_info['name'])
            if ts_project_info:
                for tsid, tsproject in ts_project_info.items():
                    ts_project_name = tsproject
                    ts_project_id = tsid
            else:
                ts_project_id = None
                ts_project_name = None
            setup_ts_name = get_jobcode_data[get_jobcode_data.keys()[0]]['name']

            get_task_data = self._return_from_tsheets(page='customfields')
            tasks = get_task_data['results']['customfields']
            ts_task_id = 0
            for t, d in tasks.items():
                if d['name'] == 'Job Tasks':
                    ts_task_id = t
                    break
            ts_task = setup_timecard['customfields'][ts_task_id]
            self.ui.current_project.setText(ts_project_name)
            self.ui.current_entity_label.setText(setup_ts_name)
            self.ui.current_task_label.setText(ts_task)
            setup_start = setup_timecard['start']
            start_datetime = self.iso_to_qt_datetime(iso_datetime=setup_start)
            self.ui.start_time.setDateTime(start_datetime)
            self.ui.start_time.setEnabled(False)
            self.ui.current_time.setEnabled(False)
            self.ui.total_time.setEnabled(False)
            self.ui.yes_btn.clicked.connect(partial(self.change_ts_timesheet,
                                                    timesheet_id=ts_id, ctx=get_context, jobcode_id=setup_jobcode_id))
            self.start(pass_time=setup_start)
        else:
            # This should eventually load the Clock_in Script... Not sure how to call that one... Yet
            # Perhaps what I'll do is just have it rewrite the UI a bit to compensate.
            return

    # ------------------------------------------------------------------------------------------------------------------
    # Clock Functions
    # ------------------------------------------------------------------------------------------------------------------
    def loop_generator(self, pass_time=None):
        now_date = str(datetime.date(datetime.now()))
        now_time = str(datetime.time(datetime.now()))
        split_date = now_date.split('-')
        split_time = now_time.split(':')
        Y = int(split_date[0])
        M = int(split_date[1])
        D = int(split_date[2])
        h = int(split_time[0])
        m = int(split_time[1])
        get_s = split_time[2].split('.')[0]
        s = int(get_s)

        while self._generator:
            if s < 59:
                s += 1
            else:
                if m < 59:
                    s = 0
                    m += 1
                elif m == 59 and h <= 22:
                    h += 1
                    m = 0
                    s = 0
            set_datetime = QtCore.QDateTime(Y, M, D, h, m, s)
            self.ui.current_time.setDateTime(set_datetime)
            if pass_time:
                split_start = pass_time.replace('T', ' ')
                split_start = split_start.rsplit('-', 1)[0]
                split_end = self.get_iso_timestamp().replace('T', ' ').rsplit('-', 1)[0]
                time_delta = datetime.strptime(split_end, '%Y-%m-%d %H:%M:%S') \
                             - datetime.strptime(split_start, '%Y-%m-%d %H:%M:%S')
                splittime = str(time_delta).split(':')
                total_time = QtCore.QTime(int(splittime[0]), int(splittime[1]), int(splittime[2]))
                self.ui.total_time.setTime(total_time)
            yield

    def start(self, pass_time=None):
        self.stop()
        self._generator = self.loop_generator(pass_time=pass_time)
        self._timerId = self.startTimer(1000)

    def stop(self):
        if self._timerId is not None:
            self.killTimer(self._timerId)
        self._timerId = None
        self._generator = None

    def timerEvent(self, event):
        if self._generator is None:
            return
        try:
            next(self._generator)
        except StopIteration:
            self.stop()

    def iso_to_qt_datetime(self, iso_datetime=None):
        qt_datetime = None
        if iso_datetime:
            iso_date = iso_datetime.split('T')[0]
            iso_time = iso_datetime.split('T')[1]
            iso_time = iso_time.split('-')[0]
            its = iso_time.split(':')
            ids = iso_date.split('-')
            qt_datetime = QtCore.QDateTime(int(ids[0]), int(ids[1]), int(ids[2]), int(its[0]), int(its[1]), int(its[2]))
        return qt_datetime

    # ------------------------------------------------------------------------------------------------------------------
    # T-Sheets Web Connection IO
    # ------------------------------------------------------------------------------------------------------------------
    def _send_to_tsheets(self, page=None, data=None):
        if page:
            if data:
                try:
                    packed_data = json.dumps(data)
                    request = urllib2.Request('%s%s' % (url, page), headers=self.headers, data=packed_data)
                    request.add_header('Content-Type', 'application/json')
                    response = urllib2.urlopen(request)
                    response_data = json.loads(response.read())
                    return response_data
                except Exception, e:
                    print 'SWITCH: Send to T-Sheets connection failed!  Error: %s' % e
            else:
                return False
        else:
            return False

    def _return_from_tsheets(self, page=None, data=None):
        if page:
            try:
                if data:
                    data_list = urllib.urlencode(data)
                    Q = '?'
                else:
                    data_list = ''
                    Q = ''
                request = urllib2.Request('%s%s%s%s' % (url, page, Q, data_list), headers=self.headers)
                response = urllib2.urlopen(request)
                response_data = json.loads(response.read())
                return response_data
            except Exception, e:
                print 'SWITCH: Return from T-Sheets Connection Failed!  Error: %s' % e
        else:
            return False

    def _edit_tsheets(self, page=None, data=None):
        if page:
            if data:
                try:
                    # This is the way I was originally trying to PUT to the REST page, but it always returns 500 Error
                    opener = urllib2.build_opener(urllib2.HTTPHandler)
                    packed_data = json.dumps(data)
                    request = urllib2.Request('%s%s' % (url, page), headers=self.headers, data=packed_data)
                    request.add_header('Content-Type', 'application/json')
                    request.get_method = lambda: 'PUT'
                    response = opener.open(request)
                    response_data = json.loads(response.read())
                    return response_data
                except Exception:
                    # So, I am also trying a different approach using the Requests library instead of the urllib2
                    try:
                        packed_data = json.dumps(data)
                        request = self.requests.put('%s%s' % (url, page), headers=self.headers, data=packed_data)
                        response_data = request
                        print response_data
                        return response_data
                    except Exception, e:
                        print 'SWITCH: Edit T-Sheets Connection Failed! Error: %s' % e
            else:
                return False
        else:
            return False

    def return_subs(self, job_id=None):
        # this returns all children of a parent job id.  It does not return sub-children.
        if job_id:
            subjobsparams = {
                'parent_ids': job_id,
                'active': 'yes'
            }
            subjoblist = urllib.urlencode(subjobsparams)
            subjob_request = urllib2.Request('%sjobcodes?%s' % (url, subjoblist), headers=self.headers)
            subjob_js = json.loads(urllib2.urlopen(subjob_request).read())
            for sj_type, sj_result in subjob_js.items():
                if sj_type == 'results':
                    sj_jobs_data = sj_result['jobcodes']
                    return sj_jobs_data
            return False
        return False

    # ------------------------------------------------------------------------------------------------------------------
    # Shotgun and T-Sheets User Information
    # ------------------------------------------------------------------------------------------------------------------
    def confirm_user(self):
        current_user = os.environ[env_user]
        current_comp = os.environ[computername]
        confirmed_user = False
        get_current_user = self.get_sg_user(sg_login=current_user)
        get_current_computer = self.get_sg_user(sg_computer=current_comp)
        if get_current_computer == get_current_user:
            user_data = get_current_user.values()[0]
            user_email = user_data['email']
            user_name = user_data['name']
            get_ts_user = self.get_ts_current_user_status(email=user_email)
            if get_ts_user:
                ts_user = '%s %s' % (get_ts_user['name'][0], get_ts_user['name'][1])
                if user_name == ts_user:
                    confirmed_user = get_ts_user
        return confirmed_user

    def get_sg_user(self, userid=None, name=None, email=None, sg_login=None, sg_computer=None):
        """
        Get a specific Shotgun User's details from any basic input.
        Only the first detected value will be searched.  If all 3 values are added, only the ID will be searched.
        :param userid: (int) Shotgun User ID number
        :param name:   (str) First and Last Name
        :param email:  (str) email@asc-vfx.com
        :return: user: (dict) Basic details
        """

        user = {}
        if userid or name or email or sg_login or sg_computer:
            filters = [
                ['sg_status_list', 'is', 'act']
            ]
            if userid:
                filters.append(['id', 'is', userid])
            elif name:
                filters.append(['name', 'is', name])
            elif email:
                filters.append(['email', 'is', email])
            elif sg_login:
                filters.append(['login', 'is', sg_login])
            elif sg_computer:
                filters.append(['sg_computer', 'is', sg_computer])
            fields = [
                'email',
                'name',
                'sg_computer',
                'login',
                'permission_rule_set',
                'projects',
                'groups'
            ]
            find_user = self.sg.shotgun.find_one('HumanUser', filters, fields)
            if find_user:
                user_id = find_user['id']
                sg_email = find_user['email']
                computer = find_user['sg_computer']
                sg_name = find_user['name']
                # Dictionary {'type': 'PermissionRuleSet', 'id': 8 'name': 'Artist'}
                permissions = find_user['permission_rule_set']
                # List of Dictionaries [{'type': 'Group', 'id': 7, 'name':'VFX'}]
                groups = find_user['groups']
                login = find_user['login']
                # List of Dictionaries [{'type': 'Project', 'id': 168, 'name': 'masterTemplate'}]
                projects = find_user['projects']

                user[user_id] = {'name': sg_name, 'email': sg_email, 'computer': computer, 'permissions': permissions,
                                 'groups': groups, 'login': login, 'project': projects}
        return user

    def get_ts_active_users(self):
        ts_users = {}
        user_params = {'per_page': '50', 'active': 'yes'}
        user_js = self._return_from_tsheets(page='users', data=user_params)
        if user_js:
            for l_type, result_data in user_js.items():
                if l_type == 'results':
                    user_data = result_data['users']
                    for user in user_data:
                        data = user_data[user]
                        first_name = data['first_name']
                        last_name = data['last_name']
                        email = data['email']
                        last_active = data['last_active']
                        active = data['active']
                        username = data['username']
                        user_id = data['id']
                        name = first_name, last_name
                        ts_users[email] = {'name': name, 'last_active': last_active, 'active': active,
                                           'username': username, 'email': email, 'id': user_id}
            return ts_users
        return False

    def get_ts_jobcode(self, jobcode=None):
        # print 'Get Jobcode %s' % jobcode
        jobcode_data = {}
        if jobcode:
            data = {'ids': jobcode}
            get_jobcode = self._return_from_tsheets(page='jobcodes', data=data)
            for keys in get_jobcode:
                if keys == 'results':
                    job_data = get_jobcode[keys]['jobcodes']
                    for job_id, job_info in job_data.items():
                        jobid = job_id
                        job_name = job_info['name']
                        has_children = job_info['has_children']
                        parent_id = job_info['parent_id']
                        jobcode_data[jobid] = {'name': job_name, 'has_children': has_children,
                                               'parent_id': parent_id}
        return jobcode_data

    def get_ts_current_user_status(self, email=None):
        data = {}
        username = email
        # Send the Username from a script that already loads the shotgun data.  This returns the T-Sheets status of a
        # single user.
        all_users = self.get_ts_active_users()
        if username in all_users.keys():
            data = all_users[username]
        return data

    def get_sg_current_context(self):
        """
        import sgtk
        tk = sgtk
        engine = tk.platform.current_engine()
        sg = engine.sgtk
        ctx = engine.context
        taskName = str(ctx).split(',')[0]
        project = ctx.project['name']
        entity = ctx.entity['type']
        print project, entity, taskName
        print ctx

        masterTemplate Shot anim.main
        anim.main, Shot MST110_029_370_cmp

        :return:
        """
        context = {}
        try:
            tk = sgtk
            engine = tk.platform.current_engine()
            ctx = engine.context
            task_name = ctx.task['name']
            task_id = ctx.task['id']
            project = ctx.project['name']
            project_id = ctx.project['id']
            shot_id = ctx.entity['id']
            shot = ctx.entity['name']
            entity_type = ctx.entity['type']
            if entity_type == 'Shot':
                seq_data = self.get_sg_sequence_from_shot_id(shot_id)
                seq = seq_data['name']
                seq_id = seq_data['id']
            else:
                seq = None
                seq_id = None
        except Exception:
            task_name = 'fx.cloth'
            task_id = 11278
            entity_type = 'Shot'
            project = 'Asura'
            project_id = 140
            shot = '125_SAF_0015'
            seq = '125_SAF'
            seq_id = 161
        context[project_id] = {
            'task': task_name,
            'task_id': task_id,
            'context': entity_type,
            'name': shot,
            'shot_id': shot_id,
            'project': project,
            'sequence': seq,
            'seq_id': seq_id
        }
        return context

    # ------------------------------------------------------------------------------------------------------------------
    # T-Sheets Timesheet Workers
    # ------------------------------------------------------------------------------------------------------------------
    def get_iso_timestamp(self):
        iso_date = datetime.date(datetime.now()).isoformat()
        iso_time = '%02d:%02d:%02d' % (datetime.now().hour, datetime.now().minute, datetime.now().second)
        iso_tz = self.timezone
        clock_out = iso_date + 'T' + iso_time + iso_tz
        return clock_out

    def get_ts_project_from_sg(self, project_name=None):
        project_info = {}
        if project_name:
            ts_projects = self.get_ts_active_projects()
            for ts_id, proj_name in ts_projects.items():
                if proj_name == project_name:
                    project_info[ts_id] = proj_name
        return project_info

    def get_ts_active_projects(self):
        jobs_params = {'active': 'yes'}
        jobs_js = self._return_from_tsheets(page='jobcodes', data=jobs_params)
        ts_projects = {}
        for j_type, result_data in jobs_js.items():
            if j_type == 'results':
                jobs_data = result_data['jobcodes']
                for project in jobs_data:
                    data = jobs_data[project]
                    has_children = data['has_children']
                    if has_children:
                        project_name = data['name']
                        project_id = data['id']
                        ts_projects[project_id] = project_name
        return ts_projects

    def get_ts_user_timesheet(self, email=None):
        timesheet = {}
        _start_date = datetime.date((datetime.today() - timedelta(days=2)))
        current_user = self.get_ts_current_user_status(email=email)
        username = current_user['username']
        name = (current_user['name'][0] + ' ' + current_user['name'][1])
        first_name = current_user['name'][0]
        last_name = current_user['name'][1]
        ts_email = current_user['email']
        user_id = current_user['id']
        tsheet_param = {'start_date': _start_date, 'user_ids': user_id, 'on_the_clock': 'yes'}
        tsheets_json = self._return_from_tsheets(page='timesheets', data=tsheet_param)
        for type, data in tsheets_json.items():
            if type == 'results':
                ts_data = data.values()
                try:
                    for card, info in ts_data[0].items():
                        if info['on_the_clock']:
                            timesheet[card] = {'name': name, 'username': username, 'user_id': user_id, 'timecard': info}
                except AttributeError:
                    # User Not clocked in
                    pass
        return timesheet

    def change_ts_timesheet(self, timesheet_id=None, ctx=None, jobcode_id=None):
        new_ts = {}
        confirmed_user = self.confirm_user()
        if confirmed_user:
            if timesheet_id and ctx:
                user_email = confirmed_user['username']
                current_timesheet = self.get_ts_user_timesheet(email=user_email)
                end_time = current_timesheet[current_timesheet.keys()[0]]['timecard']['end']
                if not end_time:
                    clock_out_timesheet = self.clock_out_ts_timesheet(timesheet_id=timesheet_id, jobcode_id=jobcode_id)
                    if clock_out_timesheet:
                        clock_in_timesheet = self.clock_in_ts_timesheet(ctx=ctx)
                        if clock_in_timesheet:
                            if clock_in_timesheet['results']['timesheets']['1']['_status_message'] == 'Created':
                                new_ts = True
        return new_ts

    def clock_in_ts_timesheet(self, ctx=None):
        """
        Clock_in_ts_timesheet is going to be a little tricky.
        It will have to split out the context, and then find the jobcode_id based on the project, shot/asset & job task.
        The user_id, start time and other things will have to be collected as well.
        :param ctx:
        :return:
        """
        new_ts = {}
        confirmed_user = self.confirm_user()
        if confirmed_user:
            if ctx:
                print ctx
                user_id = confirmed_user['id']
                user_name = confirmed_user['name']
                start = self.get_iso_timestamp()
                project_id = ctx.keys()[0]
                ctx_data = ctx[project_id]
                project = ctx_data['project']
                project_jobcode = None
                task = ctx_data['task']
                shot_or_asset = ctx_data['name']
                sequence = ctx_data['sequence']
                context = ctx_data['context']
                if context == 'Asset':
                    ts_folder = 'Assets'
                elif context == 'Shot':
                    ts_folder = 'Shots'
                ts_projects = self.get_ts_active_projects()
                for pid, proj in ts_projects.items():
                    if proj == project:
                        project_jobcode = pid
                        break
                if project_jobcode:
                    ts_proj_subs = self.return_subs(project_jobcode)
                    if ts_proj_subs:
                        for folder_id, folder_data in ts_proj_subs.items():
                            if folder_data['name'] == ts_folder:
                                if folder_data['has_children']:
                                    assets_seqs = self.return_subs(folder_id)
                                    if assets_seqs:
                                        for ass_seq_id, ass_seq_data in assets_seqs.items():
                                            if ts_folder == 'Assets':
                                                if ass_seq_data['name'] == shot_or_asset:
                                                    jobcode_id = ass_seq_id
                                                    print 'ASSET JOBCODE ID: %s' % jobcode_id
                                                    break
                                            elif ts_folder == 'Shots':
                                                if ass_seq_data['name'] == sequence:
                                                    if ass_seq_data['has_children']:
                                                        get_shots = self.return_subs(ass_seq_id)
                                                        for shot_id, shot_data in get_shots.items():
                                                            if shot_data['name'] == shot_or_asset:
                                                                jobcode_id = shot_id
                                                                print 'SHOT JOBCODE ID: %s' % jobcode_id
                                                                break
                                break
                    data = {'ids': jobcode_id}
                    get_jobcode = self._return_from_tsheets(page='jobcodes', data=data)
                    parse_data = get_jobcode['supplemental_data']
                    jobcodes = parse_data['jobcodes']
                    results = get_jobcode['results']['jobcodes']
                    for parent_ids, info in jobcodes.items():
                        if info['name'] == project:
                            ts_project = {'project_id': parent_ids, 'project_name': project}
                        elif info['name'] == context:
                            ts_context = {'context_id': parent_ids, 'shot_or_asset_name': context}
                    get_task_data = self._return_from_tsheets(page='customfields')
                    tasks = get_task_data['results']['customfields']
                    print tasks
                    task_id = 0
                    for t, d in tasks.items():
                        if d['name'] == 'Job Tasks':
                            task_id = t
                            break
                    sg_to_ts_translation = self.get_sg_translator(sg_task=task)
                    task_translation = sg_to_ts_translation['task']
                    print task_translation
                    print self.get_iso_timestamp()
                    print jobcode_id
                    new_ts_data = {
                        "data":
                            [
                                {
                                    "user_id": user_id,
                                    "type": "regular",
                                    "start": "%s" % self.get_iso_timestamp(),
                                    "end": "",
                                    "jobcode_id": "%s" % jobcode_id,
                                    "notes": "Automatic timesheet update through Shotgun",
                                    "customfields": {
                                        task_id: "%s" % task_translation
                                    }
                                }
                            ]
                    }
                    new_ts = self._send_to_tsheets(page='timesheets', data=new_ts_data)
        print 'New Timesheet: %s' % new_ts
        return new_ts

    def get_people_from_group(self, group_id=None, group_name=None):
        people = None
        if group_id and group_name:
            print group_name
            print group_id
            filters = [
                ['id', 'is', group_id],
                ['code', 'is', group_name]
            ]
            fields = [
                'users'
            ]
            group_people = self.sg.shotgun.find('Group', filters, fields)
            if group_people:
                people = group_people[0]['users']
        return people

    def clock_out_ts_timesheet(self, timesheet_id=None, jobcode_id=None, *args):
        confirm_user = self.confirm_user()
        user_email = confirm_user['username']
        clocked_out = False
        if confirm_user:
            clock_out = self.get_iso_timestamp()
            data = {
                "data":
                    [
                        {
                            "id": int(timesheet_id),
                            "end": "%s" % clock_out,
                            "jobcode_id": int(jobcode_id)
                        }
                    ]
            }
            success = self._edit_tsheets(page='timesheets', data=data)
            if success:
                if success['results']['timesheets']['1']['_status_message'] == 'Updated':
                    clocked_out = True
        self.no()
        return clocked_out

    def no(self):
        self.close()

    def get_sg_translator(self, sg_task=None):
        """
        The T-Sheets Translator requires a special Shotgun page to be created.
        The fields in the database are as follows:
        Database Name:  code:                (str) A casual name of the database.
        sgtask:         sg_sgtask:          (str-unique) The shotgun task. Specifically, '.main' namespaces are removed.
        tstask:         sg_tstask:          (str) The T-Sheets name for a task
        ts_short_code:  sg_ts_short_code:   (str) The ironically long name for a 3 letter code.
        task_depts:     sg_task_grp:        (multi-entity) Returns the groups that are associated with tasks
        people_override:sg_people_override: (multi-entity) Returns individuals assigned to specific tasks

         :param:        sg_task:            (str) Shotgun task name from context
        :return:        translation:        (dict) {
                                                    task: sg_tstask
                                                    short: sg_ts_short_code
                                                    dept: sg_task_depts
                                                    people: sg_people_override
                                                    }
        """
        translation = {}
        if sg_task:
            if '.main' in sg_task:
                task_name = sg_task.replace('.main', '')
            else:
                task_name = sg_task

            task_name = task_name.lower()

            filters = [
                ['sg_sgtask', 'is', task_name]
            ]
            fields = [
                'sg_sgtask',
                'sg_tstask',
                'sg_ts_short_code',
                'sg_task_grp',
                'sg_people_override'
            ]
            translation_data = self.sg.shotgun.find_one('CustomNonProjectEntity07', filters, fields=fields)

            if translation_data:
                task = translation_data['sg_tstask']
                short = translation_data['sg_ts_short_code']
                group = translation_data['sg_task_grp']
                people = translation_data['sg_people_override']
                translation = {'task': task, 'short': short, 'group': group, 'people': people}
        return translation
