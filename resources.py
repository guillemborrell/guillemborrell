# -*- coding: utf-8 -*-
'''
Created on Feb 9, 2014

@author: guillem
'''
import webapp2
import json
import string
import logging
import re, datetime
import xml.etree.ElementTree as ET
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from models import Article, Comment
from google.appengine.api import mail
from google.appengine.api import memcache

ITEMS_PER_PAGE = 6

class ArchiveResource(webapp2.RequestHandler):
    def get(self):
        archive = memcache.get('archive')
        if archive is not None:
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'articles':archive}))

        else:
            more = True
            archive =  list()
            curs = None
            
            while more:
                articles, curs, more = Article.query(
                ).order(-Article.when).fetch_page(50, start_cursor=curs)
                for article in articles:
                    d = article.as_dict()
                    archive.append(
                        {'title': d['title'],
                         'ncomments': len(d['comments']),
                         'when': d['when'],
                         'key': d['key']}
                    )
                     
            memcache.add('archive',archive,time=86400)
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'articles':archive}))
    

class ArticleResource(webapp2.RequestHandler):
    def get(self):
        article = ndb.Key(urlsafe = self.request.get('key')).get()
            
        if article:
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(article.as_dict()))

    def post(self):
        d = json.loads(self.request.body)
        if d['secret'] == '16jutges16':
            if 'key' in d and len(d['key']) > 10: #Keys are looong.
                article = ndb.Key(urlsafe = d['key']).get()
                logging.info('Modifying entry {}'.format(d['key']))
            else:
                article = Article()

            article.slug     = d['slug']
            article.title    = d['title']
            article.text     = d['text']
            if 'when' in d:
                # Matches isoformat into datetime object. Found in stackoverflow
                article.when = datetime.datetime(
                    *map(int, re.split('[^\d]', d['when'])[:-1])
                )
            else:
                article.when = datetime.datetime.now()

            try:
                article.keywords = string.split(d['keywords'])
            except AttributeError:
                article.keywords = d['keywords']
            
            article.put()

    def delete(self):
        article = ndb.Key(urlsafe = self.request.get('key')).get()
        secret = self.request.get('secret')

        if secret == '16jutges16':
            logging.info('Removing entry {}'.format(article.key.urlsafe()))
            article.key.delete()


class ArticleKeyFromSlugResource(webapp2.RequestHandler):
    def get(self):
        # An if that is just a router.
        # Ask for a key, return the article in json format

        if self.request.get('slug'):
            slug = self.request.get('slug')
            self.response.out.write(Article.key_from_slug(slug))


class ArticleListResource(webapp2.RequestHandler):
    '''
    classdocs
    '''           
    # Ask for a page, return a list of keys as a json list, 
    # to be processed by the client
    def get(self):
        if self.request.get('p'):
            curs = Cursor(urlsafe=self.request.get('p'))
            articles, curs, more = Article.query().order(
                -Article.when).fetch_page(ITEMS_PER_PAGE, start_cursor=curs)
            
            if more:
                curs = curs.urlsafe()
                
            else:
                curs = None
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(
                json.dumps(
                    {'articles': [a.as_dict() for a in articles],
                     'next': curs,
                     'more': more}
                )
            )
            
        # If nothing is queried, return initial page.
        # TODO: merge those two conditionals.
        else:
            articles, curs, more =  Article.query().order(
                -Article.when).fetch_page(ITEMS_PER_PAGE)
            
            if more:
                curs = curs.urlsafe()
                
            else:
                curs = None
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(
                json.dumps(
                    {'articles': [a.as_dict() for a in articles],
                     'next': curs,
                     'more': more}
                )
            )        


class ArticleLastRSS(webapp2.RequestHandler):
    def get(self):
        articles, curs, more = Article.query().order(
            -Article.when).fetch_page(ITEMS_PER_PAGE)
        
        self.response.out.headers['Content-Type'] = 'application/rss+xml'
        self.response.out.write('<?xml version="1.0" encoding="UTF-8" ?>')

        rss = ET.Element('rss')
        rss.set('version','2.0')
        channel = ET.SubElement(rss,'channel')
        ET.SubElement(channel,
                      'title').text = 'I HAVE BECOME CONFORTABLY NUMB. Guillem Borrell et al.'
        ET.SubElement(channel,
                      'description').text = 'Blog de Guillem Borrell'
        ET.SubElement(channel,
                      'link').text = 'http://guillemborrell.es/'
        ET.SubElement(channel,
                      'lastBuildDate').text = datetime.datetime.now().strftime(
                            '%a, %d %b %Y %H:%M:%S %z')
        ET.SubElement(channel,
                      'pubDate').text = datetime.datetime.now().strftime(
                               '%a, %d %b %Y %H:%M:%S %z')
        ET.SubElement(channel,
                      'ttl').text = '1800'

        items = []
        for i,article in enumerate(articles):
            items.append(ET.SubElement(channel,'item'))
            ET.SubElement(items[i],'title').text=article.title
            ET.SubElement(items[i],'description').text= article.text
            ET.SubElement(items[i],'link').text='http://guillemborrell.es/article/{}'.format(article.key.urlsafe())
            ET.SubElement(items[i],'guid').text=article.key.urlsafe()
            ET.SubElement(items[i],'pubDate').text=article.when.strftime(
                '%a, %d %b %Y %H:%M:%S %z')
            
        self.response.out.headers['Content-Type'] = 'application/rss+xml'
        self.response.out.write(ET.tostring(rss))


class CommentResource(webapp2.RequestHandler):
    '''
    classdocs
    '''
    def get(self):
        if self.request.get('key'):
            comment = ndb.Key(urlsafe = self.request.get('key')).get()
            
            if comment:
                self.response.out.headers['Content-Type'] = 'application/json'
                self.response.out.write(json.dumps(comment.as_dict()))
                
            else:
                self.abort(404)
        
        elif self.request.get('article'):
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(
                json.dumps(
                    Comment.from_article(self.request.get('article'))
                )
            )
            
        else:
            self.abort(404)
    
    def post(self):
        d = json.loads(self.request.body)
        if d['safety'] == 'Borrell':
            if 'when' in d:
                # Matches isoformat into datetime object. Found in stackoverflow
                d['when'] = datetime.datetime(
                    *map(int, re.split('[^\d]', d['when'])[:-1])
                )
            else:
                d['when'] = datetime.datetime.now()
                parent = ndb.Key(urlsafe = d['parent'])
                comment = Comment(parent = parent,
                                  author = d['author'],
                                  text = d['text'],
                                  when = d['when'])
            
                comment.put()
                
                #Send mail to me.
                mail.send_mail(
                    sender="guillemborrell@gmail.com",
                    to="Guillem Borrell <guillemborrell@gmail.com>",
                    subject="Nuevo comentario en el blog de Guillem Borrell",
                    body=u"""
Déu vos guard.

Nou comentari a http://www.guillemborrell.es/article/{}

{} | {}

{}
                    """.format(d['parent'],
                               d['author'],
                               d['when'].isoformat(),
                               d['text'])
                )
