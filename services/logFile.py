import logging
logging.basicConfig(level=logging.DEBUG, filename='logs/main.log', format='%(asctime)s, %(levelname)s: %(message)s')
formatter = logging.Formatter('%(asctime)s, %(levelname)s: %(message)s')

# Info file logger
info_log_var = logging.getLogger('info_logger')
info_log_var.propagate = False
info_hdlr = logging.FileHandler('logs/info.log')
info_hdlr.setFormatter(formatter)
info_log_var.addHandler(info_hdlr)

# Error file logger
error_log_var = logging.getLogger('error_logger')
error_log_var.propagate = False
error_hdlr = logging.FileHandler('logs/error.log')    
error_hdlr.setFormatter(formatter)
error_log_var.addHandler(error_hdlr)

# Critical file logger
critical_log_var = logging.getLogger('critical_logger')
critical_log_var.propagate = False
critical_hdlr = logging.FileHandler('logs/critical.log')    
critical_hdlr.setFormatter(formatter)
critical_log_var.addHandler(critical_hdlr)

def infoLog(msg):
	info_log_var.info(msg)

def errorLog(msg):
	error_log_var.error(msg)

def criticalLog(msg):
	critical_log_var.critical(msg)
