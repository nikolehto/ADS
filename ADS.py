#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import codecs
import os.path

'''
ADS final exercise for the ADS 2014 course.
Mikko Lehto
'''

import json
import pickle
import time
import datetime
import random 	#to find random hashtags or paths
from collections import deque


raw_data = deque([])	# data which has not be processed
data_ids = set()		# id's with some data here before processing
all_ids = set()			# Consists also 'edge' ids, ids which someone follows
messages = []			# Contains all messages in order
links_data = {}			# Contains id:idsfriends
time_data = {}			# Contains times as key and ids and messageindexes as values
hashtag_data = {}		# Contains hashtags as keys and ids, msgindexes and times as values


if sys.stdout.encoding == 'ISO-8859-1':	# 
	encodewith = 'utf-8'				# utf-8 works better than latin-1 at our schools remote desktop
else:
	encodewith = sys.stdout.encoding	# cp850 or cp1252

########### READ AND SAVE ###################

def read_json():	#1
	""" appends raw_data with data of json file. 
	remember ids with some data"""
	filename = raw_input("Filename: ") 
	
	if not os.path.isfile(filename):
		filename += ".json"
		if not os.path.isfile(filename):
			print "File doesn't exists\n"
			return
	
	print "Reading %s:" % filename
	s = time.time()
	
	with open(filename, 'r') as file:
		for line in file:			# (very)little bit faster than for line in open(filename) 
			user = json.loads(line)
			
			if not (user['id'] in data_ids):
				raw_data.append(user)
				data_ids.add(user['id'])
			else:
				print "Person", user['id'], "was already in the data"
	
	print "%.3fs" % (time.time() - s)
	process_data()

def save_data(): # Very slow.
	""" save processed data """
	filename = raw_input("Filename: ") 
	
	if not filename[-2:] == '.p':
		if not '.' in filename:
			filename += ".p"
		else:
			print "Bad Filename"
			return
			
	print "Writing %s:" % filename
	
	s = time.time()
	with open(filename, 'wb') as file:
		pickle.dump((all_ids, data_ids, messages, links_data, time_data, hashtag_data), file)
	print "%.3fs" % (time.time() - s)	
	
		
def read_data():	# very slow
	""" load processed data """
	filename = raw_input("Filename: ") 
	
	if not os.path.isfile(filename):
		filename += ".p"
		if not os.path.isfile(filename):
			print "File doesn't exists"
			return
	
	print "Reading %s:" % filename
	
	s = time.time()
	
	with open(filename, 'rb') as file:
		data = pickle.load(file)
	return data
	
def process_data(): #1
	""" empties raw_data and process it into five containers:
	links_data => {<id> : set(<connections>)}
	messages => [message]
	time_data => {<message_time>:[id, <message_index>]}
	hashtag_data => {<hash_tag>:[(id, <message_index>, time)]}
	all_ids => set(ids)
	"""
	global links_data
	global data_ids
	print "Processing:"
	s = time.time()
	#####	STAGE 1: raw_data - > containers #####
	months = {'Jan': 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4, 'May' : 5, 'Jun' : 6, 'Jul' : 7, 'Aug' : 8, 'Sep' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12}
	all_ids.update(data_ids) # if someone whose anybody doesn't follow
	while raw_data:
		user = raw_data.pop()
		id = user['id']
		userfriends = set(user['friends_ids'])
		links_data[id] = userfriends
		all_ids.update(userfriends)
		
		
		tweets = user['last_ten_tweets']
		for tweet in tweets:	
			tim = tweet['created_at']
			message_time = datetime.datetime(int(tim[-4:]), months[tim[4:7]], int(tim[8:10]), int(tim[11:13]), int(tim[14:16]), int(tim[17:19]))
			
			message = tweet['text'].encode(encodewith, 'ignore')
			messages.append(message)#, 'ignore'))				#Now latest message is last

			message_index = len(messages)-1
			
			if message_time not in time_data.keys():
				time_data[message_time] = [(id, message_index)]	# it's probably empty so create a list
			else:
				time_data[message_time].append((id, message_index)) # but if not just append.
			
			raw_hashtags = tweet['entities']['hashtags']
			for raw_hashtag in raw_hashtags:
				hashtag = raw_hashtag['text'].encode(encodewith, 'ignore')
				if hashtag in hashtag_data.keys():
					hashtag_data[hashtag].append((id, message_index, message_time))		# if there is list -> append
				else:
					hashtag_data[hashtag] = [(id, message_index, message_time)]			# else -> create a list
	
	###### Stage 2: reprocess links_data	#####
	## links_data now: {a : [a->b, a->d, a->e]} a is following
	## links_data after: (a : [a<->b, a<->c, a<->d, a<->e]) a is following or X is following a
	#############################################
	
	for user in data_ids:	# Only ids who are following someone												
		for new_connection in links_data[user]:			#There might be new connection with ids		
			if new_connection not in links_data:		
				links_data[new_connection] = set()
			links_data[new_connection].add(user)
	print "%.3fs\n\n" % (time.time() - s)
