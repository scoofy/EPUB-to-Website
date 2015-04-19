import os, jinja2, re
from collections import namedtuple
from data import data
from modules import markdown2
from google.appengine.ext import blobstore

################### Unique Global Variables ####################
BOOK_TITLE = data.BOOK_TITLE
BOOK_SUBTITLE = data.BOOK_SUBTITLE
AUTHOR_NAME = data.AUTHOR_NAME
AUTHOR_WEBSITE = data.AUTHOR_WEBSITE
####################### Global Variables #######################
URL_SAFE_CHARS = [
    "a","A","b","B","c","C","d","D","e","E","f","F","g","G","h","H","i","I",
    "j","J","k","K","l","L","m","M","n","N","o","O","p","P","q","Q","r","R",
    "s","S","t","T","u","U","v","V","w","W","x","X","y","Y","z","Z",
    "0","1","2","3","4","5","6","7","8","9","_","-"]
URL_CHECK_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    }
mkd = markdown2.Markdown()
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(extensions=['jinja2.ext.with_'],
    loader = jinja2.FileSystemLoader(template_dir), 
    autoescape = True)
upload_url = blobstore.create_upload_url('/upload')

SECTION_LIST = ["cover",
				"introquote",
				"titlepage",
				"verso",
				"reverso",
				"nav",
				"prologue",
				"etape1",
				"chapter1", 
				"chapter2", 
				"etape2",
				"chapter3", 
				"chapter4", 
				"etape3",
				"chapter5",
				"chapter6",
				"chapter7",
				"conclusion",
				"endnotes",
				"backcover",
				]
XHTML_SECTION_LIST = []
for section in SECTION_LIST:
	if section != "nav":
		XHTML_SECTION_LIST.append("text/" + section + ".xhtml")
	else:
		XHTML_SECTION_LIST.append("Navigation/" + section + ".xhtml")

SectionTuple = namedtuple("SectionTuple", ["previous_section", "next_section"])
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
	this_tuple = SectionTuple(previous_section = XHTML_SECTION_LIST[i_minus_one], next_section = XHTML_SECTION_LIST[i_plus_one])
	BOOK_SECTION_DICT[SECTION_LIST[i]] = this_tuple
	XHTML_BOOK_SECTION_DICT[XHTML_SECTION_LIST[i]] = this_tuple


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
