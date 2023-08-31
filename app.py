import sys
import os
import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

app.config['SECRET_KEY'] = 'Mavericks39!'

hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

@app.route('/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('Introduce una url por favor')
            return redirect(url_for('index'))
            
        if len(url) < len("https://partemelofinito.com/xxxx"):
            flash('Esta url no es necesario acortarla, es más corta que la que podemos ofrecerte')
            return redirect(url_for('index'))
        
        url_data = conn.execute('INSERT INTO urls (original_url) VALUES (?)',
                                (url,))
        
        conn.commit()
        conn.close()

        url_id = url_data.lastrowid
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url)
    
    return render_template('index.html')

@app.route('/<id>')
def url_redirect(id):
    conn = get_db_connection()

    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = conn.execute('SELECT original_url, clicks FROM urls'
                                ' WHERE id = (?)', (original_id,)
                                ).fetchone()
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        conn.execute('UPDATE urls SET clicks = ? WHERE id = ?',
                     (clicks+1, original_id))

        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))
     

@app.route('/css')
def root_path():
    # Infer the root path from the run file in the project root (e.g. manage.py)
    fn = getattr(sys.modules['__main__'], '__file__')
    root_path = os.path.abspath(os.path.dirname(fn))
    return root_path

print(root_path())


if __name__ == "__main__":
    app.run(host='localhost', port=5010, debug=True)