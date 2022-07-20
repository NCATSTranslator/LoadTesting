import requests
import json
import os
import logging
import webbrowser
import time
import argparse
import random
from statistics import mean
import numpy as np
import pickle
import multiprocessing as mp

BASE_PATH=os.path.dirname(
      os.path.realpath(__file__)
    )
parser = argparse.ArgumentParser(description='Load Tester')
parser.add_argument('-c', '--count', help='Number of queries to be run', default=10)
parser.add_argument('-d','--delay',help='Number of seconds to delay between each query submission',default=0)
parser.add_argument('-t', '--type', help='Analysis type to perform {response_time or completion_time}', type=str, default='response_time')
parser.add_argument('-m', '--mode', help='standard or creative mode query (creative or standard(default)', type=str, default='standard')

def sendQuery(query, url="https://ars-prod.transltr.io/ars/api/submit"):
    with open(query, "r") as f:
        query_json = json.load(f)
    r= requests.post(url,json.dumps(query_json))
    response_time = r.elapsed.total_seconds()
    rj = r.json()
    pk = rj["pk"]
    return pk, response_time 

def browser(pks,url="https://arax.ncats.io/?r="):
    logging.debug("Entering Chrome")
    if isinstance(pks, list):
        for pk in pks:
            logging.debug("Chrome processing pk: "+pk)
            logging.debug(url+pk)
            webbrowser.get('firefox').open(url+pk)
    else:
        logging.debug("Chrome processing pk: "+pks)
        logging.debug(url+pks)
        webbrowser.get('firefox').open(url+pks)


def sendAsyncQuery(query,url="https://ars-prod.transltr.io/ars/api/submit"): 

    with open(query, "r") as f:
        query_json = json.load(f)
    r= requests.post(url,json.dumps(query_json))
    rj = r.json()
    pk = rj["pk"]
    print(pk)
    browser(pk)
    total_time = single_pk_total_time(pk)
    output = {pk:(query, total_time)}
    return output


def get_files(relativePath):
    logging.debug("get_files")
    files=[]
    my_dir = BASE_PATH+relativePath
    for filename in os.listdir(my_dir):
        my_file=os.path.join(my_dir,filename)
        files.append(my_file)
    return files

def run(limit,delay, mode):
    pass
    if mode == 'standard':
        files = get_files("/queries")
    elif mode == 'creative': 
        files = get_files("/queries/creative")
    count = 0
    pk_list=[]
    response_time_list = []
    for file in files:
        current_pk, response_time= sendQuery(file)
        logging.debug("response time for the {} query is {} seconds".format(os.path.basename(file), response_time))
        pk_list.append(current_pk)
        response_time_list.append(response_time)
        time.sleep(delay)
        count+=1
        if count>=limit:
          break
    return pk_list, response_time_list

def run_async(limit, mode):
    if mode == 'standard':
        files = get_files("/queries")
    elif mode == 'creative': 
        files = get_files("/queries/creative")
    
    selected_files=random.sample(files,limit)
    pool = mp.Pool(mp.cpu_count()) 
    output = pool.map_async(sendAsyncQuery, [file for file in selected_files]).get()
    pool.close()
    
    with open(f'completion_time_{limit}_queries', 'wb') as result_file:
        pickle.dump(output, result_file)
    return output


def single_pk_total_time(pk):
    
    start_time=time.time()
    while True:
        url=f"https://ars-prod.transltr.io/ars/api/messages/{pk}?trace=y"
        r = requests.get(url)
        rj = r.json()
        if rj["status"]=="Done":
            total_time = (time.time()-start_time)/60
            logging.debug(f"all ARAs have returned results for pk {pk}")
            print(f"all ARAs have returned results for pk {pk}")
            print(f"it took {total_time} minutes for it to get completed")
            break
        elif (time.time()-start_time)/60>10:
            total_time=(time.time()-start_time)/60
            stragglers=[]
            print(f"It has taken longer than 10 minutes for pk {pk}")
            print("The following tools have not yet finished: ")
            for child in rj['children']:
                if child['status'] == "Running":
                    stragglers.append(child["actor"]["inforesid"])
            print(str(stragglers))
            break
        else:
            time.sleep(30)
    return total_time

def main():
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    args = parser.parse_args()
    count = getattr(args,"count")
    delay = getattr(args,"delay")
    type = getattr(args, "type")
    mode = getattr(args, "mode")

    logging.debug("Running {} analysis for {} {} queries".format(type, count, mode))
    if type == 'response_time':
        pks, response_time = run(int(count),delay, mode)
        logging.debug("list of pks {} for {} queries submitted ".format(pks, count))
        percentile_list=[]
        for perc in [50, 75, 90, 95, 99]:
            percentile_list.append(np.percentile(response_time, perc))
        logging.debug("Based on {} queires, the shortest response time is  {} sec, the longest response time is {} sec".format(count, min(response_time), max(response_time)))
        logging.debug("response time 50th: {}, 75th: {}, 90th: {}, 95th: {}, 99th: {}".format(percentile_list[0],percentile_list[1],percentile_list[2],percentile_list[3],percentile_list[4]))
        browser(pks)
    elif type == 'completion_time':
        results = run_async(int(count), mode)
        logging.debug("Here are results list indicating the 'pk' : (query, completion_time) for {} queries submitted on {} mode".format(count, mode))
        logging.debug(results)
    else:
        print("you have chosen a wrong analysis type, exiting...")
        quit(0)    

if __name__== '__main__':
    main()