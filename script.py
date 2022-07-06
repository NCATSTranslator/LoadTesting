import requests
import json
import os
import logging
import webbrowser
import time
import numpy as np
import argparse
import multiprocessing as mp

BASE_PATH=os.path.dirname(
      os.path.realpath(__file__)
    )
parser = argparse.ArgumentParser(description='Load Tester')
parser.add_argument('-c', '--count', help='Number of queries to be run', default=10)
parser.add_argument('-d','--delay',help='Number of seconds to delay between each query submission',default=0)


def sendQuery(query, url="https://ars-prod.transltr.io/ars/api/submit"):
    with open(query, "r") as f:
        query_json = json.load(f)
    r= requests.post(url,json.dumps(query_json))
    response_time = r.elapsed.total_seconds()
    rj = r.json()
    pk = rj["pk"]
    return pk, response_time 

def get_files(relativePath):
    logging.debug("get_files")
    files=[]
    my_dir = BASE_PATH+relativePath
    for filename in os.listdir(my_dir):
        my_file=os.path.join(my_dir,filename)
        files.append(my_file)
    return files

def run(limit,delay):
    pass
    files = get_files("/queries")
    count = 0
    pk_list=[]
    for file in files:
        print(file)
        current_pk, response_time= sendQuery(file)
        logging.debug("response time for the {} query is {}".format(os.path.basename(file), response_time))
        pk_list.append(current_pk)
        time.sleep(delay)
        count+=1
        if count>=limit:
          break
    return pk_list

def browser(pk_list,url="https://arax.ncats.io/?r="):
    logging.debug("Entering Chrome")
    for pk in pk_list:
        logging.debug("Chrome processing pk: "+pk)
        logging.debug(url+pk)
        webbrowser.get('firefox').open(url+pk)

    
def single_pk_total_time(pk):
    
    status_list=[]
    start_time=time.time()
    while True:
        url=f"https://ars-prod.transltr.io/ars/api/messages/{pk}?trace=y"
        r = requests.get(url)
        rj = r.json()
        for child in rj['children']:
            if child['status'] == "Error":
                pass
            else:
                status_list.append(child['status'])

        if all( x == "Done" for x in status_list):
            print(f"all ARAs have returned results for pk {pk}")
            logging.debug(f"all ARAs have returned results for pk {pk}")
            stop_time=time.time()
            total_time = (stop_time - start_time)/60
            print(f"it took {total_time} for it to get completed")
            logging.debug(f"it took {total_time} for it to get completed")
            break
        
        status_list=[]
        time.sleep(30)
        continue

    return total_time

def get_completion_time(pk_list):
    ##https://www.machinelearningplus.com/python/parallel-processing-python/#:~:text=The%20general%20way%20to%20parallelize,of%20Pool%20s%20parallization%20methods.
    # Step 1: Init multiprocessing.Pool()
    pool = mp.Pool(mp.cpu_count())  
    # Step 2: `pool.apply` the single_pk_total_time
    Done_time = pool.map(single_pk_total_time, np.array(pk_list))
    pool.close()  
    #Done_t = Done_time.get() 
    #print("output done time {}".format(Done_t))
    print(Done_time[:10])
    return Done_time


def main():
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    args = parser.parse_args()
    count = getattr(args,"count")
    delay = getattr(args,"delay")
    logging.debug("Number of queries to be run: {}".format(count))
    pks=run(int(count),delay)
    logging.debug("list of pks {} for {} queries submitted ".format(pks, count))
    #browser(pks)
    done_time=get_completion_time(pks)
    print(f'done time is {done_time} minuets')
    logging.debug("list of total_done time {} for {} queries submitted ".format(done_time, count))


if __name__== '__main__':
    main()