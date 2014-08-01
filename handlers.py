import os
import logging
import urllib
import webapp2
from resources import *
from google.appengine.api import users
from models import Article

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

def main_template(parent,child):
    f = open(os.path.join(os.path.dirname(__file__),
                          'templates',
                          parent))

    g = open(os.path.join(os.path.dirname(__file__),
                          'templates',
                          child))
    
    output = list()
    for l in f:
        if 'BODY' in l:
            for m in g:
                output.append(m)
        else:
            output.append(l)
                
    f.close()
    g.close()

    return output


class MainPage(webapp2.RequestHandler):    
    def get(self):
        output = main_template('main.html','index.html')
        self.response.write(''.join(output))


class ArticlePage(webapp2.RequestHandler):
    def get(self,key):
        output = main_template('main.html','article.html')
        self.response.write(''.join(output))


class ArchivePage(webapp2.RequestHandler):
    def get(self):
        output = main_template('main.html','archive.html')
        self.response.write(''.join(output))


def admin_template(parent, child, users):
    f = open(os.path.join(os.path.dirname(__file__),
                          'templates',
                          parent))

    g = open(os.path.join(os.path.dirname(__file__),
                          'templates',
                          child))
    output = list()
    for l in f:
        if 'BODY' in l:
            for m in g:
                if 'LOGOUT' in m:
                    output.append('<h3><a href="{}">Logout</a></h3>'.format(
                        users.create_logout_url('/')))
                else:
                    output.append(m)
        else:
            output.append(l)

    f.close()
    g.close()
    return output


class ManagePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if user.nickname() == 'guillemborrell':
                output = admin_template('manage.html','manager.html',users)
                self.response.write(''.join(output))

            else:
                self.response.write(
                    '<html><body><a href="{}">Not the right user. \
                    Log out.</a></body></html>'.format(
                        users.create_logout_url('/')))
                
        else:
            self.response.write(
                '<html><body><a href="{}">Sign in</a></body></html>'.format(
                    users.create_login_url('/manage')
                ))


class EditPage(webapp2.RequestHandler):
    def get(self,key):
        user = users.get_current_user()
        if user:
            if user.nickname() == 'guillemborrell':
                output = admin_template('manage.html','edit.html',users)
                self.response.write(''.join(output))

            else:
                self.response.write(
                    '<html><body><a href="{}">Not the right user. Log out.\
                    </a></body></html>'.format(
                        users.create_logout_url('/')))
                
        else:
            self.response.write(
                '<html><body><a href="{}">Sign in</a></body></html>'.format(
                    users.create_login_url('/manage')
                ))


class DeletePage(webapp2.RequestHandler):
    def get(self,key):
        user = users.get_current_user()
        if user:
            if user.nickname() == 'guillemborrell':
                output = admin_template('manage.html','delete.html',users)
                self.response.write(''.join(output))

            else:
                self.response.write(
                    '<html><body><a href="{}">Not the right user. \
                    Log out.</a></body></html>'.format(
                        users.create_logout_url('/')))
                
        else:
            self.response.write(
                '<html><body><a href="{}">Sign in</a></body></html>'.format(
                    users.create_login_url('/manage')
                ))


class ArticleFromSlug(webapp2.RequestHandler):
    def get(self,slug):
        key = Article.key_from_slug(slug)
        if len(key) == 0:
            logging.warning('wrong redirection: {}'.format(slug))
            self.redirect("/")
        else:
            self.redirect("/article/{}".format(key))

class OldRedirect(webapp2.RequestHandler):
    def get(self):
        self.redirect("/")


class MainHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
        self.response.out.write(
            '<form action="{}" method="POST" enctype="multipart/form-data">'.format(upload_url)
        )
        self.response.out.write(
            """Upload File: <input type="file" name="file"><br> <input type="submit"
            name="submit" value="Submit"> </form></body></html>""")


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/serve/{}'.format(blob_info.key()))


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)
