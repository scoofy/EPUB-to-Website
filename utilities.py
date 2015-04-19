import random, string
####################### Utility functions #######################
def remove_tag_duplicates_return_list(obj):
	the_list = obj.tags
	the_set = set(the_list)
	new_list = list(the_set)
	return new_list
def remove_list_duplicates(some_list):
	the_set = set(some_list)
	new_list = list(the_set)
	return new_list
def strip_list_whitespace(some_list):
	tag_list = some_list
	#logging.warning(tag_list)
	new_list = []
	for tag in tag_list:
		tag = " ".join(tag.split())
		new_list.append(tag)
	tag_list = new_list
	new_list = []
	for tag in tag_list:
		if tag:
			new_list.append(tag)
	return new_list
def sort_comment_child_ranks(com_ranked_children, delay=0):
	ranked_list = com_ranked_children
	tuple_list = []
	#time.sleep(int(delay))
	for com_id in ranked_list:
		com = return_thing_by_id(com_id, "Comments")
		com.rank = return_rank(com)
		tuple_list.append("%s|%d" % (str(com.rank), int(com_id)))
	#logging.warning(tuple_list)
	tuple_list.sort(key = lambda x: x.split('|')[0], reverse=True)
	#logging.warning(tuple_list)
	sorted_list = []
	for com_tuple in tuple_list:
		sorted_list.append(int(com_tuple.split('|')[1]))
		#logging.warning(sorted_list)
	ranked_list = sorted_list
	#logging.warning(ranked_list)
	return ranked_list
def strip_string_whitespace(some_string):
	stripped_string = " ".join(some_string.split())
	return stripped_string
def time_since_creation(item_epoch_var):
	raw_secs = round(time.time())-round(item_epoch_var)
	#logging.warning(raw_secs)
	raw_secs = int(raw_secs)
	time_str = None
	if raw_secs < 60:
		seconds = raw_secs
		if seconds > 1:
			time_str = "%d seconds" % seconds
		else:
			time_str = "%d second" % seconds
	elif (raw_secs >= 60) and (raw_secs < (60 * 60)):
		minutes = (raw_secs/60)
		if minutes > 1:
			time_str = "%d minutes" % minutes
		else:
			time_str = "%d minute" % minutes
	elif (raw_secs >= (60*60) and (raw_secs < (60 * 60 * 24))):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		if hours > 1:
			time_str = "%d hours" % hours
		else:
			time_str = "%d hour" % hours
	elif (raw_secs >= (60*60*24) and (raw_secs < (60*60*24*30))):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		if days > 1:
			time_str = "%d days" % days
		else:
			time_str = "%d day" % days
	elif (raw_secs >=(60*60*24*30)) and (raw_secs < (60*60*24*365)):		
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		months = (days/30)
		if months > 1:
			time_str = "%d months" % months
		else:
			time_str = "%d month" % months
	elif raw_secs >= (60*60*24*365):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		years = (days/365)
		if years > 1:
			time_str = "%d years" % years
		else:
			time_str = "%d year" % years
	else:
		logging.error("something wrong with time_since_creation function")
		time_str = None
	return time_str		
def check_url(url_str):
	link_var = url_str
	deadLinkFound = check_url_instance(link_var)
	if deadLinkFound:
		link_var = "http://" + link_var
		deadLinkFound = check_url_instance(link_var)
		if deadLinkFound:
			link_var = "http://www." + link_var
			deadLinkFound = check_url_instance(link_var)
			if deadLinkFound:
				link_var = None
	return link_var
def check_url_instance(url_str):
	link_var = url_str
	logging.warning(link_var)
	deadLinkFound = True
	try:
		f = urlfetch.fetch(url=link_var, deadline=30)
		if f.status_code == 200:
			#logging.warning(f.content)
			pass
		deadLinkFound = False
	except Exception as e:
		logging.warning('that failed')
		logging.warning(e)
	logging.warning(deadLinkFound)
	return deadLinkFound
def remove_unsafe_chars_from_list(string_list):
	escaped_list = []
	for string in string_list:
		escaped_string = []
		for char in string:
			if char in URL_SAFE_CHARS:
				escaped_string.append(char)
			else:
				if char == " ":
					escaped_string.append("_")
		string = "".join(escaped_string)
		escaped_list.append(string)
	new_string_list = escaped_list
	return new_string_list 
def is_blacklisted_referer(referer):
	global REFERER_BLACKLIST
	blacklist = REFERER_BLACKLIST
	is_blacklisted = False
	for i in blacklist:
		if referer.endswith(i):
			is_blacklisted = True
			break
	return is_blacklisted
def convert_text_to_markdown(string):
	'''escape, and save as markdown text'''
	escaped_text = cgi.escape(string)
	mkd_converted_string = mkd.convert(escaped_text)
	return mkd_converted_string


####################### Time functions #######################
start_time = None
time_since_cache = None
def check_time():
    global start_time
    global time_since_cache
    if start_time is None:
        logging.warning("Time Started")
        start_time = time.time()
    time_since_cache = time.time() - start_time
def reset_time():
    global start_time
    if time_since_cache is None:
        check_time()
    else:
        start_time = time.time()
        logging.warning("Time Reset")
#########################################################

def random_string_generator(size = random.randint(15, 20),
            chars = string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def remove_url_path_leading_slash(path):
	return path[1:]
def remove_url_path_xhtml_ending_if_present(path):
	return path.replace(".xhtml", "")