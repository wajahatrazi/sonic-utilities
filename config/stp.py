import click
import utilities_common.cli as clicommon
from swsscommon.swsscommon import ConfigDBConnector
from .validated_config_db_connector import ValidatedConfigDBConnector
from natsort import natsorted

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

MST_MIN_PORT_PATH_COST = 20000000;
MST_MAX_PORT_PATH_COST = 20000000;
MST_DEFAULT_PORT_PATH_COST = 1;

MST_AUTO_LINK_TYPE = 'auto'
MST_P2P_LINK_TYPE = 'p2p'
MST_SHARED_LINK_TYPE = 'shared'


#=============================================
# Functions
#=============================================

# GETTING INTERFACES IN VLAN MEMBER TABLE
def get_intf_list_in_vlan_member_table(db):
    config_db = ValidatedConfigDBConnector(db.cfgdb)
    config_db.connect()

    get_intf_vlan_info_from_configdb = config_db.get_table('VLAN_MEMBER')

    intf_list = []
    for key in get_intf_vlan_info_from_configdb:
        interface = key[1]
        if interface not in intf_list:
            intf_list.append(interface)
    
    return intf_list


# GETTING GLOBAL STP MODE FROM THE STP GLOBAL TABLE
def get_global_stp_mode(ctx, db):
    config_db = ValidatedConfigDBConnector(db.cfgdb)
    config_db.connect()

    try:
        stp_entry = config_db.get_entry('STP', "GLOBAL")
    except ValueError as e:
        ctx.fail ("Could not get Mode value from STP Global. Error: {}".format(e))

    mode = stp_entry.get("mode")

    return mode


def enable_mst_for_ports(ctx, db):
    # Enabling MST for all ports and portchannels
    # Storing STP interface details in STP_PORT table

    config_db = ValidatedConfigDBConnector(db.cfgdb)
    config_db.connect()

    fvs_stp_port_table = {
        'enabled': 'true',
        'root_guard': 'false',
        'bpdu_guard': 'false',
        'bpdu_guard_do': 'false',
        'path_cost': MST_DEFAULT_PORT_PATH_COST,
        'priority': MST_DEFAULT_PORT_PRIORITY,
        'edge_port': 'false',
        'link_type': MST_AUTO_LINK_TYPE,
    }

    # GETTING PORT & PORTCHANNEL TABLES
    port_dict = natsorted(config_db.get_table('PORT'))
    po_ch_dict = natsorted(config_db.get_table('PORTCHANNEL'))

    # GETTING INTERFACES IN VLAN MEMBER TABLE
    intf_list_in_vlan_member_table = get_intf_list_in_vlan_member_table(config_db)

    for port_key in port_dict:
        if port_key in intf_list_in_vlan_member_table:
            try:
                config_db.set_entry('STP_PORT', port_key, fvs_stp_port_table)
            except ValueError as e:
                ctx.fail ("Setting port values for STP Port table failed. Error: {}".format(e))

    for po_ch_key in po_ch_dict:
        if po_ch_key in intf_list_in_vlan_member_table:
            try:
                config_db.set_entry('STP_PORT', po_ch_key, fvs_stp_port_table)
            except ValueError as e:
                ctx.fail ("Setting portchannel values for STP Port table failed. Error: {}".format(e))

def stp_global_table_update(ctx, db):
    config_db = ValidatedConfigDBConnector(db.cfgdb)
    config_db.connect()

    fvs_stp_global_table = {
            'mode': 'mst',
            'rootguard_timeout': MST_DEFAULT_ROOT_GUARD_TIMEOUT,
            'forward_delay': MST_DEFAULT_FORWARD_DELAY, 
            'hello_time': MST_DEFAULT_HELLO_INTERVAL,
            'max_age': MST_DEFAULT_MAX_AGE,
            'priority': MST_DEFAULT_BRIDGE_PRIORITY
        }
    try:
        config_db.set_entry('STP', "GLOBAL", fvs_stp_global_table)
    except ValueError as e:
        ctx.fail ("STP global table configuration failed with error. Error: {}".format(e))

