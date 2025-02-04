import os
import re
import pytest
from click.testing import CliRunner

import config.main as config
import show.main as show
from utilities_common.db import Db
from .mock_tables import dbconnector

EXPECTED_SHOW_SPANNING_TREE_OUTPUT = """\
Spanning-tree Mode: PVST

VLAN 500 - STP instance 0
--------------------------------------------------------------------
STP Bridge Parameters:
Bridge           Bridge Bridge Bridge Hold  LastTopology Topology
Identifier       MaxAge Hello  FwdDly Time  Change       Change
hex              sec    sec    sec    sec   sec          cnt
8064b86a97e24e9c 20     2      15     1     0            1

RootBridge       RootPath  DesignatedBridge  RootPort           Max Hel Fwd
Identifier       Cost      Identifier                           Age lo  Dly
hex                        hex                                  sec sec sec
0064b86a97e24e9c 600       806480a235f281ec  Root               20  2   15

STP Port Parameters:
Port             Prio Path      Port Uplink State         Designated  Designated       Designated
Name             rity Cost      Fast Fast                 Cost        Root             Bridge
Ethernet4        128  200       N    N      FORWARDING    400         0064b86a97e24e9c 806480a235f281ec
"""

EXPECTED_SHOW_SPANNING_TREE_VLAN_OUTPUT = """\

VLAN 500 - STP instance 0
--------------------------------------------------------------------
STP Bridge Parameters:
Bridge           Bridge Bridge Bridge Hold  LastTopology Topology
Identifier       MaxAge Hello  FwdDly Time  Change       Change
hex              sec    sec    sec    sec   sec          cnt
8064b86a97e24e9c 20     2      15     1     0            1

RootBridge       RootPath  DesignatedBridge  RootPort           Max Hel Fwd
Identifier       Cost      Identifier                           Age lo  Dly
hex                        hex                                  sec sec sec
0064b86a97e24e9c 600       806480a235f281ec  Root               20  2   15

STP Port Parameters:
Port             Prio Path      Port Uplink State         Designated  Designated       Designated
Name             rity Cost      Fast Fast                 Cost        Root             Bridge
Ethernet4        128  200       N    N      FORWARDING    400         0064b86a97e24e9c 806480a235f281ec
"""

EXPECTED_SHOW_SPANNING_TREE_STATISTICS_OUTPUT = """\
VLAN 500 - STP instance 0
--------------------------------------------------------------------
PortNum          BPDU Tx        BPDU Rx        TCN Tx         TCN Rx
Ethernet4        10             15             15             5
"""

EXPECTED_SHOW_SPANNING_TREE_BPDU_GUARD_OUTPUT = """\
PortNum          Shutdown     Port Shut
                 Configured   due to BPDU guard
-------------------------------------------
Ethernet4        No           NA
"""

EXPECTED_SHOW_SPANNING_TREE_ROOT_GUARD_OUTPUT = """\
Root guard timeout: 30 secs

Port             VLAN   Current State
-------------------------------------------
Ethernet4        500    Consistent state
"""

