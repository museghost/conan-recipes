from conans import ConanFile, CMake
import os

class SystemcTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    options = {"stdcxx":[98,11,14], "shared":[True,False]}
    default_options = "stdcxx=11","shared=True"
    generators = "cmake"

    def configure(self):
        self.options["SystemC"].stdcxx = self.options.stdcxx
        self.options["SystemC"].shared = self.options.shared
        
    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_CXX_STANDARD"] = self.options["SystemC"].stdcxx
        cmake.definitions["CMAKE_CXX_FLAGS"]="-D_GLIBCXX_USE_CXX11_ABI=%d" %(0 if self.settings.compiler.libcxx == 'libstdc++' else 1)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')

    def test(self):
        os.chdir("bin")
        self.run(".%sexample" % os.sep)
