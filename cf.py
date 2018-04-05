import argparse
import re
import os
import csv
import math
import numpy as np
import collections as coll


def parse_argument():
    """
    Code for parsing arguments
    """
    parser = argparse.ArgumentParser(description='Parsing a file.')
    parser.add_argument('--train', nargs=1, required=True)
    parser.add_argument('--test', nargs=1, required=True)
    args = vars(parser.parse_args())
    return args


def parse_file(filename):
    """
    Given filename parse the file to give user_ratings and movie_ratings dictionaries
    Input: filename
    Output: user_ratings, movie_ratings
    """
    data = np.loadtxt(filename, delimiter=',')
    users = coll.defaultdict(dict)
    movies = coll.defaultdict(dict)
    user_ratings = {}
    movie_ratings = {}
    for row in data:
        users[row[1]][row[0]] = row[2]
        movies[row[0]][row[1]] = row[2]
    user_ratings = users
    movie_ratings = movies
    return user_ratings, movie_ratings

def compute_average_user_ratings(user_ratings):
    """ 
    Given the user_rating dict compute average user ratings

    Input: user_ratings (dictionary of user, movies, ratings)
    Output: ave_ratings (dictionary of user and ave_ratings)
    """
    ave_ratings = {}
    for user_id in user_ratings.keys():
        ave_ratings[user_id] = np.mean(user_ratings[user_id].values())
    return ave_ratings

def compute_user_similarity(d1, d2, ave_rat1, ave_rat2):
    """ 
    Computes similarity between two users

    Input: d1, d2, (dictionary of user ratings per user) 
           ave_rat1, ave_rat2 average rating per user (float)
    Ouput: user similarity (float)
    """
    # Your code here
    keys_1 = set(d1.keys())
    keys_2 = set(d2.keys())
    intersection = keys_1 & keys_2
    sum1 = 0
    sumsq1 = 0
    sumsq2 = 0
#     print intersection
    for movie in intersection:
        sum1+= (d1[movie] - ave_rat1)*(d2[movie] - ave_rat2)
        sumsq1+= (d1[movie] - ave_rat1)**2
        sumsq2+= (d2[movie] - ave_rat2)**2
    if sumsq1*sumsq2 != 0:
        return sum1/((sumsq1*sumsq2)**0.5)
    else:
        return 0.0

def main():
    """
    This function is called via commandline as follows:
    python cf.py --train [path to filename] --test [path to filename]
    """
    args = parse_argument()
    train_file = args['train'][0]
    test_file = args['test'][0]
    print train_file, test_file
    # your code here
    user_ratings, movie_ratings = parse_file(train_file)
    ave_ratings = compute_average_user_ratings(user_ratings)
    test_user_ratings, test_movie_ratings = parse_file(test_file)
    pred_ratings = coll.defaultdict(dict)
    rmse = 0
    mae = 0
    diff = []
    for user_id in test_user_ratings:
        Ri_bar = ave_ratings[user_id]
        for movie_id in test_user_ratings[user_id]:
            num = 0
            den = 0
            for user in movie_ratings[movie_id]:
                Rj_bar = ave_ratings[user]
                Rjk = movie_ratings[movie_id][user]
                Wij = compute_user_similarity(user_ratings[user_id],user_ratings[user],Ri_bar, Rj_bar)
                num+= Wij*(Rjk - Rj_bar)
                den+= abs(Wij)
            if den>0:
                pred_ratings[user_id][movie_id] = Ri_bar + (num/den)
            else:
                pred_ratings[user_id][movie_id] = Ri_bar
            diff.append(pred_ratings[user_id][movie_id] - test_user_ratings[user_id][movie_id])
    
    text_file = open("predictions.txt", "w")
    for user_id in pred_ratings.keys():
        for movie_id in pred_ratings[user_id].keys():
            text_file.write("%s,%s,%s,%s \n" %(movie_id, user_id, test_user_ratings[user_id][movie_id],pred_ratings[user_id][movie_id]))
    text_file.close()
    rmse = np.sqrt(np.mean(np.square(diff)))
    mae = np.mean(np.abs(diff))
    print 'RMSE ' + str(format(rmse,'.4f'))
    print 'MAE ' + str(format(mae,'.4f'))
if __name__ == '__main__':
    main()


