import pytest
from unittest.mock import MagicMock, patch
# from click import Context
from config.stp import (
    get_intf_list_in_vlan_member_table,
    is_valid_root_guard_timeout,
    is_valid_forward_delay,
    # is_valid_hello_interval,
    # is_valid_max_age,
    # is_valid_bridge_priority,
    MST_AUTO_LINK_TYPE,
    MST_DEFAULT_PORT_PATH_COST,
    MST_DEFAULT_PORT_PRIORITY,
    validate_params,
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


def test_disable_global_mst():
    mock_db = MagicMock()

    disable_global_mst(mock_db)

    mock_db.set_entry.assert_called_once_with('STP', "GLOBAL", None)
    mock_db.delete_table.assert_any_call('STP_MST')
    mock_db.delete_table.assert_any_call('STP_MST_INST')
    mock_db.delete_table.assert_any_call('STP_MST_PORT')
    mock_db.delete_table.assert_any_call('STP_PORT')


def test_validate_params():
    # Valid parameter
    assert validate_params(15, 20, 5) is True  # This should pass as the values meet the condition

    # Invalid parameter
    assert validate_params(15, 50, 5) is False  # This should fail as the condition is not met


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

    expected_fvs = {
        'enabled': 'true',
        'root_guard': 'false',
        'bpdu_guard': 'false',
        'bpdu_guard_do_disable': 'false',
        'portfast': 'false',
        'uplink_fast': 'false',
        'edge_port': 'false',
        'link_type': MST_AUTO_LINK_TYPE,
        'path_cost': MST_DEFAULT_PORT_PATH_COST,
        'priority': MST_DEFAULT_PORT_PRIORITY,
    }

    mock_db.set_entry.assert_any_call('STP_MST_PORT', 'MST_INSTANCE|0|Ethernet0', expected_fvs)
    mock_db.set_entry.assert_any_call('STP_MST_PORT', 'MST_INSTANCE|0|PortChannel1', expected_fvs)
    assert mock_db.set_entry.call_count == 2


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


def test_get_global_stp_max_age():
    mock_db = MagicMock()
    mock_db.get_entry.return_value = {"max_age": 20}

    result = get_global_stp_max_age(mock_db)

    assert result == 20
    mock_db.get_entry.assert_called_once_with('STP', 'GLOBAL')
