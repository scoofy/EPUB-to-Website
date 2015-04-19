# hashing functions

####################### Cookies
secret = do_not_copy.secret()
def make_secure_val(val):
    return "%s|%s" %(val, hmac.new(secret,val).hexdigest())
def check_secure_val(secure_val):
    val = secure_val.split("|")[0]
    if secure_val == make_secure_val(val):
        return val
    else:
        return None
def check_secure_bool(secure_val):
    val = secure_val.split("|")[0]
    if secure_val == make_secure_val(val):
        return True
    else:
        return False
####################### Bcrypt
def make_pw_hash(name, pw, salt=None):
    name = name.lower()
    if not salt:
        salt = bcrypt.gensalt(4) # this should be 10-12
    pw_hashed = bcrypt.hashpw(name + pw, salt)
    return '%s|%s' % (pw_hashed, salt)
def valid_pw(name, pw, h):
    name = name.lower()
    return h == make_pw_hash(name, pw, h.split('|')[1])
def make_pw_reset_hash(the_string, salt=None):
    if not salt:
        salt = bcrypt.gensalt(2) # this should be 10-12
    pw_hashed = bcrypt.hashpw(the_string, salt)
    return '%s|%s' % (pw_hashed, salt)
def valid_pw_reset_string(the_string, h):
    return h == make_pw_hash(the_string, h.split('|')[1])
def get_verified_user(username, password):
    query = User.gql('WHERE username=:username', username=username)
    user = query.get()
    if user:
        if valid_pw(username, password, user.password):
            return user
####################### Misc Hash
def users_key(group = "default"):
    return db.Key.from_path('users', group)
def gen_verify_hash(user):
    user_hash = hashlib.sha256(user.random_string).hexdigest()
    return user_hash
#########################################################