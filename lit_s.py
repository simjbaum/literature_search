import os, re
from Bio import Entrez
import time as time

asked_for_n_papers = 75 # how many papers you want to retrieve?
chunk_size = 25 # how much data you want to read in one instance - there is a limit to get server answers

def search(query):
    Entrez.email = 'your.email@example.com'
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax= asked_for_n_papers ,
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle)
    return results

##############################################################################################
##############################################################################################
##############################################################################################

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'your.email@example.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

##############################################################################################
##############################################################################################
##############################################################################################

def your_search_terms_beta(your_target_list, your_search_terms, output):
    """ get the pubmed count or titles associated with genes and your search term. You can choose between output as count for the number of hits or the abstracts to get back 
    For EXAMPLE: your_search_terms(your_target_list = ["ABC2", "ABC1"], 
                                your_search_terms = ["fibrosis"], 
                                output = "count") """ 
    
    
    # formar and check input:
    if type(your_search_terms) != list:
        return "please provide the search terms as a list e.g.: ['heart']"
    
    sleep_time = 1
    # sleep_time_long = 3
    
    
    res_d = {}
    counter_search_term = 0 # keep track if the tool makes progress
    
    for term in your_search_terms:
        counter_search_term += 1
    
        for target in your_target_list:
            print("." + target)
            print(target)

            # define the search term:
            search_term = "{} AND {}".format(target, term)
            
            papers = []
            titles_list = []
            
            time.sleep(sleep_time)
            
            trigger = True
            
            while trigger:
                # search the data base: 
                try:
                    results = search(search_term) # query ## sensitive step  - search query is fired to NCBI # this step can lead to the crash of the program
                    #print#("tried and worked")
                    trigger = False
                except:
                    #print#("didnt work")
                    time.sleep(sleep_time)
                    pass
                #print#("return to trigger")
            
            id_list = results['IdList'] # list of UIDs - this will give us the article ID
            
            
            #print#(results)
            ## add a timer here to know how many genes from the list were searched yet and how many more to go ##
            #print#("count")
            
            if id_list: # if there something found for the query it should be in the ID list
                
                for chunk_i in range(0, asked_for_n_papers , chunk_size): # if there are more than 50 papers on the search query, we cap it there, this already shows that there is plenty of literature
                    chunk = id_list[chunk_i:chunk_i + chunk_size]
                    
                    if not chunk: # if empty list
                        #print#("pass")
                        break
                    trigger_2 = True
                    while trigger_2:
                        
                        try: 
                            ##print#("searchtermfired")
                            time.sleep(sleep_time)
                            papers = fetch_details(chunk)
                            for articles in papers["PubmedArticle"]:
                                titles_list.append(articles["MedlineCitation"]["Article"]["ArticleTitle"])

                            res_d[str(target) + "_" + term] = titles_list
                            #print#("fetched")
                            trigger_2 = False
                        except: # occasionally a chunk might annoy your parser
                            time.sleep(sleep_time)
                            #print#("trapped in loop")
                            pass
            else: # if there is nothing in the list
                res_d[str(target) + "_" + term] = ["none"]
                #print#(res_d)
            
        print(counter_search_term / len(your_search_terms))

    # define the number of paper you get for your query:
    # how many papers do we collect for the query?
    ##print#(res_d)
    res_count = {}
    for query in res_d.keys():
        if res_d[query][0] == "none":
            ##print#(query)
            ##print#(type(query))
            gene = query.split("_")[0]
            res_count[gene] =  0 
        else: 
            ##print#(query.split("_")[0])
            gene = query.split("_")[0]
            res_count[gene] =  len(res_d[query]) 
            #res_count.append([query, len(res_d[query])])
    
    df = pd.DataFrame(list(res_count.values()), index = res_count.keys(), columns=[your_search_terms[0] ])

    if output == "count":
        return df

    # write data out
    if not os.path.exists("/home/jupyter-user/analysis/aortic_workshop/temp_output/" + term):
        os.makedirs("/home/jupyter-user/analysis/aortic_workshop/temp_output/" + term)

    df.write_csv("/home/jupyter-user/analysis/aortic_workshop/temp_output/" + term + "/temp.csv")
    return df, res_d