"""
Test for emulate command in context of Android
"""
import os
import unittest

# C0103 - Invalid %s name "%s"
# C0111 - Missing docstring
# R0201 - Method could be a function
# R0904 - Too many public methods
# pylint: disable=C0103, C0111, R0201, R0904
from core.device.emulator import Emulator
from core.osutils.command import run
from core.osutils.folder import Folder
from core.settings.settings import ANDROID_RUNTIME_PATH, TNS_PATH, ANDROID_KEYSTORE_PATH, ANDROID_KEYSTORE_PASS, \
    ANDROID_KEYSTORE_ALIAS, ANDROID_KEYSTORE_ALIAS_PASS
from core.tns.tns import Tns


class EmulateAndroid(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Folder.cleanup('./TNSAppNoPlatform')
        Folder.cleanup('./TNS_App')
        Tns.create_app_platform_add(app_name="TNS_App", platform="android", framework_path=ANDROID_RUNTIME_PATH)

    def setUp(self):

        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""

        Emulator.stop_emulators();
        Folder.cleanup('./TNSAppNoPlatform')
        Folder.cleanup('./TNS_App/platforms/android/build/outputs')

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        Emulator.stop_emulators();
        Folder.cleanup('./TNS_App')

    @unittest.skip("Skipped because of https://github.com/NativeScript/nativescript-cli/issues/352")
    def test_001_emulate_android_in_running_emulator(self):

        Emulator.ensure_available();

        Tns.create_app_platform_add(app_name="TNS_App", \
                                    platform="android", framework_path=ANDROID_RUNTIME_PATH)
        output = run(TNS_PATH + " emulate android --path TNS_App --timeout 600 --justlaunch", \
                         timeout=660)
        assert "Project successfully prepared" in output
        assert "Project successfully built" in output

        # Emulator can not be started without active UI
        if ('ACTIVE_UI' in os.environ) and ("YES" in os.environ['ACTIVE_UI']):
            assert "installing" in output
            assert "running" in output
            assert not "Starting Android emulator with image" in output

        # TODO: Get device id and verify files are deployed and process is
        # running on this device

    def test_002_emulate_android_release(self):

        output = run(TNS_PATH + " emulate android --avd Api19 " + \
                         "--keyStorePath " + ANDROID_KEYSTORE_PATH + \
                        " --keyStorePassword " + ANDROID_KEYSTORE_PASS + \
                        " --keyStoreAlias " + ANDROID_KEYSTORE_ALIAS + \
                        " --keyStoreAliasPassword " + ANDROID_KEYSTORE_ALIAS_PASS + \
                        " --release --path TNS_App --timeout 600 --justlaunch", timeout=660)
        assert "Project successfully prepared" in output
        assert "Project successfully built" in output
        assert "Starting Android emulator with image" in output
        assert "installing" in output
        assert "running" in output
        # TODO: Get device id and verify files are deployed and process is
        # running on this device

    # TODO: Implement this test
    @unittest.skip("Not implemented.")
    def test_014_emulate_android_genymotion(self):
        pass

    def test_200_emulate_android_inside_project_and_specify_emulator_name(self):

        current_dir = os.getcwd()
        os.chdir(os.path.join(current_dir, "TNS_App"))
        output = run(os.path.join("..", TNS_PATH) + \
                         " emulate android --avd Api19 --timeout 600 --justlaunch", timeout=660)
        os.chdir(current_dir)
        assert "Project successfully prepared" in output
        assert "Project successfully built" in output
        assert "Starting Android emulator with image Api19" in output
        assert "installing" in output
        assert "running" in output

        # TODO: Get device id and verify files are deployed and process is
        # running on this device

    def test_300_emulate_android_platform_not_added(self):
        Tns.create_app(app_name="TNSAppNoPlatform")
        output = run(TNS_PATH + \
            " emulate android --avd Api19 --timeout 600  --justlaunch --path TNSAppNoPlatform", \
            timeout=660)
        assert "Copying template files..." in output
        assert "Project successfully created." in output
        assert "Project successfully prepared" in output
        assert "Project successfully built" in output
        assert "Starting Android emulator with image Api" in output
        assert "installing" in output
        assert "running" in output

        # TODO: Get device id and verify files are deployed and process is
        # running on this device

    def test_400_emulate_invalid_platform(self):
        output = run(TNS_PATH + \
            " emulate invalidPlatform --path TNS_App --timeout 600 --justlaunch", \
            timeout=660)
        assert "The input is not valid sub-command for 'emulate' command" in output
        assert "Usage" in output

    @unittest.skip(
        "Skipped because of https://github.com/NativeScript/nativescript-cli/issues/289")
    def test_401_emulate_invalid_avd(self):
        output = run(TNS_PATH + \
            " emulate android --avd invaliddevice_id --path TNS_App --timeout 600 --justlaunch", \
            timeout=660)
        # TODO: Modify assert when issue is fixed
        assert "'invalidPlatform' is not valid sub-command for 'emulate' command" in output
        assert "Usage" in output