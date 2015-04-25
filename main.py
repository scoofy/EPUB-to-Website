from __future__ import with_statement
import os, webapp2, jinja2, hashlib, hmac, string, random, time, datetime, logging, urllib
import urllib2, mimetypes, cgi, re, uuid, json
import config 
from model import Epub, Cover
import utilities as utils
from data import data
from do_not_copy import do_not_copy
from modules import markdown2, BeautifulSoup
from modules.pybcrypt import bcrypt
from google.appengine.api import memcache
from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
#########################################################
####################### Primary Class Objects #######################
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = config.jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))
        #Need to set expires to last longer than browser open

    def set_secure_cookie_with_expiration(self, name, val):
        cookie_val = make_secure_val(val)
        expiration_time = (datetime.datetime.now() + datetime.timedelta(weeks=2)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; expires=%s; Path=/' % (name, cookie_val, expiration_time)
            )       

    def read_secure_cookie(self, cookie_name):
        cookie_val = self.request.cookies.get(cookie_name)
        if cookie_val and check_secure_val(cookie_val):
            return cookie_val
        else:
            return None

    def check_cookie_return_val(self, cookie_name):
        cookie_val = self.request.cookies.get(cookie_name)

        if cookie_val and check_secure_val(cookie_val):
            val = cookie_val.split('|')[0]
            return val
        else:
            if cookie_val:
                self.logout()
            return None

    def return_user_if_cookie(self):
        id_hash = self.request.cookies.get('user_id')
        if id_hash:
            valid = check_secure_val(id_hash)
            if valid:
                user_id = int(check_secure_val(id_hash))
                user_var = return_thing_by_id(user_id, "Users")
                if user_var:
                    return user_var
                else:
                    logging.warning("User does not exist even though hash is correct, probably local server issues (deleteing a user, but not the cookie")
                    return None
            else:
                self.logout()
                return None
        else:
            return None

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))
        self.set_secure_cookie('username', str(user.username))
        self.set_secure_cookie('over18', str(user.over18))

    def login_and_remember(self, user):
        self.set_secure_cookie_with_expiration('user_id', str(user.key().id()))
        self.set_secure_cookie_with_expiration('username', str(user.username))
        self.set_secure_cookie_with_expiration('over18', str(user.over18))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/')
        self.response.headers.add_header('Set-Cookie', 'over18=; Path=/')

    def inline_404(self):
        self.error(404)
        handle_404(self.request, self.response, 404)
class ObjectUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))
        #Need to set expires to last longer than browser open

    def set_secure_cookie_with_expiration(self, name, val):
        cookie_val = make_secure_val(val)
        expiration_time = (datetime.datetime.now() + datetime.timedelta(weeks=2)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; expires=%s; Path=/' % (name, cookie_val, expiration_time)
            )       

    def read_secure_cookie(self, cookie_name):
        cookie_val = self.request.cookies.get(cookie_name)
        if cookie_val and check_secure_val(cookie_val):
            return cookie_val
        else:
            return None

    def check_cookie_return_val(self, cookie_name):
        cookie_val = self.request.cookies.get(cookie_name)

        if cookie_val and check_secure_val(cookie_val):
            val = cookie_val.split('|')[0]
            return val
        else:
            self.logout()
            return None

    def return_user_if_cookie(self):
        id_hash = self.request.cookies.get('user_id')
        if id_hash:
            valid = check_secure_val(id_hash)
            if valid:
                user_id = int(check_secure_val(id_hash))
                user_var = return_thing_by_id(user_id, "Users")
                if user_var:
                    return user_var
                else:
                    logging.warning("User does not exist even though hash is correct, probably local server issues (deleteing a user, but not the cookie")
                    return None
            else:
                self.logout()
                return None
        else:
            return None

    def return_has_cookie(self):
        cookie_list = []
        cookie_types = ['user_id', 'username', 'over18']
        for i in cookie_types:
            cookie_val = self.check_cookie_return_val(i)
            cookie_list.append(cookie_val)
        has_cookie = True
        for i in cookie_list:
            if i is None:
                has_cookie = None
                break
        return has_cookie

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))
        self.set_secure_cookie('username', str(user.username))
        self.set_secure_cookie('over18', str(user.over18))

    def login_and_remember(self, user):
        self.set_secure_cookie_with_expiration('user_id', str(user.key().id()))
        self.set_secure_cookie_with_expiration('username', str(user.username))
        self.set_secure_cookie_with_expiration('over18', str(user.over18))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/')
        self.response.headers.add_header('Set-Cookie', 'over18=; Path=/')