############ CONNECTIONS ######################
			
def find_node_of_highest_degree(): #2
	"""Output the person with the greatest number direct c
	onnections. If there are several such persons,
	output all of them"""
	s = time.time()
	print "Finding user with the greatest number of direct connections:"
	max = -1
	for user, cons in links_data.iteritems():
		degree = len(cons)
		if degree > max:
			max = degree
			maxusers = set([user])
		elif degree == max:
			maxusers.add(user)
	
	print "%.3fs" % (time.time() - s)
	if max != -1:
		for maxuser in maxusers:
			print "User %d has %d connections:" % (maxuser, max)

	else:
		print "Nobody has any connections"
		
	print	
			
def find_shortest_link(a = None, b = None): #3
	""" Finds shortest link between a and b"""
	## Verkonleveysalgoritmi kurssin materiaaleista, Optimoitu 
	global links_data
	
	if not (a or b):
		a, b = random.sample(all_ids, 2)
	
	if not a in all_ids:
		print 'a does not exists'
		return False
		
	if not b in all_ids:
		'b does not exists'
		return False
	
	cdp = {}
	q = deque([]) 
	
	cdp[a] = 0
	q.append(a)
	while q:
		u = q.popleft()		# FIFO like in materials
		if b in links_data[u]:
			cdp[b] = u
			path = []
			while b:
				path.append(b)
				b = cdp[b]	#cdp[a] = 0 - > False
			return path

		for v in links_data[u]:						#v in a's friends
			if v not in cdp:
				cdp[v] = u
				q.append(v)

	print 'not found'
	return False

def link_of_hashtags(tag = None, id = None, printtweets = False): #3
	# Finds closest connection(s) which has message(s) with same hashtag
	# in case of many messages function controls program to print only earliest message
	notgoids = set([])
	tagfound = False	
		
	while not tag:
		tag = random.sample(hashtag_data, 1)[0]
		if len(hashtag_data[tag]) == 1:
			tag = None
			continue
			
		firstid = hashtag_data[tag][0][0]
		for i in hashtag_data[tag]:
			if firstid != i[0]:
				tagfound = True
				break	# breaks only for loop
		if not tagfound:
			tag = None	# We need to continue
			
	else:	# While-Else only in python ?
		if not tag in hashtag_data:	# Check does tag has two tweets from different ids
			print 'No messages with #%s' % tag
			return False
		
		firstid = hashtag_data[tag][0][0]
		for i in hashtag_data[tag]:
			if firstid != i[0]:
				tagfound = True
				break
		if not tagfound:
			print "Only one user has used #%s" % tag
			return False

	if not id:
		id = random.sample(hashtag_data[tag], 1)[0][0]	# 1. return set([id, msgindex,time)] , 2.take random element in list, 3. (1.[0]) open list 4. (2. [0]) take first value (id)
		print "random id is: %d" % id
	
	if printtweets:
		tweets_by_hashtag(tag)	## Test

	has_used_hashtag = False	
	for i in hashtag_data[tag]:
		if id in i:
			has_used_hashtag = True
	
	if not has_used_hashtag:
		print 'User has not used hashtag %s' % tag
		return
	
	notgoids.add(id)
	
	if tag in hashtag_data:
		count = len(hashtag_data[tag])
		if count > 1:
			shortest_path = []
			for i in hashtag_data[tag]:		# 							i in form [id, msgindex, time]
				b = i[0]	# a = where we start, b = where we go
				if b in notgoids:	# if we has visited, dont go again
					for tup in shortest_path:	# shortest_path is empty at round one but later it has form ((id,msgind, time), path) 
						if b in tup[0]:			# if id is on shortest path tup[0] form (id, msg, time)
							shortest_path.append((i, tup[1]))	# we need to add a message
							break # It found already
					continue	# Don't find path id <-> id or id <-> id where we has visited
				
				path = find_shortest_link(id,b)
				notgoids.add(b)	# If there is multiple tweets with same hashtag
				
				if not path:
					continue
				
				if len(shortest_path) == 0:
					shortest_path = [(i, path)]	# Shortest path is list of tuples
					
				elif len(path) < len(shortest_path[0][1]):
					shortest_path = [(i, path)]

				elif len(path) == len(shortest_path[0][1]):
					shortest_path.append((i, path))
					
			if len(shortest_path) > 0:	# Has found
				print "Found %d tweets with same length of connection:" % (len(shortest_path))
				find_and_print_earliest_tweet(shortest_path)

			else:
				print "Not Found"
		else:
			print "Found only one user who has used #%s." % tag

