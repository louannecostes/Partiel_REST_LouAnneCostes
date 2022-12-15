from flask import Flask, jsonify, abort, request
import mariadb
import urllib.parse

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False  # pour utiliser l'UTF-8 plutot que l'unicode


def execute_query(query, data=()):
    config = {
        'host': 'mariadb',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'mydatabase_Partiel'
    }
    """Execute une requete SQL avec les param associés"""
    # connection for MariaDB
    conn = mariadb.connect(**config)
    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute(query, data)

    if cur.description:
        # serialize results into JSON
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        list_result = []
        for result in rv:
            list_result.append(dict(zip(row_headers, result)))
        return list_result
    else:
        conn.commit()
        return cur.lastrowid


# we define the route /
@app.route('/')
def welcome():
    liens = [{}]
    liens[0]["_links"] =[ {
        "href": "/groupes",
        "rel": "groupes"
    },{
        "href": "/concerts",
        "rel": "concerts"
    },{
        "href": "/reservations",
        "rel": "reservations"
    }]
    return jsonify(liens), 200


""" ################## GROUPES ##################
    #############################################"""
@app.route('/groupes')
def get_groupes():
    """Affiche tous les groupes"""
    groupes = execute_query("select nom from groupes")
    # ajout de _links à chaque dico groupes
    for i in range(len(groupes)):
        groupes[i]["_links"] = [
            {
                "href": "/groupes/" + urllib.parse.quote(groupes[i]["nom"]),
                "rel": "self"
            },
            
        ]
    return jsonify(groupes), 200


@app.route('/groupes/<string:nom>')
def get_groupe(nom):
    """Affiche un groupe en particulier"""
    groupes = execute_query("select nom from groupes where nom=?", (nom,))
    # ajout de _links à chaque dico groupes
    for i in range(len(groupes)):
        groupes[i]["_links"] = [
            {
                "href": "/groupes/" + urllib.parse.quote(groupes[i]["nom"]),
                "rel": "self"
            },
            
        ]
    return jsonify(groupes), 200

@app.route('/groupes', methods=['POST'])
def post_groupe():
    """"Ajoute un groupe"""
    nom = request.args.get("nom")
    dates = request.args.get("dates")

    execute_query("insert into groupes (nom,dates) values (?,?)", (nom,dates,))
    # on renvoi le lien du groupe que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/groupes/" + nom,
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created

@app.route('/groupes/<string:nom>', methods=['DELETE'])
def delete_groupe(nom):
    """supprimer un groupe"""
    execute_query("delete from groupes where nom=?", (nom, ))
    return "", 204  # no data

""" ################## CONCERTS ##################
#############################################"""

@app.route('/concerts')
def get_concerts():
    """Affiche tous les concerts"""
    concerts = execute_query("select nom from concerts")
    # ajout de _links à chaque dico concerts
    for i in range(len(concerts)):
        concerts[i]["_links"] = [
            {
                "href": "/concerts/" + urllib.parse.quote(concerts[i]["nom"]),
                "rel": "self"
            },
            
        ]
    return jsonify(concerts), 200

@app.route('/concerts', methods=['POST'])
def post_concert():
    """"Ajoute un concert"""
    date_debut = request.args.get("date_debut")
    duree = request.args.get("duree")
    id_groupe = request.args.get("id_groupe")
    nom = request.args.get("nom")


    execute_query("insert into concerts (date_debut,duree, id_groupe, nom) values (?,?,?,?)", (date_debut,duree,id_groupe,nom,))
    # on renvoi le lien du groupe que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/concerts/" + id_groupe,
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created

@app.route('/groupes/<string:nom>/concerts')
def get_concert(nom):
    """Affiche les concerts d'un groupe"""
    concerts = execute_query("select * from concerts join groupes on concerts.groupe_id=groupes.id where groupes.nom=?", (nom,))  
    for i in range(len(concerts)):
        concerts[i]["_links"] = [
            {
                "href": "/concerts/" + urllib.parse.quote(concerts[i]["nom"]),
                "rel": "self"
            },
            
        ]
    return jsonify(concerts), 200

@app.route('/concerts/<string:nom>', methods=['DELETE'])
def delete_concert(nom):
    """supprimer un concert"""
    execute_query("delete from concerts where nom=?", (nom, ))
    return "", 204  # no data

""" ################## RESERVATIONS ##################
#############################################"""
@app.route('/concerts', methods=['POST'])
def post_reservation():
    """"Ajoute une reservation"""
    nom_concert = request.args.get("nom_concert")
    id_concert = request.args.get("id_concert")
    

    execute_query("insert into reservation (concerts,id_concert) values (?,?)", (nom_concert,id_concert,))
    # on renvoi le lien du groupe que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/reservations/" + id_groupe,
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created


##pas eu le temps de terminer




if __name__ == '__main__':
    # define the localhost ip and the port that is going to be used
    app.run(host='0.0.0.0', port=5000)