#########################################################
class HomePage(Handler):        
    def get(self):
        title = config.BOOK_TITLE
        subtitle = config.BOOK_SUBTITLE
        
        faux_cover_background_color = config.FAUX_COVER_BACKGROUND_COLOR_HEX

        epub_filename = config.EPUB_FILENAME
        epub_uploaded = config.EPUB_UPLOADED
        epub_file_url = config.EPUB_FILE_URL
        epub_cover_url = ""
        if config.EPUB_COVER_UPLOADED:
            epub_cover_url = config.EPUB_COVER_URL
        
        author = config.AUTHOR_NAME
        website = config.AUTHOR_WEBSITE

        support = config.AMAZON_GIFT_CARD_SUPPORT
        support_email = config.AMAZON_RECIPIENT_PUBLIC_EMAIL
        if not support and support_email:
            support = False

        self.render('homepage.html', 
                    title = title,
                    subtitle = subtitle,
                    faux_cover_background_color = faux_cover_background_color,
                    epub_filename = epub_filename,
                    epub_uploaded = epub_uploaded,
                    epub_file_url = epub_file_url,
                    epub_cover_url = epub_cover_url,
                    author = author,
                    website = website,
                    support = support,
                    )   
    def post(self):
        pass
class BookPage(Handler):
    def get(self):
        #self.render('ebook.html')
        section = self.request.get('section')
        if not section:
            section = config.SECTION_LIST[0]
        index = config.SECTION_LIST.index(section)
        path = config.XHTML_SECTION_LIST[index]
        previous_section = None
        next_section = None
        section_title = None
        try:
            this_section = config.BOOK_SECTION_DICT.get(section)
            previous_section = this_section.previous_section
            next_section = this_section.next_section
            section_title = this_section.title
        except:
            logging.error("Something went wrong with page load")
        # prevent cover pages from being enormous
        page_is_a_cover = False
        if section == config.SECTION_LIST[0] or section == config.SECTION_LIST[-1]:
            # section is front or back cover
            page_is_a_cover = True
        self.render('bookpage.html',
                    path = path,
                    book_title = config.BOOK_TITLE,
                    section_title = section_title,
                    previous_section = previous_section,
                    next_section = next_section,
                    page_is_a_cover = page_is_a_cover,

                    section_list = config.XHTML_SECTION_LIST,
                    current_page = index+1,
                    total_pages = len(config.XHTML_SECTION_LIST)
                    )
    def post(self):
        pass

class TextHandler(Handler):
    def get(self, path):
        section = utils.remove_url_path_leading_slash(path)
        # here we remove ".xhtml" but leave the anchor marker "#go_to_anchor_blah"
        section = utils.remove_url_path_xhtml_ending_if_present(section)
        # this functionality seems to work well with the redirect
        self.redirect("/thebook?section="+section)
    def post(self):
        pass
class UploadHandler(Handler):
    def get(self):
        all_previous_epub_files = list(Epub.all())
        number_of_previous_epubs = len(all_previous_epub_files)

        if config.EPUB_UPLOADED:
            self.redirect("/")
            return
        upload_url = blobstore.create_upload_url('/complete_upload')
        error_1 = self.request.get("error_1")
        error_2 = self.request.get("error_2")
        file_error = self.request.get("file_error")
        error_3 = self.request.get("error_3")
        self.render("upload.html",
                    upload_url = upload_url,
                    epub_filename = config.EPUB_FILENAME,

                    error_1 = error_1,
                    error_2 = error_2,
                    file_error = file_error,
                    error_3 = error_3,

                    all_previous_epub_files = all_previous_epub_files,
                    number_of_previous_epubs = number_of_previous_epubs,
                    )
