
# coding: utf-8

# In[47]:
import warnings
warnings.filterwarnings('ignore')

from parsing import *
from database_functions import *

import pandas as pd
import numpy as np
import random
import time
import matplotlib.pyplot as plt

import imblearn
from imblearn.under_sampling import EditedNearestNeighbours

import sklearn
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import make_scorer
from sklearn.metrics import (confusion_matrix, 
                             recall_score, 
                             f1_score, 
                             accuracy_score, 
                             precision_score,
                             roc_curve, auc)

def model_preprocess (data):
    '''
    Function that applies Edited Nearest Neighbors from the imblearn library to create a more balanced training set.
    
    Arguments:
    data: dataframe with features and labels
    
    Returns:
    train: the training set with more balanced label distribution
    trainlab: the labels for the training set
    test: test set with same label distribution as the original dataset
    test_nlab: subset of test set that does not contain the labels
    testlab: the labels for the test set
    
    '''
    a = time.time()
    #encoding
    features_encoded=pd.get_dummies(data).dropna()
    #split into testing and training
    train, test = train_test_split(features_encoded, test_size=0.2, stratify = features_encoded.Label)
    #training
    trainlab = train.Label
    train = train.drop('Label', axis=1)
    tlabels = list(train)
    #testing
    testlab = test.Label
    test_nlab = test.drop('Label', axis=1)
    
    #perform the imbalance technique: Edited Nearest Neighbors
    enn = EditedNearestNeighbours() 
    train, trainlab=enn.fit_sample(train, trainlab)
    train = pd.DataFrame(train, columns=tlabels)
    
    print('Preprocessing Completed in %.3f seconds.'% (time.time()-a))
    
    return train, trainlab, test, test_nlab, testlab

def gridsearch (t, trainlab, k):
    '''
    Performs GridSearch from sklearn library on the Random Forest Classifier model to generate ideal parameters according to f-1 score.
    
    Arguments:
    t: the training set with more balanced label distribution
    trainlab: the labels for the training set
    k: the number of cases to subset from each label set
    
    Returns:
    n_estimators: the number of decision trees to build for the ensemble model
    max_features: the maximum amount of features to use for each tree (generated as a decimal)
    class_weight: the type of weighting based on subset
    criterion: the criterion used to split the tree; either 'gini' or 'entropy'
    
    '''
    a=time.time()
    scoring = make_scorer(f1_score)
    t['Label'] = trainlab
    #randomly under sample
    neg = t[t['Label'] == 0].sample(k)
    pos = t[t['Label'] == 1].sample(k)
    
    t = pd.concat([neg, pos])
    trainlab = t.Label
    train = t.drop('Label', axis=1)
    
    param_test1 = {'n_estimators':np.arange(20,111,10).tolist(), 
                   'max_features':np.arange(0.1,1,0.1).tolist()
                   , 'class_weight':['balanced', None]
                   ,'criterion':['gini', 'entropy']
                  }
    gsearch1 = GridSearchCV(estimator = RandomForestClassifier(random_state=10), 
                   param_grid = param_test1, scoring=scoring, n_jobs=4,iid=False, cv=5)
    gsearch1.fit(train, trainlab)
    n_estimators = list(gsearch1.best_params_.values())[0]
    max_features = list(gsearch1.best_params_.values())[1]
    class_weight = list(gsearch1.best_params_.values())[2]
    criterion = list(gsearch1.best_params_.values())[3]
    
    display(gsearch1.best_params_)
    
    print('Grid Search Performed in %.3f seconds.'% (time.time()-a))
    
    return n_estimators, max_features, class_weight, criterion

