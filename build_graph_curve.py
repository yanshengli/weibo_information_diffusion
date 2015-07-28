__author__ = 'LiGe'
#encoding:utf-8
import json
from networkx.readwrite import json_graph
import time
import numpy as np
default_encoding = 'utf-8'
def build_graph_curve():
    day=list()
    user_id=dict()
    f1=open('./data/fixed_user_2_repost.txt','wb')
    with open('./data/user_repost.txt','r') as f:
        datas=f.readlines()
        for data in datas:
            data=data.strip()
            data=data.split('\t')
            user_id[data[2].strip()]=data[1].strip()

    with open('./data/user_2_repost.txt','r') as f:
        lines=f.readlines()
        for line in lines:
            line=line.strip()
            line=line.split('\t')
            temp=line[0]
            for i in range(1,len(line)):
                print line[i][1:]
                if line[i][1:] in user_id:
                    temp=temp+'\t'+user_id[line[i][1:]]
            f1.write(temp+'\n')
        f1.close()

    f2=open('./data/fixed_user_filter_repost.txt','wb')

    with open('./data/fixed_user_2_repost.txt','r') as f:
        lines=f.readlines()
        for s_line in lines:
            line=s_line.strip()
            line=line.split('\t')
            if len(line)>1:
                f2.write(s_line)
    f2.close()

    import networkx as nx

    G=nx.DiGraph()
    id_time=dict()
    f=open('./data/user_repost.txt','r')
    lines=f.readlines()
    for line in lines:
        line=line.strip()
        line=line.split('\t')
        id_time[line[1].strip()]=line[4].strip()
        G.add_node(line[1].strip(), image=line[3].strip(),name=line[2].strip())
    G.add_node('1642591402',image='http://tp3.sinaimg.cn/1642591402/180/5728664122/1',name='sina')

    day=list()
    with open('./data/fixed_user_filter_repost.txt','r') as f:###原始的二维关系
        datas=f.readlines()
        for data in datas:
            data=data.strip()
            data=data.split('\t')
            for i in range(0,len(data)-1):
                G.add_edge(data[len(data)-i-1].strip(),data[len(data)-i-2].strip(),time=id_time[data[len(data)-i-2].strip()])
            G.add_edge('1642591402', data[len(data)-1].strip(),time=id_time[data[len(data)-1].strip()])

    with open('./data/user_repost.txt','r') as f:###抽取的一维关系
        lines=f.readlines()
        for line in lines:
            line=line.strip()
            line=line.split('\t')
            id_time[line[1].strip()]=line[3].strip()
            if (line[0].strip(),line[1].strip()) not in G.edges():
                G.add_edge(line[0].strip(),line[1].strip(),time=line[4].strip())
            day.append(line[4].strip()+":00")

    day = [time.strptime(d, '%Y-%m-%d %H:%M:%S') for d in day]
    day_weibo = time.strptime('2015-06-18 14:45:00', '%Y-%m-%d %H:%M:%S') #源微博发出时间
    hours = [(int(time.mktime(i))-int(time.mktime(day_weibo)))/3600 for i in day]
    #print 'hours',hours
    values, base = np.histogram(hours, bins = int(hours[0]))
    cumulative = np.cumsum(values)
    #print values
    #print cumulative
    #print base
    #data = json_graph.node_link_data(G)
    #json_data=json.dumps(data)
    #print json_data
     #data = json_graph.node_link_data(G)
    #json_data=json.dumps(data)
    node_entry=list()
    for node in G.nodes():
        node_entry.append(dict(id=node,image=G.node[node]['image'],name=G.node[node]['name']))
    #print G.node['3665811017']['name']
    edge_entry=list()
    edge_att=nx.get_edge_attributes(G,'time')
    for edge in G.edges():
        edge_entry.append(dict(source=edge[0],target=edge[1],time=edge_att[edge[0],edge[1]]))

    base_list=list()
    value_list=list()
    cumulative_list=list()    
    for i in range(0,len(base)):
        base_list.append(int(base[i]))
        if i==0:
            value_list.append(0)
            cumulative_list.append(int(0))
        else:
            value_list.append(int(values[i-1]))
            cumulative_list.append(int(cumulative[i-1]))        

    return node_entry,edge_entry,value_list,cumulative_list,base_list

