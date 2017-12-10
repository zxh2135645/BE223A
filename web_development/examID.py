
#Function to return Exam ID of a patient given a Hospital, Modality and Department



info=pd.read_csv('C:/Users/aksha/Desktop/BIOENG/BE 223A/be223a_dataset.csv')
info['date'],info['time']=info['CompletedDTTM_D'].str.split(' ', 1).str
info=info[['Modality','Age','OrgCode','Anatomy','date','Labels','DepartmentCode','time']]



from datetime import datetime

date_time=parse_datetime(info.ScheduledDTTM_D)
df= pd.DataFrame({'datetime':date_time})
info1=pd.concat([info,df], axis=1)


#function to return department given orgcode and modality

def choose_dept(field, modality,dept,dt1,dt2): 
    
    date_time=list(info1['datetime'])
    Examid=list(info1['ExamID'])
    
    df1=info1[info1['OrgCode'].str.contains(field)]
    df2=df1[df1['Modality'].str.contains(modality)]
    df3=df2[df2['DepartmentCode'].str.contains(dept)]
    for i in range(len(date_time)):
        if date_time[i]>dt1 and date_time[i]<dt2:
            examid=Examid[i]
    return Examid