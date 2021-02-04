from datetime import datetime


import constants

## ==============================================
## AbstractDriver
## ==============================================
class AbstractDriver(object):
    def __init__(self, name, ddl):
        self.name = name
        self.driver_name = "%sDriver" % self.name.title()
        self.ddl = ddl
        
    def __str__(self):
        return self.driver_name
    
    def makeDefaultConfig(self):
        """This function needs to be implemented by all sub-classes.
        It should return the items that need to be in your implementation's configuration file.
        Each item in the list is a triplet containing: ( <PARAMETER NAME>, <DESCRIPTION>, <DEFAULT VALUE> )
        """
        raise NotImplementedError("%s does not implement makeDefaultConfig" % (self.driver_name))
    
    def loadConfig(self, config):
        """Initialize the driver using the given configuration dict"""
        raise NotImplementedError("%s does not implement loadConfig" % (self.driver_name))
        
    def formatConfig(self, config):
        """Return a formatted version of the config dict that can be used with the --config command line argument"""
        ret =  "# %s Configuration File\n" % (self.driver_name)
        ret += "# Created %s\n" % (datetime.now())
        ret += "[%s]" % self.name
        
        for name in config.keys():
            desc, default = config[name]
            if default == None: default = ""
            ret += "\n\n# %s\n%-20s = %s" % (desc, name, default) 
        return (ret)
        
    def loadStart(self):
        """Optional callback to indicate to the driver that the data loading phase is about to begin."""
        return None
        
    def loadFinish(self):
        """Optional callback to indicate to the driver that the data loading phase is finished."""
        return None

    def loadFinishItem(self):
        """Optional callback to indicate to the driver that the ITEM data has been passed to the driver."""
        return None

    def loadFinishWarehouse(self, w_id):
        """Optional callback to indicate to the driver that the data for the given warehouse is finished."""
        return None
        
    def loadFinishDistrict(self, w_id, d_id):
        """Optional callback to indicate to the driver that the data for the given district is finished."""
        return None
        
    def loadTuples(self, tableName, tuples):
        """Load a list of tuples into the target table"""
        raise NotImplementedError("%s does not implement loadTuples" % (self.driver_name))
        
    def executeStart(self):
        """Optional callback before the execution phase starts"""
        return None
        
    def executeFinish(self):
        """Callback after the execution phase finishes"""
        return None

    ### to change api
    def buildIndex(self, index_creation_sql):
        """build index"""
        return None

    def dropIndex(self, index_drop_sql):
        """drop index"""
        return None

    def setSystemParameter(self, parameter_sql):
        """set system parameter"""
        return None

    def resetDatabase(self):
        """reload the database table from table copies"""
        return None

## CLASS