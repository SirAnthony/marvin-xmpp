
import urllib
import urllib2

def goUrl(url, params={}, post=False, cookies={}):
    query = None
    if len(params):
        query = urllib.urlencode(dict([k.encode('utf-8'),unicode(v).encode('utf-8')] for k,v in params.items()))
    if not post and query:
        url = url + query
        query = None
    request = urllib2.Request(url, query, {'UserAgent': 'Mozilla/5.0 (compatible; Marvin/0.7; http://github.com/SirAnthony/marvin-xmpp)'})
    if cookies:
        request.add_header("Cookie", ';'.join(['='.join((name, value)) for name, value in cookies.iteritems()]) + ";")
    result = urllib2.urlopen(request)
    return result.read()
    