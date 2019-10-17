import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# csv_file = 'Data/Exam 2_ Tissues (Closed EB) Quiz Student Analysis Report.csv'
# csv_file = 'Data/Exam 1_ Part 2 Quiz Student Analysis Report.csv'
# sectionID = 1453
# num_groups = 3
# Homogenous = True

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
    df = dataframe
    df.set_index(keys=df['name'],inplace=True)
    df = df.select_dtypes(exclude=['object','bool'])

    df.drop(columns=['id','section_sis_id','attempt'],inplace=True)

    class_df = df[df['section_id']==sectionID]

    return class_df


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


def clean_file_all_assignments(fileName,sectionID):
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
    df = pd.read_csv(fileName, encoding='latin-1')
    df.drop(df.index[0], inplace=True)

    df.set_index(keys=df['Student'],inplace=True)

    df.drop(index = ['Test Student'], inplace=True)

    df.drop(columns=['Student','ID','SIS User ID','SIS Login ID'],inplace=True)
    df.drop(columns=['Assignments Current Points','Assignments Final Points','Assignments Unposted Current Score','Assignments Final Score'],inplace=True)
    df.drop(columns=['Assignments Unposted Final Score','Imported Assignments Current Points','Imported Assignments Final Points','Imported Assignments Current Score'],inplace=True)
    df.drop(columns=['Imported Assignments Unposted Current Score','Unposted Final Score','Final Score','Unposted Current Score'],inplace=True)
    df.drop(columns=['Assignments Current Score','Imported Assignments Final Score','Imported Assignments Unposted Final Score','Current Points','Final Points'],inplace=True)

    # Parse out Section Number
    df['Section'] = df.Section.str.extract('(\d+)')
    df = df.loc[:, df.isnull().mean() < .4]
    df.fillna(0,inplace=True)
    df['Current Score'] = df['Current Score'].apply(lambda x: float(x))

    class_df = df[df['Section']==sectionID]

    return class_df


def add_clusters(df, num_clusters=6):
    '''
    Add Clusters
    '''
    kmeans = KMeans(num_clusters)
    kmeans.fit(df)
    cluster = kmeans.predict(df)
    df['Cluster'] = cluster
    return df


def return_cluster_list(df,num_clusters=6):
    '''
    Return a List of Clustered Students
    '''
    cluster_list = []

    for i in range(num_clusters):
        cluster_list.append(list(df[df['Cluster']==i].index))

    return cluster_list


if __name__ == "__main__":
    student_df = clean_file(csv_file,sectionID)
    student_df = normalize_df(student_df)
    generate_optimized_groups(student_df, num_groups = 6,num_iter = 1000,\
        Homogeneous=True) ;
