from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import random
import re
from nlp_project_final import search

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
    if request.method == 'POST':
        if request.remote_addr in ips:
            del ips[request.remote_addr]
        try:
            db.drop_all()
            db.create_all()
            sentence_content = request.form['content']
            list_for_df = list()
            count = 0
            for i in search(request.form['content']):
                for j in i[1].keys():
                    count += 1
                    number = count
                    title = i[0]['meta']['title']
                    author = i[0]['meta']['author']
                    sentence = i[0]['sentences'][j]['text']
                    my_things = Nemo(number=number, author=author, book=title, content=sentence)
                    list_for_df.append([number, author, title, sentence])
                    db.session.add(my_things)
                    db.session.commit()
                    continue
            df = pd.DataFrame(list_for_df, columns=['Номер', 'Автор', 'Произведение', 'Предложение'])
            df.drop_duplicates()
            sentence_content_re = re.sub('"', '', sentence_content)
            ips[request.remote_addr] = str(sentence_content_re + str(random.randint(1, 50)) + '.csv')
            df.to_csv(ips[request.remote_addr], encoding='utf-8')
            return redirect('/')
        except:
            return redirect('/')
    else:
        sentences = Nemo.query.order_by(Nemo.content).all()
        return render_template('index.html', tasks=sentences)

@app.route('/download')
def downloading():
    try:
        return send_file(ips[request.remote_addr], as_attachment=True)
    except:
        return redirect('/')



if __name__ == '__main__':
    app.run()