def set_default_mst_values(ctx, db):
    config_db = ValidatedConfigDBConnector(db.cfgdb)
    config_db.connect()

    pass

def enable_mst_for_vlans(ctx, db):
    # STP configuration values for each vlan
    pass








#=============================================
# MST Main Declaration
#=============================================


@click.group(cls=clicommon.AbbreviationGroup)
def spanning_tree():
    pass


@spanning_tree.group()
def mst():
    pass

# CONFIG SPANNING_TREE MST ENABLE
@mst.command('enable')
@click.pass_context
def enable(ctx):
    config_db = ValidatedConfigDBConnector(ConfigDBConnector)
    config_db.connect()
    ctx.obj = {'db': config_db}

    mode = get_global_stp_mode(ctx, config_db)

    if mode == "mst":
        ctx.fail("MST is already configured")
    elif mode == "pvst":
        # What should It do if PVST is already configured?
        ctx.fail("PVST is already configured")
    else:
        # SETTING GLOBAL STP MODE TO MST
        stp_global_table_update(ctx, config_db)
        
        # ENABLing MST FOR PORTS IN STP_PORT TABLE
        enable_mst_for_ports(ctx, config_db)

        # SETTING DEFAULT MST VALUES IN STP_MST TABLE
        set_default_mst_values(ctx, config_db)

        #enable_mst_for_vlans(ctx, config_db)

        


# CONFIG SPANNING_TREE MST DISABLE
@mst.command('disable')
@click.pass_context
def disable(ctx):
    click.echo("MST Disabled")


# CONFIG SPANNING_TREE MST MAX-HOPS <VALUE>
@mst.command('max-hops')
@click.pass_context
@click.argument('max_hops_value', type = int)
def max_hops(ctx, max_hops_value):
    """Set maximum hops for MST"""
    click.echo(f"MST max hops set to {max_hops_value}")


# CONFIG SPANNING_TREE MST HELLO-TIME <VALUE>
@mst.command('hello-time')
@click.pass_context
@click.argument('hello_value', type=int)
def hello(ctx, hello_value):
    """Set hello time for MST"""
    click.echo(f"MST hello time set to {hello_value}")


# CONFIG SPANNING_TREE MST MAX-AGE <VALUE>
@mst.command('max-age')
@click.pass_context
@click.argument('max_age_value', type=int)
def max_age(ctx, max_age_value):
    """Set max age for MST"""
    click.echo(f"MST max age set to {max_age_value}")








"""

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
    #Enable console switch
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


    # Add entries to the STP_MST table with default values
    stp_mst_fvs = {
        'name': 'default_region',
        'revision': MST_DEFAULT_REVISION,
        'max_hop': MST_DEFAULT_HOPS,
        'max_age': MST_DEFAULT_MAX_AGE,
        'hello_time': MST_DEFAULT_HELLO_INTERVAL,
        'forward_delay': MST_DEFAULT_FORWARD_DELAY
    }
    db.set_entry('STP_MST', 'GLOBAL', stp_mst_fvs)

    # Add entries to the STP_MST_INST table with default values
    stp_mst_inst_fvs = {
        'bridge_priority': '32768',
        'vlan_list': '1-4094'
    }
    db.set_entry('STP_MST_INST', 'MST_INSTANCE:1', stp_mst_inst_fvs)

    # Add entries to the STP_MST_PORT table with default values
    stp_mst_port_fvs = {
        'path_cost': '20000000',
        'priority': '128'
    }
    for port_key in port_dict:
        if port_key in intf_list_in_vlan_member_table:
            db.set_entry('STP_MST_PORT', f'MST_INSTANCE:1|{port_key}', stp_mst_port_fvs)
    for po_ch_key in po_ch_dict:
        if po_ch_key in intf_list_in_vlan_member_table:
            db.set_entry('STP_MST_PORT', f'MST_INSTANCE:1|{po_ch_key}', stp_mst_port_fvs)
"""