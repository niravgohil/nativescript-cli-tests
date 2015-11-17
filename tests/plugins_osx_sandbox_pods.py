'''
Test for plugin* commands in context of iOS
'''
import unittest

from helpers._os_lib import cleanup_folder, run_aut, file_exists
from helpers._tns_lib import IOS_RUNTIME_SYMLINK_PATH, \
    TNS_PATH, prepare, create_project_add_platform


# C0103 - Invalid %s name "%s"
# C0111 - Missing docstring
# R0201 - Method could be a function
# R0904 - Too many public methods
# pylint: disable=C0103, C0111, R0201, R0904
class PluginsiOSSandboxPods(unittest.TestCase):

    def setUp(self):

        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""

        # Delete derived data
        run_aut("rm -rf ~/Library/Developer/Xcode/DerivedData/*")
        cleanup_folder('./TNS_App')

    def tearDown(self):
        pass

    def test_001_plugin_add_sandbox_pod_can_write_in_app_folder(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="ios",
            framework_path=IOS_RUNTIME_SYMLINK_PATH,
            symlink=True)

        output = run_aut(
            TNS_PATH +
            " plugin add QA-TestApps/CocoaPods/nativescript-ios-working-with-sandbox-plugin" + \
            " --path TNS_App")
        assert "Successfully installed plugin " + \
            "nativescript-ios-working-with-sandbox-plugin." in output

        output = run_aut("cat TNS_App/package.json")
        assert "nativescript-ios-working-with-sandbox-plugin" in output

        output = prepare(platform="ios", path="TNS_App")
        assert "Successfully prepared plugin " + \
            "nativescript-ios-working-with-sandbox-plugin for ios." in output

        output = run_aut(
            "cat TNS_App/platforms/ios/TNSApp/app/I_MADE_THIS_FILE.txt")
        assert "content" in output

    def test_401_plugin_add_sandbox_pod_can_not_write_outside_app_folder(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="ios",
            framework_path=IOS_RUNTIME_SYMLINK_PATH,
            symlink=True)

        output = run_aut(
            TNS_PATH +
            " plugin add QA-TestApps/CocoaPods/nativescript-ios-fail-with-sandbox-plugin" + \
            " --path TNS_App")
        assert "Successfully installed plugin nativescript-ios-fail-with-sandbox-plugin." in output

        output = run_aut("cat TNS_App/package.json")
        assert "nativescript-ios-fail-with-sandbox-plugin" in output

        output = prepare(platform="ios", path="TNS_App", assert_success=False)
        assert "Successfully prepared " + \
            "plugin nativescript-ios-fail-with-sandbox-plugin for ios." in output

        assert "sh: ../I_MADE_THIS_FILE.txt: Operation not permitted" in output
        assert not file_exists("TNS_App/platforms/I_MADE_THIS_FILE.txt")
