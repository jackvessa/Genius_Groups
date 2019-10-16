from flask import Flask, render_template, request, make_response
import numpy as np
import pandas as pd
from Smart_Group_Functions import calc_group_sizes, clean_file, normalize_df, generate_optimized_groups
import io
import csv
import tempfile

__author__ = 'jackvessa'

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def form():
    errors = ""

    if request.method == "POST":

        data_file = None
        section_id = None
        num_groups = None
        homogeneous_bool = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path)

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_groups = int(request.form["num_groups"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_groups"])
        try:
            homogeneous_bool = bool(request.form["homogeneous_bool"])
        except:
            errors += "<p>{!r} is not a True or False Value!</p>\n".format(request.form["homogeneous_bool"])


        if section_id is not None and num_groups is not None and homogeneous_bool is not None:
            student_df = clean_file(data_frame,section_id)
            student_df = normalize_df(student_df)
            result = generate_optimized_groups(student_df, num_groups = num_groups,num_iter = 10, Homogeneous=homogeneous_bool)
            groups_string = ""
            for i,val in enumerate(result):
                groups_string += "Group " + str(i) + ":"
                groups_string += str(list(val))
            return '''
                <html>
                    <body>
                        <p>The Ideal Grouping is {groups_string}</p>
                        <p><a href="/">Click here to group again!</a>
                    </body>
                </html>
            '''.format(groups_string=groups_string)



    return """
        <html>
            <body>
                <h1>Generate Smart Groups!</h1>

                <h2>Choose Specifications:</h2>
                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Please Upload the CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Please Enter the sectionID Here:</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Groups to Form:</p>
                    <p><input name="num_groups" /></p>

                    <p>Do you want Homogeneous Grouping?:</p>
                    <p><input name="homogeneous_bool" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
