from flask import Flask, render_template, json, request,redirect,session
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import re
import jieba
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()



app = Flask(__name__)


# MySQL configurations
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = ''
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = ''
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def getList():

        cursor = mysql.get_db().cursor()
        cursor.execute('select distinct column_id,column_title from ' )
        columns = [dict(id=row[0], title=row[1]) for row in cursor.fetchall()]
        art=1
        try:
            request.args['art']
        except:
            art=0
        col=1
        try:
            request.args['col']
        except:
            col=0


        if art==1 and col==1  :
            cursor.execute('select   html,comment from  where id='+request.args['art'] )
            content=''
            comment=''
            for row in cursor.fetchall():
                content = row[0]
                comment=row[1]
            print(comment)
            #result = re.search('(<head>.*)</html>', content,re.S)
            #content =(result.group(1))
            #content=content.replace('"img/','"static/img/')
            #content=content.replace('"font/','"static/font/')

            soup = BeautifulSoup(content, 'lxml')
            soup=soup.find(class_='article-body')

            string=soup.get_text()


            d=cutworld(string)


            cursor.execute('select   id,title,column_id from  where column_id='+request.args['col'])
            articles = [dict(id=row[0], title=row[1], cid=row[2]) for row in cursor.fetchall()]
            for article in articles:
                cid=article.get('cid')
            return render_template('index.html', columns=columns,articles=articles,content=content ,comment=comment,col=cid,wc=d)
        if col==1 and art==0 :
            cursor.execute('select   id,title,html from  where column_id='+request.args['col'])
            #articles = [dict(id=row[0], title=row[1],html=row[2]) for row in cursor.fetchall()]
            string=''
            articles=[]
            for row in cursor.fetchall() :
                articles.append(dict(id=row[0], title=row[1]))
                soup = BeautifulSoup(row[2], 'lxml')
                soup=soup.find(class_='article-body')
                string=string+soup.get_text()

            d=cutworld(string)

            return render_template('index.html', columns=columns,col=request.args['col'],articles=articles,wc=d)

        return render_template('index.html', columns=columns)


def cutworld(string):
    result = jieba.lcut(string)
    c = Counter()
    for x in result:
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    print('常用词频度统计结果')
    d=[]
    for (k,v) in c.most_common(20):
        d.append('%s%s %s  %d' % ('  '*(5-len(k)), k, '*'*int(v/10), v))
    return d

@app.route('/search')
def search():
    keyword=1
    try:
        request.args['keyword']
    except:
        keyword=0
    if keyword==0:
        return render_template('search.html')
    else:
        res = es.search(index="test-index", body={"query": {"match_all": {}}})

        ress=res['hits']['hits']

        return render_template('search.html',keyword=request.args['keyword'],ress=ress)

if __name__ == "__main__":
    app.run()
