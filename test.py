import time
from itertools import chain
import email
import imaplib
import base64
import os
import re

imap_ssl_host = 'imap.gmail.com'
imap_ssl_port = 993
username = 'allesinklusive@t-online.de'
password = 'Senderstadt'

criteria = {}
uid_max = 0

def search_string(uid_max, criteria):
    c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items())) + [('UID', '%d:*' % (uid_max+1))]
    return '(%s)' % ' '.join(chain(*c))

mail = imaplib.IMAP4_SSL(imap_ssl_host)
mail.login(username, password)
#select the folder
mail.select('inbox')

result, data = mail.uid('SEARCH', None, search_string(uid_max, criteria))
uids = [int(s) for s in data[0].split()]
if uids:
    uid_max = max(uids)
mail.logout()
