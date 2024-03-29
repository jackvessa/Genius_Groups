from flask import Flask, render_template, request, make_response, send_file
import numpy as np
import pandas as pd
from src.Genius_Group_Functions import *

import io
import csv
import tempfile

__author__ = 'jackvessa'

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("template.html")

@app.route('/getExampleCSVs/') # this is a job for GET, not POST
def example_csvs():
    return send_file('Example_CSVs/Superhero_Single_Assignment.csv',
                     mimetype='text/csv',
                     attachment_filename='Single_Superheroes_Assignment.csv',
                     as_attachment=True)

# @app.route('/getExampleCSV/') # this is a job for GET, not POST
# def example_csv():
#     return send_file('Example_CSVs/Superhero_Single_Assignments',
#                      mimetype='text/csv',
#                      attachment_filename='Single_Superheroes_Assignment.csv',
#                      as_attachment=True)

@app.route('/getExampleCSVsfull/') # this is a job for GET, not POST
def example_csvs_full():
    return send_file('Example_CSVs/Superhero_All_Assignments.csv',
                     mimetype='text/csv',
                     attachment_filename='Full_Superheroes_Gradebook.csv',
                     as_attachment=True)

# @app.route('/getExampleCSVfull/') # this is a job for GET, not POST
# def example_csv_full():
#     return send_file('Example_CSVs/Superhero_All_Assignments.csv',
#                      mimetype='text/csv',
#                      attachment_filename='All_Superheroe_Assignments.csv',
#                      as_attachment=True)


