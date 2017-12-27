#!/usr/bin/env python3

# RibbaPi - APA102 LED matrix controlled by Raspberry Pi in python
# Copyright (C) 2016  Christoph Stahl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib
import html


class RibbaPiHttpServer(HTTPServer, object):
    def __init__(self, ribbapi):
        super(RibbaPiHttpServer, self).__init__(('', 8080), RibbaPiHttpHandler)
        self.ribbapi = ribbapi


class RibbaPiHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == u'/':
            self.send_response(200)
            self.send_header(u'Content-type', u'text/html')
            self.end_headers()
            self.wfile.write(u"""<html>
            <head><title>RibbaPi Control</title><meta charset="UTF-8"></head>
            <body>
            <h1>RibbaPi</h1>
            <h2>Text display</h2>
            <form action="api/v1/displaytext" method="post">
            <fieldset>
            <legend>Enter text to be displayed on RibbaPi</legend>
            <input type="text" name="message"><br>
            <input type="submit" value="Submit">
            </fieldset>
            </form>""".encode(u"utf-8"))

            self.wfile.write(u"""
            <h2>Configuration</h2>
            <form action="api/v1/updateconfiguration" method="post">
            <fieldset>
            <legend>Configuration of RibbaPi</legend>""".encode(u"utf-8"))

            self.wfile.write(u"<input name=\"brightness\" type=\"range\" min=\"0.0\" max=\"1.0\" step=\"0.02\" value=\"{}\"/> Brightness level<br>".format(self.server.ribbapi.display.brightness).encode(u"utf-8"))

            checkbox = u"<input type=\"checkbox\" name=\"gameframe_activated\" value=\"1\" checked>Gameframe Animations<br>" if self.server.ribbapi.gameframe_activated else u"<input type=\"checkbox\" name=\"gameframe_activated\" value=\"0\">Gameframe Animations<br>"
            self.wfile.write(checkbox.encode(u"utf-8"))

            checkbox = u"<input type=\"checkbox\" name=\"blm_activated\" value=\"1\" checked>Blinkenlights Animations<br>" if self.server.ribbapi.blm_activated else u"<input type=\"checkbox\" name=\"blm_activated\" value=\"0\">Blinkenlights Animations<br>"
            self.wfile.write(checkbox.encode(u"utf-8"))

            checkbox = u"<input type=\"checkbox\" name=\"clock_activated\" value=\"1\" checked>Clock Animation<br>" if self.server.ribbapi.clock_activated else u"<input type=\"checkbox\" name=\"clock_activated\" value=\"0\">Clock Animations<br>"
            self.wfile.write(checkbox.encode(u"utf-8"))

            checkbox = u"<input type=\"checkbox\" name=\"moodlight_activated\" value=\"1\" checked>Moodlight<br>" if self.server.ribbapi.moodlight_activated else u"<input type=\"checkbox\" name=\"moodlight_activated\" value=\"0\">Moodlight<br>"
            self.wfile.write(checkbox.encode(u"utf-8"))

            self.wfile.write(u"""
            <input type="submit" value="Update Configuration">
            </fieldset>
            </form>""".encode(u"utf-8"))

            self.wfile.write(u"""<h2>Animations</h2>

            <form>
            <button formaction="api/v1/next_animation" formmethod="post">Next animation!</button>
            </form>

            <form action="api/v1/setgameframe" method="post">
            <fieldset>
            <legend>Choose gameframe animations to display</legend>""".encode(u"utf-8"))
            for animation in self.server.ribbapi.gameframe_animations:
                self.wfile.write(u"""<input type="checkbox"
                                            name="animations"
                                            value="{}" {}> <a href="{}">{}</a><br>""".format(
                                            animation,
                                            u"checked" if animation in self.server.ribbapi.gameframe_selected else u"",
                                            u"playnext/" + animation,
                                            animation).encode(u"utf-8"))
            self.wfile.write(u"""<input type="submit" value="Submit">
            </fieldset>
            </form>""".encode(u"utf-8"))
            self.wfile.write(u"</body></html>".encode(u"utf-8"))
        print self.path
        if self.path.startswith(u"/playnext"):
            self.server.ribbapi.set_next_animation(self.path[len(u"/playnext/"):])
            self.server.ribbapi.stop_current_animation()
            self.send_response(303)
            self.send_header(u'Location', u'/')
            self.end_headers()


    def do_POST(self):
        if self.path.startswith(u"/api/v1/next_animation"):
            self.server.ribbapi.stop_current_animation()
            self.send_response(303)
            self.send_header(u'Location', u'/')
            self.end_headers()
        if self.path.startswith(u"/api/v1/displaytext"):
            content_length = int(self.headers[u'Content-Length'])
            if self.headers[u'Content-Type'] == u"application/x-www-form-urlencoded":
                post_data = self.rfile.read(content_length)
                post_data = unicode(post_data, u'utf-8')
                post_data_dict = urlparse.parse_qs(post_data)
                post_data_dict = html.unescape(post_data_dict)
                message = post_data_dict[u"message"][0]
                self.server.ribbapi.text_queue.put(message)
                self.send_response(303)
                self.send_header(u'Location', u'/')
                self.end_headers()
                # self.send_response(200)
                # self.send_header('Content-type', 'text/html')
                # self.end_headers()
                # self.wfile.write("""<html>
                # <body>Message is now displayed on RibbaPi<br><br>
                # <script>
                # document.write('<a href="' + document.referrer + '">Go Back</a>');
                # </script>
                # </body>
                # </html>""".encode("utf-8"))
        if self.path.startswith(u"/api/v1/setgameframe"):
            content_length = int(self.headers[u'Content-Length'])
            if self.headers[u'Content-Type'] == u"application/x-www-form-urlencoded":
                post_data = self.rfile.read(content_length)
                post_data = unicode(post_data, u'utf-8')
                post_data_dict = urlparse.parse_qs(post_data)
                if u"animations" in post_data_dict:
                    selected_animations = post_data_dict[u"animations"]
                    selected_animations = html.unescape(selected_animations)
                    self.server.ribbapi.gameframe_selected = selected_animations
                    self.send_response(200)
                    self.send_header(u'Content-type', u'text/html')
                    self.end_headers()
                    self.wfile.write(u"""<html>
                    <body>Gameframe animations set<br><br>
                    <script>
                    document.write('<a href="' + document.referrer + '">Go Back</a>');
                    </script>
                    </body>
                    </html>""".encode(u"utf-8"))
                else:
                    self.server.ribbapi.gameframe_selected = []
                    self.send_response(200)
                    self.send_header(u'Content-type', u'text/html')
                    self.end_headers()
                    self.wfile.write(u"""<html>
                    <body>Gameframe animations set<br><br>
                    <script>
                    document.write('<a href="' + document.referrer + '">Go Back</a>');
                    </script>
                    </body>
                    </html>""".encode(u"utf-8"))
        if self.path.startswith(u"/api/v1/updateconfiguration"):
            content_length = int(self.headers[u'Content-Length'])
            if self.headers[u'Content-Type'] == u"application/x-www-form-urlencoded":
                post_data = self.rfile.read(content_length)
                post_data = unicode(post_data, u'utf-8')
                post_data_dict = urlparse.parse_qs(post_data)
                if u"brightness" in post_data_dict:
                    self.server.ribbapi.display.brightness = float(post_data_dict[u"brightness"][0])
                self.server.ribbapi.gameframe_activated = True if u"gameframe_activated" in post_data_dict else False
                self.server.ribbapi.blm_activated = True if u"blm_activated" in post_data_dict else False
                self.server.ribbapi.clock_activated = True if u"clock_activated" in post_data_dict else False
                self.server.ribbapi.moodlight_activated = True if u"moodlight_activated" in post_data_dict else False

                self.send_response(200)
                self.send_header(u'Content-type', u'text/html')
                self.end_headers()
                self.wfile.write(u"""<html>
                <body>RibbaPi configuration updated!<br><br>
                <script>
                document.write('<a href="' + document.referrer + '">Go Back</a>');
                </script>
                </body>
                </html>""".encode(u"utf-8"))
