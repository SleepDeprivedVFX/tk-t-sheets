'''
This is the script you would put into a workfiles2_scene_operation_tk-maya.py type file.  Or any other action you might
want when you want to trigger the T-Sheets connection.
'''

# Here I want to try and connect to my app.
'''
pub = self.parent
engine = pub.engine
tsheets = engine.apps.get('tk-t-sheets')
if not tsheets:
    self.logger.debug('tk-t-sheets ain\'t loaded, dude.')
    return
# try:
tsheets.check_sg_timesheet_status()

'''
# except AttributeError, e:
#     self.logger.warning('Shit hit the fan.  tk-t-sheets won\'t load the freaking nodes.')
#     return
