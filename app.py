from flask import Flask, render_template, request, redirect, url_for
from db import get_connection
import queries

app = Flask(__name__)


# Default IDs in case none selected
DEFAULT_ZONE_ID = 1
DEFAULT_TYPE_ID = 1
DEFAULT_OWNER_ID = 1


# -------------------- PAGE 1 : ACCUEIL --------------------


# Mot de passe défini
APP_PASSWORD = "2025"   # 👉 change-le comme tu veux

@app.route("/")
def first_page():
    return render_template("firstpage.html")

@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password")

    if password == APP_PASSWORD:
        return redirect(url_for("index"))
    else:
        return render_template("firstpage.html", error="Mot de passe incorrect")



# -------------------- PAGE 2 : INDEX (CARTE + FORMULAIRES) --------------------
@app.route("/index")
def index():
    conn = get_connection()
    cur = conn.cursor()



    # BATIMENTS
    cur.execute("""
        SELECT b.Id_batiment, b.nom_batiment, b.adresse_batiment, b.altitude, b.longitude,
               b.date_construction, b.niveau_protection,
               z.nom_zone, t.libelle, p.nom_proprietaire, p.type_proprietaire, p.contact
        FROM batiment b
        JOIN zone z ON b.Id_zone = z.Id_zone
        JOIN type_batiment t ON b.Id_type = t.Id_type
        JOIN proprietaire p ON b.Id_proprietaire = p.Id_proprietaire
        ORDER BY b.Id_batiment;
    """)
    batiments = cur.fetchall()

    # PRESTATAIRES
    cur.execute("SELECT Id_prestataire, nom_prestataire, type_prestataire, contact FROM prestataire ORDER BY Id_prestataire")
    prestataires = cur.fetchall()

    # INTERVENTIONS
    cur.execute("""
        SELECT i.Id_intervention, b.nom_batiment, p.nom_prestataire, i.date_travaux,
               i.type_travaux, i.cout
        FROM intervention i
        JOIN batiment b ON i.Id_batiment = b.Id_batiment
        JOIN prestataire p ON i.Id_prestataire = p.Id_prestataire
        ORDER BY i.Id_intervention;
    """)
    interventions = cur.fetchall()

    # INSPECTIONS
    cur.execute("""
        SELECT ins.Id_inspection, b.nom_batiment, ins.date_inspection, ins.rapport
        FROM inspection ins
        JOIN batiment b ON ins.Id_batiment = b.Id_batiment
        ORDER BY ins.Id_inspection;
    """)
    inspections = cur.fetchall()

    # DOCUMENTS
    cur.execute("""
        SELECT d.Id_doc, b.nom_batiment, d.chemin, d.type_doc
        FROM document d
        JOIN batiment b ON d.Id_batiment = b.Id_batiment
        ORDER BY d.Id_doc;
    """)
    documents = cur.fetchall()

    # ZONES
    cur.execute("SELECT Id_zone, nom_zone FROM zone ORDER BY Id_zone")
    zones = cur.fetchall()

    # TYPES
    cur.execute("SELECT Id_type, libelle FROM type_batiment ORDER BY Id_type")
    types = cur.fetchall()

    # PROPRIETAIRES
    cur.execute("SELECT Id_proprietaire, nom_proprietaire, type_proprietaire, contact FROM proprietaire ORDER BY Id_proprietaire")
    proprietaires = cur.fetchall()

    # ETAT CONSERVATION
    cur.execute("""
        SELECT b.nom_batiment, ec.date_etat, ec.etat
        FROM etat_conservation ec
        JOIN batiment b ON ec.Id_batiment = b.Id_batiment
        ORDER BY ec.date_etat DESC;
    """)
    etat_conservation = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html",
                           batiments=batiments,
                           prestataires=prestataires,
                           interventions=interventions,
                           inspections=inspections,
                           documents=documents,
                           zones=zones,
                           types=types,
                           proprietaires=proprietaires,
                           etat_conservation=etat_conservation)


