from google.appengine.ext import db, blobstore
####################### DB Models #######################
class Epub(db.Model):
    created         = db.DateTimeProperty(auto_now_add = True)
    epoch           = db.FloatProperty()
    file_url        = db.StringProperty()
    file_blob_key   = blobstore.BlobReferenceProperty()
    filename        = db.StringProperty()

class Cover(db.Model):
    created         = db.DateTimeProperty(auto_now_add = True)
    epoch           = db.FloatProperty()
    file_url        = db.StringProperty()
    file_blob_key   = blobstore.BlobReferenceProperty()
    filename        = db.StringProperty()
#########################################################