# ADS  
Algorithms and data structures exercise  

ADS Course work   
Tasks:  
1. Read json data  
2. Calculate sum of ids with at least one connection ( connection = a follows b or b follows a)  
3. Find id that have most connections  
4. Find shortest link between two person  
5. Find shortest link between persons using same hashtag  
Extra  
6. Test series  
7. Find random hashtag  
  
How to use:   
1. choose 1 (Read data)  
2. Filename, for example 'sample'  
  
Read data : Read another file  
Data Info : Tells how many ids json file consists, what is greatest amount of connections, and how many users is in data 
Find Shortest Links : User is able to search shortest link between two ids, or between given hashtag and id. There is also random/test functionality implemented  
Tweets and hashtags : Search all tweets which contain specific hashtag, Print messages in defined time interval (and specific usr)  
  
Sample.json is subset of actual data. It contains tweets from 12.5.2014 to 4.12.2014  
it consists over 1 000 000 unique ids, and data of 146 users  

Known bugs:  
Program can't handle if user tries to find connection between 'a' and 'a' (if ids are same)  
Hashtag search cannot be '#word', it must be typed just 'word'  
  