def rfc_metrics(test):
    '''
    Evaluate the model and generate commonly-used metrics.
    
    Arguments:
    test: the data frame with the labels and predictions attached
    
    Returns:
    plot: ROC curve and score
    details: an array containing true negatives, false positives, false negatives, true positives, accuracy, precision, recall, and F1 score.
    
    '''
    acc = accuracy_score(test.Label, test.Predictions)
    f1 = f1_score(test.Label, test.Predictions)
    prec = precision_score(test.Label, test.Predictions)
    rec = recall_score(test.Label, test.Predictions)
    
    tn, fp, fn, tp = confusion_matrix(test.Label, test.Predictions).ravel()
    
    details = [tn, fp, fn, tp, acc, prec, rec, f1]
    
    roc = roc_curve(test.Label, test.Predictions)
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    n_classes = test.Label.nunique()
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(test.Label, test.Predictions)
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Compute micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(test.Label.ravel(), test.Predictions.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    plt.figure(figsize=(10,5))
    lw = 2
    plt.plot(fpr[1], tpr[1], color='gold',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[1])
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic Example')
    plt.legend(loc="lower right")
    
    plt.savefig('ROC_curve.png')
    
    plt.show()
    
    
    show_confusion_matrix(test)
    
    return details

def show_confusion_matrix(test):
    '''
    Plot the confusion matrix, along with metrics. Adapted from http://notmatthancock.github.io/2015/10/28/confusion-matrix.html 
    
    Arguments:
    test: the data frame with the labels and predictions attached
    
    Returns:
    plot: confusion matrix, along with commonly used scores.
    '''
    
    C = confusion_matrix(test.Label, test.Predictions)
    tn, fp, fn, tp = C.ravel()
    
    NP = fn+tp # Num positive examples
    NN = tn+fp # Num negative examples
    N  = NP+NN

    fig = plt.figure(figsize=(8,8))
    ax  = fig.add_subplot(111)
    ax.imshow(C, cmap=plt.cm.gray)

    # Draw the grid boxes
    ax.set_xlim(-0.5,2.5)
    ax.set_ylim(2.5,-0.5)
    ax.plot([-0.5,2.5],[0.5,0.5], '-k', lw=2)
    ax.plot([-0.5,2.5],[1.5,1.5], '-k', lw=2)
    ax.plot([0.5,0.5],[-0.5,2.5], '-k', lw=2)
    ax.plot([1.5,1.5],[-0.5,2.5], '-k', lw=2)


    # Set xlabels
    ax.set_xlabel('Predicted Label', fontsize=16)
    ax.set_xticks([0,1,2])
    ax.set_xticklabels(['Show', 'No Show'])
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    # These coordinate might require some tinkering. Ditto for y, below.
    ax.xaxis.set_label_coords(0.34,1.06)

    # Set ylabels
    ax.set_ylabel('True Label', fontsize=16, rotation=90)
    ax.set_yticklabels(['Show', 'No Show'])
    ax.set_yticks([0,1,2])
    ax.yaxis.set_label_coords(-0.09,0.65)


    # Fill in initial metrics: tp, tn, etc...
    ax.text(0,0,
            'True Negatives: %d\n(Total Negatives: %d)'%(tn,NN),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(0,1,
            'False Negatives: %d'%fn,
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(1,0,
            'False Positives: %d'%fp,
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))


    ax.text(1,1,
            'True Positives: %d\n(Total Positives: %d)'%(tp,NP),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    # Fill in secondary metrics: accuracy, true pos rate, etc...
    ax.text(2,0,
        'True Negative Rate' + '\n' +'(Specificity):%.2f'%(tn / (fp+tn+0.)),
        va='center',
        ha='center',
        bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(2,1,
            'True Positive Rate' + '\n' + '(Sensitivity):%.2f'%(tp / (tp+fn+0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(2,2,
            'F-1 Score: %.2f'%(round(2*tp/((2*tp) + fp + fn),3)),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(0,2,
            'Negative Predictive ' + '\n' + 'Value: %.2f'%(1-fn/(fn+tn+0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(1,2,
            'Positive Predictive ' + '\n' + 'Value: %.2f'%(tp/(tp+fp+0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))


    plt.tight_layout()
    plt.savefig('confusionmatrix_withscores.png')
    plt.show()
    
    
    return None

def feat_imprt(rf, test):
    '''
    Determines and plots the feature importances for the Random Forest model.
    
    Arguments:
    rf: the Random Forest model
    test: the data frame pased to the model
    
    Returns:
    plot: bar plot displaying the importance of each feature, sorted in descending order
    sort_features: a list of the features, sorted in descending order of importance
    
    '''
    importances = rf.feature_importances_
    std = np.std([tree.feature_importances_ for tree in rf.estimators_],
                 axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")

    features = list(test)
    sort_features = []
    for f in range(test.shape[1]):
    #    print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))
    #    print("%a: %f" % (features[indices[f]], importances[indices[f]]))
        sort_features.append(features[indices[f]])

    # Plot the feature importances of the forest
    plt.figure(figsize=(30,10))
    plt.title("Feature importances")
    plt.bar(range(test.shape[1]), importances[indices],
           color="teal", yerr=std[indices], align="center")
    plt.xticks(range(test.shape[1]), sort_features, rotation = 90)
    plt.xlim([-1, test.shape[1]])

    plt.tick_params(axis='both', which='major', labelsize=8)
    plt.savefig('feature_importances.png')
    plt.show()
    
    
    return sort_features

def prob_cm (test):
    '''
    Displays the confusion matrix for each bin of predicted probability
    
    Arguments:
    test: the data frame with the labels and predictions attached
    
    Returns:
    plot: a plot showing the confusion matrix for each probability bin
    prob: the confusion matrices for each probability bin
    groups: a groupby object that contains the binning for the probabilities
    
    '''
    a=time.time()
    # Bin the data
    bins = np.linspace(0, 1, 10)
    groups = test.groupby(np.digitize(test.Probabilities, bins))
    
    #create a dataframe detailing the confusion matrix
    df = pd.DataFrame(columns=["tn", "fp", "fn", "tp"])
    probs = []
    bins = np.arange(1,11,1).tolist()
    for i in bins: 
        subset = groups.get_group(i)
        tn, fp, fn, tp = confusion_matrix(subset.Label, subset.Predictions).ravel()
        probs.append(str('P (' + str((i/10))) + ")")
        df.loc[-1] = [tn, fp, fn, tp]
        df.index = [probs]
    
    #create the total columns
    df['Sums'] = df.sum(axis = 1).astype(int)
    
    dfp = df.iloc[:,:].div(df.Sums, axis=0)*100
    dfp

    tns = dfp.tn
    fps = dfp.fp
    fns = dfp.fn
    tps = dfp.tp  
    width = 0.50
    
    plt.figure(figsize=(10,5))
    p1 = plt.bar(bins, tns, width, color = 'teal')
    p2 = plt.bar(bins, tps, width, color = 'darkslateblue', bottom=tns)
    p3 = plt.bar(bins, fns, width, color = 'darkorange', bottom=tns+tps)
    p4 = plt.bar(bins, fps, width, color = 'gold', bottom=tns+tps+fns)
    
    plt.ylabel('Percent of Appointments')
    plt.xlabel('Predicted Probability')
    plt.title('Confusion Matrix by Probability')
    plt.xticks(bins, ('10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'))
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('TN', 'TP', 'FN', 'FP'), bbox_to_anchor=(1, 1))
    
    plt.savefig('probability_confusionmatrix.png')

    plt.show()
    
    
    print('Model Analysis processed in %.3f seconds.'% (time.time()-a))
    return df, groups

def create_df(data, merge1, merge2, fk1, fk2):
    '''
    Calls table_merge to merge data frames based on features.
    
    Arguments:
    data: the data frame to which the merging frames will be appended
    merge1: the first table to be merged
    merge2: the second table to be merged
    fk1: the key used to map merge1 to data
    fk2: the key used to map merge1 to data
    
    Returns:
    data: the merged data frame
    
    '''
    data = table_merge(data, merge1, fk1)
    data = table_merge(data, merge2, fk2)   
    return data

def table_merge(data, merge, foreignk):
    '''
    Calls merge columns for every feature in a target data frame, resulting in a fully merged data frame.
    
    Arguments:
    data: the data frame to which the merging frames will be appended
    merge: the first table to be merged
    foreignk: the key used to map merge1 to data
    
    Returns:
    data: the merged data frame 
    
    '''
    
    features = list(merge)
    features.remove(foreignk)
    for i in features:
        data = merge_columns(data, merge, foreignk, str(i))
    return data


def run_model(data, k = 5000, tune_parameters = False, exam_id = 'Exam_ID', pt_id = 'Patient_ID', drops = ['Datetime Obj', 'Dayofyear']):
    '''
    Creates a separate data frame with patient IDs, Exam IDs, and the indices, called ids.
    Calls model_preprocess to undersample the dominant class using Edited Nearest Neighbors, a technique that involves clustering the data, and choosing from those clusters. This outputs a test set with the same distribution as the total set, and a training set that is more balanced.
    Runs the RandomForestClassifier from the sklearn library. If model_preprocess was run, it uses those parameters; if not, default parameters are specified from manual tuning. The function uses the builtin methods to predict the labels as well as the probabilities for each test case.
    The function then performs a series of analyses:
    rfc_metrics: generates the standard measures of performance (accuracy, precision, recall F-1), and plots the ROC AUC.
    show_confusion_matrix: with those metrics generated above, this function generates a confusion matrix and reports them, along with the confusion matrix.
    prob_cm: this takes the probabilities predicted from the model, puts them into bins (e.g., 0.1-0.2) and plots the false and true values for each bin.
    feat_imprt: this takes the fitted Random Forest, and plots the features in order of their importance to the classifier model. This function then outputs:
    
    Arguments:
    data: the relevant data frame
    tune_parameters: boolean that determines if Grid Search will be run. Default to False
    exam_id: the column header for exam IDs. Default set to "Exam_ID"
    pt_id: the column header for patient IDs. Default set to "Patient_ID"
    drops: the columns to be dropped from this dataset.
    
    Returns:
    results: the probabilities and labels for each test case
    prob: the confusion matrices for each probability bin
    groups: a groupby object that contains the binning for the probabilities
    test: the test dataset, with the labels attached
    evalstats: an array with all of the evaluation statistics
    sort_features: a sorted list of features, ranked by importance
    
    '''
    
    a = time.time()
    
    ids = data[[exam_id, pt_id]]
    data = data.drop(drops +[exam_id, pt_id], axis = 1)
    
    #preprocess the data: ENN
    train, trainlab, test, test_nlab, testlab = model_preprocess(data)
    
    if tune_parameters:
        print('Running GridSearch. Tuned Parameters:')
        class_weight, criterion, max_features, n_estimators  = gridsearch(train, trainlab, k)
        train = train.drop('Label', axis=1)
    else:
        class_weight, criterion, max_features, n_estimators  = 'balanced', 'entropy', 0.8, 50
        print("GridSearch was not run. Default parameters selected:" + "\n" +
              "- Class Weight: "+ class_weight + "\n" +
              "- Criterion: " + criterion + "\n" +
              "- Maximum Features: " + str(max_features) + "\n" +
              "- Number of Estimators: " + str(n_estimators))    
    
    print("Running the Random Forest Classifier.")
    b = time.time()
    rfc = RandomForestClassifier(n_estimators = n_estimators, 
                             max_features = max_features,
                             class_weight = str(class_weight),
                             criterion = criterion,
                             random_state = 10)
    
    rfc.fit(train, trainlab) 
    results = rfc.predict(test_nlab)
    
    sort_features = feat_imprt(rfc, test_nlab)
    
    test['Predictions'] = results
    test['Probabilities'] = rfc.predict_proba(test_nlab)[:,1]
    
    print('Random Forest Classifier Model run in %.3f seconds.'% (time.time()-b))
    
    evalstats = rfc_metrics(test)
    
    prob, groups = prob_cm(test)
    
    m = dict(zip(
    ids.index.values.tolist(),
    ids.Exam_ID.values.tolist()
    ))

    results = test[['Probabilities', 'Predictions']]
    results['Exam_ID'] = [m.get(i, 'supplemental') for i in results.index]
    results

    
    ### One more function: push results to DB (both labels and probabilities) 
    
    print('Pipeline completed in %.3f seconds.'% (time.time()-a))
    
    return results, test, prob, groups, evalstats, sort_features


