#! /usr/local/bin/python3
# init.py find your unread messages and send them to you aa a summary
# I know it have a lot of failures but with this I think you can make your own improved version

#first of all (maybe Fourth), my first language is not English, so I may have faults writing it, thank you for your understanding

#to make this work you need to download the Google APIs Client Library for Python
#more info how to do it, in https://developers.google.com/api-client-library/python/start/installation

import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import time
from datetime import timezone
from datetime import timedelta
from datetime import datetime
import sendEmail
import listMail
import modifyMail
import re  # regex library
import getMessage as mess

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


''' the main function is at the bottom '''

""" TODO obtain this data from a properties file"""
#global scope variables
FROM = 'Roberto Morales <razielku@razielku.cl>' # your mail
TO = 'razielku@razielku.cl' #
NAME = 'Roberto' #
CC = None # email to Copy in format 'email1@domain.com; email2@domain.com'
BCC = None #the same as CC
TIMEZONE = -4 #the actual time zone, to change dates if they are in UTC


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-test.json') #this file is where the account's credentials go after the authentication with the secret
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:

        ''' If modifying these scopes, delete your previously saved credentials
         at ~/.credentials/gmail-python-test.json'''
        scopes = 'https://mail.google.com/'  # more info about scopes in https://developers.google.com/gmail/api/auth/scopes#gmail_scopes

        clientSecretFile = 'client_secret.json'

        """ this is important, your own json file with the OAUTH2 Google access to the Gmail Api
        more info in https://developers.google.com/identity/protocols/OAuth2  and  https://developers.google.com/api-client-library/python/guide/aaa_oauth
        I put an example of client_secret.json file
        you can download your own file in the developer console, more info in https://support.google.com/cloud/answer/6158857?hl=en&ref_topic=6262490
        in my case, I generated the file and didn't changed anything of it
        """

        appName = 'Gmail API Python Test'
        flow = client.flow_from_clientsecrets(clientSecretFile, scopes)
        flow.user_agent = appName
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def labels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label)


def markUnread(service, mailID, count=0):
    try:
        modifyMail.ModifyMessage(service, 'me', mailID, modifyMail.MarkUnreadLabel())
    except Exception:
        print(" an exception ocurred while Trying to 'read' the email : " + str(Exception))
        if count < 3:
            time.sleep(60) #wait a minute before retrying (I know there are better option to retry an action, but this work, so let it be)
            markUnread(service, mailID, count=count+1)


def markRead(service, mailID, count = 0):
    try:
        modifyMail.ModifyMessage(service, 'me', mailID, modifyMail.MarkReadLabel())
    except Exception:
        print(" an exception ocurred while Trying to 'unread' the email : " + str(Exception))
        if count < 3:
            time.sleep(60) #
            markRead(service, mailID, count=count+1)


