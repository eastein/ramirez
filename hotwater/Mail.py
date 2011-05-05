import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

class MailTransport:
    """ a mechanism which will accept an E-mail message and deliver it to an MTA """

    def __init__(self, mailHost, user, password):
        self.MTA = smtplib.SMTP(mailHost)
        self.MTA.set_debuglevel(0)
        self.MTA.login(user, password)

    def sendMessage(self, message):
        self.MTA.sendmail(message.fromAddress, message.toList,
                          message.wholeMessage.as_string())

    def done(self):
        self.MTA.quit()

class MailMessage:
    """ the details of an E-mail message for a single recipient """

    def __init__(self, txtBody, subject = 'No subject given', fromAddress = None, toList = None):

        self.fromAddress = fromAddress
        if self.fromAddress == None:
            self.fromAddress = 'FROMADDRESS'
    
        self.toList = toList
        if self.toList == None:
            self.toList = [ self.fromAddress ]

        self.wholeMessage = MIMEMultipart('alternative')
        self.wholeMessage.attach(MIMEText(txtBody))

        self.wholeMessage['Subject'] = self.wholeMessage.preamble = subject
        self.wholeMessage['From'] = 'Water Alerts <' + self.fromAddress + '>'

        destEmail = ''
        for email in toList:
            if destEmail != '':
                destEmail = destEmail + ','
            destEmail = destEmail + email
        self.wholeMessage['To'] = destEmail

    def done(self):
        return

