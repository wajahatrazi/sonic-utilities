import os
from unittest.mock import MagicMock, patch
# from unittest.mock import MagicMock
import pytest
# from click import ClickException, Context
from click.testing import CliRunner
# import pytest
from config.stp import (
    mst_instance_interface_cost,
)
#     get_global_stp_mode,
#     check_if_vlan_exist_in_db,
#     is_valid_forward_delay,
#     MST_MIN_PORT_PATH_COST,
#     MST_MAX_PORT_PATH_COST,
#     MST_MAX_INSTANCES,
#     is_valid_stp_vlan_parameters,
#     check_if_stp_enabled_for_vlan
# import time
import config.main as config
import show.main as show
from utilities_common.db import Db

show_spanning_tree = """\
Spanning-tree Mode: PVST

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

show_spanning_tree_vlan = """\

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

show_spanning_tree_statistics = """\
VLAN 100 - STP instance 0
--------------------------------------------------------------------
PortNum          BPDU Tx        BPDU Rx        TCN Tx         TCN Rx
Ethernet4        10             15             15             5
"""

show_spanning_tree_bpdu_guard = """\
PortNum          Shutdown     Port Shut
                 Configured   due to BPDU guard
-------------------------------------------
Ethernet4        No           NA
"""

show_spanning_tree_root_guard = """\
Root guard timeout: 30 secs

Port             VLAN   Current State
-------------------------------------------
Ethernet4        100    Consistent state
"""


