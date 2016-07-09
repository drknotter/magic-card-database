#! /usr/bin/python

import urllib, urllib2, re, string, subprocess, sys, sqlite3
from BeautifulSoup import BeautifulSoup, NavigableString
from datetime import datetime

class CardGroup(list):

    def __init__(self, multiverseid=1):

        # ********** get list of ids **********
        content = urllib2.urlopen('http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=%i' % multiverseid).read()
        soup = BeautifulSoup(content);
        labels = soup.findAll('div',{'class':'label'})
        values = soup.findAll('div',{'class':'value'})

        ids = list()
        for index in range(len(labels)):
            if( re.search('All Sets',labels[index].prettify()) != None ):
                ids.extend(map(lambda tag: re.sub('Details\.aspx\?multiverseid=(\d+)','\g<1>',tag['href']), values[index].findAll('a',{'href':re.compile('Details\.aspx\?multiverseid=\d+')})))
        if( len(ids) == 0 ):
            for index in range(len(labels)):
                if( re.search('Expansion',labels[index].prettify()) != None ):
                    ids.extend(map(lambda tag: re.sub('Details\.aspx\?multiverseid=(\d+)','\g<1>',tag['href']), values[index].findAll('a',{'href':re.compile('Details\.aspx\?multiverseid=\d+')})))
                if( re.search('Other Sets',labels[index].prettify()) != None ):
                    ids.extend(map(lambda tag: re.sub('Details\.aspx\?multiverseid=(\d+)','\g<1>',tag['href']), values[index].findAll('a',{'href':re.compile('Details\.aspx\?multiverseid=\d+')})))

        for mid in ids:

            sys.stderr.write('  working on %s\n' % mid)

            content = urllib2.urlopen('http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=%s' % mid).read()
            soup = BeautifulSoup(content);
            labels = soup.findAll('div',{'class':'label'})
            values = soup.findAll('div',{'class':'value'})

            ncols = len(soup.findAll('td',{'class':'rightCol'}))
            indices = [0]
            for i in range(ncols-1):
                indices.append(map(lambda tag: reduce(lambda a,i: a+unicode(i), tag.contents).strip(), labels)[indices[-1]+1:].index('Card Name:'))
            for i in range(len(indices)-1):
                sublabels = labels[indices[i]:indices[i+1]]
                subvalues = values[indices[i]:indices[i+1]]
                self.append(self.create_card_dict(sublabels,subvalues))
            self.append(self.create_card_dict(labels[indices[-1]:],values[indices[-1]:]))
            
            multipart = map(lambda tag: tag['href'], soup.findAll('a',{'href':re.compile('part=')}))
            for part in multipart:
                content = urllib2.urlopen('http://gatherer.wizards.com'+part).read()
                soup = BeautifulSoup(content);
                labels = soup.findAll('div',{'class':'label'})
                values = soup.findAll('div',{'class':'value'})

                ncols = len(soup.findAll('td',{'class':'rightCol'}))
                indices = [0]
                for i in range(ncols-1):
                    indices.append(map(lambda tag: reduce(lambda a,i: a+unicode(i), tag.contents).strip(), labels)[indices[-1]+1:].index('Card Name:'))
                for i in range(len(indices)-1):
                    sublabels = labels[indices[i]:indices[i+1]]
                    subvalues = values[indices[i]:indices[i+1]]
                    self.append(self.create_card_dict(sublabels,subvalues))
                self.append(self.create_card_dict(labels[indices[-1]:],values[indices[-1]:]))
            
    def create_card_dict(self,labels,values):

        labels = map(lambda tag: reduce(lambda a,i: a+unicode(i), tag.contents).strip(), labels)
        values = map(lambda tag: reduce(lambda a,i: a+unicode(i), tag.contents).strip(), values)

        # add multiverseid to labels and values
        for index in range(len(labels)):
            if( re.search('Expansion:',labels[index]) ):
                multiverseid = re.search('Details\.aspx\?multiverseid=([^"]+)',values[index])
                labels.append(u'multiverseid')
                values.append(multiverseid.group(1))
                break;


        # fix the labels
        labels = map(lambda l: re.sub('(:|\s+|/)','',l.lower()), labels)
        labels = map(lambda l: re.sub('#','num',l.lower()), labels)

        # fix the values
        values = map(lambda v: re.sub('<img src=\"/Handlers/Image\.ashx\?size=[^&]*&amp;name=([^&]+)&amp;type=symbol\" alt=\"[^\"]+\" align=\"absbottom\" />','{\g<1>}',v), values)
        values = map(lambda v: re.sub('</?(i|a|span|br)[^>]*>','',v), values)
        values = map(lambda v: re.sub('<div class="cardtextbox">([^<]+)</div>','<item>\g<1></item>',v), values)
        values = map(lambda v: re.sub('<[/]?(div)[^>]*>','',v), values)
        values = map(lambda v: re.sub('&nbsp;',' ',v), values)
        values = map(lambda v: v.strip(), values)

        d = dict(zip(labels,values))

        # fix the dictionary
        if( 'allsets' in d ):
            del d['allsets']

        if( 'othersets' in d ):
            del d['othersets']

        if( 'communityrating' in d ):
            m = re.search('Rating: ([^\s]+) / ([^\s]+)  \(([^\s]+) votes?\)',d['communityrating'])
            d[u'rating'] = u'%s/%s' % m.group(1,2)
            d[u'votes'] = u'%s' % m.group(3)
            del d[u'communityrating']

        if( 'pt' in d ):
            m = re.search('([^\s]+) / ([^\s]+)',d['pt'])
            d[u'power'] = m.group(1)
            d[u'toughness'] = m.group(2)
            del d['pt']

        if( 'types' in d ):
            split = re.split(unichr(8212),d['types'],re.UNICODE)
            d[u'type'] = split[0].strip()
            if( len(split) == 2 ):
                d[u'subtype'] = split[1].strip()
            del d['types']            

        return d
# ********** end CardGroup **********

def make_sqlite_stmt(card):
    keys = reduce(lambda a,k: a+','+k,card.keys(),'')[1:]
    values = reduce(lambda a,v: a+',\''+v.replace("'","''")+'\'',card.values(),'')[1:]
    return 'insert or ignore into cards ('+keys+') values ('+values+')'

# ********** end make_sqlite_stmt **********

try:

    content = urllib2.urlopen('http://gatherer.wizards.com/Pages/Search/Default.aspx?page='+sys.argv[1]+'&output=compact&action=advanced&cmc=+%3E%3d%5b0%5d').read()
    s = re.findall("\<a id=\"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl00_listRepeater_ctl\d\d_cardTitle\" onclick=\"return CardLinkAction\(event, this, \'SameWindow\'\);\" href=\"../Card/Details.aspx\?multiverseid=(\d+)\">.*?</a>",content)

    conn = sqlite3.connect('mtg.db')
    cursor = conn.cursor()

    for multiverseid in s:

        multiverseid = int(multiverseid)
        sys.stderr.write("processing multiverseid "+str(multiverseid)+"\n")
        group = CardGroup(multiverseid)
        for card in group:
            cursor.execute(make_sqlite_stmt(card))

    conn.commit()

except:
    sys.stderr.write("Whoops! Exception!\n")
    raise
    sys.exit(1)

sys.exit(0)