class UploadCompletionHandler(ObjectUploadHandler):
    def post(self):
        if config.EPUB_UPLOADED:
            self.redirect("/")
            return
        filename = self.request.get("filename")
        password = self.request.get("password")
        epub = self.request.get("epub")
        confirm = self.request.get("confirm")
        if not (filename and password and epub and confirm):
            # Unsuccessful
            error_1 = ""
            error_2 = ""
            error_3 = ""
            file_error = ""
            if not filename:
                error_1 = "You must have a filename."
            if not password:
                error_2 = "You must confirm your password."
            if not epub:
                file_error = "Hmm, it looks like you forgot to select a file to upload."
            if not confirm:
                error_3 = "You must confirm that everything is correct"
            self.redirect("/upload?error_1=%s&error_2=%s&error_3=%s&file_error=%s" % (error_1, error_2, error_3, file_error))
            return
        if password != do_not_copy.secret():
            if not password:
                error_2 = "Your password was incorrect."
            self.redirect("/upload?error_2=%s" % error_2)
            return
        #Success, now check to delete:
        number_of_previous_epubs = self.request.get("number_of_previous_epubs")
        if number_of_previous_epubs == "":
            logging.error("number_of_previous_epubs was None")
            return
        number_of_previous_epubs = int(number_of_previous_epubs)
        if number_of_previous_epubs > 1000:
            logging.error("Someone is trying to cleverly overload the server. Nice try, jerks.")
            return
        files_to_delete_list = []
        for i in range(number_of_previous_epubs + 1):
            file_id = self.request.get("epub_to_delete_"+str(i))
            if file_id:
                files_to_delete_list.append(file_id)
        if files_to_delete_list:
            # Let's delete some files and blobs!
            for file_id in files_to_delete_list:
                obj = Epub.get_by_id(int(file_id))
                if obj:
                    blobinfo = obj.file_blob_key
                    blobinfo.delete()
                    obj.delete()

        # Deleting over, back to the uploading!
        try:
            file_data = self.get_uploads()[0]
        except:
            self.redirect('/result')
            return
        file_url = '/serve/%s' % file_data.key()
        file_blob_key = file_data.key()
        new_epub = Epub(epoch = float(time.time()),
                        file_url = file_url,
                        file_blob_key = file_data.key(),
                        filename = str(file_data.filename),
                        )
        new_epub.put()
        self.redirect('/result?file_url=%s' % file_url)
class CoverResultHandler(Handler):
    def get(self):
        file_url = self.request.get("file_url")
        if not file_url:
            error = True
        else:
            error = False
        self.render("result.html", 
                    file_url = file_url,
                    error = error,
                    )

class ResultHandler(Handler):
    def get(self):
        file_url = self.request.get("file_url")
        if not file_url:
            error = True
        else:
            error = False
        self.render("result.html", 
                    file_url = file_url,
                    error = error,
                    )


class CoverHandler(Handler):
    def get(self):
        all_previous_files = list(Cover.all())
        number_of_previous = len(all_previous_files)

        if config.EPUB_COVER_UPLOADED:
            self.redirect("/")
            return
        upload_url = blobstore.create_upload_url('/cover_upload')
        error_1 = self.request.get("error_1")
        error_2 = self.request.get("error_2")
        file_error = self.request.get("file_error")
        error_3 = self.request.get("error_3")
        self.render("upload_cover.html",
                    upload_url = upload_url,

                    error_1 = error_1,
                    error_2 = error_2,
                    file_error = file_error,
                    error_3 = error_3,

                    all_previous_files = all_previous_files,
                    number_of_previous = number_of_previous,
                    )
