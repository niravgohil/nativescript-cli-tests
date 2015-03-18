import os
import unittest

from helpers._os_lib import CleanupFolder, runAUT
from helpers._tns_lib import CreateProjectAndAddPlatform, iosRuntimeSymlinkPath, tnsPath
from helpers.device import GivenRealDeviceRunning


class Run_OSX(unittest.TestCase):
    
    def setUp(self):
        
        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""
        
        CleanupFolder('./TNS_App')
        GivenRealDeviceRunning(platform="ios") 
        
    def tearDown(self):        
        pass
    
    @unittest.skip("Skipped because of https://github.com/NativeScript/nativescript-cli/issues/248")  
    def test_001_Run_iOS(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimeSymlinkPath, symlink=True) 
        output = runAUT(tnsPath + " run ios --path TNS_App")
        assert ("Project successfully prepared" in output) 
        assert ("CONFIGURATION Debug" in output)
        assert ("Project successfully built" in output)   
        assert ("Successfully deployed on device with identifier" in output)  
        #TODO: Get device id and verify files are deployed and process is running on this device 
    
    @unittest.skip("Skipped because of https://github.com/NativeScript/nativescript-cli/issues/248")          
    def test_002_Run_iOS_ReleaseConfiguration(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimeSymlinkPath, symlink=True)
        output = runAUT(tnsPath + " run ios --release --path TNS_App")
        assert ("Project successfully prepared" in output) 
        assert ("CONFIGURATION Release" in output)
        assert ("Project successfully built" in output)   
        assert ("Successfully deployed on device with identifier" in output)         
        #TODO: Get device id and verify files are deployed and process is running on this device
 
    def test_003_Run_iOS_Simulator(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimeSymlinkPath, symlink=True)
        output = runAUT(tnsPath + " run ios --emulator --path TNS_App")
        assert ("Project successfully prepared" in output) 
        assert ("CONFIGURATION Debug" in output)
        assert ("Project successfully built" in output)   
        assert ("Starting iOS Simulator" in output)  
        assert ("Session started without errors" in output)  
        #TODO: Get device id and verify files are deployed and process is running on this device 

    def test_004_Run_iOS_ReleaseConfiguration_Simulator(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimeSymlinkPath, symlink=True)
        output = runAUT(tnsPath + " run ios --emulator --release --path TNS_App")
        assert ("Project successfully prepared" in output) 
        assert ("CONFIGURATION Release" in output)
        assert ("Project successfully built" in output)   
        assert ("Starting iOS Simulator" in output)  
        assert ("Session started without errors" in output)  
        #TODO: Get device id and verify files are deployed and process is running on this device 
        
    @unittest.skip("Skipped because of https://github.com/NativeScript/nativescript-cli/issues/248")     
    def test_200_Run_iOS_InsideProject(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimeSymlinkPath, symlink=True)    
        currentDir = os.getcwd()   
        os.chdir(os.path.join(currentDir,"TNS_App"))    
        output = runAUT(os.path.join("..", tnsPath) + " run ios --path TNS_App")
        os.chdir(currentDir);
        assert ("Project successfully prepared" in output) 
        assert ("CONFIGURATION Debug" in output)
        assert ("Project successfully built" in output)   
        assert ("Successfully deployed on device with identifier" in output)  