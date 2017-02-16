#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
from datetime import datetime, timedelta
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required=True)
    blog = db.TextProperty(required=True)
    created = db.DateTimeProperty(required=True)

class MainPage(Handler):
    def render_front(self, title="", blog="", created="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("index.html", title=title, blog=blog, created="", error=error, blogs=blogs)

    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_front(self, error="", msg="", entry_title="", entry_blog=""):
        self.render("new_post.html", error=error, msg=msg, entry_title=entry_title, entry_blog=entry_blog)

    def get(self):
        self.render("new_post.html", error="", msg="", entry_title="", entry_blog="")

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")
        created = datetime.today() + timedelta(hours=-6)
        msg = ""
        entry_title = self.request.get('title')
        entry_blog = self.request.get('blog')

        if title and blog:
            a = Blog(title=title, blog=blog, created=created)
            a.put()
            # self.redirect("/")
            msg = "You have successfully submitted a new post!"
            self.render_front(msg)
        else:
            error = "Submit a title and blog post."
            self.render_front(error, msg, entry_title, entry_blog)

class ViewPostHandler(Handler):
    def render_blog(self, id=""):
        blogs = db.GqlQuery("SELECT * FROM Blog Where __key__ = KEY('Blog', " + id + ")"
                            " ORDER BY created DESC LIMIT 5")
        self.render("blog.html", blogs=blogs, id=id)

    def get(self, id):
        self.render_blog(id)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/new_post', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
    # ('/perma', ViewPostHandler)
], debug=True)
