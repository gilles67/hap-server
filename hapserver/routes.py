from flask import flash, redirect, render_template, url_for
from uuid import uuid4
from tinydb import Query
from hapserver import app, tydb
from hapserver.forms import WebradioForm

@app.route('/')
@app.route('/radio')
def radio_list():
	Webradio = Query()
	webras = tydb.search(Webradio.type == 'webradio')
	return render_template('webradio-list.html.j2', db=webras, title='Webradio', async_mode="eventlet")

@app.route('/radio/add', methods=['GET', 'POST'])
def radio_add():
	form = WebradioForm()
	if form.validate_on_submit():
		tydb.insert({'id': str(uuid4()), 'type': 'webradio', 'name': form.name.data, 'url': form.url.data})
		return redirect(url_for('radio_list'))
	return render_template('webradio-add.html.j2', form=form, title='Add Radio', async_mode="eventlet")

@app.route('/radio/<id>/delete')
def radio_delete(id):
	return redirect(url_for('radio_list'))

@app.route('/radio/<id>/edit', methods=['GET', 'POST'])
def radio_edit(id):
	Webradio = Query()
	webra = tydb.get(Webradio.id == id)
	form = WebradioForm()
	if form.validate_on_submit():
		tydb.update({'name': form.name.data, 'url': form.url.data}, Webradio.id == id)
		return redirect(url_for('radio_list'))
	else:
		form.name.data = webra['name']
		form.url.data = webra['url']
	return render_template('webradio-add.html.j2', form=form, title=("Edit Radio: %s" % webra['name']), async_mode="eventlet")
