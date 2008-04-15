#!/usr/bin/env python2.4 

import urllib2
import urllib
import string
import xml.sax
import xml.dom.minidom
import encodings
import os
import unicodedata
import stat
import md5
import sys

apiurl="https://api.smugmug.com/hack/rest/1.1.1/"
apikey='sJQ4mAvri7ndkdxfTayx3Vhjw2R2CnzK'



albumdir='/path/to/photos'
password='USEYOUROWN'
address='USEYOUROWN@DOMAIN'

sys.setdefaultencoding('iso-8859-1')

def qp(s):
    return urllib.quote_plus( i88591e(norm(s)))

def norm(s):
    return unicodedata.normalize('NFKC',unicode(s))


def u8d(s):
   return encodings.codecs.utf_8_decode(s)[0]

def u8e(s):
   return encodings.codecs.utf_8_encode(s)[0]

def i88591e(s):
   return encodings.codecs.latin_1_encode(s)[0]

def getElement(x,path):
    for p in x.childNodes:
      if p.nodeName == path[0]:
      	 if len(path) == 1:
	    return p
	 else:
	    return getElement(p,path[1:])


def login():

  u=urllib2.urlopen(apiurl+'?method=smugmug.login.withPassword&EmailAddress=%s&Password=%s&APIKey=%s' % (qp(address),qp(password),apikey) )
  s=string.join(u.readlines(),'')
  x = xml.dom.minidom.parseString(s)

  s = getElement(x,['rsp','Login','SessionID'])
  r = s.childNodes[0].nodeValue 
  x.unlink()

  return r

def getAlbums(s):
  u=urllib2.urlopen(apiurl+'?method=smugmug.albums.get&SessionID=%s' % (s))
  s=string.join(u.readlines(),'')
  x = xml.dom.minidom.parseString(s)

  albums={}

  a = getElement(x,['rsp','Albums'])
  
  if not a or not a.childNodes:
     return {}

  for p in a.childNodes:
      if p.nodeName == 'Album':
      	 id = p.getAttribute('id')
	 attrs= {}

	 for q in p.childNodes:
	   if len(q.childNodes): 
	    attrs[q.nodeName] = norm(q.childNodes[0].nodeValue)
	 
	 albums[id] = attrs

  x.unlink()

  return albums

def createAlbum(s,n):
  u=urllib2.urlopen(apiurl+'?method=smugmug.albums.create&SessionID=%s&CategoryID=0&Title=%s&Public=0' % (s,qp(n)))
  s=string.join(u.readlines(),'')
  x = xml.dom.minidom.parseString(s)
  x.unlink()



def fixAlbum(s,id):
  u=urllib2.urlopen(apiurl+'?method=smugmug.album.changeSettings&SessionID=%s&AlbumID=%s&Public=0' % (s,id))


sessid=login()

al=getAlbums(sessid)


for p in al.keys():
  print p
  print al[p]
  fixAlbum(sessid,p)
  
