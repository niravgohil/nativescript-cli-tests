"""
Test for specific needs of Android runtime.
"""
import os
import time

from core.base_class.BaseClass import BaseClass
from core.device.device import Device
from core.device.emulator import Emulator
from core.device.helpers.adb import Adb
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import ANDROID_PACKAGE, EMULATOR_ID, TEST_RUN_HOME
from core.tns.tns import Tns
from core.tns.tns_platform_type import Platform
from core.tns.tns_verifications import TnsAsserts
from tests.webpack.helpers.helpers import Helpers


class RuntimeTests(BaseClass):
    custom_js_file = os.path.join(BaseClass.app_name, "app", "my-custom-class.js")
    tns_folder = os.path.join(BaseClass.app_name, TnsAsserts.PLATFORM_ANDROID_SRC_MAIN_PATH, "java", "com", "tns")
    gen_folder = os.path.join(tns_folder, "gen")
    generated_java_file = os.path.join(tns_folder, "MyJavaClass.java")

    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)
        Emulator.ensure_available()
        Folder.cleanup('./' + cls.app_name)

    def tearDown(self):
        Tns.kill()
        BaseClass.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()
        Folder.cleanup(cls.app_name)

    def test_200_calling_custom_generated_classes_declared_in_manifest(self):
        Tns.create_app(self.app_name, attributes={"--template": os.path.join("data", "apps", "sbg-test-app.tgz")})
        Tns.platform_add_android(attributes={"--frameworkPath": ANDROID_PACKAGE, "--path": self.app_name})
        Adb.clear_logcat(device_id=EMULATOR_ID)
        Tns.run_android(attributes={"--path": self.app_name, "--device": EMULATOR_ID, "--justlaunch": ""})
        time.sleep(10)
        output = Adb.get_logcat(device_id=EMULATOR_ID)

        # make sure app hasn't crashed
        assert "Displayed org.nativescript.TNSApp/com.tns.ErrorReportActivity" not in output, \
            "App crashed with error activity"
        # check if we got called from custom activity that overrides the default one
        assert "we got called from onCreate of custom-nativescript-activity.js" in output, "Expected output not found"
        # make sure we called custom activity declared in manifest
        assert "we got called from onCreate of my-custom-class.js" in output, "Expected output not found"

    def test_300_verbose_log_android(self):
        Tns.create_app(self.app_name,
                       attributes={"--template": os.path.join("data", "apps", "verbose-hello-world.tgz")})
        Tns.platform_add_android(attributes={"--frameworkPath": ANDROID_PACKAGE, "--path": self.app_name})

        output = File.read(os.path.join(self.app_name, "app", "app.js"), print_content=True)
        assert "__enableVerboseLogging()" in output, "Verbose logging not enabled in app.js"

        # `tns run android` and wait until app is deployed
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', EMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        time.sleep(10)
        log_string = File.read(log)
        assert "TNS.Native" in log_string, "__enableVerboseLogging() do not enable TNS.Native logs!"
        assert "TNS.Java" in log_string, "__enableVerboseLogging() do not enable TNS.Java logs!"

    def test_301_native_package_starting_with_in_are_working(self):
        """
         Test native packages starting with in could be accessed
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-1046', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join('data', "issues", 'android-runtime-1046', 'app.gradle')
        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native packages starting with in could not be accessed'

    def test_302_check_if_class_implements_java_interface_javascript(self):
        """
         Test if java class implements java interface
         https://github.com/NativeScript/android-runtime/issues/739
        """
        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-739', 'javascript', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application',
                   "### TEST PASSED ###"]

        try:
            Tns.wait_for_log(log_file=log, string_list=strings,
                             timeout=300, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Javascript : Check(instanceof) for java class implements java interface does not work' \
                           '(myRunnable instanceof java.lang.Runnable)'

    def test_303_check_if_class_implements_java_interface_java(self):
        """
         Test if java class implements java interface
         https://github.com/NativeScript/android-runtime/issues/739
        """
        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-739', 'java', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application',
                   "### TEST PASSED ###"]

        try:
            Tns.wait_for_log(log_file=log, string_list=strings,
                             timeout=300, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'JAVA : Check(instanceof) for java class implements java interface does not work' \
                           '(myRunnable instanceof java.lang.Runnable)'

    def test_304_support_HeapByteBuffer_to_ArrayBuffer(self):
        """
         Test support HeapByteBuffer to ArrayBuffer
         https://github.com/NativeScript/android-runtime/issues/1060
        """
        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-1060', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        Tns.wait_for_log(log_file=log, string_list=['Successfully synced application'], timeout=240, check_interval=10,
                         clean_log=False)
        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST PASSED###"], timeout=100, check_interval=10,
                             clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'HeapByteBuffer to ArrayBuffer conversion is not working'

    def test_305_native_package_with_compile_app_gradle(self):
        """
         Test that native packages could be used with with compile in app.gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-993', "compile", 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join('data', "issues", 'android-runtime-993', "compile", 'app.gradle')
        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)

        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST COMPILE PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native packages could not be used with compile in app.gradle'

    def test_306_native_package_with_implementation_app_gradle(self):
        """
         Test that native packages could be used with implementation in app.gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-993', "implementation", 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join('data', "issues", 'android-runtime-993', "implementation", 'app.gradle')
        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)

        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST IMPLEMENTATION PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native packages could not be used with implementation in app.gradle'

    def test_307_native_package_with_api_app_gradle(self):
        """
         Test that native packages could be used with api in app.gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-993', "api", 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join('data', "issues", 'android-runtime-993', "api", 'app.gradle')
        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)

        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST API PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native packages could not be used with api in app.gradle'

    def test_308_native_package_in_plugin_include_gradle_with_compile(self):
        """
         Test native packages in plugin could be used with compile in include gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-993', "plugins", 'compile', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)
        # Change app include.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join('data', "issues", 'android-runtime-993', "compile", 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-993', "plugins",
                                 'without_dependency', 'src', 'platforms', 'android', 'include.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_js, dest=target_js)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        source_js = os.path.join('data', "issues", 'android-runtime-993', "plugins", 'app.gradle')
        File.copy(src=source_js, dest=target_js)

        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-993', "plugins",
                                   'without_dependency', 'src')
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)

        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST COMPILE PLUGIN PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native packages could not be used in plugin with compile in include gradle'

    def test_309_native_package_in_plugin_include_gradle_with_implementation(self):
        """
         Test native packages in plugin could be used with implementation in include gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-993', "plugins",
                                 'implementation', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)
        # Change app include.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join('data', "issues", 'android-runtime-993', "implementation", 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-993', "plugins",
                                 'without_dependency', 'src', 'platforms', 'android', 'include.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_js, dest=target_js)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        source_js = os.path.join('data', "issues", 'android-runtime-993', "plugins", 'app.gradle')
        File.copy(src=source_js, dest=target_js)

        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-993', "plugins",
                                   'without_dependency', 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)

        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST IMPLEMENTATION PLUGIN PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native packages could not be used in plugin with implementation in include gradle'

    def test_310_native_package_in_plugin_include_gradle_with_api(self):
        """
         Test native packages in plugin could be used with api in include gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join('data', "issues", 'android-runtime-993', "plugins", 'api', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)
        # Change app include.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join('data', "issues", 'android-runtime-993', "api", 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-993', "plugins",
                                 'without_dependency', 'src', 'platforms', 'android', 'include.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_js, dest=target_js)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        source_js = os.path.join('data', "issues", 'android-runtime-993', "plugins", 'app.gradle')
        File.copy(src=source_js, dest=target_js)

        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-993', "plugins",
                                   'without_dependency', 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)

        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST API PLUGIN PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native packages could not be used in plugin with api in include gradle'

    def test_311_native_package_in_arr_plugin(self):
        """
         Test native packages in arr plugin
         https://github.com/NativeScript/android-runtime/issues/993
        """

        source_js = os.path.join('data', "issues", 'android-runtime-993', "plugins",
                                 'with_dependency', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        source_js = os.path.join('data', "issues", 'android-runtime-993', "plugins", 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-993', "plugins",
                                   'with_dependency', 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)

        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST ARR PLUGIN PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native packages could not be used in arr plugin'

    def test_312_check_minsdk_error_when_building_plugin_with_api23(self):
        """
         Test plugin with minSdk(23) fails when build with default minSdk(17)
         https://github.com/NativeScript/android-runtime/issues/1104
        """

        source_js = os.path.join('data', "issues", 'android-runtime-1104', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-1104', "plugin", 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = [
            'uses-sdk:minSdkVersion 17 cannot be smaller than version 23 declared in library [:com.tns-release:]',
            'as the library might be using APIs not available in 17',
            'Suggestion: use a compatible library with a minSdk of at most 17',
            'or increase this project\'s minSdk version to at least 23',
            'or use tools:overrideLibrary="com.example.comtns" to force usage (may lead to runtime failures)'
        ]

        try:
            Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Should not be able to build with plugin which minsdk version is 23!'

    def test_313_check_minsdk_could_be_set_in_App_gradle(self):
        """
         Test minSdk works in app.gradle
         https://github.com/NativeScript/android-runtime/issues/1104
        """

        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        source_js = os.path.join('data', "issues", 'android-runtime-1104', 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-1104', "plugin", 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        try:
            Tns.wait_for_log(log_file=log, string_list=["### TEST SHOULD NOT CRASH ###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Minsdk set in app.gradle is not working!'

    def test_314_check_minsdk_could_be_set_in_AndroidManifest(self):
        """
         Test minSdk works in AndroidManifest.xml
         https://github.com/NativeScript/android-runtime/issues/1104
        """

        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        source_js = os.path.join('data', "issues", 'android-runtime-1104', 'default_gradle', 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        source_xml = os.path.join('data', 'issues', 'android-runtime-1104', 'AndroidManifest.xml')
        target_xml = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', "src", "main",
                                  'AndroidManifest.xml')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_xml, dest=target_xml)
        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-1104', "plugin", 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        try:
            Tns.wait_for_log(log_file=log, string_list=["### TEST SHOULD NOT CRASH ###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Minsdk set in AndroidManifest is not working!'

    def test_315_check_minsdk_set_in_AndroidManifest_17_app_gradle_23(self):
        """
         Test minSdk in AndroidManifest set to 17 and app.gradle set to 23
         https://github.com/NativeScript/android-runtime/issues/1104
        """

        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        source_js = os.path.join('data', "issues", 'android-runtime-1104', 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        source_xml = os.path.join('data', 'issues', 'android-runtime-1104', "api17_AndroidManifest",
                                  'AndroidManifest.xml')
        target_xml = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', "src", "main",
                                  'AndroidManifest.xml')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_xml, dest=target_xml)
        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-1104', "plugin", 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = [
            'uses-sdk:minSdkVersion 17 cannot be smaller than version 23 declared in library [:com.tns-release:]',
            'as the library might be using APIs not available in 17',
            'Suggestion: use a compatible library with a minSdk of at most 17',
            'or increase this project\'s minSdk version to at least 23',
            'or use tools:overrideLibrary="com.example.comtns" to force usage (may lead to runtime failures)'
        ]

        try:
            Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Test minSdk in AndroidManifest set to 17 and app.gradle set to 23 fails!'

    def test_316_check_minsdk_set_in_AndroidManifest_23_app_gradle_17(self):
        """
         Test minSdk in AndroidManifest set to 23 and app.gradle set to 17
         https://github.com/NativeScript/android-runtime/issues/1104
        """

        target_js = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.remove(target_js, True)
        source_js = os.path.join('data', "issues", 'android-runtime-1104', 'api17_gradle', 'app.gradle')
        File.copy(src=source_js, dest=target_js)
        source_xml = os.path.join('data', 'issues', 'android-runtime-1104', 'AndroidManifest.xml')
        target_xml = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', "src", "main",
                                  'AndroidManifest.xml')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_xml, dest=target_xml)
        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-1104', "plugin", 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        try:
            Tns.wait_for_log(log_file=log, string_list=["### TEST SHOULD NOT CRASH ###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Test minSdk in AndroidManifest set to 23 and app.gradle set to 17 fails!'

    def test_317_check_native_crash_will_not_crash_when_discardUncaughtJsExceptions_used(self):
        """
         Test native crash will not crash the app when discardUncaughtJsExceptions used
         https://github.com/NativeScript/android-runtime/issues/1119
        """
        source_js = os.path.join('data', "issues", 'android-runtime-1119', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)

        source_js = os.path.join('data', "issues", 'android-runtime-1119', 'main-view-model.js')
        target_js = os.path.join(self.app_name, 'app', 'main-view-model.js')
        File.copy(src=source_js, dest=target_js)

        # Change app package.json so it contains the options for autoCatchJSMethodNativeCalls
        source_js = os.path.join('data', "issues", 'android-runtime-1119', 'package.json')
        target_js = os.path.join(self.app_name, 'app', 'package.json')
        File.copy(src=source_js, dest=target_js)

        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        time.sleep(40)
        Device.click(device_id=EMULATOR_ID, text="TAP", timeout=20)
        time.sleep(15)
        try:
            strings = ["Error: java.lang.Exception: Failed resolving method createTempFile on class java.io.File",
                       "Caused by: java.lang.Exception: Failed resolving method createTempFile on class java.io.File"]
            Tns.wait_for_log(log_file=log, string_list=strings,
                             timeout=100, check_interval=10, clean_log=False)
            Helpers.android_screen_match("No-crash-image", timeout=120, tolerance=1)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Native crash should not crash the app when discardUncaughtJsExceptions used fails!'

    def test_318_generated_classes_not_be_deleted_on_rebuild(self):
        # https: // github.com / NativeScript / nativescript - cli / issues / 3560
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name},
                            assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        target = os.path.join(self.app_name, 'app')
        source = os.path.join(TEST_RUN_HOME, 'data', 'issues', 'android-runtime-904', 'MyActivity.js')
        File.copy(source, target)

        Tns.build_android(attributes={"--path": self.app_name})

        assert File.exists(self.app_name + "/app/MyActivity.js")
        assert File.exists(self.app_name + "/platforms/android/app/src/main/java/com/tns/MyActivity.java")

        File.remove(self.app_name + '/app/MyActivity.js')

        Tns.build_android(attributes={"--path": self.app_name})

        assert not File.exists(self.app_name + "/platforms/android/app/src/main/java/com/tns/MyActivity.java")

    def test_319_build_project_with_foursquare_android_oauth(self):
        # This is required when build with different SDK
        Folder.cleanup(self.app_name)
        Tns.create_app(self.app_name)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})

        # Add foursquare native library as dependency
        source = os.path.join('data', 'issues', 'android-runtime-755', 'app.gradle')
        target = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(src=source, dest=target)

        # Build the project
        output = Tns.build_android(attributes={"--path": self.app_name}, assert_success=False)
        assert ':asbg:generateBindings', 'Static Binding Generator not executed'
        assert 'cannot access its superclass' not in output


    def test_320_check_public_method_in_abstract_interface_could_be_called_api23(self):
        """
         Test public method in abstract interface could be called
         https://github.com/NativeScript/android-runtime/issues/1157
        """

        source_js = os.path.join('data', "issues", 'android-runtime-1157', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_js, dest=target_js)
        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-1157', 'API23', 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST CALL PUBLIC METHOD IN ABSTRACT INTERFACE PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Test public method in abstract interface could be called fails for api23!'

    def test_321_check_public_method_in_abstract_interface_could_be_called_api25(self):
        """
         Test public method in abstract interface could be called
         https://github.com/NativeScript/android-runtime/issues/1157
        """

        source_js = os.path.join('data', "issues", 'android-runtime-1157', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_js, dest=target_js)
        plugin_path = os.path.join(TEST_RUN_HOME, 'data', "issues", 'android-runtime-1157', 'API25', 'src')
        Tns.plugin_remove("mylib", assert_success=False, attributes={"--path": self.app_name})
        output = Tns.plugin_add(plugin_path, assert_success=False, attributes={"--path": self.app_name})
        assert "Successfully installed plugin mylib" in output, "mylib plugin not installed correctly!"
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application'
                   ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)
        try:
            Tns.wait_for_log(log_file=log, string_list=["###TEST CALL PUBLIC METHOD IN ABSTRACT INTERFACE PASSED###"],
                             timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Test public method in abstract interface could be called fails for api25!'

    def test_322_extends_method_is_working_in_non_native_inheritance(self):
        """
        Test __extends is working non native inheritance
        https://github.com/NativeScript/android-runtime/issues/1181
        """
        Folder.cleanup(self.app_name)
        Tns.create_app(self.app_name, attributes={"--vue":""})
        Tns.platform_add_android(attributes={"--frameworkPath": ANDROID_PACKAGE, "--path": self.app_name})

        source_js = os.path.join('data', "issues", 'android-runtime-1181', 'js', 'app.js')
        target_js = os.path.join(self.app_name, 'app', 'app.js')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_js, dest=target_js)

        log = Tns.run_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID, "--bundle":""}, wait=False,
                                      assert_success=False)
        strings = ['Project successfully built',
                    'Successfully installed on device with identifier', EMULATOR_ID,
                    'Successfully synced application'
                    ]

        Tns.wait_for_log(log_file=log, string_list=strings, timeout=240, check_interval=10, clean_log=False)

        try:
            Tns.wait_for_log(log_file=log, string_list=["'NativeScript-Vue has \"Vue.config.silent\" set to true, to see output logs set it to false.'"],
                        timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Test __extends is working non native inheritance ts code fails!'

        source_js = os.path.join('data', "issues", 'android-runtime-1181', 'ts', 'app.js')
        target_js = os.path.join(self.app_name, 'app', 'app.js')
        if File.exists(target_js):
            File.remove(target_js, True)
        File.copy(src=source_js, dest=target_js)

        try:
            Tns.wait_for_log(log_file=log, string_list=[
                "'NativeScript-Vue has \"Vue.config.silent\" set to true, to see output logs set it to false.'"],
                        timeout=100, check_interval=10, clean_log=False)
        except Exception as e:
            print str(e)
            assert 1 == 2, 'Test extends is working non native inheritance fails for js code!'

    def test_350_sgb_fails_generating_custom_activity(self):
        """
        Static Binding Generator fails if class has static properties that are used within the class
        https://github.com/NativeScript/android-runtime/issues/1160
        """
        Folder.cleanup(self.app_name)
        Tns.create_app(self.app_name)
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name},
                            assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})

        source = os.path.join('data', "issues", 'android-runtime-1160', 'testActivity.android.js')
        target = os.path.join(self.app_name, 'app')
        File.copy(src=source, dest=target)

        Tns.build_android(attributes={"--path": self.app_name}, assert_success=False)
        activity_class_path = os.path.join(self.app_name, "platforms", "android", "app", "src", "main", "java", "com",
                                           "test")

        if File.exists(os.path.join(activity_class_path, "Activity.java")):
            assert True
        else:
            assert False, "Fail: Custom activity class is NOT generated in {0} !".format(activity_class_path)

    def test_360_applying_before_plugins_gradle(self):
        """
        Applying before-plugin.gradle file before plugin's include.gradle

        https://github.com/NativeScript/android-runtime/issues/1183
        """

        source = os.path.join('data', 'issues', 'android-runtime-1183', 'before-plugins.gradle')
        target = os.path.join(self.app_name, 'app', 'App_Resources', 'Android')
        File.copy(src=source, dest=target)

        plugin_path = os.path.join(TEST_RUN_HOME, 'data', 'plugins', 'sample-plugin', 'src')
        Tns.plugin_add(plugin_path, attributes={"--path": self.app_name})

        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name},
                            assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})

        output = Tns.build_android(attributes={"--path": self.app_name}, assert_success=False)
        messages = "MESSAGE: Before plugins gradle is applied!\nMESSAGE: Plugin include gradle is applied!"
        assert messages in output, "FAIL: before-plugins.gradle is NOT applied correctly!"

    def test_420_include_gradle_flavor(self):
        # https://github.com/NativeScript/android-runtime/pull/937
        # https://github.com/NativeScript/nativescript-cli/pull/3467
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name},
                            assert_success=False)
        source = os.path.join(TEST_RUN_HOME, 'data', 'issues', 'android-runtime-pr-937', 'app.gradle')
        target = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(src=source, dest=target)

        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})

        Tns.run_tns_command("build android", attributes={"--path": self.app_name})

        assert File.exists(self.app_name +
                           "/platforms/android/app/build/outputs/apk/arm64Demo/debug/app-arm64-demo-debug.apk")
        assert File.exists(self.app_name +
                           "/platforms/android/app/build/outputs/apk/arm64Full/debug/app-arm64-full-debug.apk")
        assert File.exists(self.app_name +
                           "/platforms/android/app/build/outputs/apk/armDemo/debug/app-arm-demo-debug.apk")
        assert File.exists(self.app_name +
                           "/platforms/android/app/build/outputs/apk/armFull/debug/app-arm-full-debug.apk")
        assert File.exists(self.app_name +
                           "/platforms/android/app/build/outputs/apk/x86Demo/debug/app-x86-demo-debug.apk")
        assert File.exists(self.app_name +
                           "/platforms/android/app/build/outputs/apk/x86Full/debug/app-x86-full-debug.apk")

    def test_430_verify_JSParser_in_SBG_is_failing_the_build_when_there_is_an_error(self):
        """
         JSParser in SBG fail the build when there is an error
        https://github.com/NativeScript/android-runtime/issues/1152
        """

        # Change main-page.js with sbg Error
        source_js = os.path.join('data', "issues", 'android-runtime-1152', 'main-page.js')
        target_js = os.path.join(self.app_name, 'app', 'main-page.js')
        File.copy(src=source_js, dest=target_js)
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name}, assert_success=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})
        log = Tns.build_android(attributes={'--path': self.app_name, '--device': EMULATOR_ID},
                                assert_success=False)

        assert "FAILURE: Build failed with an exception" in log
        assert "JSParser Error: Not enough or too many arguments passed(0) when trying to extend interface: " \
               "java.util.List in file: main-page" in log
        assert "Execution failed for task ':app:runSbg'" in log
