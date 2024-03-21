import sys
import csv
import pandas as pd
import os
from pandas_ods_reader import read_ods

def main():
    dicColumns = {}
    header = []
    rows = []
    base_path = "/home/pcald32/logBookHumiTest.ods"
    df = read_ods(base_path, 1, headers=True)
    HVeff= df["HV eff [V]"].tolist()
    Triggers= df["Trigger_#"].tolist()
    bin= df["File bin"].tolist()
    runNum= df["Run #"].tolist()
    print(df)
    #os.chdir('/home/pcald32/')
    """
    with open('runsPandasDataframe', 'a+') as pandasDataframeFile:
        dfPandas = pd.DataFrame()
        csvreaderPandas = csv.DictReader(pandasDataframeFile)
        header = str(csvreaderPandas)
    for row in header:
        rows.append(row)
        print(rows[0])
    #print(csvreader)
    
        header = [] #empty list
        headerEncoded = csvreader.encode('utf-8').strip()
        header = str(next(data)) #returns the current row and moves to the next row
        header
        #now it's time to extract te values of each header. To do this, a empty row list is created
        rows = []
        #iterate through the csvreader object and append each row to the rows list
        for row in data:
            rows.append(row)
            rows
        
        mystring=''.join(map(str,header))
        if (x == "RUN #" for x in mystring):
            print(mystring)
        else:
            return 0
            
            
            
        for i in header:
            if header[i] == str('RUN #'):
                print(header[i])
            else:
                break
            #print(rows)
            #print(type(header))
        
        csvFile.close()
        pandasDataframeFile.close() #close the file
        """
        


if __name__ == "__main__":
    main()