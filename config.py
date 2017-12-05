# -*- coding: utf-8 -*-

import os

basedir = os.path.abspath(os.path.dirname(__file__))

#mssqlconn = 'DRIVER={SQL Server};SERVER=footballnstance.cm9y2qwmtapu.us-east-1.rds.amazonaws.com;PORT=1433;Database=football;UID=root;PWD=password123'
#mssqlconn = urllib.parse.quote_plus(mssqlconn)
#mssqlconn = 'mssql+pyodbc:///?odbc_connect=%s' % mssqlconn

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app/database/database.sqlite')

#SQLALCHEMY_DATABASE_URI = mssqlconn

WTF_CSRF_ENABLED = True
SECRET_KEY = 'it-is-easy-guess-try~again!'

