import os, requests, json, time, threading
import PySimpleGUI as sg

prev_timer = time.time()
curr_search = []

def timer():
    global prev_timer
    prev_timer = time.time()

def timer_thread(dic):   
    global prev_timer
    global curr_search

    while (time.time() - prev_timer) <= 2:
        time.sleep(0.02)
    print(f'initiating search for {curr_search}')
    window['LIST'].update(search(dic, curr_search))

def initiate_thread(dic):
    thread_running = False
    for thread in threading.enumerate():
        if thread.name == 'timer_t':
            print(f'thread still running')
            thread_running = True
            break
    if not thread_running:
        print('spawning new thread')
        t = threading.Thread(name='timer_t', target=timer_thread, args=(dic,))
        t.start()
    timer()
    print(f'threads: {threading.active_count()}: {"-".join([thread.name for thread in threading.enumerate() if thread.name == "timer_t"])}')

def init(db):
    if not db:
        db = {}
        db['time_updated'] = time.time()
        db['folders_to_index'] = ['/usr/share/wordlists']
        db['files'] = []
    return db


def get_db():
    if os.path.isfile(db_file):
        with open(db_file, 'r') as f:
            db = json.load(f)
            return db
    else:
        return None

def write_db(db, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(db, f)
    except:
        print('error while writing to file')

def index(db, filename):
    db['files'] = []
    for path in db['folders_to_index']:
        for root, dirs, files in os.walk(path):
            for name in files:
                fname = os.path.join(root, name)
                if not fname in db['files']:
                    db['files'].append(fname)
    write_db(db, filename)
    return db

def search(dic, searchfor):
    # tstart = time.time()
    res = [val for key, val in dic.items() if searchfor in key] 
    # tstop = time.time()
    # print(f'function ran for {(tstop - tstart)} seconds')
    return res

if __name__ == "__main__":
    # initialize database, move to dict for performance (might need to clean this up later, got it twice in memory, or is it a pointer??)
    db_file = 'filedb.json'
    db = get_db()
    dic = {key.lower(): key for key in db['files']}
    db = init(db)
    # db = index(db)
    # initialize timer, to delay redrawing the listbox too soon, leading to performance issues. search function itself too, but its pretty fast at around 0.003 seconds
    max_key_delay = 0.2 #seconds delay between keypresses before running query

    layout = [[
            sg.Input(size=(100,100), change_submits=True, focus=True, key='SEARCH'), sg.Button('Copy', size=(15,1),key='__COPY__', bind_return_key=True), sg.Button('Open', size=(15,1),key='__OPEN__')
            ],[
            sg.Listbox([], size=(140,50),background_color='black', text_color='white', key='LIST')
            ],[
                sg.Text('0 results, 0 files in db, last update unknown')
            ]]
    sg.theme = 'dark'

    window = sg.Window("Find & Forget", layout, return_keyboard_events=True)
    while True:
        event, values = window.read(timeout=100)
        if event != '__TIMEOUT__':
            print(event, values)
        if event == None or event == sg.WIN_CLOSED:
            break
        if event == 'SEARCH' and len(values['SEARCH']) >= 4:
            prevsearch = values['SEARCH']
            curr_search = values['SEARCH']
            initiate_thread(dic)

        if event == 'Up':
            pass
        if event == 'Down':
            pass
        if event == 'Escape':
            break
        if event == '__COPY__' and len(values['SEARCH']) >= 4:
            print(values['SEARCH'])


