try:
	# Allow using PyMySQL as MySQLdb replacement when using MySQL on Windows
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	# If PyMySQL isn't installed or import fails, just continue. Settings will fall back to sqlite.
	pass
