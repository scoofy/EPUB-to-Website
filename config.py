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
EPUB_FILENAME = data.EPUB_FILENAME

EPUB_UPLOADED = data.EPUB_UPLOADED
EPUB_FILE_URL = data.EPUB_FILE_URL

AMAZON_GIFT_CARD_SUPPORT = data.AMAZON_GIFT_CARD_SUPPORT
AMAZON_RECIPIENT_PUBLIC_EMAIL = data.AMAZON_RECIPIENT_PUBLIC_EMAIL
####################### Global Variables #######################
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(extensions=['jinja2.ext.with_'],
    loader = jinja2.FileSystemLoader(template_dir), 
    autoescape = True)

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

REG_EX_LETTERS_AND_NUMBERS = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
REG_EX_LETTERS_NUMBERS_DOT_AND_POUND = r'(/(?:[\.\#a-zA-Z0-9_-]+/?)*)'
