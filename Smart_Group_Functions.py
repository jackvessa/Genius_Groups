import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# csv_file = 'Data/Exam 2_ Tissues (Closed EB) Quiz Student Analysis Report.csv'
# csv_file = 'Data/Exam 1_ Part 2 Quiz Student Analysis Report.csv'
# sectionID = 1453
# num_groups = 3
# Homogenous = True

# Create Group Sizes
def calc_group_sizes(num_students, num_groups):
    '''
    Parameters
    -----------
    num_students : int
        Number of students in the class
    num_groups : int
        Number of groups to break students into

    Returns
    ---------
    group_size : List of ideal group sizes
    '''
    group_sizes = []

    class_size = int(num_students)
    group_num_count = int(num_groups)
    group_num = int(num_groups)

    for i in range(group_num_count):
        temp = class_size // group_num
        class_size -= temp
        group_num -= 1
        group_sizes.append(temp)

    return group_sizes

# Clean DataFrame by Section
def clean_file(dataframe,sectionID):
    '''
    Clean CSV file
    --------------------

    Parameters
    -----------
    .csv file :
    sectionID : Class/Period Number to Group

    Returns
    ---------
    Pandas DataFrame (Cleaned)
    '''
    sectionID = str(sectionID)

    df = dataframe
    df.set_index(keys=df['name'],inplace=True)

    df['section'] = df.section.str.extract('(\d+)')
    df = df[df['section']==sectionID]

    df = df.select_dtypes(exclude=['object','bool'])

    df.drop(columns=['id','section_sis_id','attempt','section_id'],inplace=True)

    return df

# Normalize DataFrame (0-1)
def normalize_df(df):
    '''
    Normalize DataFrame Values from 0-1

    Parameters
    ----------
    df : DataFrame to Normalize

    Returns
    -------
    Normalized DataFrame
    '''
    return df.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)) \
        if np.min(x) != np.max(x) else x)

# Generate Optimized Group (Based on Residual Sum of Squares)
def generate_optimized_groups(student_df, num_iter = 100, num_groups = 6, Homogeneous = 0, criteria = 'score'):
    '''

    Parameters
    ----------
    student_df : DataFrame with student names as index and score column
    num_iter : int
        Number of Iterations to run loss function
    num_groups : int
        Number of groups to divide students into
    Homogeneous : bool
        If True, create Homogeneous (similar) groups.
        If False, create Heterogeneous (different) groups

    Returns
    -------
    Optimal Groups
    '''
    index_list = list(student_df.index)

    if Homogeneous == 0:
        ideal_loss = 9999
    elif Homogeneous == 1:
        ideal_loss = 0
    num_students = len(student_df)

    size_list = calc_group_sizes(num_students,num_groups)

    for i in range(num_iter):
        randomized_index_list = np.random.choice(index_list, size = len(index_list),replace=False)
        group_set = set({})
        index_track = 0
        total_loss = 0

        for num in size_list:
            j = frozenset(randomized_index_list[0 + index_track:index_track+num])
            group_set.add(j)
            index_track += num

        for group in group_set:
            unfrozen = set(group)
            group_loss = 0
            avg_score = np.mean(student_df.loc[unfrozen][criteria])

            for s in range(len(group)):
                group_loss += (student_df.loc[unfrozen][criteria][s] - avg_score) ** 2

            total_loss += group_loss

        if Homogeneous == 0 and total_loss < ideal_loss:
            ideal_loss = total_loss
            best_group = group_set
            print("New Best Homogeneous Group Loss:", ideal_loss)

        elif Homogeneous == 1 and total_loss > ideal_loss:
            ideal_loss = total_loss
            best_group = group_set
            print("New Best Heterogeneous Group Loss:", ideal_loss)

    print("\n")
    print("Final Best Group Loss:", ideal_loss)
    print("Final Best Grouping:\n")


    for i,g in enumerate(best_group):
        print("Group",i+1)
        print(student_df.loc[set(g)][criteria],"\n")

    return best_group

# Clean File Based on All Gradebook Assignments and Section
def clean_file_all_assignments(dataframe,sectionID):
    '''
    Clean CSV file
    --------------------

    Parameters
    -----------
    .csv file :
    sectionID : Class/Period Number to Group

    Returns
    ---------
    Pandas DataFrame (Cleaned)
    '''
    sectionID = str(sectionID)
    df = dataframe
    df.drop(df.index[0], inplace=True)

    df.set_index(keys=df['Student'],inplace=True)
    df.drop(index = ['Test Student'], inplace=True)

    # Parse out Section Number
    df['Section'] = df.Section.str.extract('(\d+)')
    df = df[df['Section']==sectionID]

    df.drop(columns=['Student','ID','SIS User ID','SIS Login ID'],inplace=True)
    df.drop(columns=['Assignments Current Points','Assignments Final Points','Assignments Unposted Current Score','Assignments Final Score'],inplace=True)
    df.drop(columns=['Assignments Unposted Final Score','Imported Assignments Current Points','Imported Assignments Final Points','Imported Assignments Current Score'],inplace=True)
    df.drop(columns=['Imported Assignments Unposted Current Score','Unposted Final Score','Final Score','Unposted Current Score'],inplace=True)
    df.drop(columns=['Assignments Current Score','Imported Assignments Final Score','Imported Assignments Unposted Final Score','Current Points','Final Points'],inplace=True)

    df = df.loc[:, df.isnull().mean() < .4]
    df.fillna(0,inplace=True)
    class_df = df.copy()
    class_df['Current Score'] = df['Current Score'].apply(lambda x: float(x))

    return class_df

