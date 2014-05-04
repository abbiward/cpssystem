'''
A simple class for logging data for errors. 
This allows me to store data in an object and then choose to print it later on.
'''

class ErrorLog:
    
    def __init__(self):
        # self.info = {}
        self.info = []

    def reset(self):
        # self.info = {}
        self.info = []

    def record(self, name, value):
        # self.info[name] = value
        self.info.append((name,value))

    def __str__(self):
        output_str = "ERROR OBJECT\n"
        for item in self.info:
            output_str += str(item[0]) + ":" + str(item[1]) + "\n"
        # for key,value in self.info.iteritems():
        #     output_str += str(key) + ":" + str(value) + "\n"
        #     # print key, ":", value
        output_str += "------------END------------\n"
        return output_str