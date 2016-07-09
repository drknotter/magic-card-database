#!/usr/bin/python

import sqlite3, re, time, string, traceback

def cardmatch(expr, match_type, item):
    try:
        if item is None:
            return None
        if match_type == 'number':
            if( re.search('\*',item) ):
                return False
            item = re.sub('{1/2}','.5',item)
            if expr[0] == '>':
                return float(expr[1:]) < float(item)
            elif expr[0] == '<':
                return float(expr[1:]) > float(item)
            else:
                return float(expr) == float(item)
        elif match_type == 'regex':
            if expr[0:2] == 'r/':
                reg = re.compile(expr[2:])
            else:
                reg = re.compile(expr,re.I)
            return reg.search(item) is not None

        elif match_type == 'exact':
            return expr == item

        elif match_type == 'mana':

            itemsplit = re.split('\{([^\}]+)\}',item)[1::2]
            if expr[0] == '>' or expr[0] == '<':
                exprsplit = re.split('\{([^\}]+)\}',expr[1:])
            else:
                exprsplit = re.split('\{([^\}]+)\}',expr)

            symbols = []
            for i in exprsplit[0::2]:
                if isinstance(i,unicode):
                    for letter in i:
                        symbols.append(letter)
            symbols.extend(exprsplit[1::2])

            exprfreq = dict([(i, symbols.count(i)) for i in set(symbols)])
            itemfreq = dict([(i, itemsplit.count(i)) for i in set(itemsplit)])

            if expr[0] == '>':
                for symbol in exprfreq:
                    if re.search('^\d+$',symbol):
                        flag = False
                        for s in itemfreq:
                            if re.search('^\d+$',s):
                                flag = True
                                if int(s) < int(symbol):
                                    return None
                        if flag == False:
                            return None
                    elif symbol not in itemfreq.keys() or itemfreq[symbol] < exprfreq[symbol]:
                        return None
                return True
            elif expr[0] == '<':
                for symbol in itemfreq:
                    if re.search('^\d+$',symbol):
                        flag = False
                        for s in exprfreq:
                            if re.search('^\d+$',s):
                                flag = True
                                if int(s) < int(symbol):
                                    return None
                        if flag == False:
                            return None
                    elif symbol not in exprfreq.keys() or exprfreq[symbol] < itemfreq[symbol]:
                        return None
                return True
            else:
                return exprfreq == itemfreq

        return None
    except:
        print 'Exception: badly formatted search term:',expr
        print traceback.print_exc()
        return None
        
if __name__ == '__main__':
    db_conn = sqlite3.connect('mtg.db');
    db_conn.create_function("CARDMATCH", 3, cardmatch)
    db_conn.row_factory = sqlite3.Row
    db_cursor = self.db_conn.cursor();

    db_cursor.execute(stmt)
    results = self.db_cursor.fetchall()
