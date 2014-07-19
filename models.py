'''
Created on Feb 8, 2014

@author: guillem
'''
from google.appengine.ext import ndb

class Article(ndb.Model):
    '''
    classdocs
    '''
    title = ndb.StringProperty()
    slug = ndb.StringProperty()
    keywords = ndb.StringProperty(repeated=True)
    text = ndb.TextProperty()
    when = ndb.DateTimeProperty(auto_now_add=True)

        
    def as_dict(self):
        return {'title': self.title,
                'slug' : self.slug,
                'keywords': self.keywords,
                'text': self.text,
                'when': self.when.isoformat(),
                'key': self.key.urlsafe(),
                'comments':Comment.from_article(self.key.urlsafe())}

    @classmethod
    def key_from_slug(cls,slug):
        try:
            return cls.query(cls.slug==slug).fetch(1)[0].key.urlsafe()
        except IndexError:
            return ""

    
class Comment(ndb.Model):
    author = ndb.StringProperty()
    text = ndb.TextProperty()
    when = ndb.DateTimeProperty()
    
    def as_dict(self):
        return {'author': self.author,
                'text': self.text,
                'when': self.when.isoformat()}
    
    @classmethod
    def from_article(cls,article):
        key = ndb.Key(urlsafe=article)
        return [c.as_dict() for c in cls.query(ancestor=key).order(-cls.when)]

