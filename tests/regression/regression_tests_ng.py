import os

from core.base_class.BaseClass import BaseClass
from core.device.emulator import Emulator
from core.device.simulator import Simulator
from core.osutils.folder import Folder
from core.osutils.os_type import OSType
from core.settings.settings import TEST_RUN_HOME, CURRENT_OS, SIMULATOR_NAME, \
    ANDROID_KEYSTORE_PATH, ANDROID_KEYSTORE_PASS, ANDROID_KEYSTORE_ALIAS, ANDROID_KEYSTORE_ALIAS_PASS, \
    EMULATOR_ID
from core.tns.replace_helper import ReplaceHelper
from core.tns.tns import Tns
from tests.webpack.helpers.helpers import Helpers


class RegressionTestsNG(BaseClass):
    SIMULATOR_ID = ""

    image_original = 'hello-world-ng'
    image_change = 'hello-world-ng-js-css-xml'

    html_change = ['app/item/items.component.html', '[text]="item.name"', '[text]="item.id"']
    ts_change = ['app/item/item.service.ts', 'Ter Stegen', 'Stegen Ter']
    css_change = ['app/app.css', 'core.light.css', 'core.dark.css']

    target_app = os.path.join(TEST_RUN_HOME, BaseClass.app_name)
    source_app = os.path.join(TEST_RUN_HOME, 'data', 'apps', 'test-app-ng-34')

    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)

        Folder.cleanup(cls.target_app)
        Folder.copy(cls.source_app, cls.target_app)

        Emulator.ensure_available()
        if CURRENT_OS == OSType.OSX:
            cls.SIMULATOR_ID = Simulator.ensure_available(simulator_name=SIMULATOR_NAME)

    def setUp(self):
        Tns.kill()
        BaseClass.tearDown(self)

    def tearDown(self):
        BaseClass.tearDown(self)
        Tns.kill()

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()

    def test_001_build_android(self):
        # Debug build
        Tns.build_android(attributes={"--path": self.app_name})

        # Release build
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": ""})

    def test_100_run_android(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=['successfully built', 'Successfully installed'], timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.ts_change)
        ReplaceHelper.replace(self.app_name, self.html_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_change)

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.ts_change)
        ReplaceHelper.rollback(self.app_name, self.html_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)

    def test_200_build_android_webpack(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": "",
                                      "--env.uglify": "",
                                      "--env.snapshot": ""})
        Helpers.run_android_via_adb(app_name=self.app_name, config="release", image=self.image_original)