@app.route('/group/', methods=["GET", "POST"])
def group():
    errors = ""

    if request.method == "POST":

        section_id = None
        num_groups = None
        homogeneous_bool = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_groups = int(request.form["num_groups"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_groups"])
        try:
            homogeneous_bool = int(request.form["homogeneous_bool"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["homogeneous_bool"])


        if section_id is not None and num_groups is not None and homogeneous_bool is not None:
            student_df = clean_file(data_frame,section_id)
            student_df = normalize_df(student_df)
            result = generate_optimized_groups(student_df, num_groups = num_groups,num_iter = 300, Homogeneous=homogeneous_bool)
            groups_string = ""
            for i,val in enumerate(result):
                groups_string += "<br/>Group " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                groups_string += ("Average Score: " +
                    str(round((np.mean(student_df.loc[val]['score']))*100,2)) +"%<br/>")
                groups_string += ("Score Range: " +
                    str(round((np.max(student_df.loc[val]['score'])-np.min(student_df.loc[val]['score']))*100,2)) +"%<br/>")
            return '''
                <html>

                    <head>
                        <title>Genius Grouping Results (Single Assignment)</title>
                        <h1>Genius Groups (Based on Single Assignment):</h1>
                        <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">
                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to group again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>
            <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">

              <head>
                <meta charset="utf-8">
                <title>Genius Grouping Setup</title>

                <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">

              </head>

            <body>
                <h1>Generate Genius Groups (Based on Single Assignment)!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here (Single Assignment):</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
                    <p>* For Example CSV Options are 4 or 6 *</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Groups to Form:</p>
                    <p><input name="num_groups" /></p>

                    <p>Enter 0 for Homogeneous (Similar) Groups  <br> or 1 for Heterogeneous (Mixed) Groups :</p>
                    <p><input name="homogeneous_bool" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


@app.route('/group_all/', methods=["GET", "POST"])
def group_all():
    errors = ""

    if request.method == "POST":

        section_id = None
        num_groups = None
        homogeneous_bool = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_groups = int(request.form["num_groups"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_groups"])
        try:
            homogeneous_bool = int(request.form["homogeneous_bool"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["homogeneous_bool"])


        if section_id is not None and num_groups is not None and homogeneous_bool is not None:
            student_df = clean_file_all_assignments(data_frame,section_id)
            student_df = normalize_df(student_df)
            result = generate_optimized_groups(student_df, num_groups = num_groups,num_iter = 300,
                Homogeneous=homogeneous_bool, criteria = 'Current Score')
            groups_string = ""
            for i,val in enumerate(result):
                groups_string += "<br/>Group " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                groups_string += ("Average Score: " +
                    str(round((np.mean(student_df.loc[val]['Current Score']))*100,2)) +"%<br/>")
                groups_string += ("Score Range: " +
                    str(round((np.max(student_df.loc[val]['Current Score'])-np.min(student_df.loc[val]['Current Score']))*100,2)) +"%<br/>")

            return '''
                <html>

                    <head>
                        <title>Genius Grouping Results</title>
                        <h1>Genius Groups (Full Gradebook):</h1>
                        <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">
                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to group again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>

              <head>
                <meta charset="utf-8">
                <title>Genius Grouping Setup</title>

                <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">

              </head>

            <body>
                <h1>Generate Genius Groups (Based on Full Gradebook)!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here (Full):</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
                    <p>* For Example CSV Options are 2 or 3 *</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Groups to Form:</p>
                    <p><input name="num_groups" /></p>

                    <p>Enter 0 for Homogeneous (Similar) Groups  <br> or 1 for Heterogeneous (Mixed) Groups :</p>
                    <p><input name="homogeneous_bool" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """



@app.route('/cluster/', methods=["GET", "POST"])
def cluster():
    errors = ""

    if request.method == "POST":

        section_id = None
        num_clusters = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_clusters = int(request.form["num_clusters"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_clusters"])

        if section_id is not None and num_clusters is not None:
            student_df = clean_file(data_frame,section_id)
            student_df = normalize_df(student_df)
            student_df = add_clusters(student_df, num_clusters = num_clusters)
            result = return_cluster_list(student_df, num_clusters)
            groups_string = ""
            for i,val in enumerate(result):
                groups_string += "<br/>Cluster " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                groups_string += ("Average Score: " +
                    str(round(np.mean(student_df.loc[val]['score'])*100,2)) +"%<br/>")
            return '''
                <html>

                    <head>
                        <h1>Genius Clusters:</h1>
                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to cluster again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>
            <body>
                <h1>Generate Genius Clusters (Single Assignment)!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here (Single):</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
                    <p>* For Example CSV Options are 4 or 6 *</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Clusters to Form:</p>
                    <p><input name="num_clusters" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


@app.route('/cluster_all/', methods=["GET", "POST"])
def cluster_all():
    errors = ""

    if request.method == "POST":

        section_id = None
        num_clusters = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_clusters = int(request.form["num_clusters"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_clusters"])

        if section_id is not None and num_clusters is not None:
            student_df = clean_file_all_assignments(data_frame,section_id)
            student_df = normalize_df(student_df)
            student_df = add_clusters(student_df, num_clusters = num_clusters)
            result = return_cluster_list(student_df, num_clusters)
            groups_string = ""
            for i,val in enumerate(result):
                groups_string += "<br/>Cluster " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                groups_string += ("Average Score: " +
                    str(round(np.mean(student_df.loc[val]['Current Score'])*100,2)) +"%<br/>")

            return '''
                <html>

                    <head>
                        <h1>Genius Clusters (Full Gradebook):</h1>
                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to cluster again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>
            <body>
                <h1>Generate Genius Clusters (Full Gradebook)!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
                    <p>* For Example CSV Options are 2 or 3 *</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Clusters to Form:</p>
                    <p><input name="num_clusters" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


@app.route('/cluster_questions/', methods=["GET", "POST"])
def cluster_questions():
    errors = ""

    if request.method == "POST":

        section_id = None
        num_clusters = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_clusters = int(request.form["num_clusters"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_clusters"])
        try:
            strength_bool = int(request.form["strength_bool"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["strength_bool"])


        if section_id is not None and num_clusters is not None and strength_bool is not None:
            quest_list = create_questions_list(data_frame)
            topics_dict, labels = cluster_question_topics(quest_list, num_clust = num_clusters)

            strength_and_growth_df = make_student_growth_and_strength_df(data_frame,section_id,labels)

            if strength_bool == 0:
                clust_groups = generate_strength_groups(strength_and_growth_df,num_clusters)
            else:
                clust_groups = generate_growth_groups(strength_and_growth_df,num_clusters)

            quest_dict = labels_to_dict(labels)

            groups_string = ""
            for i,val in enumerate(clust_groups):
                groups_string += "<br/>Cluster " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                if strength_bool == 0:
                    groups_string += ("Strength Area Questions: " +
                        str(quest_dict[i]) + "<br/>")
                    groups_string += ("Question Cluster Topics: " +
                        str(topics_dict[i]) + "<br/>")
                else:
                    groups_string += ("Growth Area Questions: " +
                        str(quest_dict[i]) + "<br/>")
                    groups_string += ("Question Cluster Topics: " +
                        str(topics_dict[i]) + "<br/>")
            return '''
                <html>

                    <head>
                        <h1>Genius Clusters (Single Assignment):</h1>
                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to cluster again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>
            <body>
                <h1>Generate Genius Clusters (Based on Single Assignment)!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
                    <p>* For Example CSV Options are 4 or 6 *</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Clusters to Form:</p>
                    <p><input name="num_clusters" /></p>

                    <p>Enter 0 for "Strength" Groups  <br> or 1 for "Growth Area" Groups :</p>
                    <p><input name="strength_bool" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """



@app.route('/form')
def form():
    return render_template('form.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=5000)
