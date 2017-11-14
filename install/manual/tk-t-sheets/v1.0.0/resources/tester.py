# # import wx
# #
# # app = wx.App()
# #
# # moving = app.MainLoop()
# # test = wx.
# # x = 0
# # while x < 100000:
# #     print moving
# #     if moving:
# #         print 'Moving'
#
# from __future__ import print_function
#
#
# import ctypes
# import time
# from datetime import datetime
# import threading
# from PySide import QtCore, QtGui
# import psutil
#
#
# # def detect_magic():
# #     for p in psutil.process_iter():
# #         if p.name() == 'maya.exe':
# #             print p.name()
# #             print psutil.cpu_percent()
# #             print p.children.im_self
# #         proc = psutil.Process()
# #         print proc.open_files()
#
# #
# # def DetectClick(button, watchtime = 25):
# #     '''Waits watchtime seconds. Returns True on click, False otherwise'''
# #     if button in (1, '1', 'l', 'L', 'left', 'Left', 'LEFT'):
# #         bnum = 0x01
# #     elif button in (2, '2', 'r', 'R', 'right', 'Right', 'RIGHT'):
# #         bnum = 0x02
# #
# #     start = time.time()
# #     while 1:
# #         if ctypes.windll.user32.GetKeyState(bnum) not in [0, 1]:
# #             # ^ this returns either 0 or 1 when button is not being held down
# #             print 'button click'
# #             print ctypes.windll.user32.GetKeyState(bnum)
# #             return True
# #         elif time.time() - start >= watchtime:
# #             # break
# #             print ctypes.windll.user32.GetKeyState(bnum)
# #             pass
# #         time.sleep(0.001)
# #     return False
# #
#
# # class watch_mouse(QtGui.QWidget):
# #     def __init__(self):
# #         QtGui.QWidget.__init__(self)
# #         run_mouse_watch = self.mouse_watch()
# #
# #     def mouse_watch(self):
# #         bnum = 0x01
# #         start = time.time()
# #         self._generator = None
# #         self._timerId = None
# #         self.start(click=bnum)
# #
# #
# #     def loop_generator(self, click=None):
# #         now_time = str(datetime.time(datetime.now()))
# #         split_time = now_time.split(':')
# #         h = int(split_time[0])
# #         m = int(split_time[1])
# #         get_s = split_time[2].split('.')[0]
# #         s = int(get_s)
# #
# #         while self._generator:
# #             if s < 59:
# #                 s += 1
# #             else:
# #                 if m < 59:
# #                     s = 0
# #                     m += 1
# #                 elif m == 59 and h <= 22:
# #                     h += 1
# #                     m = 0
# #                     s = 0
# #             if s > 15:
# #                 if click:
# #                     if ctypes.windll.user32.GetKeyState(click) not in [0, 1]:
# #                         print 'Clicked!'
# #                         s = 0
# #
# #             yield
# #
# #     def start(self, click=None):
# #         self.stop()
# #         self._generator = self.loop_generator(click=click)
# #         self._timerId = self.startTimer(1000)
# #
# #     def stop(self):
# #         if self._timerId is not None:
# #             self.killTimer(self._timerId)
# #         self._timerId = None
# #         self._generator = None
# #
# #     def timerEvent(self, event):
# #         if self._generator is None:
# #             return
# #         try:
# #             next(self._generator)
# #         except StopIteration:
# #             self.stop()
# #
# # This is free and unencumbered software released into the public domain.
# #
# # Anyone is free to copy, modify, publish, use, compile, sell, or
# # distribute this software, either in source code form or as a compiled
# # binary, for any purpose, commercial or non-commercial, and by any
# # means.
# #
# # In jurisdictions that recognize copyright laws, the author or authors
# # of this software dedicate any and all copyright interest in the
# # software to the public domain. We make this dedication for the benefit
# # of the public at large and to the detriment of our heirs and
# # successors. We intend this dedication to be an overt act of
# # relinquishment in perpetuity of all present and future rights to this
# # software under copyright law.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# # IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# # OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# # ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# # OTHER DEALINGS IN THE SOFTWARE.
# #
# # For more information, please refer to <http://unlicense.org/>
# import traceback
# import atexit
# import textwrap
# import io
#
# try:
#     import __builtin__ as builtins
# except ImportError:
#     import builtins
#
# class FileMonitor(object):
#     """
#     Collect stacktraces of where files are opened, and prints them out before the
#     program exits.
#
#     - Has partial support for python3
#
#     Example
#     -------
#
#     # BEGIN monitor.py
#     from filemonitor import FileMonitor
#     FileMonitor().patch()
#     f = open('/bin/ls')
#     # END monitor.py
#
#     $ python monitor.py
#       ----------------------------------------------------------------------------
#       path = /bin/ls
#       >   File "monitor.py", line 3, in <module>
#       >     f = open('/bin/ls')
#       ----------------------------------------------------------------------------
#
#     Acknowledgements
#     ----------------
#     http://stackoverflow.com/questions/2023608/check-what-files-are-open-in-python
#     Solution modified from http://stackoverflow.com/a/2023709. Authored by Claudiu
#     """
#     def __init__(self, print_only_open=True):
#         self.openfiles = []
#         self.oldopen = builtins.open
#
#         self.oldfile = getattr(builtins, 'file', io.FileIO)
#
#         self.do_print_only_open = print_only_open
#         self.in_use = False
#
#         class File(self.oldfile):
#
#             def __init__(this, *args, **kwargs):
#                 path = args[0]
#
#                 self.oldfile.__init__(this, *args, **kwargs)
#                 if self.in_use:
#                     return
#                 self.in_use = True
#                 self.openfiles.append((this, path, this._stack_trace()))
#                 self.in_use = False
#
#             def close(this):
#                 self.oldfile.close(this)
#
#             def _stack_trace(this):
#                 try:
#                     raise RuntimeError()
#                 except RuntimeError as e:
#                     stack = traceback.extract_stack()[:-2]
#                     return traceback.format_list(stack)
#
#         self.File = File
#
#     def patch(self):
#         builtins.open = self.File
#
#         try:
#             builtins.file = self.File
#         except AttributeError:
#             pass
#
#         atexit.register(self.exit_handler)
#
#     def unpatch(self):
#         builtins.open = self.oldopen
#         try:
#             builtins.file = self.oldfile
#         except AttributeError:
#             pass
#
#     def exit_handler(self):
#         indent = '  > '
#         terminal_width = 80
#         for file, path, trace in self.openfiles:
#             if file.closed and self.do_print_only_open:
#                 continue
#             print("-" * terminal_width)
#             print("  {} = {}".format('path', path))
#             lines = ''.join(trace).splitlines()
#             _updated_lines = []
#             for l in lines:
#                 ul = textwrap.fill(l,
#                                    initial_indent=indent,
#                                    subsequent_indent=indent,
#                                    width=terminal_width)
#                 _updated_lines.append(ul)
#             lines = _updated_lines
#             print('\n'.join(lines))
#             print("-" * terminal_width)
#             print()
#
# if __name__ == '__main__':
#     FileMonitor().patch()
#     open('/bin/ls')