import pytest
import click
from unittest.mock import MagicMock, patch
# from click import Context
from click.testing import CliRunner
from config.stp import (
    get_intf_list_in_vlan_member_table,
    is_valid_root_guard_timeout,
    is_valid_forward_delay,
    # check_if_stp_enabled_for_interface,
    # check_if_interface_is_valid,
    # stp_global_hello_interval,
    # stp_interface_link_type_point_to_point,
    # dot spanning_tree_enable,
    stp_global_max_age,
    stp_global_max_hops,
    stp_mst_region_name,
    stp_global_revision,
    # stp_global_root_guard_timeout,
    is_valid_hello_interval,
    stp_disable,
    # is_valid_max_age,
    # is_valid_bridge_priority,
    enable_mst_instance0,
    # dot stp_global_forward_delay,
    MST_AUTO_LINK_TYPE,
    MST_DEFAULT_PORT_PATH_COST,
    MST_DEFAULT_PORT_PRIORITY,
    MST_DEFAULT_BRIDGE_PRIORITY,
    # MST_MAX_REVISION,
    # MST_MIN_REVISION,
    # validate_params,
    is_valid_stp_vlan_parameters,
    is_valid_stp_global_parameters,
    # update_stp_vlan_parameter,
    # check_if_vlan_exist_in_db,
    enable_stp_for_vlans,
    # get_stp_enabled_vlan_count,
    # vlan_enable_stp,
    # interface_enable_stp,
    # is_vlan_configured_interface,
    # is_interface_vlan_member,
    get_vlan_list_for_interface,
    # get_pc_member_port_list,
    # get_vlan_list_from_stp_vlan_intf_table,
    # get_intf_list_from_stp_vlan_intf_table,
    # is_portchannel_member_port,
    # enable_stp_for_interfaces,
    is_global_stp_enabled,
    check_if_global_stp_enabled,
    get_global_stp_mode,
    get_global_stp_forward_delay,
    get_global_stp_hello_time,
    get_global_stp_max_age,
    get_global_stp_priority,
    get_bridge_mac_address,
    # do_vlan_to_instance0,
    enable_mst_for_interfaces,
    disable_global_pvst,
    disable_global_mst
)


@pytest.fixture
def mock_db():
    # Create the mock database
    mock_db = MagicMock()

    # Mock cfgdb as itself to mimic behavior
    mock_db.cfgdb = mock_db

    # Mock for get_entry with a default side_effect
    def get_entry_side_effect(table, entry):
        # Define common mock responses based on table and entry
        if table == 'STP' and entry == 'GLOBAL':
            return {'mode': 'mst'}  # Default mode (adjust as necessary)
        if table == 'STP_MST' and entry == 'GLOBAL':
            return {'name': 'TestRegion'}  # Mock response for MST region name
        return {}

    # Set the side effect for get_entry
    mock_db.cfgdb.get_entry.side_effect = get_entry_side_effect

    # Mock mod_entry method (commonly used for modifications)
    mock_db.cfgdb.mod_entry = MagicMock()

    return mock_db


def test_get_intf_list_in_vlan_member_table():
    mock_db = MagicMock()
    mock_db.get_table.return_value = {
        ('Vlan10', 'Ethernet0'): {},
        ('Vlan20', 'Ethernet1'): {}
    }

    expected_interfaces = ['Ethernet0', 'Ethernet1']
    result = get_intf_list_in_vlan_member_table(mock_db)

    assert result == expected_interfaces
    mock_db.get_table.assert_called_once_with('VLAN_MEMBER')


@pytest.fixture
def patch_functions():
    # Patch external function calls inside the function
    with patch('config.stp.check_if_global_stp_enabled', return_value=True), \
         patch('config.stp.get_global_stp_mode', return_value='mst'):
        yield


def test_stp_mst_region_name_invalid(mock_db, patch_functions):
    # Create the runner for the CLI
    runner = CliRunner()

    region_name = "A" * 33  # Example invalid region name (more than 32 characters)

    # Invoke the CLI command with an invalid region name
    result = runner.invoke(stp_mst_region_name, [region_name], obj=mock_db)

    # Assert the exit code is non-zero, indicating failure
    assert result.exit_code != 0
    assert "Region name must be less than 32 characters" in result.output


