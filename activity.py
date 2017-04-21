# Copyright (c) 2012 Bert Freudenberg
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""
Activity: TestMultiTouch
Shows multi-touch events
"""

from gi.repository import Gtk
from gi.repository import Gdk
from random import random
from math import pi as M_PI

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import TitleEntry
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton
from sugar3.activity.widgets import DescriptionItem

class TestMultiTouchActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.max_participants = 1

        toolbar_box = ToolbarBox()

        activity_button = ActivityButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        title_entry = TitleEntry(self)
        toolbar_box.toolbar.insert(title_entry, -1)
        title_entry.show()

        description_item = DescriptionItem(self)
        toolbar_box.toolbar.insert(description_item, -1)
        description_item.show()

        share_button = ShareButton(self)
        toolbar_box.toolbar.insert(share_button, -1)
        share_button.show()
        
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        # main view
        touch_area = TouchArea()
        self.set_canvas(touch_area)
        touch_area.show()


class TouchArea(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.fingers = {}
        self.time = 0
        self.set_events(Gdk.EventMask.TOUCH_MASK)
        self.connect('draw', self.__draw_cb)
        self.connect('event', self.__event_cb)

    def __event_cb(self, widget, event):
        if event.type in (
                Gdk.EventType.TOUCH_BEGIN,
                Gdk.EventType.TOUCH_UPDATE,
                Gdk.EventType.TOUCH_CANCEL,
                Gdk.EventType.TOUCH_END):
            # sequence is a void ptr object identifying the finger
            # we make it a string for use as dict key
            seq = str(event.touch.sequence)
            if event.type == Gdk.EventType.TOUCH_BEGIN:
                if event.touch.time - self.time > 100:
                    self.remove_inactive_fingers()
                self.fingers[seq] = Finger(event)
            else:
                self.fingers[seq].update(event)
            self.time = event.touch.time
            self.queue_draw()

    def __draw_cb(self, widget, ctx):
        alloc = self.get_allocation()
        ctx.set_source_rgb(1, 1, 1)
        ctx.paint()
        for f in self.fingers:
            self.fingers[f].draw(ctx, alloc.width, alloc.height)

    def remove_inactive_fingers(self):
        for f in self.fingers:
            if self.fingers[f].active:
                return
        self.fingers = {}

class Finger:

    def __init__(self, event):
        self.trail = [ Point(event.touch.x, event.touch.y) ]
        self.color = (random(), random(), random())
        self.active = True

    def update(self, event):
        if event.type == Gdk.EventType.TOUCH_UPDATE:
            self.trail.append( Point(event.touch.x, event.touch.y) )
        elif event.type == Gdk.EventType.TOUCH_END:
            self.active = False
        elif event.type == Gdk.EventType.TOUCH_CANCEL:
            self.active = False
            self.color = (1, 0, 0)

    def draw(self, ctx, width, height):
        (r, g, b) = self.color
        ctx.set_source_rgb(r, g, b)
        self.draw_trail(ctx)
        if self.active:
            self.draw_touch(ctx)
            ctx.set_source_rgb(0.5, 0.5, 0.5)
            self.draw_crosshair(ctx, width, height)

    def draw_crosshair(self, ctx, width, height):
        p = self.trail[-1]
        ctx.set_line_width(1)
        ctx.move_to(p.x, 0)
        ctx.line_to(p.x, height)
        ctx.move_to(0, p.y)
        ctx.line_to(width, p.y)
        ctx.stroke()

    def draw_touch(self, ctx):
        p = self.trail[-1]
        ctx.set_line_width(10)
        ctx.arc(p.x, p.y, 30, 0, 2 * M_PI)
        ctx.stroke()

    def draw_trail(self, ctx):
        ctx.set_line_width(5)
        p = self.trail[0]
        ctx.move_to(p.x, p.y)
        for p in self.trail:
            ctx.line_to(p.x, p.y)
        ctx.stroke()


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y
