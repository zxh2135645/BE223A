import pandas as pd
import numpy as np

info=pd.read_csv('C:/Users/aksha/Desktop/BIOENG/BE 223A/be223a_dataset.csv')
info['date'],info['time']=info['CompletedDTTM_D'].str.split(' ', 1).str
info=info[['Modality','Age','OrgCode','Anatomy','date','Labels']]


#@app.route('/charts' , methods=['GET', 'POST'])
def displaycharts(field): # field information is obtained from the html and has to be fetched from database (for eg: modality)
    show=[]
    Noshow=[]
    data=list(info[field].unique())        #Number of unique elements in that field
    for i in range(len(data)):      
        df1=info[info[field].str.contains(data[i])]    
        count=(df1['Labels'] == 0).sum()
        count1=(df1['Labels'] != 0).sum()
        show.append(count)
        Noshow.append(count1) 
    return show,Noshow,data  # show and no show list for each field which needs to be made as stacked bar plot

#data, frequency, show and no show all are needed for visualizing stacked bar plot 