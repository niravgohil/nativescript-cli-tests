"""
Tests for deploy command
"""
import os
import unittest

from core.base_class.BaseClass import BaseClass
from core.device.device import Device
from core.device.emulator import Emulator
from core.java.java import Java
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import ANDROID_PACKAGE, TNS_PATH, ANDROID_KEYSTORE_PASS, ANDROID_KEYSTORE_PATH, \
    ANDROID_KEYSTORE_ALIAS, ANDROID_KEYSTORE_ALIAS_PASS, EMULATOR_ID
from core.settings.strings import *
from core.tns.tns import Tns
from core.tns.tns_platform_type import Platform
from core.tns.tns_verifications import TnsAsserts


class DeployAndroidTests(BaseClass):
    app_name_noplatform = "Test_AppNoPlatform"

    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)
        Emulator.ensure_available()
        Device.ensure_available(platform=Platform.ANDROID)
        Tns.create_app(cls.app_name)
        Tns.platform_add_android(attributes={"--path": cls.app_name, "--frameworkPath": ANDROID_PACKAGE})
        Tns.prepare_android(attributes={"--path": cls.app_name})

    def setUp(self):
        BaseClass.setUp(self)
        Folder.cleanup(self.app_name_noplatform)
        Device.uninstall_app(app_prefix="org.nativescript", platform=Platform.ANDROID)

    def tearDown(self):
        BaseClass.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()

    def test_001_deploy_android(self):
        Device.uninstall_app(app_prefix="org.nativescript", platform=Platform.ANDROID)
        output = Tns.deploy_android(attributes={"--path": self.app_name, "--justlaunch": ""}, timeout=240)

        device_ids = Device.get_ids(platform=Platform.ANDROID)
        for device_id in device_ids:
            print device_id
            assert device_id in output

    def test_002_deploy_android_release(self):
        output = Tns.deploy_android(attributes={"--path": self.app_name,
                                                "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                                "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                                "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                                "--keyStoreAliasPassword":
                                                    ANDROID_KEYSTORE_ALIAS_PASS,
                                                "--release": "",
                                                "--justlaunch": ""
                                                }, timeout=240)

        device_ids = Device.get_ids(platform=Platform.ANDROID)
        for device_id in device_ids:
            assert device_id in output

    def test_200_deploy_android_deviceid(self):
        output = Tns.deploy_android(attributes={"--path": self.app_name, "--device": EMULATOR_ID, "--justlaunch": ""},
                                    timeout=180)

        # We executed build once, but this is first time we call build --release -> we need a prepare
        assert successfully_prepared in output
        assert installed_on_device.format(EMULATOR_ID) in output
        device_ids = Device.get_ids(platform=Platform.ANDROID)
        for device_id in device_ids:
            if "emulator" not in device_id:
                assert device_id not in output

    def test_201_deploy_android_inside_project(self):
        current_dir = os.getcwd()
        os.chdir(os.path.join(current_dir, self.app_name))
        output = Tns.deploy_android(attributes={"--path": self.app_name, "--justlaunch": ""},
                                    tns_path=os.path.join("..", TNS_PATH), timeout=180, assert_success=False)
        os.chdir(current_dir)

        # Now we do not need prepare, because previous test also did build in debug mode
        assert successfully_prepared not in output

        device_ids = Device.get_ids(platform=Platform.ANDROID)
        for device_id in device_ids:
            assert device_id in output

    @unittest.skipIf(Java.version() !="1.8", "Runonly if Java version is 8.")
    def test_300_deploy_android_platform_not_added(self):
        Tns.create_app(app_name=self.app_name_noplatform)
        output = Tns.deploy_android(attributes={"--path": self.app_name_noplatform, "--justlaunch": ""}, timeout=240)

        # It is brand new project and we need a prepare for first run
        assert copy_template_files in output
        assert "Installing tns-android" in output
        assert successfully_prepared in output

        device_ids = Device.get_ids(platform=Platform.ANDROID)
        for device_id in device_ids:
            assert device_id in output

    def test_401_deploy_invalid_platform(self):
        output = Tns.run_tns_command("deploy " + invalid.lower(), attributes={"--path": self.app_name,
                                                                              "--justlaunch": ""
                                                                              })
        assert "Invalid platform {0}. Valid platforms are ios or android.".format(invalid.lower()) in output

    def test_402_deploy_invalid_device(self):
        output = Tns.run_tns_command("deploy android", attributes={"--path": self.app_name,
                                                                   "--justlaunch": "",
                                                                   "--device": "invaliddevice_id"
                                                                   })
        TnsAsserts.invalid_device(output=output)
