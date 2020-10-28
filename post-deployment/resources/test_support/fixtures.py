# third party dependencies
import logging
import functools
import os
from sys import exec_prefix
from kubernetes.stream import stream
from contextlib import contextmanager
from kubernetes import config, client 
from collections import namedtuple
import pytest
from tango import DeviceProxy
# direct dependencies
from resources.test_support.helpers import resource
from resources.test_support.event_waiting import sync_telescope_shutting_down,watchSpec,sync_telescope_starting_up,\
sync_subarray_assigning,sync_subarray_releasing,sync_subarray_configuring,sync_release_configuration
from resources.test_support.persistance_helping import update_resource_config_file,load_config_from_file,update_scan_config_file

LOGGER = logging.getLogger(__name__)

# state asserting
def assert_telescope_is_standby():
    resource('ska_mid/tm_subarray_node/1').assert_attribute('State').equals('OFF')
    #TODO ignoring csp master as the events and get of attributes are out of sync
    #resource('mid_csp/elt/master').assert_attribute('State').equals('ON')
    #resource('mid_csp/elt/master').assert_attribute('State').equals('STANDBY')
    resource('ska_mid/tm_central/central_node').assert_attribute('State').equals('OFF')

def assert_telescope_is_running():
    resource('ska_mid/tm_subarray_node/1').assert_attribute('State').equals('ON')
    #TODO ignoring csp master as the events and get of attributes are out of sync
    #resource('mid_csp/elt/master').assert_attribute('State').equals('ON')
    resource('ska_mid/tm_central/central_node').assert_attribute('State').equals('ON')

def assert_subarray_is_idle(id):
    resource(f'ska_mid/tm_subarray_node/{id}').assert_attribute('obsState').equals('IDLE')

def assert_subarray_is_empty(id):
    resource(f'ska_mid/tm_subarray_node/{id}').assert_attribute('obsState').equals('EMPTY')

def assert_subarray_configured(id: int):
    resource(f'ska_mid/tm_subarray_node/{id}').assert_attribute('obsState').equals('READY')

@contextmanager
def wrap_assertion_as_predicate(predicate: bool):
    try:
        yield
    except:
        predicate = False

# state checkinhg
def is_telescope_standby() -> bool:
    predicate =  True
    with wrap_assertion_as_predicate(predicate):
        assert_telescope_is_standby()
    return predicate

def is_telescope_running() -> bool:
    predicate =  True
    with wrap_assertion_as_predicate(predicate):
        assert_telescope_is_running()
    return predicate

def is_subarray_idle(id) -> bool:
    predicate =  True
    with wrap_assertion_as_predicate(predicate):
        assert_subarray_is_idle(id)
    return predicate

def is_subarray_configured(id) -> bool:
    predicate =  True
    with wrap_assertion_as_predicate(predicate):
        assert_subarray_configured(id)
    return predicate

## pytest fixtures
ENV_VARS = [
    'HELM_RELEASE',
    'KUBE_NAMESPACE',
    'TANGO_HOST',
    'MARK']
RunContext = namedtuple('RunContext', ENV_VARS)

@pytest.fixture(scope="session")
def run_context():
     # list of required environment vars
    values = list()
    
    for var in ENV_VARS:
        assert os.environ.get(var) # all ENV_VARS must have values set
        values.append(os.environ.get(var))

    return RunContext(*values)

class K8_env():
    '''
    An object to help with managing the k8 context in order to 
    ensure tests are not effected by dirty environments
    '''
    def __init__(self, run_context:RunContext ) -> None:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            # if Config exception try loading it from config file
            # assumes this is therefore run from a bash shell with different user than root
            _, active_context = config.list_kube_config_contexts()
            config.load_kube_config(context=active_context['name'])
        self.v1 = client.CoreV1Api()
        self.extensions_v1_beta1 = client.ExtensionsV1beta1Api()
        self.env = run_context
        # TODO: Only run this block of code in case of TMC mid deployment
        #if 'mid' in self.env.MARK:
        self.clean_config_etcd()

    def _lookup_by(self,item,key: str,value: str) -> bool:
        if item.metadata.labels is not None:
           return item.metadata.labels.get(key) == value
        else:
            return False

    def clean_config_etcd(self) -> None:
        exec_command = [ 'sh', '-c', 'ETCDCTL_API=3 etcdctl del --prefix ""'] 
        app_name = 'etcd'
        namespace = self.env.KUBE_NAMESPACE
        logging.debug(f'lookging for sdp in namespace:{namespace}')
        try:
            pods = self.v1.list_namespaced_pod(namespace).items
        except Exception as e:
            logging.warning(e)
            raise e
        assert pods is not None, f'error in cleaning config db: no pods installed in namespace {namespace} not found'
        pod = [p.metadata.name for p in pods if self._lookup_by(p,'app',app_name)]   
        assert len(pod) > 0, f'error in cleaning config db: pod labeled as {app_name} not found'
        assert len(pod) < 2, f'error in cleaning config db: duplicate pods labeled as {app_name} found'
        pod = pod[0]
        resp = stream(self.v1.connect_get_namespaced_pod_exec, 
                pod, 
                namespace, 
                command=exec_command, 
                stderr=True, stdin=False, 
                stdout=True, tty=False)  
        logging.info(f'cleaning configdb:{resp}')


@pytest.fixture(scope='session',autouse=True)
def k8(run_context) -> None:
    '''
    An fixture to help with managing the k8 context in order to 
    ensure tests are not effected by dirty environments
    '''
    yield  K8_env(run_context)

@pytest.fixture
def running_telescope() -> None:
    set_telescope_to_running()
    try:
        yield
    except RecoverableException as e:
        # only set telescope to standby if an recoverable exception was raised
        set_telescope_to_standby()
        raise e
    # at the moment only set to telescope if no exceptions was raised or Recoverable Exception
    # in order to investigate the cause of failure
    set_telescope_to_standby()

@pytest.fixture
def idle_subarray(request,running_telescope) -> None:
    id = getattr(request.module, "subbarray_id",1)
    resource_config_file = getattr(request.module, "config_file", 'resources/test_data/TMC_integration/assign_resources1.json')
    sdp_block = update_resource_config_file(resource_config_file,disable_logging=True)
    subArray = SubArray(id)
    assign_subarray(subArray,resource_config_file)
    try:
        yield subArray,sdp_block
    except RecoverableException as e: 
        release_subarray(subArray)
        raise e
    release_subarray(subArray)


@pytest.fixture
def configured_subarray(request,idle_subarray) -> None:
    scan_config_file = getattr(request.module, "config_file", 'resources/test_data/OET_integration/configure1.json')
    subArray,sdp_block = idle_subarray
    update_scan_config_file(scan_config_file, sdp_block,disable_logging=True)
    configure_subarray(subArray,scan_config_file)
    try:
        yield subArray
    except RecoverableException as e:
        release_configuration(subArray)
        raise e
    release_configuration(subArray)



@pytest.fixture
def resource_config() -> str:
    assign_resources_file = 'resources/test_data/TMC_integration/assign_resources1.json'
    update_resource_config_file(assign_resources_file,disable_logging=True)
    config = load_config_from_file(assign_resources_file)
    yield config

@pytest.fixture
def resource_config_file() -> str:
    assign_resources_file = 'resources/test_data/TMC_integration/assign_resources1.json'
    update_resource_config_file(assign_resources_file,disable_logging=True)
    yield 'resources/test_data/TMC_integration/assign_resources1.json'




