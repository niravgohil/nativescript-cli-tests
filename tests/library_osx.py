import unittest

from helpers._os_lib import CleanupFolder, CheckFilesExists, FolderExists, runAUT
from helpers._tns_lib import Build, CreateProject, PlatformAdd, LibraryAdd

class Library_OSX(unittest.TestCase):

    def setUp(self):

        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""
        
        CleanupFolder('./TNS_App');

    def tearDown(self):
        pass

    def test_001_Library_Add_iOS_Framework(self):
        CreateProject(projName="TNS_App")
        PlatformAdd(platform="ios", path="TNS_App")

        LibraryAdd(platform="ios", libPath="QA-TestApps/external-lib/TelerikUI.framework", path="TNS_App")
        assert (CheckFilesExists("TNS_App/lib/iOS/TelerikUI/TelerikUI.framework", "library_add_Framework_1.1.0.txt"))

        Build(platform="ios", path="TNS_App")
        output = runAUT("cat TNS_App/platforms/ios/TNSApp.xcodeproj/project.pbxproj | grep TelerikUI")
        assert ("TelerikUI.framework in Frameworks" in output)
        assert ("TelerikUI.framework in Embed Frameworks" in output)
        assert ("/TelerikUI.framework" in output)
        assert not ("TNS_App/lib/iOS/TelerikUI/TelerikUI.framework" in output)

    def test_401_Library_Add_iOS_NoLib(self):
        CreateProject(projName="TNS_App") 
        PlatformAdd(platform="ios", path="TNS_App")
        
        output = LibraryAdd(platform="ios", libPath="TelerikUI.framework", path="TNS_App", assertSuccess=False)
        assert (".framework does not exist" in output)
        assert not FolderExists("TNS_App/lib")