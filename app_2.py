from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app_2 = Flask(__name__)
app_2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app_2)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Tasl %r>' % self.id


@app_2.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.drop_all()
            db.create_all()
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'ERORKA BRUH!!! LOL!!!1!'
    else:
        tasks = Todo.query.order_by(Todo.content).all()
        return render_template('index.html', tasks=tasks)

@app_2.route('/search')
def searching():
    args = request.args
    print(args)
    return "No query string received", 200


if __name__ == '__main__':
    app_2.run()