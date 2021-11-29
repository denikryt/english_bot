try:    
    raise Exception
except Exception as e:
    print("Error {0}".format(str(e.args[0])).encode("utf-8"))