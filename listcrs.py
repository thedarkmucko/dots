import subprocess
import shlex
import re


def query_clusterware():
    """
    Return a list of cluster resources 
    """
    
    crsctl_query_runtime = 'crsctl status res -v -w "TYPE = ora.database.type" -attr DB_UNIQUE_NAME,DATABASE_TYPE,USR_ORA_INST_NAME,TARGET_SERVER,ROLE,USR_ORA_OPEN_MODE,STATE_DETAILS'
    grep = 'grep -v ^NAME'

    args = shlex.split(crsctl_query_runtime)
    args_2 = shlex.split(grep)
    
    crs = subprocess.Popen(args, stdout=subprocess.PIPE)
    out = subprocess.check_output(args_2,stdin=crs.stdout)
    crs.wait()
    
    out_data = list()
    for line in out.splitlines():
        if line:
            out_data.append(line)
    
    return out_data


def query_unique_names():
    srvctl = 'srvctl config database -verbose'
    args = shlex.split(srvctl)
    cmd = subprocess.Popen(args, stdout=subprocess.PIPE)    
    out = cmd.stdout.readlines()
    
    list_out = list()
    for line in out:
        tmp = line.split('\t')
        list_out.append((tmp[0], tmp[1]))
    
    return list_out


class CRSObject:
    _all_objects = list()

    def __init__(self, dbuniqname, id):
        if dbuniqname:
            self.db_unique_name = dbuniqname
        self.instances = list()
        self.type = ''
        self.mode = list()
        self.role = ''
        self.details = list()
        self.id = id
        self.target_server = list()
        CRSObject._all_objects.append(self)
    
    @classmethod
    def search(cls, item):
        for index, obj in enumerate(cls._all_objects):
            if obj.db_unique_name == item:
                return True
        return False
    
    def __getitem__(self, index):
        return self._all_objects[index]
        
    @property
    def db_unique_name(self):
        return self.db_unique_name
    
    def add_type(self, input):
        self.type = input
    
    def add_server(self, input):
        self.target_server.append(input)
    
    def add_instance(self, input):
        self.instances.append(input)
        
    def add_mode(self, input):
        self.mode.append(input)
    
    def add_role(self, input):
        self.role = input
        
    def add_details(self, input):
        self.details.append(input)
    
    def __str__(self):
        uniq = self.db_unique_name
        type = self.type 
        role = self.role
        details = self.details
        instances = self.instances
        server = self.target_server
        o_details_instances = list(zip(details, instances))
        
        if role == 'PRIMARY':
            role = 'PRIM'
        elif role == 'PHYSICAL_STANDBY':
            role = 'PS'
        elif role == 'SNAPSHOT_STANDBY':
            role = 'SS'
        else:
            role = 'LS'
                
        o_d_i = ''
        for no in range(0, len(o_details_instances)):
            state = o_details_instances[no][0]
            instance = o_details_instances[no][1]
            if no == (len(o_details_instances)-1): 
                o_d_i += instance + ' -> ' + state[0] 
            else:
                o_d_i += instance + ' -> ' + state[0] + ', '
            
        serv_out = ''
        for s in server:
            serv_out += s + ' '

        type_role = type + ' - ' + role

        return '{0: >15} -> {2:<15} STATE: {1: <70}'.format(uniq, o_d_i, type_role)


class CRSDatabase:
    def __init__(self):
        self.data = query_clusterware()
        self.config = query_unique_names()
    
    def generate(self): 
        list_of_CRSObj = list()
        
        if self.data.count == 0:
            return "No CRS Objects"
        
        obj_iter = -1
        for line in self.data:
            # DB_UNIQUE_NAME,DATABASE_TYPE,USR_ORA_INST_NAME,ROLE,USR_ORA_OPEN_MODE,STATE_DETAILS
            """
            Fill the objects with a db_unique_name
            """
            
            data = line.split('=')[1]
            
            if re.search('DB_UNIQUE_NAME=', line):
                if not CRSObject.search(data):
                    obj_iter += 1 
                    list_of_CRSObj.append(CRSObject(data, obj_iter))
            
            if re.search('DATABASE_TYPE=',line):
                list_of_CRSObj[obj_iter].add_type(data)
                    
            if re.search('USR_ORA_INST_NAME=',line):
                list_of_CRSObj[obj_iter].add_instance(data)
                    
            if re.search('ROLE=',line):
                list_of_CRSObj[obj_iter].add_role(data)
                    
            if re.search('USR_ORA_OPEN_MODE=',line):
                list_of_CRSObj[obj_iter].add_mode(data)
                    
            if re.search('STATE_DETAILS=',line):
                data = data.split(',')
                list_of_CRSObj[obj_iter].add_details(data)
                
            if re.search('TARGET_SERVER=',line):
                data = data.split(',')[0]
                list_of_CRSObj[obj_iter].add_server(data)
                
        return list_of_CRSObj
            
    
if __name__ == '__main__':
    crs = CRSDatabase()
    crs_obj = crs.generate()

    print('\n')
    for o in crs_obj:
        print(o)
    print('\n')
