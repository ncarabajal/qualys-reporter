#!/usr/bin/python

import qualysapi
import traceback
import xmltodict
import datetime
import time
import os.path
import glob
import re

folder		= os.getcwd()+'/results/'
resid		= []
result		= []


# check if the credential file ".qcrc" is in the cwd, else create it
def connect_api():
	if not os.path.isfile(os.getcwd()+'/.qcrc'):

		# create the qcrc, enter your qualys credentials
		print('creating .qcrc in '+folder+', enter your qualysguard credentials below;')
		#print'creating .qcrc in '+folder+', enter your qualysguard credentials below;'
		qgs	= qualysapi.connect(remember_me=True)

	else:
		# connect using existing .qcrc
		qgs	= qualysapi.connect()

	# connect to the API and list reports as an XML
	ret 	= qgs.request('/api/2.0/fo/report', {'action': 'list'})
	root	= xmltodict.parse(ret)

	# iterate over available reports for your account, parse timestamps in epoch
	for x in root['REPORT_LIST_OUTPUT']['RESPONSE']['REPORT_LIST']['REPORT']:
		#print(x)

		y1	= x['LAUNCH_DATETIME']
		y2	= datetime.datetime.strptime(str(y1), '%Y-%m-%dT%H:%M:%SZ').strftime('%s')

		z1	= x['EXPIRATION_DATETIME']
		z2	= datetime.datetime.strptime(str(z1), '%Y-%m-%dT%H:%M:%SZ').strftime('%s')

		a	= x['ID']+','+y1+','+y2+','+z1+','+z2+','+x['USER_LOGIN']+','+x['OUTPUT_FORMAT']+','+x['SIZE']
		print(a)
		#print a

		result.append(str(a)+'\n')
		resid.append(int(x['ID']))

	#print ''
	print('')
	# check for reports that arent downloaded yet, else skip
	tmp	= []
	tmp.append(glob.glob(os.getcwd()+'/results/*csv'))

	for x in resid:
		found	= False
		for y in tmp:
			if re.search(str(x), str(y)):
				found	= True

		fname	= str(x)+'_'+str(y2)+'.csv'

		if found == False:
			print ('downloading '+fname)
			#print 'downloading '+fname
			download_report(x, fname)
		else:
			print('skipping '+fname)
			#print 'skipping '+fname

	# write an overview of report metadata to a csv
	f	= open(os.getcwd()+'/reports.csv', 'wb')
	for x in result:
		f.write(x)
	f.close


# download reports based on their ID value
def download_report(rid, fname):
	qgs	= qualysapi.connect()
	ret = qgs.request('/api/2.0/fo/report', {'action': 'fetch', 'id': rid})
	#print(ret)

	# write the report  as csv to disk with the id and timestamp in fname
	f	= open(str(folder+fname), 'w')
	f.write(ret)
	f.close

###

connect_api()