@app.route("/add_batiment", methods=["POST"])
def add_batiment():
    try:
        nom = request.form["name"]
        adresse = request.form.get("adresse", "")
        year = request.form["year"]
        etat = request.form["etat"]
        lat = request.form["latitude"]
        lon = request.form["longitude"]
        zone = request.form.get("zone")
        zone_id = zone if zone else None
        type_b = request.form["type"]
        prop = request.form["proprietaire"]

        date_construction = f"{year}-01-01"

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO batiment 
            (nom_batiment, adresse_batiment, Id_zone, Id_type, Id_proprietaire, 
             date_construction, altitude, longitude, niveau_protection)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nom, adresse, zone, type_b, prop,
              date_construction, lat, lon, etat))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    except Exception as e:
        return f"Erreur add_batiment : {e}"



# -------------------- AJOUT PRESTATAIRE --------------------
@app.route("/add_prestataire", methods=["POST"])
def add_prestataire():
    try:
        nom = request.form["nom"]
        type_p = request.form["type"]
        contact = request.form.get("contact", "")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO prestataire (nom_prestataire, type_prestataire, contact)
            VALUES (%s, %s, %s)
        """, (nom, type_p, contact))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    except Exception as e:
        return f"Erreur add_prestataire : {e}"


# -------------------- AJOUT INTERVENTION --------------------
@app.route("/add_intervention", methods=["POST"])
def add_intervention():
    try:
        bat = request.form["batiment"]
        pres = request.form["prestataire"]
        date_t = request.form["date_travaux"]
        type_t = request.form["type_travaux"]
        cout = request.form.get("cout") or None

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO intervention (Id_batiment, Id_prestataire, date_travaux, type_travaux, cout)
            VALUES (%s, %s, %s, %s, %s)
        """, (bat, pres, date_t, type_t, cout))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    except Exception as e:
        return f"Erreur add_intervention : {e}"


# -------------------- AJOUT INSPECTION --------------------
@app.route("/add_inspection", methods=["POST"])
def add_inspection():
    try:
        bat = request.form["batiment"]
        date_i = request.form["date_inspection"]
        rapport = request.form.get("rapport", "")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO inspection (Id_batiment, date_inspection, rapport)
            VALUES (%s, %s, %s)
        """, (bat, date_i, rapport))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    except Exception as e:
        return f"Erreur add_inspection : {e}"


# -------------------- AJOUT DOCUMENT --------------------
@app.route("/add_document", methods=["POST"])
def add_document():
    try:
        bat = request.form["batiment"]
        chemin = request.form["chemin"]
        type_doc = request.form.get("type_doc", "")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO document (Id_batiment, chemin, type_doc)
            VALUES (%s, %s, %s)
        """, (bat, chemin, type_doc))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    except Exception as e:
        return f"Erreur add_document : {e}"


# -------------------- PAGE RAPPORTS --------------------
@app.route("/rapports")
def rapports():
    mauvais = queries.batiments_mauvais_etat()
    interventions = queries.interventions_par_entreprise()
    annee = request.args.get("annee", 2025)
    restaures = queries.batiments_restaures_annee(annee)
    cout_quartier = queries.cout_total_par_quartier()
    prestataires = queries.prestataires_plus_de_3_chantiers()

    return render_template("rapports.html",
                           mauvais=mauvais,
                           interventions=interventions,
                           annee=annee,
                           restaures=restaures,
                           cout_quartier=cout_quartier,
                           prestataires=prestataires)