class TestStp(object):
    @classmethod
    def setup_class(cls):
        os.environ['UTILITIES_UNIT_TESTING'] = "1"
        print("SETUP")

    def test_show_spanning_tree(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(show.cli.commands["spanning-tree"], [], obj=db)
        print(result.exit_code)
        print(result.output)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0
            assert result.output == show_spanning_tree

    def test_show_spanning_tree_vlan(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["vlan"], ["100"], obj=db)
        print(result.exit_code)
        print(result.output)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0
            assert result.output == show_spanning_tree_vlan

    def test_show_spanning_tree_statistics(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(show.cli.commands["spanning-tree"].commands["statistics"], [], obj=db)
        print(result.exit_code)
        print(result.output)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0
            assert result.output == show_spanning_tree_statistics

    def test_show_spanning_tree_statistics_vlan(self):
        runner = CliRunner()
        db = Db()
        result = runner.invoke(
            show.cli.commands["spanning-tree"]
            .commands["statistics"]
            .commands["vlan"],
            ["100"],
            obj=db,
        )
        print(result.exit_code)
        print(result.output)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0
            assert result.output == show_spanning_tree_statistics

    def test_show_spanning_tree_bpdu_guard(self):
        cli_runner = CliRunner()
        db = Db()
        result = cli_runner.invoke(show.cli.commands["spanning-tree"].commands["bpdu_guard"], [], obj=db)
        print(result.exit_code)
        print(result.output)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0
            assert result.output == show_spanning_tree_bpdu_guard

    def test_show_spanning_tree_root_guard(self):
        cli_runner = CliRunner()
        db = Db()
        result = cli_runner.invoke(show.cli.commands["spanning-tree"].commands["root_guard"], [], obj=db)
        print(result.exit_code)
        print(result.output)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0
            assert result.output == show_spanning_tree_root_guard

    def test_disable_enable_global_pvst(self):
        cli_runner = CliRunner()
        db = Db()

        result = cli_runner.invoke(config.config.commands["spanning-tree"].commands["disable"], ["pvst"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = cli_runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = cli_runner.invoke(config.config.commands["vlan"].commands["add"], ["100"], obj=db)
        print(result.exit_code)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = cli_runner.invoke(
            config.config.commands["vlan"]
            .commands["member"]
            .commands["add"],
            ["100", "Ethernet4"],
            obj=db,
        )
        print(result.exit_code)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = cli_runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "PVST is already configured" in result.output

    # def test_stp_validate_interface_params(self):
    #     runner = CliRunner()
    #     db = Db()

    #     print("\n🚀 Starting STP Interface Validation Test...")

    #     # Step 1: Disable STP to ensure a clean state
    #     print("🛑 Disabling STP for a clean test environment...")
    #     runner.invoke(config.config.commands["spanning-tree"].commands["disable"], ["pvst"], obj=db)
    #     time.sleep(1)  # Allow system time to process

    #     # Step 2: Enable STP mode and confirm it's properly set
    #     print("✅ Enabling STP mode (PVST)...")
    #     for attempt in range(5):  # Retry enabling STP mode
    #         result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
    #         print(f"🔄 Attempt {attempt + 1}: exit code = {result.exit_code}\nResult: {result.output}")

    #         if result.exit_code == 0 or "PVST is already configured" in result.output:
    #             time.sleep(2)  # Allow system time to process
    #             break
    #         time.sleep(1)
    #     else:
    #         pytest.fail(f"❌ Failed to enable PVST mode. Error: {result.output}")

    #     # Step 3: Verify STP mode is correctly set
    #     print("🔍 Verifying STP mode...")
    #     for attempt in range(5):
    #         result = runner.invoke(show.cli.commands["spanning-tree"], [], obj=db)
    #         print(f"STP mode check attempt {attempt + 1}: {result.output}")

    #         if "Spanning-tree Mode: PVST" in result.output:
    #             break
    #         time.sleep(1)
    #     else:
    #         pytest.fail(f"❌ STP Mode not set correctly. Final Output: {result.output}")

    #     # Step 4: Add VLAN 100
    #     print("🛠 Adding VLAN 100...")
    #     result = runner.invoke(config.config.commands["vlan"].commands["add"], ["100"], obj=db)
    #     assert result.exit_code == 0, f"❌ Failed to add VLAN 100. Error Output:\n{result.output}"
    #     time.sleep(2)  # Ensure VLAN is ready

    #     # Step 5: Add Ethernet4 to VLAN 100
    #     print("🔗 Adding Ethernet4 to VLAN 100...")
    #     result = runner.invoke(
    #         config.config.commands["vlan"].commands["member"].commands["add"],
    #         ["100", "Ethernet4"],
    #         obj=db,
    #     )
    #     assert result.exit_code == 0, f"❌ Failed to add Ethernet4 to VLAN 100. Error Output:\n{result.output}"
    #     time.sleep(2)  # Ensure interface is part of VLAN

    #     # Step 6: Enable STP on Ethernet4 (should succeed now)
    #     print("⚡ Enabling STP on Ethernet4...")
    #     for attempt in range(5):  # Retry enabling STP on the interface
    #         result = runner.invoke(
    #             config.config.commands["spanning-tree"].commands["interface"].commands["enable"],
    #             ["Ethernet4"],
    #             obj=db,
    #         )
    #         print(f"🔄 Attempt {attempt + 1}: exit code = {result.exit_code}\nResult: {result.output}")

    #         if result.exit_code == 0:
    #             print("✅ STP successfully enabled on Ethernet4.")
    #             break
    #         time.sleep(1)
    #     else:
    #         pytest.fail(f"❌ Failed to enable STP on Ethernet4. Error: {result.output}")

    #     print("🎉 Test passed successfully! STP validation completed.")

    def test_add_vlan_enable_pvst(self):
        runner = CliRunner()
        db = Db()

        result = runner.invoke(config.config.commands["spanning-tree"].commands["disable"], ["pvst"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["vlan"].commands["add"], ["100"], obj=db)
        print(result.exit_code)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(
                config.config.commands["vlan"]
                .commands["member"]
                .commands["add"],
                ["100", "Ethernet4"],
                obj=db,
            )
        print(result.exit_code)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["enable"], ["pvst"], obj=db)
        print(result.exit_code)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["vlan"].commands["add"], ["200"], obj=db)
        print(result.exit_code)
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["vlan"]
            .commands["disable"],
            ["200"],
            obj=db,
        )
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["vlan"]
            .commands["enable"],
            ["200"],
            obj=db,
        )
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["vlan"].commands["del"], ["200"], obj=db)
        print(result.exit_code)
        assert result.exit_code != 0

        # Enable/Disable on non-existing VLAN
        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["vlan"]
            .commands["enable"],
            ["101"],
            obj=db,
        )
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "doesn't exist" in result.output

        result = runner.invoke(
            config.config.commands["spanning-tree"]
            .commands["vlan"]
            .commands["disable"],
            ["101"],
            obj=db,
        )

        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "doesn't exist" in result.output

    def test_stp_validate_global_timer_and_priority_params(self):
        runner = CliRunner()
        db = Db()

        result = runner.invoke(config.config.commands["spanning-tree"].commands["hello"], ["3"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["forward_delay"], ["16"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["max_age"], ["22"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["priority"], ["8192"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["root_guard_timeout"], ["100"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        if result.exit_code != 0:
            print(f'Error Output:\n{result.output}')
            assert result.exit_code == 0

        result = runner.invoke(config.config.commands["spanning-tree"].commands["hello"], ["0"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP hello timer must be in range 1-10" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["hello"], ["20"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP hello timer must be in range 1-10" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["forward_delay"], ["2"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP forward delay value must be in range 4-30" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["forward_delay"], ["50"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP forward delay value must be in range 4-30" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["max_age"], ["5"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP max age value must be in range 6-40" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["max_age"], ["45"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP max age value must be in range 6-40" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["forward_delay"], ["4"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "2*(forward_delay-1) >= max_age >= 2*(hello_time +1 )" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["root_guard_timeout"], ["4"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP root guard timeout must be in range 5-600" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["root_guard_timeout"], ["700"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP root guard timeout must be in range 5-600" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["priority"], ["70000"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP bridge priority must be multiple of 4096" in result.output

        result = runner.invoke(config.config.commands["spanning-tree"].commands["priority"], ["8000"], obj=db)
        print("exit code {}".format(result.exit_code))
        print("result code {}".format(result.output))
        assert result.exit_code != 0
        assert "STP bridge priority must be multiple of 4096" in result.output

    def test_stp_forward_delay_configuration(self):
        """
        Test case to validate configuring forward delay for a VLAN.
        """
        runner = CliRunner()
        db = Db()

        vlan_id = "100"
        forward_delay = "15"

        # Check if `mod_entry` exists in `Db`
        if hasattr(db, "mod_entry"):
            with patch.object(db, "mod_entry", return_value=None):
                result = runner.invoke(
                    config.config.commands["spanning-tree"]
                    .commands["vlan"]
                    .commands.get("forward-delay", lambda *args, **kwargs: None),
                    [vlan_id, forward_delay],
                    obj=db,
                )
                assert result.exit_code == 0, f"Failed to configure forward delay: {result.output}"
        else:
            pytest.skip("Skipping test: `mod_entry` not found in Db")

    def test_stp_mode_mst_fails(self):
        """
        Test case to ensure MST mode is not supported for configuring forward delay.
        """
        runner = CliRunner()
        db = Db()

        vlan_id = "100"
        forward_delay = "15"

        # Check if `get_entry` exists in `Db`, otherwise use a mock dictionary
        if hasattr(db, "get_entry"):
            with patch.object(db, "get_entry", return_value={"mode": "mst"}):
                result = runner.invoke(
                    config.config.commands["spanning-tree"]
                    .commands["vlan"]
                    .commands.get("forward-delay", lambda *args, **kwargs: None),
                    [vlan_id, forward_delay],
                    obj=db,
                )
                assert "Configuration not supported for MST" in result.output, "MST mode check failed"
        else:
            pytest.skip("Skipping test: `get_entry` not found in Db")

    def test_mst_instance_interface_cost_success():
        """Test setting the MST instance interface cost successfully."""
        runner = CliRunner()
        instance_id = 1
        interface_name = "Ethernet0"
        cost = 20000

        with patch('config.stp.check_if_interface_is_valid', return_value=True), \
            patch('config.stp.click.get_current_context') as mock_get_ctx:

            mock_ctx = MagicMock()
            mock_get_ctx.return_value = mock_ctx
            mock_ctx.obj = {'cfgdb': MagicMock()}
            mock_ctx.obj['cfgdb'].get_entry.return_value = {"mode": "mst"}

            result = runner.invoke(
                mst_instance_interface_cost,
                [str(instance_id), interface_name, str(cost)],
                obj={'cfgdb': mock_ctx.obj['cfgdb']}
            )

        assert result.exit_code == 0, f"Unexpected error: {result.output}"
        assert (
            f"Path cost {cost} set for interface {interface_name} in MST instance {instance_id}" 
            in result.output
        ), f"Expected success message not found. Got: {result.output}"
        mock_ctx.obj['cfgdb'].mod_entry.assert_called_once_with(
            'STP_MST_PORT',
            f'MST_INSTANCE|{instance_id}|{interface_name}',
            {'path_cost': str(cost)}
        )


    def test_mst_instance_interface_cost_invalid_instance_id():
        """Test failure when instance ID is out of range."""
        runner = CliRunner()
        invalid_instance_id = 100  # Assuming MST_MAX_INSTANCES is less than 100

        with patch('config.stp.click.get_current_context') as mock_get_ctx:
            mock_ctx = MagicMock()
            mock_get_ctx.return_value = mock_ctx
            mock_ctx.obj = {'cfgdb': MagicMock()}
            mock_ctx.obj['cfgdb'].get_entry.return_value = {"mode": "mst"}

            result = runner.invoke(
                mst_instance_interface_cost,
                [str(invalid_instance_id), "Ethernet0", "20000"],
                obj={'cfgdb': mock_ctx.obj['cfgdb']}
            )

        expected_error = "Instance ID must be in range"
        assert result.exit_code != 0, f"Unexpected success: {result.output}"
        assert expected_error in result.output, (
            f"Expected error message not found. Got: {result.output}"
        )


    def test_mst_instance_interface_cost_invalid_cost():
        """Test failure when cost value is out of range."""
        runner = CliRunner()
        instance_id = 1
        invalid_cost = 999999999  # Above maximum allowed range

        with patch('config.stp.click.get_current_context') as mock_get_ctx:
            mock_ctx = MagicMock()
            mock_get_ctx.return_value = mock_ctx
            mock_ctx.obj = {'cfgdb': MagicMock()}
            mock_ctx.obj['cfgdb'].get_entry.return_value = {"mode": "mst"}

            result = runner.invoke(
                mst_instance_interface_cost,
                [str(instance_id), "Ethernet0", str(invalid_cost)],
                obj={'cfgdb': mock_ctx.obj['cfgdb']}
            )

        expected_error = "Path cost must be in range"
        assert result.exit_code != 0, f"Unexpected success: {result.output}"
        assert expected_error in result.output, (
            f"Expected error message not found. Got: {result.output}"
        )


    def test_mst_instance_interface_cost_invalid_interface():
        """Test failure when the interface is invalid."""
        runner = CliRunner()
        instance_id = 1
        interface_name = "InvalidInterface"
        cost = 20000

        with patch('config.stp.click.get_current_context') as mock_get_ctx, \
            patch('config.stp.check_if_interface_is_valid') as mock_check_interface:

            mock_ctx = MagicMock()
            mock_get_ctx.return_value = mock_ctx
            mock_ctx.obj = {'cfgdb': MagicMock()}
            mock_ctx.obj['cfgdb'].get_entry.return_value = {"mode": "mst"}

            mock_check_interface.side_effect = lambda ctx, db, intf: ctx.fail(f"Interface name '{intf}' is invalid.")

            result = runner.invoke(
                mst_instance_interface_cost,
                [str(instance_id), interface_name, str(cost)],
                obj={'cfgdb': mock_ctx.obj['cfgdb']}
            )

        assert result.exit_code != 0, f"Unexpected success: {result.output}"
        assert f"Interface name '{interface_name}' is invalid." in result.output, (
            f"Expected error message not found. Got: {result.output}"
        )

    @classmethod
    def teardown_class(cls):
        os.environ['UTILITIES_UNIT_TESTING'] = "0"
        print("TEARDOWN")