class TestStp(object):
    @classmethod
    def setup_class(cls):
        os.environ['UTILITIES_UNIT_TESTING'] = "1"
        print("SETUP")

    @pytest.fixture(scope="module")
    def runner(self):
        return CliRunner()

    @pytest.fixture(scope="module")
    def db(self):
        return Db()

    def test_show_spanning_tree(self, runner, db):
        result = runner.invoke(show.cli.commands["spanning-tree"], [], obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == 0
        assert (re.sub(r'\s+', ' ', result.output.strip())) == (re.sub(
                r'\s+', ' ', EXPECTED_SHOW_SPANNING_TREE_OUTPUT.strip()))

    def test_show_spanning_tree_vlan(self, runner, db):
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["vlan"], ["500"], obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == 0
        assert re.sub(r'\s+', ' ', result.output.strip()) == re.sub(
                      r'\s+', ' ', EXPECTED_SHOW_SPANNING_TREE_VLAN_OUTPUT.strip())

    def test_show_spanning_tree_statistics(self, runner, db):
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["statistics"], [], obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == 0
        assert re.sub(r'\s+', ' ', result.output.strip()) == re.sub(
                      r'\s+', ' ', EXPECTED_SHOW_SPANNING_TREE_STATISTICS_OUTPUT.strip())

    def test_show_spanning_tree_statistics_vlan(self, runner, db):
        result = runner.invoke(
            show.cli.commands["spanning-tree"].commands["statistics"].commands["vlan"], ["500"], obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == 0
        assert re.sub(r'\s+', ' ', result.output.strip()) == re.sub(
                      r'\s+', ' ', EXPECTED_SHOW_SPANNING_TREE_STATISTICS_OUTPUT.strip())

    def test_show_spanning_tree_bpdu_guard(self, runner, db):
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["bpdu_guard"], [], obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == 0
        assert re.sub(r'\s+', ' ', result.output.strip()) == re.sub(
                      r'\s+', ' ', EXPECTED_SHOW_SPANNING_TREE_BPDU_GUARD_OUTPUT.strip())

    def test_show_spanning_tree_root_guard(self, runner, db):
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["root_guard"], [], obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == 0
        assert re.sub(r'\s+', ' ', result.output.strip()) == re.sub(
                      r'\s+', ' ', EXPECTED_SHOW_SPANNING_TREE_ROOT_GUARD_OUTPUT.strip())

    @pytest.mark.parametrize("command, args, expected_exit_code, expected_output", [
        # Disable PVST
        (config.config.commands["spanning-tree"].commands["disable"], ["pvst"], 0, None),
        # Enable PVST
        (config.config.commands["spanning-tree"].commands["enable"], ["pvst"], 0, None),
        # Disable MST
        (config.config.commands["spanning-tree"].commands["disable"], ["mst"], 0, None),
        # Enable MST
        (config.config.commands["spanning-tree"].commands["enable"], ["mst"], 0, None),
        # Configure MST region
        (config.config.commands["spanning-tree"].commands["mst"].commands["region-name"], ["TestRegion"], 0, None),
        # Configure MST revision
        (config.config.commands["spanning-tree"].commands["mst"].commands["revision"], ["10"], 0, None),
        # Configure MST instance priority
        (
            config.config.commands["spanning-tree"]
            .commands["mst"]
            .commands["instance"]
            .commands["1"]
            .commands["priority"],
            ["4096"],
            0,
            None,
        ),

        # Add and remove VLAN in MST instance
        (
            config.config.commands["spanning-tree"]
            .commands["mst"]
            .commands["instance"]
            .commands["1"]
            .commands["vlan"]
            .commands["add"],
            ["500"],
            0,
            None,
        ),

        (
            config.config.commands["spanning-tree"]
            .commands["mst"]
            .commands["instance"]
            .commands["1"]
            .commands["vlan"]
            .commands["del"],
            ["500"],
            0,
            None,
        ),

    ])
    def test_stp_validate_mst_commands(self, runner, db, command, args, expected_exit_code, expected_output):
        result = runner.invoke(command, args, obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == expected_exit_code
        if expected_output:
            assert expected_output in result.output

    @pytest.mark.parametrize("command, args, expected_exit_code, expected_output", [
        # Enable STP on an interface
        (config.config.commands["spanning-tree"].commands["interface"].commands["enable"], ["Ethernet4"], 0, None),
        # Attempt to enable STP again (should fail)
        (config.config.commands["spanning-tree"].commands["interface"].commands["enable"], ["Ethernet4"],
            2, "STP is already enabled for Ethernet4"),
        # Disable STP on an interface
        (config.config.commands["spanning-tree"].commands["interface"].commands["disable"], ["Ethernet4"], 0, None),
        # Enable STP again after disabling
        (config.config.commands["spanning-tree"].commands["interface"].commands["enable"], ["Ethernet4"], 0, None),
        # Set interface priority
        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["priority"],
            ["Ethernet4", "16"],
            0,
            None,
        ),

        # Set interface path cost
        (config.config.commands["spanning-tree"].commands["interface"].commands["cost"], ["Ethernet4", "500"], 0, None),
        # Configure edgeport enable/disable
        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["edgeport"]
            .commands["enable"],
            ["Ethernet4"],
            0,
            None,
        ),

        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["edgeport"]
            .commands["disable"],
            ["Ethernet4"],
            0,
            None,
        ),

        # Configure BPDU guard enable/disable
        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["bpdu_guard"]
            .commands["enable"],
            ["Ethernet4"],
            0,
            None,
        ),

        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["bpdu_guard"]
            .commands["disable"],
            ["Ethernet4"],
            0,
            None,
        ),

        # Configure root guard enable/disable
        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["root_guard"]
            .commands["enable"],
            ["Ethernet4"],
            0,
            None,
        ),

        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["root_guard"]
            .commands["disable"],
            ["Ethernet4"],
            0,
            None,
        ),

        # Configure link type for interface
        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["link_type"]
            .commands["point-to-point"],
            ["Ethernet4"],
            0,
            None,
        ),

        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["link_type"]
            .commands["shared"],
            ["Ethernet4"],
            0,
            None,
        ),

        (
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["link_type"]
            .commands["auto"],
            ["Ethernet4"],
            0,
            None,
        ),

        # Attempt setting invalid cost and priority values
        (config.config.commands["spanning-tree"].commands["interface"].commands["cost"], ["Ethernet4", "0"],
            2, "STP interface path cost must be in range 1-200000000"),
        (config.config.commands["spanning-tree"].commands["interface"].commands["priority"], ["Ethernet4", "1000"],
            2, "STP interface priority must be in range 0-240"),
    ])
    def test_stp_validate_interface_params(self, runner, db, command, args, expected_exit_code, expected_output):
        result = runner.invoke(command, args, obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == expected_exit_code
        if expected_output:
            assert expected_output in result.output

    @pytest.mark.parametrize("command, args, expected_exit_code, expected_output", [
        # Add VLAN and member
        (config.config.commands["vlan"].commands["add"], ["500"], 0, None),
        (config.config.commands["vlan"].commands["member"].commands["add"], ["500", "Ethernet4"], 0, None),
        # Enable STP on VLAN
        (config.config.commands["spanning-tree"].commands["vlan"].commands["enable"], ["500"], 0, None),
        # Disable STP on VLAN
        (config.config.commands["spanning-tree"].commands["vlan"].commands["disable"], ["500"], 0, None),
        # Configure VLAN STP parameters
        (config.config.commands["spanning-tree"].commands["vlan"].commands["hello"], ["500", "3"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["max_age"], ["500", "21"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["forward_delay"], ["500", "16"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["priority"], ["500", "4096"], 0, None),
        # Invalid VLAN parameters
        (config.config.commands["spanning-tree"].commands["vlan"].commands["hello"], ["500", "0"],
            2, "STP hello timer must be in range 1-10"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["forward_delay"], ["500", "2"],
            2, "STP forward delay value must be in range 4-30"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["priority"], ["500", "65536"],
            2, "STP bridge priority must be in range 0-61440"),
        # Remove VLAN member and delete VLAN
        (config.config.commands["vlan"].commands["member"].commands["del"], ["500", "Ethernet4"], 0, None),
        (config.config.commands["vlan"].commands["del"], ["500"], 0, None),
    ])
    def test_stp_validate_vlan_params(self, runner, db, command, args, expected_exit_code, expected_output):
        result = runner.invoke(command, args, obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == expected_exit_code
        if expected_output:
            assert expected_output in result.output

    @pytest.mark.parametrize("command, args, expected_exit_code, expected_output", [
        (config.config.commands["spanning-tree"].commands["disable"], ["pvst"], 0, None),
        (config.config.commands["spanning-tree"].commands["enable"], ["pvst"], 0, None),
        # Add VLAN 500 and assign a member port
        (config.config.commands["vlan"].commands["add"], ["500"], 0, None),
        (config.config.commands["vlan"].commands["member"].commands["add"], ["500", "Ethernet4"], 0, None),
        # Enable PVST globally
        (config.config.commands["spanning-tree"].commands["enable"], ["pvst"], 0, None),
        # Add VLAN 600
        (config.config.commands["vlan"].commands["add"], ["600"], 0, None),
        # Disable and then enable spanning-tree on VLAN 600
        (config.config.commands["spanning-tree"].commands["vlan"].commands["disable"], ["600"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["enable"], ["600"], 0, None),
        # Attempt to delete VLAN 600 while STP is enabled
        (config.config.commands["vlan"].commands["del"], ["600"], 0, None),
        # Enable STP on non-existing VLAN 1010
        (config.config.commands["spanning-tree"].commands["vlan"].commands["enable"], ["1010"], 2, "doesn't exist"),
        # Disable STP on non-existing VLAN 1010
        (config.config.commands["spanning-tree"].commands["vlan"].commands["disable"], ["1010"], 2, "doesn't exist"),
    ])
    def test_add_vlan_enable_pvst(self, runner, db, command, args, expected_exit_code, expected_output):
        result = runner.invoke(command, args, obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == expected_exit_code
        if expected_output:
            assert expected_output in result.output

    @pytest.mark.parametrize("command, args, expected_exit_code, expected_output", [
        # Valid cases
        (config.config.commands["spanning-tree"].commands["hello"], ["3"], 0, None),
        (config.config.commands["spanning-tree"].commands["forward_delay"], ["16"], 0, None),
        (config.config.commands["spanning-tree"].commands["max_age"], ["22"], 0, None),
        (config.config.commands["spanning-tree"].commands["priority"], ["8192"], 0, None),
        (config.config.commands["spanning-tree"].commands["root_guard_timeout"], ["500"], 0, None),
        # Invalid hello timer values
        (config.config.commands["spanning-tree"].commands["hello"], ["0"], 2,
            "STP hello timer must be in range 1-10"),
        (config.config.commands["spanning-tree"].commands["hello"], ["20"], 2,
            "STP hello timer must be in range 1-10"),
        # Invalid forward delay values
        (config.config.commands["spanning-tree"].commands["forward_delay"], ["2"], 2,
            "STP forward delay value must be in range 4-30"),
        (config.config.commands["spanning-tree"].commands["forward_delay"], ["50"], 2,
            "STP forward delay value must be in range 4-30"),
        # Invalid max age values
        (config.config.commands["spanning-tree"].commands["max_age"], ["5"], 2,
            "STP max age value must be in range 6-40"),
        (config.config.commands["spanning-tree"].commands["max_age"], ["45"], 2,
            "STP max age value must be in range 6-40"),
        # Consistency check for forward delay and max age
        (config.config.commands["spanning-tree"].commands["forward_delay"], ["4"], 2,
            "2*(forward_delay-1) >= max_age >= 2*(hello_time +1 )"),
        # Invalid root guard timeout values
        (config.config.commands["spanning-tree"].commands["root_guard_timeout"], ["4"], 2,
            "STP root guard timeout must be in range 5-600"),
        (config.config.commands["spanning-tree"].commands["root_guard_timeout"], ["700"], 2,
            "STP root guard timeout must be in range 5-600"),
        # Invalid priority values
        (config.config.commands["spanning-tree"].commands["priority"], ["65536"], 2,
            "STP bridge priority must be in range 0-61440"),
        (config.config.commands["spanning-tree"].commands["priority"], ["8000"], 2,
            "STP bridge priority must be multiple of 4096"),
    ])
    def test_stp_validate_global_timer_and_priority_params(
        self, runner, db, command, args, expected_exit_code, expected_output
    ):
        result = runner.invoke(command, args, obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == expected_exit_code
        if expected_output:
            assert expected_output in result.output

    @pytest.mark.parametrize("command, args, expected_exit_code, expected_output", [
        (config.config.commands["spanning-tree"].commands["disable"], ["pvst"], 0, None),
        (config.config.commands["spanning-tree"].commands["enable"], ["pvst"], 0, None),
        # Add VLAN and member
        (config.config.commands["vlan"].commands["add"], ["500"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["hello"], ["500", "3"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["max_age"], ["500", "21"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["forward_delay"], ["500", "16"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["priority"], ["500", "4096"], 0, None),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["hello"], ["500", "0"],
            2, "STP hello timer must be in range 1-10"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["hello"], ["500", "20"],
            2, "STP hello timer must be in range 1-10"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["forward_delay"], ["500", "2"],
            2, "STP forward delay value must be in range 4-30"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["forward_delay"], ["500", "42"],
            2, "STP forward delay value must be in range 4-30"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["max_age"], ["500", "4"],
            2, "STP max age value must be in range 6-40"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["max_age"], ["500", "45"],
            2, "STP max age value must be in range 6-40"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["forward_delay"], ["500", "4"],
            2, "2*(forward_delay-1) >= max_age >= 2*(hello_time +1 )"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["priority"], ["500", "65536"],
            2, "STP bridge priority must be in range 0-61440"),
        (config.config.commands["spanning-tree"].commands["vlan"].commands["priority"], ["500", "8000"],
            2, "STP bridge priority must be multiple of 4096"),
        (config.config.commands["vlan"].commands["del"], ["500"], 0, None),
    ])
    def test_stp_validate_vlan_timer_and_priority_params(self, runner, db, command, args, expected_exit_code, expected_output):
        result = runner.invoke(command, args, obj=db)
        print(result.exit_code)
        print(result.output)
        assert result.exit_code == expected_exit_code
        if expected_output:
            assert expected_output in result.output

    @classmethod
    def teardown_class(cls):
        os.environ['UTILITIES_UNIT_TESTING'] = "0"
        print("TEARDOWN")
        dbconnector.load_namespace_config()
        dbconnector.dedicated_dbs.clear()
