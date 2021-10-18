#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json

def get_config(data):
    file_route = './data/' + list(data.value.values())[0]['metadata']['name']

    with open(file_route) as f:
        system_config = json.load(f)

    return(system_config)

# To return the ROUTE of the uploaded CSV file
def get_data_route(data_files):
    return(data_files)