def test_stp_mst_region_name_pvst(mock_db, patch_functions):
    # Patch the get_global_stp_mode function to return 'pvst'
    with patch('config.stp.get_global_stp_mode', return_value='pvst'):
        # Create the runner for the CLI
        runner = CliRunner()

        region_name = "TestRegion"  # Example region name

        # Invoke the CLI command with region name
        result = runner.invoke(stp_mst_region_name, [region_name], obj=mock_db)

        # Assert the exit code is non-zero, indicating failure for PVST mode
        assert result.exit_code != 0
        assert "Configuration not supported for PVST" in result.output


def test_stp_disable_correct_mode():
    with patch('config.stp.get_global_stp_mode', return_value="pvst"), \
         patch('config.stp.disable_global_pvst') as mock_pvst:

        # Simulate invoking the command with "pvst" mode
        ctx = click.testing.CliRunner().invoke(stp_disable, ['pvst'])

        # Assert that the function ran successfully (exit code 0)
        assert ctx.exit_code == 0

        # Ensure that disable_global_pvst was called
        mock_pvst.assert_called_once()


@patch('config.stp.check_if_global_stp_enabled')  # Mock the imported function
@patch('config.stp.get_global_stp_mode')          # Mock the imported function
@patch('config.stp.clicommon.pass_db')  # Mock the decorator
def test_stp_global_revision_mst(mock_pass_db, mock_get_global_stp_mode, mock_check_if_global_stp_enabled):
    runner = CliRunner()
    db = MagicMock()
    mock_pass_db.return_value = db

    # Simulate MST mode
    mock_get_global_stp_mode.return_value = 'mst'

    # Test with valid revision
    result = runner.invoke(stp_global_revision, ['5000'])
    assert result.exit_code == 0, f"Failed: {result.output}"

    # Test with invalid revision (below range)
    result = runner.invoke(stp_global_revision, ['--', '-1'])
    assert result.exit_code != 0
    assert "STP revision number must be in range 0-65535" in result.output

    # Test with invalid revision (above range)
    result = runner.invoke(stp_global_revision, ['--', '65536'])
    assert result.exit_code != 0
    assert "STP revision number must be in range 0-65535" in result.output


@patch('config.stp.check_if_global_stp_enabled')
@patch('config.stp.get_global_stp_mode')
@patch('config.stp.clicommon.pass_db')
def test_stp_global_revision_pvst(mock_pass_db, mock_get_global_stp_mode, mock_check_if_global_stp_enabled):
    runner = CliRunner()
    db = MagicMock()
    mock_pass_db.return_value = db

    # Simulate PVST mode
    mock_get_global_stp_mode.return_value = 'pvst'

    result = runner.invoke(stp_global_revision, ['5000'])
    assert result.exit_code != 0
    assert "Configuration not supported for PVST" in result.output


def test_is_valid_root_guard_timeout():
    mock_ctx = MagicMock()

    # Valid case
    try:
        is_valid_root_guard_timeout(mock_ctx, 30)
    except SystemExit:
        pytest.fail("Unexpected failure on valid root guard timeout")

    # Invalid case
    mock_ctx.fail = MagicMock()  # Mocking the fail method to prevent actual exit
    is_valid_root_guard_timeout(mock_ctx, 700)
    mock_ctx.fail.assert_called_once_with("STP root guard timeout must be in range 5-600")


def test_is_valid_forward_delay():
    mock_ctx = MagicMock()

    # Valid case
    try:
        is_valid_forward_delay(mock_ctx, 15)
    except SystemExit:
        pytest.fail("Unexpected failure on valid forward delay")

    # Invalid case
    mock_ctx.fail = MagicMock()  # Mocking the fail method to prevent actual exit
    is_valid_forward_delay(mock_ctx, 31)
    mock_ctx.fail.assert_called_once_with("STP forward delay value must be in range 4-30")


def test_is_valid_stp_vlan_parameters():
    mock_ctx = MagicMock()
    mock_db = MagicMock()
    mock_db.get_entry.return_value = {
        "forward_delay": 15,
        "max_age": 20,
        "hello_time": 2
    }

    # Valid case
    try:
        is_valid_stp_vlan_parameters(mock_ctx, mock_db, "Vlan10", "max_age", 20)
    except SystemExit:
        pytest.fail("Unexpected failure on valid STP VLAN parameters")

    # Invalid case
    mock_ctx.fail = MagicMock()  # Mocking the fail method to prevent actual exit
    is_valid_stp_vlan_parameters(mock_ctx, mock_db, "Vlan10", "max_age", 50)
    mock_ctx.fail.assert_called_once_with(
        "2*(forward_delay-1) >= max_age >= 2*(hello_time +1 ) not met for VLAN"
    )