def find_and_print_earliest_tweet(nodes): #3
	### Form of node: [((id,msgindex,time), [path])]
	## containers are not made for this
	## because I didn't read well the instructions
	### So i just reprocess data
	times = {}
	for node in nodes:
		times[node[0][2]] = node
	id_msgindex_time = times[min(times)]
	path_printer(id_msgindex_time[1])
	print 
	print "%s\n%d: %s " % (str(id_msgindex_time[0][2]), id_msgindex_time[0][0], messages[id_msgindex_time[0][1]])


def path_printer(path): #3
	#if not path:
	#	print 'Not Found'
	#	return False
	
	print "Lenght: %d" % (len(path)-1)
	print "Path:",
	for node in reversed(path):
		print "%d" % node,
		if node != path[0]:
			print "<->",
	print


def tweets_by_hashtag(tag):
	message_times = {}				# time: (id, message)
	print "Messages with #%s:\n" % tag
	print
	
	if tag not in hashtag_data:
		print "Not found any tweets"
		return
		
	for i in hashtag_data[tag]:							
		message_times[i[2]] = (i[0], messages[i[1]])	# time: (id, message)
	
	for time in sorted(message_times):
		print str(time)
		print "%d: %s" % (message_times[time][0], message_times[time][1])
		print
		
		
def tweets(start = None, end = None, user = None):
	""" parameters are optional """
	if not start:		# But this function can be called with empty strings
		start = datetime.datetime.min
	if not end:
		end = datetime.datetime.max
	if not user:		# Just to make it clear	
		user = None
		
	somethinghasprinted = 0
	for time in sorted(time_data):
		if (start <= time <= end):
			for i in time_data[time]:	# messages at same second, very short list
				if (not user) or (user == i[0]):
					print str(time)
					print "%d: %s" % (i[0], messages[i[1]])
					print "*********************************"
					somethinghasprinted = 1
	if not somethinghasprinted:
		print "No any tweets"
	print

		
############## MAIN MENU ####################

#def read_or_save():
#	menu = -1	# Local
#	options1 = { '1' : read_json,
#				 '2' : read_data,
#				 '3' : save_data,
#				 '4' : None}
	
#	while menu:
#		menu = -1
#		print "**** READ OR SAVE ****"
#		print "1: Read .json file"				# Part 1: 1, 2, Part 5:
#		print "2: Read .p file"
#		print "3: Write .p file"
#		print "4: Previous Menu"
#		while menu not in options:
#			menu = raw_input("Choice: ")
#		if menu == '4':
#			break
		
#		options1[menu]()
#	print 
	
def c_find_shortest_link():
	a = None
	b = None
	
	while not a:
		a = raw_input("'r' for random ids \nGive id A: ")
		if a == ('r' or 'R'):
			path_printer(find_shortest_link())
			return
			
		try:
			a = int(a)
		except ValueError:
			a = None
			
	while not b: 
		try:
			b = int(raw_input("Give id B: "))
		except ValueError:
			b = None
			
	path_printer(find_shortest_link(a,b))
	
def c_link_of_hashtags():
	tag = None
	id = None
	
	while not tag:
		tag = raw_input("'r' for random hashtag and id\nGive hashtag: ")
		if tag == ('r' or 'R'):
			link_of_hashtags()
			return
	
	while not id:
		id = raw_input("'r' for random id\nGive id: ")
		if id == ('r' or 'R'):
			link_of_hashtags(tag)
			return
		else:
			try:
				id = int(id)
			except ValueError:
				id = None
		
	link_of_hashtags(tag, id)
	
	
