import sqlite3
import os
import json

def load_models():
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()

    dirmodels = []
    for path, subdirs, file in os.walk(get_models_url()):
        for name in file:
            if name.split('.')[-1] == 'stl':
                model = os.path.join(path, name)
                dirmodels.append(model.split('static/')[1])

    connection.row_factory = sqlite3.Row
    models = connection.execute('SELECT * FROM models').fetchall()
    databaseModels = []
    for model in models:
        databaseModels.append(model['url'])

    toInsert = []
    for model in dirmodels:
        if (model in databaseModels):
            continue
        toInsert.append((model.split('/')[-1].split('.')[:-1][0], model))

    cur.executemany("INSERT INTO models (name, url) VALUES (?, ?)", toInsert)

    toDelete = []
    models = connection.execute('SELECT * FROM models').fetchall()
    for model in models:
        if model['url'] not in dirmodels:
            toDelete.append((model['url'],))

    if (len(toDelete) > 0):
        cur.executemany("DELETE FROM models WHERE url = ?", toDelete)

    connection.commit()
    connection.close()

def save_tags(tags):
    connection = sqlite3.connect('database.db')
    connection.cursor().executemany("INSERT INTO tags (name) VALUES (?)", tags)
    connection.commit()
    connection.close()

def create_tag_assignments(assignments):
    tagAssignments = []
    modelId = assignments['modelId']
    for tagId in assignments['tagIds']:
        tagAssignments.append((modelId, tagId))

    connection = sqlite3.connect('database.db')
    connection.cursor().executemany("INSERT INTO tagAssignments (modelId, tagId) VALUES (?, ?)", tagAssignments)
    connection.commit()
    connection.close()

def get_models_url():
    f = open('settings.json')
    data = json.load(f)
    return 'static/' + data['models_url']
