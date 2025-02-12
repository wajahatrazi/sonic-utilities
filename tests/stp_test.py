from click.testing import CliRunner
from utilities_common.db import Db
import show.main as show
import config.main as config


class TestStp:
    def test_show_spanning_tree(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(show.cli.commands["spanning-tree"], [], obj=db)
        assert result.exit_code == 0
        expected_output = """Spanning-tree Mode: PVST

VLAN 100 - STP instance 0
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
        assert result.output.strip() == expected_output.strip()

    def test_show_spanning_tree_vlan(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["vlan"], ["100"], obj=db)
        assert result.exit_code == 0
        expected_output = """
VLAN 100 - STP instance 0
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
        assert result.output.strip() == expected_output.strip()

    def test_show_spanning_tree_statistics(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["statistics"], [], obj=db)
        assert result.exit_code == 0
        expected_output = """VLAN 100 - STP instance 0
--------------------------------------------------------------------
PortNum          BPDU Tx        BPDU Rx        TCN Tx         TCN Rx
Ethernet4        10             15             15             5
"""
        assert result.output.strip() == expected_output.strip()

    def test_show_spanning_tree_statistics_vlan(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(
            show.cli.commands["spanning-tree"].commands["statistics"].commands["vlan"],
            ["100"],
            obj=db
        )

        assert result.exit_code == 0
        expected_output = """VLAN 100 - STP instance 0
--------------------------------------------------------------------
PortNum          BPDU Tx        BPDU Rx        TCN Tx         TCN Rx
Ethernet4        10             15             15             5
"""
        assert result.output.strip() == expected_output.strip()

    def test_show_spanning_tree_root_guard(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["root_guard"], [], obj=db)
        assert result.exit_code == 0
        expected_output = """Root guard timeout: 30 secs

Port             VLAN   Current State
-------------------------------------------
Ethernet4        100    Consistent state
"""
        assert result.output.strip() == expected_output.strip()

    def test_disable_enable_global_pvst(self):
        runner = CliRunner()
        db = Db()

        result = runner.invoke(config.config.commands["spanning-tree"].commands["disable"], ["pvst"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["vlan"].commands["add"], ["100"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["vlan"]
            .commands["member"]
            .commands["add"],
            ["100", "Ethernet4"],
            obj=db
        )
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        assert "PVST is already configured" in result.output

    def test_stp_validate_interface_params(self):
        runner = CliRunner()
        db = Db()

        result = runner.invoke(config.config.commands["spanning-tree"].commands["disable"], ["pvst"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["enable"],
            ["Ethernet4"],
            obj=db
        )
        assert "Global STP is not enabled" in result.output

        result = runner.invoke(config.config.commands["vlan"].commands["add"], ["100"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["vlan"]
            .commands["member"]
            .commands["add"],
            ["100", "Ethernet4"],
            obj=db
        )
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["priority"],
            ["Ethernet4", "16"],
            obj=db
        )
        assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["cost"],
            ["Ethernet4", "100"],
            obj=db
        )
        assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["disable"],
            ["Ethernet4"],
            obj=db
        )
        assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["enable"],
            ["Ethernet4"],
            obj=db
        )
        assert result.exit_code == 0

    def test_stp_vlan_deletion(self):
        runner = CliRunner()
        db = Db()

        result = runner.invoke(config.config.commands["vlan"].commands["add"], ["500"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["vlan"].commands["add"], ["600"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["vlan"].commands["del"], ["500"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["vlan"].commands["del"], ["600"], obj=db)
        assert result.exit_code == 0

    def test_stp_global_timer_priority_validation(self):
        runner = CliRunner()
        db = Db()

        result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        assert result.exit_code == 0

        # Testing invalid max age
        result = runner.invoke(config.config.commands["spanning-tree"].commands["max-age"], ["40"], obj=db)
        assert "Max age must be between 6 and 40" in result.output

        # Testing invalid hello time
        result = runner.invoke(config.config.commands["spanning-tree"].commands["hello-time"], ["15"], obj=db)
        assert "Hello time must be between 1 and 10" in result.output

        # Testing invalid forward delay
        result = runner.invoke(config.config.commands["spanning-tree"].commands["forward-time"], ["30"], obj=db)
        assert "Forward delay must be between 4 and 30" in result.output

        # Testing valid priority range
        result = runner.invoke(config.config.commands["spanning-tree"].commands["priority"], ["4096"], obj=db)
        assert result.exit_code == 0

    def test_stp_interface_priority_cost_validation(self):
        runner = CliRunner()
        db = Db()

        result = runner.invoke(config.config.commands["vlan"].commands["add"], ["100"], obj=db)
        assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["vlan"]
            .commands["member"]
            .commands["add"],
            ["100", "Ethernet4"],
            obj=db
        )
        assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        assert result.exit_code == 0

        # Testing invalid path cost
        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["cost"],
            ["Ethernet4", "300000000"],
            obj=db
        )

        assert "STP interface path cost must be in range 1-200000000" in result.output

        # Testing invalid priority
        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["priority"],
            ["Ethernet4", "256"],
            obj=db
        )

        assert "STP per VLAN port priority must be in range 0-240" in result.output

    def test_stp_interface_vlan_membership(self):
        runner = CliRunner()
        db = Db()

        result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        assert result.exit_code == 0

        # Testing interface not a member of VLAN
        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["interface"]
            .commands["enable"],
            ["Ethernet8"],
            obj=db
        )
        assert "Interface not a member of VLAN" in result.output
