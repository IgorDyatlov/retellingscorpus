from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import random
import re
import pymorphy2
import os
from nlp_project_final import morph, corpus, pos_translation, all_lemmas, all_words, all_POS, single_word_search, \
    collocation_search, search

import json
with open('data-20160406T0100.json', 'r', encoding='utf-8') as file:
    text = file.read()
text_loaded = json.loads(text)

ips = dict()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nemo.db'
db = SQLAlchemy(app)
db.drop_all()
db.create_all()

class Nemo(db.Model):
    number = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(200), nullable=True)
    book = db.Column(db.String(200), nullable=True)
    content = db.Column(db.String(2000), nullable=False)

    def __repr__(self):
        return '<Sentence %r>' % self.number


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    #global name
    if request.method == 'POST':
        #if 'name' in globals():
            #os.remove(name)
        if request.remote_addr in ips:
            del ips[request.remote_addr]
        try:
            db.drop_all()
            db.create_all()
            sentence_content = request.form['content']
            list_for_df = list()
            #for one in text_loaded:
                #if one['District'] == str(sentence_content):
                    #my_things = Nemo(author=str(one['Location']), book=str(one['AdmArea']), content=sentence_content)
                    #list_for_df.append([str(one['Location']), str(one['AdmArea']), sentence_content])
                    #db.session.add(my_things)
                    #db.session.commit()
            for i in search(request.form['content']):
                for j in i[1].keys():
                    title = i[0]['meta']['title']
                    author = i[0]['meta']['author']
                    sentence = i[0]['sentences'][j]['text']
                    my_things = Nemo(author=author, book=title, content=sentence)
                    list_for_df.append([author, title, sentence])
                    db.session.add(my_things)
                    db.session.commit()
                    continue
            df = pd.DataFrame(list_for_df, columns=['Автор', 'Произведение', 'Предложение'])
            df.drop_duplicates()
            #name = str(sentence_content + str(random.randint(1, 50)) + '.csv')
            sentence_content_re = re.sub('"', '', sentence_content)
            ips[request.remote_addr] = str(sentence_content_re + str(random.randint(1, 50)) + '.csv')
            #df.to_csv(name, encoding='utf-8')
            df.to_csv(ips[request.remote_addr], encoding='utf-8')
            return redirect('/')
        except:
            return 'ERORKA BRUH!!! LOL!!!1!'
    else:
        sentences = Nemo.query.order_by(Nemo.content).all()
        return render_template('index.html', tasks=sentences)

@app.route('/download')
def downloading():
    #global name
    try:
        #return send_file(name, as_attachment=True)
        return send_file(ips[request.remote_addr], as_attachment=True)
    except:
        return redirect('/')



if __name__ == '__main__':
    app.run()