def test_enable_stp_for_vlans():
    mock_db = MagicMock()
    mock_db.get_table.return_value = ["Vlan10", "Vlan20"]

    enable_stp_for_vlans(mock_db)

    mock_db.set_entry.assert_any_call('STP_VLAN', 'Vlan10', {
        'enabled': 'true',
        'forward_delay': mock_db.get_entry.return_value.get('forward_delay'),
        'hello_time': mock_db.get_entry.return_value.get('hello_time'),
        'max_age': mock_db.get_entry.return_value.get('max_age'),
        'priority': mock_db.get_entry.return_value.get('priority')
    })


def test_is_global_stp_enabled():
    mock_db = MagicMock()

    # Enabled case
    mock_db.get_entry.return_value = {"mode": "pvst"}
    assert is_global_stp_enabled(mock_db) is True

    # Disabled case
    mock_db.get_entry.return_value = {"mode": "none"}
    assert is_global_stp_enabled(mock_db) is False


def test_disable_global_pvst():
    mock_db = MagicMock()

    disable_global_pvst(mock_db)

    mock_db.set_entry.assert_called_once_with('STP', "GLOBAL", None)
    mock_db.delete_table.assert_any_call('STP_VLAN')
    mock_db.delete_table.assert_any_call('STP_PORT')
    mock_db.delete_table.assert_any_call('STP_VLAN_PORT')


# Define constants
STP_MIN_FORWARD_DELAY = 4
STP_MAX_FORWARD_DELAY = 30
STP_DEFAULT_FORWARD_DELAY = 15


def test_disable_global_mst():
    mock_db = MagicMock()

    disable_global_mst(mock_db)

    mock_db.set_entry.assert_called_once_with('STP', "GLOBAL", None)
    mock_db.delete_table.assert_any_call('STP_MST')
    mock_db.delete_table.assert_any_call('STP_MST_INST')
    mock_db.delete_table.assert_any_call('STP_MST_PORT')
    mock_db.delete_table.assert_any_call('STP_PORT')


def test_get_bridge_mac_address():
    mock_db = MagicMock()
    mock_db.get_entry.return_value = {"mac": "00:11:22:33:44:55"}  # Updated key

    result = get_bridge_mac_address(mock_db)

    assert result == "00:11:22:33:44:55"
    mock_db.get_entry.assert_called_once_with("DEVICE_METADATA", "localhost")


def test_get_global_stp_priority():
    mock_db = MagicMock()
    mock_db.get_entry.return_value = {"priority": "32768"}

    result = get_global_stp_priority(mock_db)

    # Compare the result as a string
    assert result == "32768"  # Updated to match the string type returned by the function

    mock_db.get_entry.assert_called_once_with("STP", "GLOBAL")


def test_get_vlan_list_for_interface():
    mock_db = MagicMock()
    mock_db.get_table.return_value = {
        ("Vlan10", "Ethernet0"): {},
        ("Vlan20", "Ethernet0"): {}
    }

    result = get_vlan_list_for_interface(mock_db, "Ethernet0")

    assert result == ["Vlan10", "Vlan20"]
    mock_db.get_table.assert_called_once_with("VLAN_MEMBER")


def test_enable_mst_for_interfaces():
    # Create a mock database
    mock_db = MagicMock()

    # Mock the return value of db.get_table for 'PORT' and 'PORTCHANNEL'
    mock_db.get_table.side_effect = lambda table: {
        'PORT': {'Ethernet0': {}, 'Ethernet1': {}},
        'PORTCHANNEL': {'PortChannel1': {}}
    }.get(table, {})

    # Mock the return value of get_intf_list_in_vlan_member_table
    with patch('config.stp.get_intf_list_in_vlan_member_table', return_value=['Ethernet0', 'PortChannel1']):
        enable_mst_for_interfaces(mock_db)

    expected_fvs_port = {
        'edge_port': 'false',
        'link_type': MST_AUTO_LINK_TYPE,
        'enabled': 'true',
        'bpdu_guard': 'false',
        'bpdu_guard_do': 'false',
        'root_guard': 'false',
        'path_cost': MST_DEFAULT_PORT_PATH_COST,
        'priority': MST_DEFAULT_PORT_PRIORITY
    }

    expected_fvs_mst_port = {
        'path_cost': MST_DEFAULT_PORT_PATH_COST,
        'priority': MST_DEFAULT_PORT_PRIORITY
    }

    # Assert that set_entry was called with the correct key names
    mock_db.set_entry.assert_any_call('STP_MST_PORT', 'MST_INSTANCE|0|Ethernet0', expected_fvs_mst_port)
    mock_db.set_entry.assert_any_call('STP_MST_PORT', 'MST_INSTANCE|0|PortChannel1', expected_fvs_mst_port)
    mock_db.set_entry.assert_any_call('STP_PORT', 'Ethernet0', expected_fvs_port)
    mock_db.set_entry.assert_any_call('STP_PORT', 'PortChannel1', expected_fvs_port)

    # Ensure the correct number of calls were made to set_entry
    assert mock_db.set_entry.call_count == 4


