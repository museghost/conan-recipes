from conans import ConanFile, CMake, tools
import os

class RocksDBConan(ConanFile):
    name = "rocksdb"
    version = "6.7.3"
    license = "Apache 2.0 License"
    url = "https://github.com/facebook/rocksdb/"
    description = "A library that provides an embeddable, persistent key-value store for fast storage."
    settings = "os", "compiler", "build_type", "arch"
    options = {"stdcxx":[11,14], "shared":[True, False], "fPIC":[True, False]}
    default_options = {"stdcxx":14, "shared": False, "fPIC": True}
    generators = ["cmake", "cmake_find_package", "cmake_paths"]
    #source_subfolder = "rocksdb-%s"% version
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    #exports_sources = ["rocksdb/*"]
    exports_sources = ["CMakeLists.txt"]

    source_tgz = "https://github.com/facebook/rocksdb/archive/v%s.tar.gz" % version
    
    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove('fPIC')

    def source(self):
        self.output.info("Downloading %s" %self.source_tgz)
        tools.download(self.source_tgz, "rocksdb.tar.gz")
        tools.unzip("rocksdb.tar.gz")
        os.remove("rocksdb.tar.gz")
        os.rename("rocksdb-{}".format(self.version), self.source_subfolder)

    def requirements(self):
        self.requires("zlib/1.2.11@conan/stable")
        self.requires("bzip2/1.0.8@conan/stable")
        self.requires("lz4/1.9.2")
        self.requires("gflags/2.2.2")
        self.requires("snappy/1.1.8")
        self.requires("zstd/1.4.4")

    def build(self):
        # temp patch
        search_path = "{0}/CMakeLists.txt".format(self.source_subfolder)
        if self.settings.os == "Macos":
            tools.replace_in_file(search_path, r"find_package(ZLIB REQUIRED)", r"find_package(zlib REQUIRED)")
            tools.replace_in_file(search_path, r"ZLIB::ZLIB", r"zlib::zlib")
        tools.replace_in_file(search_path, r"find_package(BZip2 REQUIRED)", r"find_package(bzip2 REQUIRED)")
        tools.replace_in_file(search_path, r"list(APPEND THIRDPARTY_LIBS ${BZIP2_LIBRARIES})", r"list(APPEND THIRDPARTY_LIBS bzip2::bzip2)")

        cmake = CMake(self, parallel=True)
        
        if self.settings.compiler != 'Visual Studio':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        cmake.definitions["ROCKSDB_BUILD_SHARED"] = "OFF"
        cmake.definitions["CMAKE_CXX_STANDARD"] = str(self.options.stdcxx)
        cmake.definitions["WITH_LZ4"] = "ON"
        cmake.definitions["WITH_ZLIB"] = "ON"
        cmake.definitions["WITH_BZ2"] = "ON"
        cmake.definitions["WITH_CORE_TOOLS"] = "ON"
        cmake.definitions["WITH_TOOLS"] = "ON"
        cmake.definitions["WITH_TESTS"] = "OFF"
        #cmake.definitions["DISABLE_STALL_NOTIF"] = True
        cmake.definitions["WITH_BENCHMARK_TOOLS"] = "OFF"
        if self.settings.compiler == "clang":
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-Wshadow -pedantic -fvisibility-inlines-hidden -Wgnu-statement-expression, -Wgnu-zero-variadic-macro-arguments"
        elif self.settings.compiler == "gcc":
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-fvisibility-inlines-hidden"

        cmake.configure(
                #source_folder=self.source_subfolder,
                #build_folder=self.build_subfolder
                #args=[
                    #'-DCMAKE_CXX_FLAGS:="-D_GLIBCXX_USE_CXX11_ABI=%d"' % (0 if self.settings.compiler.libcxx == 'libstdc++' else 1),
                    #'-DROCKSDB_BUILD_SHARED=%s' % ('ON' if self.options.shared else 'OFF'),
                    #'-DCMAKE_POSITION_INDEPENDENT_CODE=%s' % ('ON' if self.options.fPIC else 'OFF'),
                    #'-DCMAKE_CXX_STANDARD=%s' % self.options.stdcxx,
                    #'-DWITH_LZ4=ON -DWITH_ZLIB=ON -DWITH_BZ2=ON -DDISABLE_STALL_NOTIF=ON -DWITH_TOOLS=ON -DWITH_TESTS=OFF',
                    #'-DWITH_LZ4=ON -DWITH_ZLIB=ON -DWITH_BZ2=ON -DDISABLE_STALL_NOTIF=ON -DWITH_TOOLS=OFF -DWITH_TESTS=OFF',
                    #'-DWITH_BENCHMARK_TOOLS=OFF -DWITH_CORE_TOOLS=OFF -DWITH_TOOLS=OFF -DWITH_TESTS=OFF'
                    #]
                )
        #cmake.build(target='rocksdb')
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("LICENSE.Apache", src=self.source_subfolder, keep_path=False)
        self.copy("LICENSE.leveldb", src=self.source_subfolder, keep_path=False)
        self.copy("*.h", dst="include", src=("%s/include" % self.source_subfolder))
        self.copy("librocksdb.a", dst="lib", keep_path=False)
        self.copy("ldb*", dst="bin", keep_path=False)
        self.copy("sst_dump*", dst="bin", keep_path=False)

    def package_info(self):
        #self.cpp_info.libs = ["rocksdb"]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