def c_test_series():
	count_of_connections = None
	count_of_hashtags = None
	
	while not (count_of_connections and count_of_hashtags):
		try:
			count_of_connections = int(raw_input("How many shortest links: "))
			count_of_hashtags = int(raw_input("How many hashtags links: "))
		except ValueError:
			print 'Bad Input'
		if ((count_of_connections == 0) and count_of_hashtags) or (count_of_connections and (count_of_hashtags == 0)):
			break
	
	s = time.time()
	print "Finding %d shortest links, and %d hashtag links" % (count_of_connections, count_of_hashtags)
	
	while count_of_connections > 0:
		path_printer(find_shortest_link())
		count_of_connections -= 1
	
	while count_of_hashtags > 0:
		link_of_hashtags()
		count_of_hashtags -= 1
	
	print "Time: %.3fs" % (time.time() - s)
	
	
def c_tweets_hashtags():
	tag = raw_input('Hashtag:')
	tweets_by_hashtag(tag)
	
def c_tweets_time_user():
	user = raw_input('User (optional): ')
	if user:
		try:
			user = int(user)
		except ValueError:
			print 'Bad input'
			return
	
	print "Tweets after time (optional):"
	print "YYYYMMDD"
	start = raw_input('')
	if start:
		try:
			start = datetime.datetime(int(start[:4]), int(start[4:6]), int(start[6:8]))
		except ValueError:
			print 'Bad Input'
			return
	
	print "Tweets before time (optional):"
	print "YYYYMMDD"
	end = raw_input('')
	if end:
		try:
			end = datetime.datetime(int(end[:4]), int(end[4:6]), int(end[6:8]))

		except ValueError:
			print 'Bad Input'
			return

		day = datetime.timedelta(days = 1)
		end = end + day	# all messages of last day 
			
			
	tweets(start, end, user)
											
def data_info():
	print "**** DATA INFO ****"
	print "file consists data of %d users" % len(data_ids)
	print "file consists %d ids with at least one connection" % len(links_data)	# Part 3
	print "file consists %d ids" % len(all_ids)
	find_node_of_highest_degree()				# Part 1: 4, Part 3
	print
	
def shortest_link_menu():
	menu = -1	# Local
	options3 = { '1' : c_find_shortest_link,
				 '2' : c_link_of_hashtags,
				 '3' : c_test_series,
				 '4' : None}
	while menu:
		menu = -1
		print "**** SHORTEST LINK ****"
		print "1: Shortest link of two given ids"	# Part 1: 3 , Part 3
		print "2: Shortest link of given hashtag"	# Part 3
		print "3: Test Series"
		print "4: Back"
		while menu not in options:
			menu = raw_input("Choice: ")
		if menu == '4':
			break
			
		options3[menu]()
	print
		
def tags_tweets_menu():
	menu = -1	# Local
	options4 = { '1' : c_tweets_hashtags,
				 '2' : c_tweets_time_user,
				 '3' : None}
	while menu:
		menu = -1
		print "**** TWEETS MENU ****"
		print "1: Print tweets with hashtag"		# Part 1: 5, Part 4
		print "2: Print messages in time interval or user"	# Part 1: 6, Part 4
		print "3: Back"
		while menu not in options:
			menu = raw_input("Choice: ")
		if menu == '3':
			break
			
		options4[menu]()
	print

############################	
#Main Menu
############################	
if __name__ == '__main__':

	
	
	options = { '1' : read_json,		# User is able to add first/new file
				'2' : data_info,			# Shows greatest number of connections, number of users
				'3' : shortest_link_menu,	# Shortest link between two numbers
				'4' : tags_tweets_menu,		# print messages with tags, all tweet things
				'9' : sys.exit}
	
	menu = -1
	
	while menu:
		menu = -1
		print "**** Twitter Analyser ****"
		print "1: Read data"
		
		if data_ids:
			print "2: Data Info"
			print "3: Find shortest links"
			print "4: Tweets and hashtags"
			print "9: Exit"
		
		while menu not in options:
			menu = raw_input("Choice: ")
			if not data_ids and menu != '1':
				menu = -1
				
		print
		options[menu]()
