from __future__ import with_statement
import os, webapp2, jinja2, hashlib, hmac, string, random, time, datetime, logging, urllib
import urllib2, mimetypes, cgi, re, uuid, json
import config
import utilities as utils
from data import data
from do_not_copy import do_not_copy
from modules import markdown2, BeautifulSoup
from modules.pybcrypt import bcrypt
from google.appengine.api import memcache, taskqueue, mail, images, files, urlfetch
from google.appengine.ext import deferred, db, blobstore, webapp
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
        epub_filename = config.EPUB_FILENAME
        author = config.AUTHOR_NAME
        website = config.AUTHOR_WEBSITE
        self.render('homepage.html', 
                    title = title,
                    subtitle = subtitle,
                    epub_filename = epub_filename,
                    author = author,
                    website = website,
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

class RobotPage(Handler):
    def get(self):
        pass
################### Caching #############################
def users_cache(update = False, delay = 0):
    key = 'all_users'
    user_list = memcache.get(key)
    if user_list is None or update:
        if update:
            logging.warning('db query sleep')
            time.sleep(int(delay))
        logging.warning("DB Users Query")
        all_users = db.GqlQuery("SELECT * FROM Users WHERE deleted = FALSE ORDER BY created DESC")
        user_list = list(all_users)
        try:
            memcache.set(key, user_list)
        except Exception as exception:
            logging.error("memcache set error")
            print exception
    return user_list
def user_page_cache(user_id, update=False, delay = 0):
    # changed key to be identical key to return_thing_by_id for a user
    key = "Users_%s" % str(user_id)
    user_in_db = memcache.get(key)
    if user_in_db is None or update:
        if update:
            logging.warning('db query sleep')
            time.sleep(int(delay))
        logging.warning("DB Page Query -- user_page_cache")
        user_in_db = Users.get_by_id(user_id)
        user_in_db = [user_in_db]
        try:
            memcache.set(key, user_in_db)
        except Exception as exception:
            logging.error("memcache set error")
            print exception
    return user_in_db[0]
#########################################################

#########################################################
app = webapp2.WSGIApplication([
        ('/', HomePage),
        ('/thebook', BookPage),
        (r'/text' + config.REG_EX_LETTERS_NUMBERS_DOT_AND_POUND, TextHandler),
        (r'/Navigation' + config.REG_EX_LETTERS_NUMBERS_DOT_AND_POUND, TextHandler),
        ('/robots', RobotPage)
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