class CoverCompletionHandler(ObjectUploadHandler):
    def post(self):
        if config.EPUB_COVER_UPLOADED:
            self.redirect("/")
            return
        #epub
        password = self.request.get("password")
        cover = self.request.get("cover")
        confirm = self.request.get("confirm")
        if not (password and cover and confirm):
            # Unsuccessful
            error_2 = ""
            error_3 = ""
            file_error = ""
            if not password:
                error_2 = "You must confirm your password."
            if not cover:
                file_error = "Hmm, it looks like you forgot to select a file to upload."
            if not confirm:
                error_3 = "You must confirm that everything is correct"
            self.redirect("/cover?error_2=%s&error_3=%s&file_error=%s" % (error_2, error_3, file_error))
            return
        if password != do_not_copy.secret():
            if not password:
                error_2 = "Your password was incorrect."
            self.redirect("/cover?error_2=%s" % error_2)
            return
        #Success, now check to delete:
        number_of_previous = self.request.get("number_of_previous")
        if number_of_previous == "":
            logging.error("number_of_previous was None")
            return
        number_of_previous = int(number_of_previous)
        if number_of_previous > 1000:
            logging.error("Someone is trying to cleverly overload the server. Nice try, jerks.")
            return
        files_to_delete_list = []
        for i in range(number_of_previous + 1):
            file_id = self.request.get("file_to_delete_"+str(i))
            if file_id:
                files_to_delete_list.append(file_id)
        if files_to_delete_list:
            # Let's delete some files and blobs!
            for file_id in files_to_delete_list:
                obj = Cover.get_by_id(int(file_id))
                if obj:
                    blobinfo = obj.file_blob_key
                    blobinfo.delete()
                    obj.delete()

        # Deleting over, back to the uploading!
        try:
            file_data = self.get_uploads()[0]
        except:
            self.redirect('/result')
            return
        file_url = '/serve/%s' % file_data.key()
        file_blob_key = file_data.key()
        new_cover = Cover(epoch = float(time.time()),
                        file_url = file_url,
                        file_blob_key = file_data.key(),
                        filename = str(file_data.filename),
                        )
        new_cover.put()
        self.redirect('/result_cover?file_url=%s' % file_url)


class SupportHandler(Handler):
    def get(self):
        if not (config.AMAZON_GIFT_CARD_SUPPORT and config.AMAZON_RECIPIENT_PUBLIC_EMAIL):
            self.redirect("/")
            return
        support_email = config.AMAZON_RECIPIENT_PUBLIC_EMAIL
        self.render("support/support.html",
                    support_email = support_email)

class RobotPage(Handler):
    def get(self):
        pass

class FileServe(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        if not blobstore.get(blob_key):
            self.error(404)
            return
        else:
            resource = str(urllib.unquote(blob_key))
            self.send_blob(blob_key)

#########################################################
app = webapp2.WSGIApplication([
        ('/', HomePage),
        ('/thebook', BookPage),
        (r'/text' + config.REG_EX_LETTERS_NUMBERS_DOT_AND_POUND, TextHandler),
        (r'/Navigation' + config.REG_EX_LETTERS_NUMBERS_DOT_AND_POUND, TextHandler),
        ('/upload', UploadHandler),
        ('/complete_upload', UploadCompletionHandler),
        ('/result', ResultHandler),

        ('/cover', CoverHandler),
        ('/cover_upload', CoverCompletionHandler),
        ('/result_cover', CoverResultHandler),

        ('/support', SupportHandler),
        ('/robots.txt', RobotPage),
        (r'/serve/([^/]+)?', FileServe),
        ], debug=True)

################## Error Handlers #######################
def handle_404(request, response, exception):
    logging.exception(exception)
    response.write('''
        <div style="
            width: 920px; 
            display: block; 
            margin-right: auto; 
            margin-left: auto;
            ">
            <img src="/images/error_images/404.png" />
        </div>
        ''')
    response.set_status(404)
app.error_handlers[404] = handle_404
def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('''
        <div style="
            width: 920px; 
            display: block; 
            margin-right: auto; 
            margin-left: auto;
            ">
            <img src="/images/error_images/500.png" />
        </div>
        ''')
    response.set_status(500)
app.error_handlers[500] = handle_500

