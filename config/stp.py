import click
import utilities_common.cli as clicommon
from swsscommon.swsscommon import ConfigDBConnector
from swsscommon.swsscommon import SonicV2Connector
from .validated_config_db_connector import ValidatedConfigDBConnector


###############################################
# MST Global Values
###############################################

MST_MIN_HOPS = 1
MST_MAX_HOPS = 40
MST_DEFAULT_HOPS = 20

MST_MIN_HELLO_INTERVAL = 1
MST_MAX_HELLO_INTERVAL = 10
MST_DEFAULT_HELLO_INTERVAL = 2

MST_MIN_MAX_AGE = 6
MST_MAX_MAX_AGE = 40
MST_DEFAULT_MAX_AGE = 20

MST_MIN_REVISION = 0
MST_MAX_REVISION = 65535
MST_DEFAULT_REVISION = 0

MST_MIN_BRIDGE_PRIORITY = 0
MST_MAX_BRIDGE_PRIORITY = 61440
MST_DEFAULT_BRIDGE_PRIORITY = 32768

MST_MIN_PORT_PRIORITY = 0
MST_MAX_PORT_PRIORITY = 240
MST_DEFAULT_PORT_PRIORITY = 128

MST_MIN_FORWARD_DELAY = 4
MST_MAX_FORWARD_DELAY = 30
MST_DEFAULT_FORWARD_DELAY = 15

MST_MIN_ROOT_GUARD_TIMEOUT = 5
MST_MAX_ROOT_GUARD_TIMEOUT = 600
MST_DEFAULT_ROOT_GUARD_TIMEOUT = 30

MST_MIN_INSTANCES = 0
MST_MAX_INSTANCES = 63
MST_DEFAULT_INSTANCE = 0



###############################################
# Functions
###############################################

def get_global_stp_mode(db):
    config_db = ValidatedConfigDBConnector(db.cfgdb)
    config_db.connect()

    stp_entry = config_db.get_entry('STP', "GLOBAL")
    mode = stp_entry.get("mode")

    return mode


def enable_mst_for_interfaces(db):
    print ("Setting mode for all the interfaces")

def enable_mst_for_vlans(db):
    print ("...")

    set_vlan_to_instance(db, 0)

def set_vlan_to_instance(db, default_instance):
    print ("...")


###############################################
# MST Main Declaration
###############################################


@click.group(cls=clicommon.AbbreviationGroup)
def spanning_tree():
    """Multiple spanning tree related configurations"""
    pass


@spanning_tree.group()
def mst():
    pass

###############################################
# MST Global commands implementation
###############################################

@mst.command('enable')
@click.pass_context
def enable(ctx):
    """Enabling MST Globally"""

    config_db = ValidatedConfigDBConnector(ConfigDBConnector)
    config_db.connect()
    ctx.obj = {'db': config_db}

    mode = get_global_stp_mode(config_db)

    if mode == "mst":
        ctx.fail("MST is already configured")
    elif mode == "pvst":
        ctx.fail("PVST mode is enabled. Disable it to enable MST")

    fvs = {
        'mode': 'mst',
        'forward_delay': MST_DEFAULT_FORWARD_DELAY, 
        'hello_time': MST_DEFAULT_HELLO_INTERVAL,
        'max_age': MST_DEFAULT_MAX_AGE,
        'priority': MST_DEFAULT_BRIDGE_PRIORITY
    }

    try:
        config_db.set_entry('STP', "GLOBAL", fvs)
    except ValueError as e:
        ctx.fail ("MST Configuration Failed. Error: {}.format(e)")

    enable_mst_for_interfaces(config_db)
    enable_mst_for_vlans(config_db)


    
    #set_vlan_to_instance(config_db, 0)


    #LOGIC
        #Check if mst is already there in the config db gloabl table 
        #if there, fail ctx, and if not, set the mode
        #Only one mode should be enabled at a time, either mst or pvst
        #along with setting mode, it needs to set up default forward delay, default hello interval, default max age, default bridge priority.
        #after this checks vlans, and maps vlans to default instance 0
        #this default instance 0 is created by default 





    click.echo("MST Enabled")



@mst.command()
@click.pass_context
def disable(ctx):
    click.echo("MST Disabled")



@mst.command()
@click.pass_context
@click.argument('max_hops_value', type = int)
def max_hops(ctx, max_hops_value):
    """Set maximum hops for MST"""
    click.echo(f"MST max hops set to {max_hops_value}")



@mst.command()
@click.pass_context
@click.argument('hello_value', type=int)
def hello(ctx, hello_value):
    """Set hello time for MST"""
    click.echo(f"MST hello time set to {hello_value}")



@mst.command()
@click.pass_context
@click.argument('max_age_value', type=int)
def max_age(ctx, max_age_value):
    """Set max age for MST"""
    click.echo(f"MST max age set to {max_age_value}")













# --------------

def add_table_kv(table, entry, key, val):
    config_db = ValidatedConfigDBConnector(ConfigDBConnector())
    config_db.connect()
    try:
        config_db.mod_entry(table, entry, {key:val})
    except ValueError as e:
        ctx = click.get_current_context()
        ctx.fail("Invalid ConfigDB. Error: {}".format(e))



def del_table_key(table, entry, key):
    config_db = ValidatedConfigDBConnector(ConfigDBConnector())
    config_db.connect()
    data = config_db.get_entry(table, entry)
    if data:
        if key in data:
            del data[key]
        try:
            config_db.set_entry(table, entry, data)
        except (ValueError, JsonPatchConflict) as e:
            ctx = click.get_current_context()
            ctx.fail("Invalid ConfigDB. Error: {}".format(e))



@console.command('enable')
@clicommon.pass_db
def enable_console_switch(db):
    """Enable console switch"""
    config_db = ValidatedConfigDBConnector(db.cfgdb)

    table = "CONSOLE_SWITCH"
    dataKey1 = 'console_mgmt'
    dataKey2 = 'enabled'

    data = { dataKey2 : "yes" }
    try:
        config_db.mod_entry(table, dataKey1, data)
    except ValueError as e:
        ctx = click.get_current_context()
        ctx.fail("Invalid ConfigDB. Error: {}".format(e))