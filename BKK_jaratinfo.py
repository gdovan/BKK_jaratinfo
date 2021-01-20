import tkinter as tk
from tkinter import ttk
import csv
import urllib.request
import json
import datetime
import time

csvFilename='stops.txt'
megallok_dict={}
megallok_list=[]

def Stop_read():
    csvFileObj = open(csvFilename, encoding='utf-8')
    reader= csv.DictReader(csvFileObj)
    for row in reader:
        if reader.line_num == 1:
            continue # skip first row
        megallok_dict[row['stop_id']] = row['stop_name']
    csvFileObj.close()

root= tk.Tk()
root.title('BKK járatinfó')
root.geometry('400x300')
frame_1=tk.Frame(root)
frame_1.pack()
Stop_read()

for key, value in megallok_dict.items():
    temp = value+' : '+ key
    megallok_list.append(temp)
megallok_list.sort()
#e = Entry(root, width=35,borderwidth=5)
#e.grid(row=0,column=0,columnspan=3,padx=10,pady=10)

selected_megallo = tk.StringVar()
megallo = ttk.Combobox(root,width=50, textvariable=selected_megallo)
megallo["values"] = megallok_list
m_valasztas=''
m_azon=''
def handle_selection(event):
    global m_valasztas,m_azon
    m_valasztas=megallo.get()
    m_azon='BKK_'+ m_valasztas[m_valasztas.find(':')+2:]
    get_data()
    
def get_data():
    if m_valasztas=='':
        return
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686)"
    datum=datetime.datetime.now().strftime('%Y%m%d')
    request=urllib.request.Request('https://futar.bkk.hu/api/query/v1/ws/otp/api/where/schedule-for-stop.json?key=apaiary-test&version=3&appVersion=apiary-1.0&includeReferences=true&stopId='+m_azon+'&onlyDepartures=false&date='+datum,headers=headers)
    response_body = urllib.request.urlopen(request).read().decode('UTF-8')
    bkk_dict=json.loads(response_body)
    bkk_data=bkk_dict.get('data')
    bkk_entry=bkk_data.get('entry')    
    percelore=3600
    most=datetime.datetime.now()
    label_time.config(text=str(most))
    most_epoch=time.mktime(most.timetuple())
    text.delete('1.0',tk.END)
    sor=1
    #print(f'Megálló: {m_valasztas}')
    for c in range(len(bkk_entry['schedules'])):
        #print(bkk_entry['schedules'][c]['routeId'])
        jarattipus=(bkk_entry['schedules'][c]['routeId'][4:5])
        #print(jarattipus)
        text.insert(str(sor)+".0",bkk_entry['schedules'][c]['routeId']+'\n')
        text.tag_add("start", str(sor)+".0", str(sor)+".30")
        if jarattipus in('0','1','2','9'): #busz
            text.tag_config("start", background="blue",foreground="black")
        if jarattipus=='3': #villamos
            text.tag_config("start", background="yellow", foreground="black")
        if jarattipus=='4': #troli
            text.tag_config("start", background="red", foreground="black")
        if jarattipus=='5': #Metró
            text.tag_config("start", background="yellow", foreground="black")
        if jarattipus=='6': #HÉV
            text.tag_config("start", background="green", foreground="black")
        sor+=1
        for a in range(len(bkk_entry['schedules'][c]['directions'])):
            #print(bkk_entry['schedules'][c]['directions'][a]['groups'].values())
            gk=list(bkk_entry['schedules'][c]['directions'][a]['groups'].keys())
            #print(bkk_entry['schedules'][c]['directions'][a]['groups'][gk[0]]['headsign'])
            text.insert(str(sor)+".0",bkk_entry['schedules'][c]['directions'][a]['groups'][gk[0]]['description']+'\n')
            sor+=1
            text.insert(str(sor)+".0",bkk_entry['schedules'][c]['directions'][a]['groups'][gk[0]]['headsign']+' felé\n')
            sor+=1
            for i in range(len(bkk_entry['schedules'][c]['directions'][a]['stopTimes'])):
                indulas=bkk_entry['schedules'][c]['directions'][a]['stopTimes'][i]['departureTime']
                indulas_f=datetime.datetime.fromtimestamp(int(indulas)).strftime("%Y.%m.%d %H:%M")
                try:
                    indulas=bkk_entry['schedules'][c]['directions'][a]['stopTimes'][i]['predictedDepartureTime']
                    indulas_f=datetime.datetime.fromtimestamp(int(pre_indulas)).strftime("%Y.%m.%d %H:%M")
                except:
                    pre_indulas_f='N/A'
                if indulas-30<=most_epoch<=indulas:
                    #print('MOST')
                    text.insert(str(sor)+".0",'I: MOST \n')
                    sor+=1
                if most_epoch< indulas < most_epoch+percelore:
                    #print ( indulas_f)
                    if int(indulas-most_epoch)>60:
                        meg=str(int(int(indulas-most_epoch)/60))+' perc'
                    else:
                        meg=str(int(indulas-most_epoch))+' másodperc'
                    text.insert(str(sor)+".0",'I:'+indulas_f+' '+meg+'\n')
                    sor+=1

megallo.bind("<<ComboboxSelected>>", handle_selection) 
megallo["state"] = "readonly"  # "normal is the counterpart"
button_refr = ttk.Button(frame_1,text="Frissítés",command=get_data).pack(side=tk.LEFT)
button_exit = ttk.Button(frame_1,text="Kilépés",command=root.destroy).pack(side=tk.RIGHT)
#most_str = tk.StringVar()
most_str=str(datetime.datetime.now())
label_time = ttk.Label(root,text=most_str)
label_time.pack(side=tk.BOTTOM)
#button_refr.grid(row=3,column=0)
text = tk.Text(root, height=12)  
text.pack()


megallo.pack()

root.mainloop()
