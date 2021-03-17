import tpcc
import util

args = {
    'debug': False,
    'system': 'mysql',
    'ddl': '',
    'clients': 32,
    'warehouses': 10,
    'scalefactor': 10,
    'stop_on_error': False,
    'duration': 1
}

## Create a handle to the target client driver
driverClass = tpcc.createDriverClass(args['system'])
driver = driverClass(args['ddl'])
# add dbms configure
defaultConfig = driver.makeDefaultConfig()
config = dict(map(lambda x: (x, defaultConfig[x][1]), defaultConfig.keys()))
config['reset'] = False
config['load'] = False
config['execute'] = True
driver.loadConfig(config)

scaleParameters = util.scaleparameters.makeWithScaleFactor(args['warehouses'], args['scalefactor'])
proc_info = {"payment": 0, "delivery": 0,"new_order": 0}
scaleParameters.changeInvokeProcedure(proc_info)

tx_results = tpcc.startExecution(driverClass, scaleParameters, args, config)
print(tx_results)