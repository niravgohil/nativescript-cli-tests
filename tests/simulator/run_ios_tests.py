"""
Test for `tns run ios` command.

Run should sync all the changes correctly:
 - Valid changes in CSS, JS, XML should be applied.
 - Invalid changes in XML should be logged in the console and lives-sync should continue when XML is fixed.
 - Hidden files should not be synced at all.
 - --syncAllFiles should sync changes in node_modules
 - --justlaunch should release the console.

If simulator is not started and device is not connected `tns run ios` should start simulator.
"""

import os
import time
import unittest

import nose

from core.base_class.BaseClass import BaseClass
from core.device.device import Device
from core.device.emulator import Emulator
from core.device.simulator import Simulator
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import IOS_PACKAGE, SIMULATOR_NAME, TEST_RUN_HOME
from core.tns.replace_helper import ReplaceHelper
from core.tns.tns import Tns
from core.tns.tns_platform_type import Platform
from core.tns.tns_prepare_type import Prepare
from core.tns.tns_verifications import TnsAsserts


class RunIOSSimulatorTests(BaseClass):
    SIMULATOR_ID = ''
    one_hundred_symbols_string = "123456789012345678901234567890123456789012345678901234567890" \
                                 "1234567890123456789012345678901234567890"
    very_long_string = ''
    for x in range(0, 30):
        very_long_string = very_long_string + one_hundred_symbols_string

    max_long_string = ''
    for x in range(0, 9):
        max_long_string = max_long_string + one_hundred_symbols_string
    max_long_string = max_long_string + "1234567890123456789012345678901234567890123456789012345678901234567890" \
                                        "123456789"
    plugin_path = os.path.join(TEST_RUN_HOME, 'data', 'plugins', 'sample-plugin', 'src')

    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)
        Emulator.stop()
        Simulator.stop()
        cls.SIMULATOR_ID = Simulator.ensure_available(simulator_name=SIMULATOR_NAME)
        Folder.cleanup(cls.app_name)
        Tns.create_app(cls.app_name,
                       attributes={'--template': os.path.join('data', 'apps', 'livesync-hello-world.tgz')},
                       update_modules=True)
        Tns.platform_add_ios(attributes={'--path': cls.app_name, '--frameworkPath': IOS_PACKAGE})
        Folder.cleanup(TEST_RUN_HOME + "/data/TestApp")
        Folder.copy(TEST_RUN_HOME + "/" + cls.app_name, TEST_RUN_HOME + "/data/TestApp")

    def setUp(self):
        BaseClass.setUp(self)
        self.SIMULATOR_ID = Simulator.ensure_available(simulator_name=SIMULATOR_NAME)
        Folder.cleanup(self.app_name)
        Folder.copy(TEST_RUN_HOME + "/data/TestApp", TEST_RUN_HOME + "/TestApp")

    def tearDown(self):
        Tns.kill()
        BaseClass.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()
        Emulator.stop()
        Folder.cleanup(TEST_RUN_HOME + "/data/TestApp")

    def test_001_tns_run_ios_js_css_xml(self):
        """Make valid changes in JS,CSS and XML"""

        # `tns run ios` and wait until app is deployed
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=150, check_interval=10)

        # Verify app looks correct inside simulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home', timeout=60)

        # Change JS and wait until app is synced
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_JS, sleep=10)
        strings = ['Successfully transferred', 'main-view-model.js', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Change XML and wait until app is synced
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_XML, sleep=3)
        strings = ['Successfully transferred', 'main-page.xml', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Change CSS and wait until app is synced
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_CSS, sleep=3)
        strings = ['Successfully transferred', 'app.css', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify application looks correct
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_js_css_xml', timeout=60)

        # Rollback all the changes
        ReplaceHelper.rollback(self.app_name, ReplaceHelper.CHANGE_JS, sleep=10)
        strings = ['Successfully transferred', 'main-view-model.js', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        ReplaceHelper.rollback(self.app_name, ReplaceHelper.CHANGE_CSS, sleep=3)
        strings = ['Successfully transferred', 'app.css', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        ReplaceHelper.rollback(self.app_name, ReplaceHelper.CHANGE_XML, sleep=3)
        strings = ['Successfully transferred', 'main-page.xml', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify app looks correct inside simulator
        Device.screen_match(device_name=SIMULATOR_NAME,
                            device_id=self.SIMULATOR_ID, expected_image='livesync-hello-world_home', timeout=60)

    def test_180_tns_run_ios_console_log(self):
        """
         Test console info, warn, error, assert, trace, time and logging of different objects.
        """

        # Change main-page.js so it contains console logging
        source_js = os.path.join('data', 'console-log', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        john_obj = "{\n" \
                   "\"name\": \"John\",\n" \
                   "\"age\": 34\n" \
                   "}"

        john_obj2 = "[\n" + "1,\n" \
                            "5,\n" \
                            "12.5,\n" \
                            "{\n" \
                            "\"name\": \"John\",\n" \
                            "\"age\": 34\n" \
                            "},\n" \
                            "\"text\",\n" \
                            "42\n" \
                            "]"

        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.SIMULATOR_ID,
                   "CONSOLE LOG",
                   "true",
                   "false",
                   "null",
                   "undefined",
                   "-1",
                   "text",
                   john_obj,
                   "number: -1",
                   "string: text",
                   "text -1",
                   "CONSOLE INFO",
                   "info",
                   "CONSOLE WARN",
                   "warn",
                   "CONSOLE ERROR",
                   "error",
                   "false == true",
                   "empty string evaluates to 'false'",
                   "CONSOLE TRACE",
                   "console.trace() called",
                   "0: pageLoaded",
                   "Button(8)",
                   "-1 text {",
                   john_obj2,
                   self.max_long_string,
                   "CONSOLE DEBUG Time:",
                   "### TEST END ###"
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=150, check_interval=10)
        assert self.very_long_string not in log

    def test_181_tns_run_ios_console_dir(self):
        """
         Test console.dir() of different objects.
        """

        # Change main-page.js so it contains console logging
        source_js = os.path.join('data', 'console-dir', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        john_obj = "==== object dump start ====\n" \
                   "name: John\n" \
                   "age: 34\n" \
                   "==== object dump end ===="

        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.SIMULATOR_ID,
                   "true",
                   "false",
                   "null",
                   "undefined",
                   "-1",
                   "text",
                   self.max_long_string,
                   john_obj
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=150, check_interval=10)
        assert self.very_long_string not in log

    def test_200_tns_run_ios_break_and_fix_app(self):
        """
        Make changes in xml that break the app and then changes that fix the app.
        """

        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Project successfully prepared', 'Project successfully built',
                   'Successfully installed on device with identifier', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=120, check_interval=10)

        # Verify app looks correct inside emulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

        # Break the app with invalid xml changes
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_XML_INVALID_SYNTAX)

        # Verify console notify user for broken xml
        strings = ['main-page.xml has syntax errors', 'unclosed xml attribute',
                   'Successfully synced application', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=120, check_interval=10)

        # Revert changes
        ReplaceHelper.rollback(self.app_name, ReplaceHelper.CHANGE_XML_INVALID_SYNTAX)
        strings = ['Successfully transferred', 'main-page.xml', 'Successfully synced application', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=120, check_interval=10)

        # Verify app looks correct inside emulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

    def test_210_tns_run_ios_add_remove_files_and_folders(self):
        """
        New files and folders should be synced properly.
        """

        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False,
                          assert_success=False)
        strings = ['Project successfully prepared', 'Project successfully built',
                   'Successfully installed on device with identifier', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=120, check_interval=10)

        # Verify app looks correct inside emulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

        # Add new files
        new_file_name = 'main-page2.xml'
        source_file = os.path.join(self.app_name, 'app', 'main-page.xml')
        destination_file = os.path.join(self.app_name, 'app', new_file_name)
        File.copy(source_file, destination_file)
        strings = ['Successfully transferred', 'main-page2.xml', 'Successfully synced application', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify new file is synced and available on device.
        error_message = 'Newly created file {0} not found on {1}'.format(new_file_name, self.SIMULATOR_ID)
        app_id = Tns.get_app_id(app_name=self.app_name)
        path = 'app/{0}'.format(new_file_name)
        assert Simulator.path_exists(package_id=app_id, path=path), error_message

        # Revert changes(rename file and delete file)
        File.copy(destination_file, source_file)
        File.remove(destination_file)
        strings = ['Successfully transferred', 'main-page.xml', 'Successfully synced application', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify new file is synced and available on device.
        error_message = '{0} was deleted, but still available on {1}'.format(new_file_name, self.SIMULATOR_ID)
        assert Simulator.path_does_not_exist(package_id=app_id, path=path), error_message

        # Add folder
        new_folder_name = 'test2'
        source_file = os.path.join(self.app_name, 'app', 'test')
        destination_file = os.path.join(self.app_name, 'app', new_folder_name)
        Folder.copy(source_file, destination_file)
        strings = ['Successfully transferred', 'test2', 'Successfully transferred', 'test.txt', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify new folder is synced and available on device.
        error_message = 'Newly created folder {0} not found on {1}'.format(new_folder_name, self.SIMULATOR_ID)
        path = 'app/{0}'.format(new_folder_name)
        assert Simulator.path_exists(package_id=app_id, path=path), error_message

        # Delete folder
        Folder.cleanup(destination_file)
        strings = ['Successfully synced application', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify new folder is sysched and available on device.
        error_message = 'Deleted folder {0} is still available on {1}'.format(new_folder_name, self.SIMULATOR_ID)
        assert Simulator.path_does_not_exist(package_id=app_id, path=path), error_message

        # Verify app looks correct inside emulator
        Device.screen_match(device_name=SIMULATOR_NAME,
                            device_id=self.SIMULATOR_ID, expected_image='livesync-hello-world_home')

    def test_300_tns_run_ios_just_launch_and_incremental_builds(self):
        """
        This test verify following things:
        1. `--justlaunch` option release the console.
        2. Prepare is not triggered if no changed are done.
        3. Incremental prepare is triggered if js, xml and css files are changed.
        """

        # Execute `tns run android --path TNS_App --justlaunch` and verify app looks correct on emulator
        Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--justlaunch': ''}, timeout=180)
        Device.screen_match(device_name=SIMULATOR_NAME,
                            device_id=self.SIMULATOR_ID, expected_image='livesync-hello-world_home')

        # Execute `tns run android --path TNS_App --justlaunch` again
        # without any changes on app under test and verify incremental prepare works
        output = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--justlaunch': ''},
                             assert_success=False, timeout=30)
        TnsAsserts.prepared(app_name=self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.SKIP)

        # Verify app looks correct inside emulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

        # Replace JS, XML and CSS files
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_JS)
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_CSS)
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_XML)

        # Run `tns run ios` after file changes (this should trigger incremental prepare).
        output = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--justlaunch': ''},
                             assert_success=False, timeout=60)
        TnsAsserts.prepared(app_name=self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.INCREMENTAL)

        # Verify app looks is update after changes in js, css and xml
        Device.screen_match(device_name=SIMULATOR_NAME,
                            device_id=self.SIMULATOR_ID, expected_image='livesync-hello-world_js_css_xml')

    def test_315_tns_run_ios_change_appResources_check_per_platform(self):
        # https://github.com/NativeScript/nativescript-cli/pull/3619
        output = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=output, string_list=strings, timeout=150, check_interval=10)

        source = os.path.join('data', 'issues', 'nativescript-cli-3619', 'icon-1025.png')
        target = os.path.join(self.app_name, 'app', 'App_Resources', 'iOS', 'Assets.xcassets', 'AppIcon.appiconset')
        File.copy(source, target)
        strings = ['Xcode build']
        Tns.wait_for_log(log_file=output, string_list=strings, clean_log=False)
        assert "Gradle build" not in output

    def test_330_tns_run_ios_sync_all_files(self):
        """
        Verify '--syncAllFiles' option will sync all files, including node modules.
        """
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--syncAllFiles': ''},
                          wait=False, assert_success=False)
        strings = ['Successfully installed on device with identifier',
                   'Successfully synced application',
                   self.SIMULATOR_ID,  # Verify device id
                   'CONSOLE LOG']  # Verify console log messages are shown.
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=120, check_interval=10)

        ReplaceHelper.replace(app_name=self.app_name, file_change=ReplaceHelper.CHANGE_TNS_MODULES)

        strings = ['Successfully transferred', 'application-common.js', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify app looks correct inside simulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

    def test_340_tns_run_should_not_sync_hidden_files(self):
        """
        Adding hidden files should not break run and they should not be transferred.
        """

        # `tns run ios` and wait until app is deployed
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        sync_message = 'Successfully synced application {0} on device {1}' \
            .format(Tns.get_app_id(self.app_name), self.SIMULATOR_ID)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', sync_message]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=120, check_interval=10)

        # Verify app looks correct inside simulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

        # Add some hidden files
        source_file = os.path.join(self.app_name, 'app', 'main-page.xml')
        destination_file = os.path.join(self.app_name, 'app', '.tempfile')
        File.copy(source_file, destination_file)

        # Give it 10 sec and check no messages are available in log files
        time.sleep(10)
        output = File.read(log)
        assert 'Successfully' not in output, 'Sync is triggered after adding hidden file.'
        assert 'synced' not in output, 'Sync is triggered after adding hidden file.'
        assert 'tempfile' not in output, 'Sync is triggered after adding hidden file.'
        assert self.SIMULATOR_ID not in output, 'Sync is triggered after adding hidden file.'

        # Verify hidden file does not exists on mobile device.
        path = 'app/{0}'.format('.tempfile')
        app_id = Tns.get_app_id(self.app_name)
        error_message = 'Hidden file {0} is transferred to {1}'.format(path, self.SIMULATOR_ID)
        assert Simulator.path_does_not_exist(package_id=app_id, path=path), error_message

        # Verify app looks correct inside simulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

    def test_350_tns_run_ios_should_start_simulator(self):
        """
        `tns run ios` should start iOS Simulator if device is not connected.
        """
        count = Device.get_count(platform=Platform.IOS)
        if count == 0:
            Simulator.stop()
            Tns.run_ios(attributes={'--path': self.app_name, '--justlaunch': ''})
            assert Simulator.wait_for_simulator(timeout=10), 'iOS Simulator not started by `tns run ios`!'
        else:
            raise nose.SkipTest('This test is not valid when devices are connected.')

    def test_360_tns_run_ios_changes_in_app_resources_rebuild_app(self):
        """
        https://github.com/NativeScript/nativescript-cli/issues/3658
        In case when some change occurs in App_Resources/Android and tns run ios command is executed,
        the application is fully rebuild when it should not.
        """

        # Run app twice and check the second time it's not rebuild
        log1 = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log1, string_list=strings, timeout=150, check_interval=10, clean_log=False)

        log2 = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Skipping prepare', 'Successfully transferred all files', 'Refreshing application',
                   'Successfully synced application']
        Tns.wait_for_log(log_file=log2, string_list=strings, timeout=150, check_interval=10, clean_log=False)

        # Make change in App_Resources/Android folder
        app_resources_file = os.path.join(self.app_name, "app", "App_Resources", "Android", "values",
                                          "colors.xml")
        file_to_change = os.path.join("data", "issues", "nativescript-cli-3658", "colors.xml")
        File.copy(file_to_change, app_resources_file)

        # Run again the app and ensure it's not rebuild
        log3 = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Skipping prepare', 'Successfully synced application', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log3, string_list=strings, timeout=150, check_interval=10, clean_log=False)
        assert 'Building project' not in log3, "Project is rebuilt when it should not."

    def test_370_tns_run_plugin_add(self):
        """
        `tns run ios` should do full rebuild after plugin is added.
        """
        # `tns run ios` and wait until app is deployed
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False,
                          log_trace=True)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=150, check_interval=10)

        # Verify app looks correct inside simulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

        # Add plugin
        Tns.plugin_add("nativescript-telerik-ui", attributes={"--path": self.app_name})

        # Change JS and wait for full sync
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_JS, sleep=10)
        strings = ['BUILD SUCCEEDED', 'Project successfully built', 'Successfully installed on device with identifier',
                   self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Rollback JS changes and verify sync is incremental
        ReplaceHelper.rollback(self.app_name, ReplaceHelper.CHANGE_JS, sleep=10)
        strings = ['Successfully transferred', 'main-view-model.js', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings, clean_log=False)
        assert 'BUILD SUCCEEDED' not in File.read(log), "Second change of JS files after plugin add is not incremental!"
        File.write(file_path=log, text="")  # Clean log file

        # Change XML and wait until app is synced
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_XML, sleep=3)
        strings = ['Successfully transferred', 'main-page.xml', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings, clean_log=False)
        assert 'BUILD SUCCEEDED' not in File.read(log), "Change of XML files after plugin add is not incremental!"
        File.write(file_path=log, text="")  # Clean log file

        # Change CSS and wait until app is synced
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_CSS, sleep=3)
        strings = ['Successfully transferred', 'app.css', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings, clean_log=False)
        assert 'BUILD SUCCEEDED' not in File.read(log), "Change of CSS files after plugin add is not incremental!"
        File.write(file_path=log, text="")  # Clean log file

    def test_380_tns_run_ios_plugin_dependencies(self):
        """
        issue https://github.com/NativeScript/ios-runtime/issues/890
        Check app is running when reference plugin A - plugin A depends on plugin B which depends on plugin C.
        Plugin A has dependency only to plugin B.
        Old behavior (version < 4.0.0) was in plugin A to reference plugin B and C.
        """

        # Add plugin with specific dependencies
        Tns.plugin_add(self.plugin_path, attributes={"--path": self.app_name})

        # `tns run ios` and wait until app is deployed
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.SIMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=150, check_interval=10)

        folder_path = os.path.join(os.getcwd(), self.app_name, "platforms", "ios", self.app_name, "app",
                                   "tns_modules", "nativescript-ui-core")
        assert Folder.exists(folder_path), "Cannot find folder: " + folder_path

        # Verify app looks correct inside simulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

    def test_385_tns_run_ios_source_code_in_ios_part_plugin(self):
        """
        https://github.com/NativeScript/nativescript-cli/issues/3650
        """

        # Add plugin with source code in iOS part of the plugin
        Tns.plugin_add(self.plugin_path, attributes={"--path": self.app_name})

        # Replace main-page.js to call method from the source code of the plugin
        source_js = os.path.join('data', "issues", 'nativescript-cli-3650', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': ''}, wait=False, assert_success=False)

        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.SIMULATOR_ID,
                   'Hey!']
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=150, check_interval=10)

        # Verify app looks correct inside simulator
        Device.screen_match(device_name=SIMULATOR_NAME, device_id=self.SIMULATOR_ID,
                            expected_image='livesync-hello-world_home')

    def test_390_tns_run_ios_should_warn_if_package_ids_do_not_match(self):
        """
        If bundle identifiers in package.json and Info.plist do not match CLI should warn the user.
        """
        str1 = "<string>${EXECUTABLE_NAME}</string>"
        str2 = "<string>${EXECUTABLE_NAME}</string>" \
               "<key>CFBundleIdentifier</key>" \
               "<string>org.nativescript.myapp</string>"
        info = os.path.join(self.app_name, 'app', 'App_Resources', 'iOS', 'Info.plist')
        File.replace(file_path=info, str1=str1, str2=str2)
        # `--emulator` added to workaround https://github.com/NativeScript/nativescript-cli/issues/3644
        output = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--justlaunch': ''})
        assert "[WARNING]: The CFBundleIdentifier key inside the 'Info.plist' will be overriden" in output
        assert "Successfully synced application org.nativescript.TestApp" in output

    def test_400_tns_run_on_folder_with_spaces(self):
        """
        `tns run ios` for apps with spaces
        """
        destination_path = os.path.join(TEST_RUN_HOME, "folder with spaces", "Test App")
        Folder.cleanup(folder=destination_path)
        Folder.copy(src=self.app_name, dst=destination_path)
        output = Tns.run_ios(
            attributes={'--path': "\"" + destination_path + "\"", '--emulator': '', '--justlaunch': ''})
        assert "Multiple errors were thrown" not in output
        assert "fail" not in output

    def test_404_tns_run_ios_on_not_existing_device_should_not_start_simulator(self):
        Simulator.stop()
        output = Tns.run_ios(attributes={'--path': self.app_name, '--device': 'fakeId', '--justlaunch': ''},
                             assert_success=False)
        assert not Simulator.wait_for_simulator(
            timeout=10)[0], "Simulator should not be started after run `tns run ios --device <invalid_device_id>`"
        TnsAsserts.invalid_device(output=output)

    @unittest.skipIf(Device.get_count(platform=Platform.IOS) > 0 or Device.get_count(platform=Platform.ANDROID) > 0,
                     "Valid only if there are no devices.")
    def test_410_run_without_platform_and_without_devices(self):
        Simulator.stop()
        Emulator.stop()
        Tns.create_app(self.app_name, update_modules=True)
        output = Tns.run(attributes={'--path': self.app_name, '--justlaunch': ''}, assert_success=False)
        assert "Unable to find applicable devices to execute operation " \
               "and unable to start emulator when platform is not specified" in output
