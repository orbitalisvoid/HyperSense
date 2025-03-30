#ifndef FEATURE_MANAGER_H
#define FEATURE_MANAGER_H

#include <iostream>
#include <unordered_map>
#include <nlohmann/json.hpp>
#include <cpr/cpr.h>

using json = nlohmann::json;

class FeatureManager
{
public:
    FeatureManager(const std::string &serverUrl);
    ~FeatureManager();
    bool isFeatureEnabled(const std::string &featureName);

private:
    void fetchConfig(const std::string &serverUrl);
    void pollConfig();

    std::string serverUrl_;
    std::unordered_map<std::string, bool> features;
    std::thread pollingThread_;
    std::atomic<bool> running_;
    std::mutex featuresMutex_;
};

#endif