@app.route("/add_zone", methods=["POST"])
def add_zone():
    try:
        nom = request.form["nom_zone"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO zone (nom_zone) VALUES (%s)", (nom,))
        conn.commit()

        cur.close()
        conn.close()
        return redirect("/index")

    except Exception as e:
        return f"Erreur add_zone : {e}"

#type
@app.route("/add_type", methods=["POST"])
def add_type():
    try:
        lib = request.form["libelle"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO type_batiment (libelle) VALUES (%s)", (lib,))
        conn.commit()

        cur.close()
        conn.close()
        return redirect("/index")

    except Exception as e:
        return f"Erreur add_type : {e}"

@app.route("/add_proprietaire", methods=["POST"])
def add_proprietaire():
    try:
        nom = request.form["nom_proprietaire"]
        type_p = request.form["type_proprietaire"]
        contact = request.form.get("contact", "")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO proprietaire (nom_proprietaire, type_proprietaire, contact)
            VALUES (%s, %s, %s)
        """, (nom, type_p, contact))

        conn.commit()

        cur.close()
        conn.close()
        return redirect("/index")

    except Exception as e:
        return f"Erreur add_proprietaire : {e}"
    


    ################################################################
@app.route("/edit_zone/<int:id>", methods=["GET", "POST"])
def edit_zone(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        nom = request.form["nom_zone"]
        cur.execute("UPDATE zone SET nom_zone=%s WHERE Id_zone=%s", (nom, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    cur.execute("SELECT nom_zone FROM zone WHERE Id_zone=%s", (id,))
    zone = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_zone.html", zone=zone, id=id)

##
@app.route("/edit_type/<int:id>", methods=["GET", "POST"])
def edit_type(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        libelle = request.form["libelle"]
        cur.execute("UPDATE type_batiment SET libelle=%s WHERE Id_type=%s", (libelle, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    cur.execute("SELECT libelle FROM type_batiment WHERE Id_type=%s", (id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_type.html", data=data, id=id)
##########


#####
@app.route("/edit_proprietaire/<int:id>", methods=["GET", "POST"])
def edit_proprietaire(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        nom = request.form["nom"]
        type_p = request.form["type"]
        contact = request.form["contact"]

        cur.execute("""
            UPDATE proprietaire 
            SET nom_proprietaire=%s, type_proprietaire=%s, contact=%s
            WHERE Id_proprietaire=%s
        """, (nom, type_p, contact, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    cur.execute("""
        SELECT nom_proprietaire, type_proprietaire, contact
        FROM proprietaire WHERE Id_proprietaire=%s
    """, (id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_proprietaire.html", data=data, id=id)
############
@app.route("/edit_batiment/<int:id>", methods=["GET", "POST"])
def edit_batiment(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        nom = request.form["nom"]
        etat = request.form["etat"]

        cur.execute("""
            UPDATE batiment
            SET nom_batiment=%s, niveau_protection=%s
            WHERE Id_batiment=%s
        """, (nom, etat, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    cur.execute("""
        SELECT nom_batiment, niveau_protection
        FROM batiment WHERE Id_batiment=%s
    """, (id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_batiment.html", data=data, id=id)
#########
@app.route("/edit_prestataire/<int:id>", methods=["GET", "POST"])
def edit_prestataire(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        nom = request.form["nom"]
        type_p = request.form["type"]
        contact = request.form["contact"]

        cur.execute("""
            UPDATE prestataire
            SET nom_prestataire=%s, type_prestataire=%s, contact=%s
            WHERE Id_prestataire=%s
        """, (nom, type_p, contact, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    cur.execute("""
        SELECT nom_prestataire, type_prestataire, contact
        FROM prestataire WHERE Id_prestataire=%s
    """, (id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_prestataire.html", data=data, id=id)
##################
@app.route("/edit_intervention/<int:id>", methods=["GET", "POST"])
def edit_intervention(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        type_t = request.form["type"]
        cout = request.form["cout"]

        cur.execute("""
            UPDATE intervention
            SET type_travaux=%s, cout=%s
            WHERE Id_intervention=%s
        """, (type_t, cout, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    cur.execute("""
        SELECT type_travaux, cout
        FROM intervention WHERE Id_intervention=%s
    """, (id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_intervention.html", data=data, id=id)
#################
@app.route("/edit_inspection/<int:id>", methods=["GET", "POST"])
def edit_inspection(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        rapport = request.form["rapport"]
        cur.execute("""
            UPDATE inspection SET rapport=%s
            WHERE Id_inspection=%s
        """, (rapport, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    cur.execute("""
        SELECT rapport FROM inspection
        WHERE Id_inspection=%s
    """, (id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_inspection.html", data=data, id=id)
#######################""
@app.route("/edit_document/<int:id>", methods=["GET", "POST"])
def edit_document(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        chemin = request.form["chemin"]
        type_doc = request.form["type"]

        cur.execute("""
            UPDATE document
            SET chemin=%s, type_doc=%s
            WHERE Id_doc=%s
        """, (chemin, type_doc, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/index")

    cur.execute("""
        SELECT chemin, type_doc
        FROM document WHERE Id_doc=%s
    """, (id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_document.html", data=data, id=id)
#######################


@app.route("/update_batiment", methods=["POST"])
def update_batiment():
    id = request.form["id_batiment"]
    nom = request.form["name"]
    year = request.form["year"]
    etat = request.form["etat"]
    lat = request.form["latitude"]
    lon = request.form["longitude"]
    adresse = request.form["adresse"]
    zone = request.form["zone"] or None
    type_b = request.form["type"] or None
    prop = request.form["proprietaire"] or None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE batiment SET
            nom_batiment=%s,
            date_construction=%s,
            niveau_protection=%s,
            altitude=%s,
            longitude=%s,
            adresse_batiment=%s,
            Id_zone=%s,
            Id_type=%s,
            Id_proprietaire=%s
        WHERE Id_batiment=%s
    """, (
        nom, f"{year}-01-01", etat,
        lat, lon, adresse,
        zone, type_b, prop,
        id
    ))

    conn.commit()
    cur.close()
    conn.close()
    return redirect("/index")

######################## Fask zone  route de modification 
@app.route("/update_zone", methods=["POST"])
def update_zone():
    id = request.form["id_zone"]
    nom = request.form["nom_zone"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE zone SET nom_zone=%s WHERE Id_zone=%s",
        (nom, id)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/index")

########################################## Flask route modifier Proprietaire  
@app.route("/update_proprietaire", methods=["POST"])
def update_proprietaire():
    id = request.form["id_proprietaire"]
    nom = request.form["nom_proprietaire"]
    type_p = request.form["type_proprietaire"]
    contact = request.form.get("contact", "")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE proprietaire
        SET nom_proprietaire=%s,
            type_proprietaire=%s,
            contact=%s
        WHERE Id_proprietaire=%s
    """, (nom, type_p, contact, id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/index")
#########################################################Route flask de modification type batiments 
@app.route("/update_type", methods=["POST"])
def update_type():
    id = request.form["id_type"]
    libelle = request.form["libelle"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE type_batiment SET libelle=%s WHERE Id_type=%s",
        (libelle, id)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/index")
#########################################modifier prestatire 
@app.route("/update_prestataire", methods=["POST"])
def update_prestataire():
    id = request.form["id_prestataire"]
    nom = request.form["nom"]
    type_p = request.form["type"]
    contact = request.form.get("contact", "")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE prestataire
        SET nom_prestataire=%s,
            type_prestataire=%s,
            contact=%s
        WHERE Id_prestataire=%s
    """, (nom, type_p, contact, id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/index")
############################################################# Modifuier intervention 
@app.route("/update_intervention", methods=["POST"])
def update_intervention():
    id = request.form["id_intervention"]
    bat = request.form["batiment"]
    pres = request.form["prestataire"]
    date_t = request.form["date_travaux"]
    type_t = request.form["type_travaux"]
    cout = request.form.get("cout") or None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE intervention
        SET Id_batiment=%s,
            Id_prestataire=%s,
            date_travaux=%s,
            type_travaux=%s,
            cout=%s
        WHERE Id_intervention=%s
    """, (bat, pres, date_t, type_t, cout, id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/index")

#######################flast route modefier inspection
@app.route("/update_inspection", methods=["POST"])
def update_inspection():
    id = request.form["id_inspection"]
    bat = request.form["batiment"]
    date_i = request.form["date_inspection"]
    rapport = request.form.get("rapport", "")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE inspection
        SET Id_batiment=%s,
            date_inspection=%s,
            rapport=%s
        WHERE Id_inspection=%s
    """, (bat, date_i, rapport, id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/index")
###########################################


    








# -------------------- LANCEMENT --------------------
if __name__ == "__main__":
    app.run(debug=True)