def readEmails(service):
    labels(service) #print all the labels in the account
    emails = listMail.ListMessagesWithLabels(service, 'me', ['UNREAD'])
    #we search all the emails with the label ID UNREAD, if you want to add labels just add the ID like this ['UNREAD','your_label']
    analized = {}
    global FROM  #Global Scope variables
    global CC
    global BCC
    global TO
    global FROM
    global NAME
    global TIMEZONE

    #email regex
    emailRegex= re.compile(r'''(
                                [a-zA-Z0-9._%+-]+   #username
                                @                   # arroba
                                [a-zA-Z0-9.-]+      #dominio
                                \.[a-zA-Z]{2,4}   #punto algo
                                )''', re.VERBOSE)
    #regex to find the From, Date and Subject of the email
    fromRegex = re.compile(r'From:\s*(\w*\W*\s*)*?((<)*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})(>)*)') # the same but a little more permisive in the name
    dateRegex = re.compile(r'Date:\s(\w+,\s\d+\s\w+\s\d+\s\d+:\d+:\d+\s?\-\d+)')
    subjectRegex = re.compile(r'Subject:\s([\w\d\s\W]+?)\n')
    try:
        if not emails:
            print('No emails found. Exiting...')
            exit()
        else:
            print(str(len(emails))+' emails:')
            for mail in emails:
                mimeMail = mess.GetMimeMessage(service, 'me', mail['id'])# we obtain the email by the id
                body = str(mimeMail) #pass the mime Message to string
                sender = (emailRegex.findall(str(fromRegex.findall(body))))[0]
                date = dateRegex.findall(body)[0]
                subj = subjectRegex.findall(body)[0]
                

                if sender:
                    if sender not in analized.keys(): #we add it to the dictionary if not exist in it
                        analized[sender] = {'count': 1,'subjects':{subj:1,},}
                    else: #otherwise add 1 to the count
                        analized[sender]['count'] += 1
                        if subj not in analized[sender]['subjects']: #the same with the subject
                            analized[sender]['subjects'][subj] = 1
                        else:
                            analized[sender]['subjects'][subj] += 1

                    date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z') #pass the string date we found in the message and return a datetime object
                    if date and date.tzinfo == timezone.utc: #if the timezone of the email is UTC add our timezone
                        date = date + timedelta(hours=TIMEZONE)

                    if 'fromDate' in analized[sender].keys(): #compare the dates in the dictionary to put the greatest as last Date and the minim as first Date
                        if analized[sender]['fromDate'] > date:
                            if 'toDate' in analized[sender].keys():
                                if analized[sender]['toDate'] < analized[sender]['fromDate']:
                                    analized[sender]['toDate'] = analized[sender]['fromDate']
                                analized[sender]['fromDate'] = date
                            else:
                                analized[sender]['toDate'] = analized[sender]['fromDate']
                                analized[sender]['fromDate'] = date
                        elif 'toDate' in analized[sender].keys():
                            if analized[sender]['toDate'] < date:
                                analized[sender]['toDate'] = date
                        else:
                            analized[sender]['toDate'] = date
                    else:
                        analized[sender]['fromDate'] = date

        bndbnt = ' mornings' if int(time.strftime("%H"))<=12 else ' night' if int(time.strftime("%H"))>=20 else ' evening'
        s = 's' if len(emails)>1 else ''
        a = 'an' if len(emails)==1  else str(len(emails))

        initMessage = '<p>Good'+bndbnt+' '+NAME+', I found '+a+' unread message'+s + ' .  </p>\n'
        bodyMessage = initMessage +'<table>\n'
        for sender in analized.keys():
            dates = '<td>'+('at '+str(analized[sender]['fromDate'].date()) +' '+ str(analized[sender]['fromDate'].time())   #str(fdesde.date())+' '+str(fdesde.time())
                            if 'toDate' not in analized[sender] else
                            'from: '+str(analized[sender]['fromDate'].date()) +' '+ str(analized[sender]['fromDate'].time())
                            +' to: '+str(analized[sender]['toDate'].date()) +' '+ str(analized[sender]['toDate'].time()))+'</td>'
            bodyMessage += '<tr>' +'<td> From '+str(sender)+'</td> ' \
                            '<td>'+str(analized[sender]['count'])+ (' times' if analized[sender]['count']>1 else ' time')+'</td>'+\
                           dates+'</tr>\n'
            for subject in analized[sender]['subjects']:
                bodyMessage += '<tr> <td>with the Subject: '+str(subject)+'</td>' \
                                    '<td>'+str(analized[sender]['subjects'][subject])+ (' times' if analized[sender]['subjects'][subject]>1 else ' time')+'</td></tr>\n'

        bodyMessage += '</table>\n'
        mensajeEnd = '<p></p><p></p>\n' \
                     '<p>Sincerely </p>\n' \
                     '<p>Your Own Script Who Analize Your Email For You. A.K.A. YOSWAYEFY  </p>\n'  #the sign ;)

        finalMessage = bodyMessage + mensajeEnd #

        subject = str(len(emails))+' Unread Email'+s+' ' #the Subject of this email

        email = sendEmail.CreateFullMessage(FROM,TO,subject,finalMessage,CC,BCC)
        if len(analized) > 0:
            sendEmail.SendMessage(service,'me',email)
            print(finalMessage)
            for email in emails: # it marked READ just removing the UNREAD label
                markRead(service, email['id'])

    except Exception as e:
        print('an error has ocurred while do something: '+str(e), e.with_traceback())
        print('returning UNREAD label to '+str(len(emails))+' emails')
        for email in emails:
            markUnread(service, email['id'])


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    readEmails(service)


if __name__ == '__main__':
    main()


#done by Me(Roberto Morales) at 2016 to simplify my work
