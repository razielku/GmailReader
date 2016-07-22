# GmailReader
This Phyton3 code, is used in a Gmail account to do what you want with it, (send mail, check the read ones, organize them, etc.) Just be creative.

This code is a mixture of my authorship with the reading of the [Gmail Api Docs for Python](https://developers.google.com/gmail/api/quickstart/python), so I do not feel entitled to ask you to give me credit, unless you want to  (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ ✧ﾟ･: *ヽ(◕ヮ◕ヽ)

The functional example is in the file [init.py](https://github.com/razielku/GmailReader/blob/master/init.py)
# More information
the links where I found the information that was useful to me.:
 - [Google APIs Client Library for Python Installation](https://developers.google.com/api-client-library/python/start/installation) (you need this)
 - [Oauth2 Protocol](https://developers.google.com/identity/protocols/OAuth2)
 - [Api Client Oauth Guide](https://developers.google.com/api-client-library/python/guide/aaa_oauth)
 - [Console Help for Credentials, access, security, and identity](https://support.google.com/cloud/answer/6158857?hl=en&ref_topic=6262490)
 - [Gmail Api Auth Scopes Info](https://developers.google.com/gmail/api/auth/scopes#gmail_scopes)
  
You will need to enter your [Google developer Console](https://console.developers.google.com) to enable [Gmail Api](https://console.developers.google.com/apis/api/gmail/overview) and generate a secret.json file in the [Google Developer Console Api Credentials List](https://console.developers.google.com/apis/credentials)

# Why I did this code?
I've made this code because I have a minor task of reviewing emails where failures were announced, a repetitive task that I wanted to automate,so I created this, at least it works for me.

# Why I don't use SMTP/POP3/IMAP or other Python/Gmail librarys?
Well, I've tried, but to make them work I needed to unable the extra security of Gmail and I felt it was not necessary, so I've looked for the official way of Google to do so, and found it.

![Razielku](https://avatars3.githubusercontent.com/u/16324160?v=3&s=96)
