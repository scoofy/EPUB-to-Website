import os, jinja2, re, logging
from collections import namedtuple
from data import data
from modules import markdown2, BeautifulSoup
from google.appengine.ext import blobstore

################### Unique Global Variables ####################
BOOK_TITLE = data.BOOK_TITLE
BOOK_SUBTITLE = data.BOOK_SUBTITLE
AUTHOR_NAME = data.AUTHOR_NAME
AUTHOR_WEBSITE = data.AUTHOR_WEBSITE
####################### Global Variables #######################
URL_CHECK_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    }
mkd = markdown2.Markdown()
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(extensions=['jinja2.ext.with_'],
    loader = jinja2.FileSystemLoader(template_dir), 
    autoescape = True)
upload_url = blobstore.create_upload_url('/upload')

# epub filename
EPUB_FILENAME = data.EPUB_FILENAME

# parse the package.opf file for chapter order
package_soup = BeautifulSoup.BeautifulSoup(open("package/package.opf"))
if not package_soup:
    raise Exception("You must have a package.opf in the package folder.")
    sys.exit()

SECTION_LIST = []
for item_ref in package_soup('itemref'):
    item = package_soup.find(id=item_ref.get('idref'))
    chapter_filename = item.get("href")
    chapter_filename = chapter_filename.split("/")
    if len(chapter_filename) != 2 or chapter_filename[0] not in ['text', "Navigation"]:
        improperly_formatted_file_path = chapter_filename
        improperly_formatted_file_path.pop()
        improperly_formatted_file_path = "/".join(improperly_formatted_file_path)
        logging.error("Your EPUB isn't properly formatted, you will have to reset the /templates/text or /templates/Navigation folder to: /templates/" + improperly_formatted_file_path)
    chapter_filename = chapter_filename[-1].replace(".xhtml","")
    SECTION_LIST.append(chapter_filename)
##
XHTML_SECTION_LIST = []
for section in SECTION_LIST:
    if section != "nav":
        XHTML_SECTION_LIST.append("text/" + section + ".xhtml")
    else:
        XHTML_SECTION_LIST.append("Navigation/" + section + ".xhtml")

SectionData = namedtuple("SectionData", ["previous_section", "next_section", "title"])
BOOK_SECTION_DICT = {}
XHTML_BOOK_SECTION_DICT = {}
for i in range(len(XHTML_SECTION_LIST)):
    if i == 0:
        i_minus_one = len(XHTML_SECTION_LIST)-1
        i_plus_one = i+1
    elif i == len(XHTML_SECTION_LIST)-1:
        i_minus_one = i-1
        i_plus_one = 0
    else:
        i_minus_one = i-1
        i_plus_one = i+1
    section_soup = BeautifulSoup.BeautifulSoup(open("templates/" + str(XHTML_SECTION_LIST[i])))
    section_title = section_soup.html.head.title.string.strip()
    this_tuple = SectionData(previous_section = SECTION_LIST[i_minus_one], next_section = SECTION_LIST[i_plus_one], title = section_title)
    this_xhtml_tuple = SectionData(previous_section = XHTML_SECTION_LIST[i_minus_one], next_section = XHTML_SECTION_LIST[i_plus_one], title = section_title)
    BOOK_SECTION_DICT[SECTION_LIST[i]] = this_tuple
    XHTML_BOOK_SECTION_DICT[XHTML_SECTION_LIST[i]] = this_xhtml_tuple


# Multi Drag/Drop Globals
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
ACCEPT_FILE_TYPES = IMAGE_TYPES
IMAGE_EXTENTION_LIST = ["jpg", "jpeg", "gif", "png"]
IMAGE_TYPES_LIST = ["image/" + x for x in IMAGE_EXTENTION_LIST]

#########################################################
REFERER_BLACKLIST = [
    '/login', 
    '/logout', 
    '/signup', 
    '/welcome', 
    '/user_page_img_upload',
    '/object_img_upload',
    '/object_img_delete',
    '/visitor_img_upload']
REG_EX_LETTERS_AND_NUMBERS = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
REG_EX_LETTERS_NUMBERS_DOT_AND_POUND = r'(/(?:[\.\#a-zA-Z0-9_-]+/?)*)'
