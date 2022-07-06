import requests
import json
import os
import logging
import webbrowser
import time
import argparse
from statistics import mean

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
    response_time_list = []
    for file in files:
        print(file)
        current_pk, response_time= sendQuery(file)
        logging.debug("response time for the {} query is {} seconds".format(os.path.basename(file), response_time))
        pk_list.append(current_pk)
        response_time_list.append(response_time)
        time.sleep(delay)
        count+=1
        if count>=limit:
          break
    return pk_list, response_time_list

def browser(pk_list,url="https://arax.ncats.io/?r="):
    logging.debug("Entering Chrome")
    for pk in pk_list:
        logging.debug("Chrome processing pk: "+pk)
        logging.debug(url+pk)
        webbrowser.get('firefox').open(url+pk)



def main():
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    args = parser.parse_args()
    count = getattr(args,"count")
    delay = getattr(args,"delay")
    logging.debug("Number of queries to be run: {}".format(count))
    pks, response_time=run(int(count),delay)
    logging.debug("list of pks {} for {} queries submitted ".format(pks, count))
    logging.debug("Based on {} queires, the shortest response time is  {} sec, the longest response time is {} sec, and the average response time is {} sec".format(count, min(response_time), max(response_time), mean(response_time)))
    #browser(pks)

if __name__== '__main__':
    main()