#ifndef PLUGIN_LOADER_H
#define PLUGIN_LOADER_H

#include <iostream>
#include <string>

#ifdef _WIN32
    #include <windows.h>
    using LibraryHandle = HMODULE;
#elif defined(__linux__) || defined(__APPLE__)
    #include <dlfcn.h>
    using LibraryHandle = void*;
#else
    #error "Unsupported platform"
#endif

class PluginLoader {
public:
    PluginLoader(const std::string& libPath);
    ~PluginLoader();
    void* getFunction(const std::string& functionName);

private:
    LibraryHandle handle;
};

#endif
