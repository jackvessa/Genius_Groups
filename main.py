from flask import Flask, render_template, request, make_response
import numpy as np
import pandas as pd
from Smart_Group_Functions import (calc_group_sizes, clean_file, normalize_df,
generate_optimized_groups, add_clusters, return_cluster_list,
clean_file_all_assignments)
import io
import csv
import tempfile

__author__ = 'jackvessa'

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("template.html")

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
                        <title>Smart Grouping Results</title>
                        <h1>Smart Groups:</h1>
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
                <title>Smart Grouping Setup</title>

                <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">

              </head>

            <body>
                <h1>Generate Smart Groups!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
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

            return '''
                <html>

                    <head>
                        <title>Smart Grouping Results</title>
                        <h1>Smart Groups:</h1>
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
                <title>Smart Grouping Setup</title>

                <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">

              </head>

            <body>
                <h1>Generate Smart Groups!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
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
                        <h1>Smart Clusters:</h1>
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
                <h1>Generate Smart Clusters!!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
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
                        <h1>Smart Clusters:</h1>
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
                <h1>Generate Smart Clusters!!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Clusters to Form:</p>
                    <p><input name="num_clusters" /></p>

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
