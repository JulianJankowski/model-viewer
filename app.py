from flask import Flask, render_template, url_for, redirect, request
import sqlite3
from DAO import load_models, save_tags, create_tag_assignments
from formatter import format_url
import json
import ast

app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        load_models()
        return redirect(url_for('home'))
    else:
        conn = get_db_connection()
        databaseModels = conn.execute('SELECT * FROM models').fetchall()
        databaseTags = conn.execute('SELECT * FROM tags').fetchall()
        conn.close
        models = []
        tags = []

        for databaseModel in databaseModels:
            model = {}
            model['id'] = databaseModel['id']
            model['name'] = databaseModel['name']
            model['url'] = url_for('static', filename=databaseModel['url'])
            model['filename'] = databaseModel['url'].split('/')[-1]
            model['folder_path'] = format_url(model['url'])
            models.append(model)

        for databaseTag in databaseTags:
            tagDict = {}
            tagDict['id'] = databaseTag['id']
            tagDict['name'] = databaseTag['name']
            tags.append(tagDict)

        return render_template("index.html",
            stl_viewer=url_for('static', filename='scripts/stl_viewer.min.js'),
            datatable_js=url_for('static', filename='scripts/DataTables/datatables.js'),
            datatable_css=url_for('static', filename='scripts/DataTables/datatables.css'),
            models=models,
            tags=tags,
            tags_url=url_for('manage_tags'))

@app.route("/tags", methods=['POST', 'GET'])
def manage_tags():
    if request.method == 'POST':
        tags = []
        tags.append((request.form.get('tagName'),))
        save_tags(tags)
        return redirect(url_for('manage_tags'))
    else:
        conn = get_db_connection()
        tags = conn.execute('SELECT * FROM tags').fetchall()
        conn.close
        return render_template("manage_tags.html",
            tags=tags)

@app.route("/model/<ident>", methods=['POST', 'GET'])
def singleView(ident):
    if request.method == 'POST':
        tagAssignments = {}
        tagAssignments['modelId'] = ident
        tagAssignments['tagIds'] = request.form.getlist('tags')
        try:
            create_tag_assignments(tagAssignments)
        except:
            pass
        return redirect(url_for('singleView', ident=ident))
    else:
        conn = get_db_connection()
        databaseModels = conn.execute('SELECT * FROM models WHERE id = ?', [ident]).fetchall()
        tags = conn.execute('SELECT * FROM tags').fetchall()
        tagAssignments = conn.execute('SELECT a.modelId, a.tagId, t.name, t.Id FROM tagAssignments a INNER JOIN tags t on t.Id = a.tagId WHERE modelId = ?', [ident]).fetchall()
        assignedTags = []
        for tag in tagAssignments:
            tagDict = {}
            tagDict['name'] = tag['name']
            tagDict['Id'] = tag['Id']
            assignedTags.append(tagDict)
        conn.close
        model = {}
        model['id'] = databaseModels[0]['id']
        model['name'] = databaseModels[0]['name']
        model['url'] = url_for('static', filename=databaseModels[0]['url'])
        model['folder_path'] = format_url(model['url'])
        return render_template('modelView.html',
            stl_viewer=url_for('static', filename='scripts/stl_viewer.min.js'),
            search_url=url_for('search'),
            model=model,
            tags=tags,
            assignedTags=assignedTags
        )

@app.route("/removeTag", methods=["POST"])
def removeTag():
    if request.method == "POST":
        tagId, modelId = request.form.get('delete').split('.')
        conn = get_db_connection()
        conn.execute('DELETE FROM tagAssignments WHERE tagId = ? AND modelId = ?', [tagId, modelId])
        conn.commit()
        conn.close
        return redirect(url_for('singleView', ident=modelId))

@app.route("/deleteTag", methods=["POST"])
def deleteTag():
    if request.method == "POST":
        tagId = request.form.get('delete')
        conn = get_db_connection()
        conn.execute('DELETE FROM tags WHERE Id = ?', tagId)
        conn.execute('DELETE FROM tagAssignments WHERE tagId = ?', tagId)
        conn.commit()
        conn.close
        return redirect(url_for('manage_tags'))

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == 'POST':
        formTags = request.form.getlist('tags')
        return redirect(url_for('searchTags', tags=formTags))
    conn = get_db_connection()
    databaseTags = conn.execute('SELECT * FROM tags').fetchall()
    conn.close
    tags = {}
    models = {}
    for dTag in databaseTags:
        tag = {}
        tag['Id'] = dTag['Id']
        tag['Name'] = dTag['name']
        tags[tag['Id']] = tag
    return render_template('search.html',
        tags=tags,
        models=models)

@app.route("/search/<tags>", methods=["POST", "GET"])
def searchTags(tags):
    if request.method == 'POST':
        formTags = request.form.getlist('tags')
        return redirect(url_for('searchTags', tags=formTags))
    conn = get_db_connection()
    databaseTags = conn.execute('SELECT * FROM tags').fetchall()
    tags = ast.literal_eval(tags)
    query = 'SELECT a.modelId, a.tagId, m.name, m.id, m.url FROM tagAssignments a INNER JOIN models m on m.Id = a.modelId WHERE a.tagId IN ({tag})'.format(
        tag=','.join(['?']*len(tags)))
    tagAssignments = conn.execute(query, tags).fetchall()
    conn.close
    tags = {}
    models = {}
    foundModels = []
    for dTag in databaseTags:
        tag = {}
        tag['Id'] = dTag['Id']
        tag['Name'] = dTag['name']
        tags[tag['Id']] = tag
    for tagA in tagAssignments:
        model = {}
        model['id'] = tagA['id']
        model['name'] = tagA['name']
        model['url'] = url_for('static', filename=tagA['url'])
        model['filename'] = tagA['url'].split('/')[-1]
        model['folder_path'] = format_url(model['url'])
        if (model['url'] in foundModels):
            models[model['id']]['tags'] += ', ' + tags[tagA['tagId']]['Name']
            continue
        model['tags'] = tags[tagA['tagId']]['Name']
        models[model['id']] = model
        foundModels.append(model['url'])
    return render_template('search.html',
        tags=tags,
        models=models)

@app.route("/settings", methods=['POST', 'GET'])
def settings():
    if request.method == 'POST':
        settings = {}
        settings['models_url'] = request.form.get('model_base_url')
        with open('settings.json', 'w') as outfile:
            outfile.write(json.dumps(settings, indent=4))
    f = open('settings.json')
    data = json.load(f)
    return render_template(
        'settings.html',
        current_url=data['models_url']
    )