def test_check_if_global_stp_enabled():
    # Create mock objects for db and ctx
    mock_db = MagicMock()
    mock_ctx = MagicMock()

    # Case 1: Global STP is enabled
    with patch('config.stp.is_global_stp_enabled', return_value=True):
        check_if_global_stp_enabled(mock_db, mock_ctx)
        mock_ctx.fail.assert_not_called()  # Fail should not be called when STP is enabled

    # Case 2: Global STP is not enabled
    with patch('config.stp.is_global_stp_enabled', return_value=False):
        check_if_global_stp_enabled(mock_db, mock_ctx)
        mock_ctx.fail.assert_called_once_with("Global STP is not enabled - first configure STP mode")


def test_is_valid_stp_global_parameters():
    # Create mock objects for db and ctx
    mock_db = MagicMock()
    mock_ctx = MagicMock()

    # Mock STP global entry in db
    mock_db.get_entry.return_value = {
        "forward_delay": "15",
        "max_age": "20",
        "hello_time": "2",
    }

    # Patch validate_params to control its behavior
    with patch('config.stp.validate_params') as mock_validate_params:
        mock_validate_params.return_value = True  # Simulate valid parameters

        # Call the function with valid parameters
        is_valid_stp_global_parameters(mock_ctx, mock_db, "forward_delay", "15")
        mock_validate_params.assert_called_once_with("15", "20", "2")
        mock_ctx.fail.assert_not_called()  # fail should not be called for valid parameters

        # Simulate invalid parameters
        mock_validate_params.return_value = False

        # Call the function with invalid parameters
        is_valid_stp_global_parameters(mock_ctx, mock_db, "forward_delay", "15")
        mock_ctx.fail.assert_called_once_with("2*(forward_delay-1) >= max_age >= 2*(hello_time +1 ) not met")


def test_enable_mst_instance0():
    # Create a mock database
    mock_db = MagicMock()

    # Expected field-value set for MST instance 0
    expected_mst_inst_fvs = {
        'bridge_priority': MST_DEFAULT_BRIDGE_PRIORITY
    }

    # Call the function with the mock database
    enable_mst_instance0(mock_db)

    # Assert that set_entry was called with the correct arguments
    mock_db.set_entry.assert_called_once_with(
        'STP_MST_INST', 'MST_INSTANCE:INSTANCE0', expected_mst_inst_fvs
    )


def test_get_global_stp_mode():
    # Create a mock database
    mock_db = MagicMock()

    # Mock different scenarios for the STP global entry
    # Case 1: Mode is set to a valid value
    mock_db.get_entry.return_value = {"mode": "mst"}
    result = get_global_stp_mode(mock_db)
    assert result == "mst"
    mock_db.get_entry.assert_called_once_with("STP", "GLOBAL")

    # Reset mock_db
    mock_db.get_entry.reset_mock()

    # Case 2: Mode is set to "none"
    mock_db.get_entry.return_value = {"mode": "none"}
    result = get_global_stp_mode(mock_db)
    assert result == "none"
    mock_db.get_entry.assert_called_once_with("STP", "GLOBAL")

    # Reset mock_db
    mock_db.get_entry.reset_mock()

    # Case 3: Mode is missing
    mock_db.get_entry.return_value = {}
    result = get_global_stp_mode(mock_db)
    assert result is None
    mock_db.get_entry.assert_called_once_with("STP", "GLOBAL")


def test_get_global_stp_forward_delay():
    mock_db = MagicMock()
    mock_db.get_entry.return_value = {"forward_delay": 15}

    result = get_global_stp_forward_delay(mock_db)

    assert result == 15
    mock_db.get_entry.assert_called_once_with('STP', 'GLOBAL')


def test_get_global_stp_hello_time():
    mock_db = MagicMock()
    mock_db.get_entry.return_value = {"hello_time": 2}

    result = get_global_stp_hello_time(mock_db)

    assert result == 2
    mock_db.get_entry.assert_called_once_with('STP', 'GLOBAL')


