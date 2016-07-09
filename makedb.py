#! /usr/bin/python

import re, sqlite3

def regexp(expr, item):
    reg = re.compile(expr);
    return reg.search(item) is not None;

conn = sqlite3.connect('mtg.db');
conn.create_function("REGEXP", 2, regexp);

c = conn.cursor();

c.execute('create table cards (multiverseid text, cardname text, manacost text, convertedmanacost text, type text, subtype text, cardtext text, flavortext text, power text, toughness text, expansion text, rarity text, loyalty integer, cardnum text, artist text, colorindicator text, rating text, votes text, watermark text)');

conn.commit()

c.close()

