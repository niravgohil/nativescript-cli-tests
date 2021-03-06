"""
Test platform add (android)
"""
import unittest

from core.base_class.BaseClass import BaseClass
from core.java.java import Java
from core.npm.npm import Npm
from core.osutils.folder import Folder
from core.settings.settings import TNS_PATH, ANDROID_PACKAGE, TEST_RUN_HOME, USE_YARN
from core.settings.strings import *
from core.tns.tns import Tns
from core.tns.tns_platform_type import Platform
from core.tns.tns_verifications import TnsAsserts


# noinspection PyMethodMayBeStatic
class PlatformAndroidTests(BaseClass):

    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)
        Tns.create_app(cls.app_name, update_modules=False)

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()

    def setUp(self):
        BaseClass.setUp(self)
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)

    def test_100_platform_add_android(self):
        """ Default `tns platform add` command"""
        Tns.platform_add_android(attributes={"--path": self.app_name})

    def test_110_platform_add_android_framework_path(self):
        """ Add platform from local package"""
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})

    def test_120_platform_add_android_inside_project(self):
        """ Add platform inside project folder (not using --path)"""
        Folder.navigate_to(self.app_name)
        output = Tns.platform_add_android(tns_path=os.path.join("..", TNS_PATH), assert_success=False)
        Folder.navigate_to(TEST_RUN_HOME, relative_from_current_folder=False)
        TnsAsserts.platform_added(self.app_name, platform=Platform.ANDROID, output=output)

    def test_130_platform_remove_and_platform_add_android_custom_version(self):
        """Verify platform add supports custom versions"""

        # Add custom version number
        Tns.platform_add_android(version="5.0.0", attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"5.0.0\""])

        # Add remove
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name})

        # Add custom version with tag
        Tns.platform_add_android(version="rc", attributes={"--path": self.app_name})

    @unittest.skipIf(Java.version() != "1.8", "Run only if Java version is 8.")
    def test_200_platform_update_android(self):
        """Update platform"""

        # Create project with tns-android@4
        Tns.platform_add_android(version="4.0.0", attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"4.0.0\""])

        # Update platform to 5
        Tns.platform_update(platform=Platform.ANDROID, version="5.0.0", attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"5.0.0\""])

    def test_210_platform_update_android_when_platform_not_added(self):
        """`platform update` should work even if platform is not added"""
        output = Tns.platform_update(platform=Platform.ANDROID, attributes={"--path": self.app_name},
                                     assert_success=False)
        TnsAsserts.platform_added(self.app_name, platform=Platform.ANDROID, output=output)

    @unittest.skipIf(Java.version() != "1.8", "Run only if Java version is 8.")
    def test_220_platform_clean_android(self):
        """Prepare after `platform clean` should add the same version that was before clean"""

        # Create project with tns-android@5.0.0
        Tns.platform_add_android(version="5.0.0", attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"5.0.0\""])

        # Clean platform and verify platform is 5.0.0
        Tns.platform_clean(platform=Platform.ANDROID, attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"5.0.0\""])

    @unittest.skipIf(Java.version() != "1.8", "Run only if Java version is 8.")
    def test_230_tns_update(self):
        """ Default `tns platform add` command"""
        Tns.platform_add_android(attributes={"--path": self.app_name}, version="latest")

        output = Tns.update(attributes={"--path": self.app_name})
        if USE_YARN == "False":
            self.verify_update(output)
            modules_version = Npm.get_version("tns-core-modules")
            TnsAsserts.package_json_contains(self.app_name, [modules_version])

            output = Tns.update(attributes={"5.0.0": "", "--path": self.app_name})
            self.verify_update(output)
            TnsAsserts.package_json_contains(self.app_name, ["5.0.0"])

            Tns.update(attributes={"next": "", "--path": self.app_name})
            self.verify_update(output)
            modules_version = Npm.get_version("tns-android@next")
            android_version = Npm.get_version("tns-core-modules@next")
            TnsAsserts.package_json_contains(self.app_name, [modules_version, android_version])
        else:
            self.verify_update(output)

    def test_390_platform_list(self):
        """Platform list command should list installed platforms and if app is prepared for those platforms"""
        # issue with v2 of templates - workaround with remove ios platform
        Tns.platform_remove(platform=Platform.IOS, attributes={"--path": self.app_name}, assert_success=False)

        # `tns platform list` on brand new project
        output = Tns.platform_list(attributes={"--path": self.app_name})
        TnsAsserts.platform_list_status(output=output, prepared=Platform.NONE, added=Platform.NONE)

        # `tns platform list` when android is added
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        output = Tns.platform_list(attributes={"--path": self.app_name})
        TnsAsserts.platform_list_status(output=output, prepared=Platform.NONE, added=Platform.ANDROID)

        # `tns platform list` when android is prepared
        Tns.prepare_android(attributes={"--path": self.app_name})
        output = Tns.platform_list(attributes={"--path": self.app_name})
        TnsAsserts.platform_list_status(output=output, prepared=Platform.ANDROID, added=Platform.ANDROID)

    def test_400_platform_list_wrong_path(self):
        output = Tns.run_tns_command("platform list")
        assert "No project found at or above" in output
        assert "and neither was a --path specified." in output

        output = Tns.run_tns_command("platform list", attributes={"--path": "invalidPath"})
        assert "No project found at or above" in output
        assert "and neither was a --path specified." in output

    def test_420_platform_add_existing_platform(self):
        self.test_110_platform_add_android_framework_path()
        output = Tns.platform_add_android(attributes={"--path ": self.app_name}, assert_success=False)
        assert "Platform android already added" in output

    def test_421_platform_add_android_wrong_option(self):
        # frameworkPath point to missing file
        output = Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": "invalidFile.tgz"},
                                          assert_success=False)
        assert "Invalid frameworkPath: invalidFile.tgz" in output
        assert "Please ensure the specified frameworkPath exists." in output

        # Wrong frameworkPath option
        output = Tns.platform_add_android(attributes={"--path": self.app_name, "--" + invalid: "tns-android.tgz"},
                                          assert_success=False)
        assert invalid_option.format(invalid) in output

        # Empty platform, only `tns platform add`
        output = Tns.platform_add(attributes={"--path": self.app_name}, assert_success=False)
        assert no_platform in output
        assert "Usage" in output

    def test_430_platform_remove_missing_invalid_or_empty_platform(self):
        output = Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name},
                                     assert_success=False)
        assert "The platform android is not added to this project"
        assert "Usage" in output

        output = Tns.platform_remove(platform="invalidPlatform", attributes={"--path": self.app_name},
                                     assert_success=False)
        assert "Invalid platform invalidplatform. Valid platforms are ios or android." in output
        assert "Usage" in output

        output = Tns.platform_remove(attributes={"--path": self.app_name}, assert_success=False)
        assert no_platform in output
        assert "Usage" in output

    def test_440_platform_update_empty_platform(self):
        output = Tns.platform_update(attributes={"--path": self.app_name}, assert_success=False)
        assert no_platform in output
        assert "Usage" in output

    @staticmethod
    def verify_update(output):
        assert "Platform android successfully removed" in output
        assert "Successfully removed plugin tns-core-modules" in output
        assert "Platform android successfully added" in output
        assert "Successfully installed plugin tns-core-modules" in output
