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



albumdir='/path/to/photos/'
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



def getImages(s,id):
  u=urllib2.urlopen(apiurl+'?method=smugmug.images.get&SessionID=%s&AlbumID=%s&' % (s,id))
  s=string.join(u.readlines(),'')
  x = xml.dom.minidom.parseString(s)

  images={}
  i = getElement(x,['rsp','Images'])

  if not i or not i.childNodes:
    return {}

  for p in i.childNodes:
      if p.nodeName == 'Image':
      	 id = p.getAttribute('id')
	 attrs= {}

	 for q in p.childNodes:
	   if len(q.childNodes): 
	    attrs[q.nodeName] = norm(q.childNodes[0].nodeValue)
	 
	 images[id] = attrs

  x.unlink()

  return images


def getImageInfo(sessid, imageId):
  u=urllib2.urlopen(apiurl+'?method=smugmug.images.getInfo&SessionID=%s&ImageID=%s&' % (sessid,imageId))
  s=string.join(u.readlines(),'')
  x = xml.dom.minidom.parseString(s)

  images={}
  i = getElement(x,['rsp','Info'])

  kl = i
  #raise IOError("")

  if not i or not i.childNodes:
    return {}

  for p in i.childNodes:

      if p.nodeName == 'Image':
      	 id = p.getAttribute('id')
	 attrs= {}

	 for q in p.childNodes:
	   if len(q.childNodes): 
	    attrs[q.nodeName] = norm(q.childNodes[0].nodeValue)
	 
	 images[id] = attrs

  x.unlink()

  return images
    


def uploadAlbum(sessid,albumid,album):
    i = getImages(sessid, albumid)

    captions = {}
    for p in open('./'+album+'/.captions').readlines():
    	p=p.strip()
	ip=p.find(' ---- ')
	if ip != -1:
	   captions[ norm(u8d(p[:ip])) ] = norm(u8d(p[ip+6:]))

    inamed = {} 
    for p in i.keys():
       istruct = getImageInfo(sessid, p)

       inamed[ norm(istruct[p]['FileName'] )] = istruct[p]
       #print istruct
    

    for f in os.listdir('./'+album+'/large/'):
      fname='./'+album+'/large/'+f
      fn = norm(u8d(f))
 
      m = md5.new()

      for p in open(fname).readlines():
        m.update(p)

      if fn not in inamed.keys() or m.hexdigest() != inamed[fn]['MD5Sum']:
        if fn in captions.keys():
    	  uploadImage(sessid,albumid, fname, fn,captions[fn])
	else:
	  uploadImage(sessid,albumid,fname,fn)



def uploadImage(sessid,albumid,file,fname,caption=''):
    m = md5.new()
    filedata = open(file).read(2000000000)   
    m.update(filedata)

    #print fname
    #print caption
    print "%s -- %s" % (u8e(fname),u8e(caption))

    headers={}
    headers['Content-Length']=len(filedata)
    headers['Content-MD5']=m.hexdigest()
    headers['X-Smug-SessionID']=sessid
    headers['X-Smug-Version']='1.1.1'
    headers['X-Smug-ResponseType']='REST'
    headers['X-Smug-AlbumID']=albumid
    headers['X-Smug-FileName']=i88591e(fname)

    if caption:
      headers['X-Smug-Caption']=i88591e(caption)
  
    r = urllib2.Request(url='http://upload.smugmug.com/photos/xmlrawadd.mg', data=filedata, headers=headers)
    u=urllib2.urlopen(r)

    #raise IOError

sessid=login()

al=getAlbums(sessid)

titled = {}
for p in al.keys():
  titled[ norm(al[p]['Title']) ] = p

os.chdir(albumdir)

f=''

for p in os.listdir('.'):
  try:
     if stat.S_ISDIR(os.stat(p)[stat.ST_MODE]):
        print "%s is a directory." % p
        if norm(u8d(p)) not in titled.keys():
           print "New album"
   	   f = u8d(p)
   	   createAlbum(sessid,u8d(p))
        else:
           uploadAlbum(sessid, titled[norm(u8d(p))],p)
  except IOError,e:
        print e
	pass 	
  except OSError,e:
        print e
	pass 	