# Add Cluster Column to DataFrame
def add_clusters(df, num_clusters=6):
    '''
    Add Clusters
    '''
    kmeans = KMeans(num_clusters)
    kmeans.fit(df)
    cluster = kmeans.predict(df)
    df['Cluster'] = cluster
    return df

# Return a list of Clusters
def return_cluster_list(df,num_clusters=6):
    '''
    Return a List of Clustered Students
    '''
    cluster_list = []

    for i in range(num_clusters):
        cluster_list.append(list(df[df['Cluster']==i].index))

    return cluster_list


## NLP Clustering of Questions

# Create a List of Question Strings
def create_questions_list(df, cols=['id','sis_id','section_id','section_sis_id','submitted','attempt','score','name','section']):
    '''
    Takes DataFrame and creates a NumPy array.

    Parameters
    ----------
    df : Pandas DataFrame
    cols : list of columns to drop from DataFrame

    Returns
    -------
    List of Questions
    '''
    df.drop(columns=cols,inplace=True)
    df = df.select_dtypes(exclude=['float'])
    df = df.select_dtypes(exclude=['int'])
    column_name_list = np.array(list(df.columns))
    quest_list = []
    for quest in column_name_list:
        quest_list.append(quest[6:])
    return np.array(quest_list)


# Group Questions into Clusters
def cluster_question_topics(quest_list,num_clust = 3,num_top_words = 3,stop_words = ["q"], max_features = 50):
    '''
    Create clusters of questions based on word usage

    Parameters
    ----------
    quest_list : list of questions
    num_clust : number of question clusters to create
    num_top_words : number of words to display in result
    stop_words : list of words to remove from clustering
    max_features : number of words to include in clustering (top X by frequency)

    Returns
    -------
    String of results
    Labels of Clustered Questions
    '''

#     my_stop_words = text.ENGLISH_STOP_WORDS.union(["ae","word","exam","alphabetical","options","order",
#                                         "things","used",'________','called','likely','provides','provide',
#                                         '_____','10','correct','match','12','14','32777','isa','thing','11',
#                                         '13','sentence','definition','suffix','suffixes','prefix','prefixes',
#                                         'uses','terms','means','following','function','specialist',
#                                         'position','correctly','directional','body','anatomical','plane',
#                                         'means_________'])

    my_stop_words = text.ENGLISH_STOP_WORDS.union(stop_words)

    vectorizer = TfidfVectorizer(strip_accents='ascii',stop_words=my_stop_words,max_features=max_features)
    X = vectorizer.fit_transform(quest_list)
    means = KMeans(num_clust,).fit(X)

    print("Top terms per cluster:")
    order_centroids = means.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()

    string_results = ""
    for i in range(num_clust):
        print("\nCluster {}:".format(str(i+1)))
        string_results += ("\nCluster {}:".format(str(i+1)))
        for ind in order_centroids[i, :num_top_words]:
            print(' %s' % terms[ind])
            string_results += (' %s' % terms[ind])
    print(means.labels_)

    return (string_results, np.array(means.labels_))


# Make Student Strength/Growth Areas DataFrame
def make_student_growth_and_strength_df(df,sectionID,cluster_labels):
    '''
    Create a DataFrame that includes students strengths and growth areas for question clusters

    Return a List of Clustered Students

    Parameters
    ----------
    df : Pandas DataFrame
    sectionID : Section Number for Students

    Returns
    -------
    Pandas DataFrame with strengths and growth areas for question clusters

    '''
    clean_df = clean_file(df,sectionID)
    quest_num_df = clean_df.iloc[:,0:-3]
    quest_num_df.columns = cluster_labels
    quest_num_df_grouped = quest_num_df.groupby(quest_num_df.columns, axis=1).sum()
    grouped_quest_normed_df = normalize_df(quest_num_df_grouped)

    x = grouped_quest_normed_df.copy().ix[0]
    x.index[x.argmin()]
    min_list, max_list = [], []

    for i in range (len(grouped_quest_normed_df)):
        x = grouped_quest_normed_df.ix[i]

        min_list.append(x.index[x.argmin()])
        max_list.append(x.index[x.argmax()])


    grouped_quest_normed_df['Strength Area'] = max_list
    grouped_quest_normed_df['Growth Area'] = min_list

    return grouped_quest_normed_df


# Generate Growth Areas Groups
def generate_growth_groups(df,num_groups):
    '''

    Parameters
    ----------
    student_df : DataFrame with student names as index and Strength/Growth Areas included

    Returns
    -------
    Growth Area Groups
    '''
    index_list = list(df.index)

    cluster_focus = []

    for i in range(num_groups):

        cluster_focus.append(list(df[df['Growth Area']==i].index))

    print("Grouping by Growth Areas:\n")

    for i,g in enumerate(cluster_focus):
        print("Group",i+1)
        print(str(g)+"\n")

    return cluster_focus


# Generate Strength Areas Groups
def generate_strength_groups(df,num_groups):
    '''

    Parameters
    ----------
    student_df : DataFrame with student names as index and Strength/Growth Areas included

    Returns
    -------
    Growth Area Groups
    '''
    index_list = list(df.index)

    cluster_focus = []

    for i in range(num_groups):

        cluster_focus.append(list(df[df['Strength Area']==i].index))

    print("Grouping by Strength Areas:\n")

    for i,g in enumerate(cluster_focus):
        print("Group",i+1)
        print(str(g)+"\n")

    return cluster_focus
 


if __name__ == "__main__":
    student_df = clean_file(csv_file,sectionID)
    student_df = normalize_df(student_df)
    generate_optimized_groups(student_df, num_groups = 6,num_iter = 1000,\
        Homogeneous=True) ;