def test_is_valid_hello_interval():
    # Mock the ctx object
    mock_ctx = MagicMock()

    # Test valid hello interval (in range)
    for valid_value in range(1, 11):  # Assuming 1-10 is the valid range
        mock_ctx.reset_mock()  # Reset the mock to clear previous calls
        is_valid_hello_interval(mock_ctx, valid_value)
        # Assert that ctx.fail is not called for valid values
        mock_ctx.fail.assert_not_called()

    # Test invalid hello interval (out of range)
    for invalid_value in [-1, 0, 11, 20]:  # Out-of-range values
        mock_ctx.reset_mock()
        is_valid_hello_interval(mock_ctx, invalid_value)
        # Assert that ctx.fail is called with the correct message
        mock_ctx.fail.assert_called_once_with("STP hello timer must be in range 1-10")


def test_get_global_stp_max_age():
    mock_db = MagicMock()
    mock_db.get_entry.return_value = {"max_age": 20}

    result = get_global_stp_max_age(mock_db)

    assert result == 20
    mock_db.get_entry.assert_called_once_with('STP', 'GLOBAL')


@pytest.fixture
def mock_ctx():
    mock_ctx = MagicMock()
    return mock_ctx


def test_stp_global_max_hops_invalid_mode(mock_db):
    """Test the scenario where the mode is PVST, and max_hops is not supported."""
    # Simulate PVST mode
    mock_db.cfgdb.get_entry.return_value = {"mode": "pvst"}

    runner = CliRunner()
    result = runner.invoke(stp_global_max_hops, ['20'], obj=mock_db)  # Test max_hops for PVST

    # Check if the function fails with the correct error message
    assert "Max hops not supported for PVST" in result.output
    assert result.exit_code != 0  # Error exit code


# # Test case for stp_interface_link_type_point_to_point function
# def test_stp_interface_link_type_point_to_point_success(
#     mock_db, mock_check_if_interface_is_valid, mock_check_if_stp_enabled_for_interface
# ):
#     # Set up the mock return values for the validation functions
#     mock_check_if_interface_is_valid.return_value = None
#     mock_check_if_stp_enabled_for_interface.return_value = None
#     mock_db.cfgdb.mod_entry.return_value = None  # Simulating that the modification was successful

#     # Call the function
#     interface_name = "Ethernet0"  # Example interface name
#     stp_interface_link_type_point_to_point(mock_db, interface_name)

#     # Assert that the correct database call was made
#     mock_db.cfgdb.mod_entry.assert_called_once_with(
#         'STP_PORT', interface_name, {'link_type': 'point-to-point'}
#     )

#     # Check that the validation functions were also called
#     mock_check_if_interface_is_valid.assert_called_once_with(mock_db, interface_name)
#     mock_check_if_stp_enabled_for_interface.assert_called_once_with(mock_db, interface_name)


def test_stp_global_max_age_mst_mode(mock_db, mock_ctx):
    """Test for the 'mst' mode scenario."""

    # Mocking the behavior of the database and context
    mock_ctx.fail = MagicMock()
    mock_db.cfgdb.get_global_stp_mode.return_value = "mst"  # Simulate MST mode

    # Mock the helper functions
    with patch('config.stp.check_if_global_stp_enabled') as check_if_global_stp_enabled, \
         patch('config.stp.is_valid_max_age') as is_valid_max_age:

        stp_global_max_age(mock_db, 25)  # Test with max_age = 25

        # Assert that the helper functions are called correctly
        check_if_global_stp_enabled.assert_called_once()
        is_valid_max_age.assert_called_once_with(mock_ctx, 25)
        mock_db.cfgdb.mod_entry.assert_called_once_with('STP_MST', "GLOBAL", {'max_age': 25})


def test_stp_global_max_age_invalid_mode(mock_db, mock_ctx):
    """Test for the case when no valid STP mode is enabled (invalid mode)."""

    # Mocking the behavior of the database and context
    mock_ctx.fail = MagicMock()
    mock_db.cfgdb.get_global_stp_mode.return_value = "invalid_mode"  # Simulate an invalid mode

    with pytest.raises(SystemExit):  # We expect a failure (SystemExit) due to invalid mode
        stp_global_max_age(mock_db, 30)  # Test with max_age = 30

    mock_ctx.fail.assert_called_once_with("Invalid STP mode configuration, no mode is enabled")
