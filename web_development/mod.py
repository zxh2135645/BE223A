#Function to create a dictionary of Modalities avalilable under a Hospital

#Used in Dropdown feature in calendar



def choose(field):
    data=list(info[field].unique())
    d=defaultdict(list)
    for i in data:
        info1=info[info[field].str.contains(i)]
        Mod=list(info1['Modality'].unique())
        d[i].append(Mod)
    return d