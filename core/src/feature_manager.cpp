#include "include/feature_manager.h"

#include <cpr/cookies.h>
#include <thread>
#include <chrono>
#include <atomic>
#include <iostream>

FeatureManager::FeatureManager(const std::string &serverUrl)
    : serverUrl_(serverUrl), running_(true)
{
    fetchConfig(serverUrl);

    this->pollingThread_ = std::thread(&FeatureManager::pollConfig, this);
}

FeatureManager::~FeatureManager()
{
    running_ = false;
    if (pollingThread_.joinable())
    {
        pollingThread_.join();
    }
}

void FeatureManager::fetchConfig(const std::string &serverUrl)
{
    cpr::Response r = cpr::Get(cpr::Url{serverUrl});

    if (r.status_code != 200)
    {
        std::cerr << "Error: Could not fetch config from server.\n";
        return;
    }

    json config = json::parse(r.text);
    std::lock_guard<std::mutex> lock(featuresMutex_);

    bool changed = false;

    for (auto &[key, value] : config.items())
    {
        if (features[key] != value.get<bool>())
        {
            features[key] = value.get<bool>();
            changed = true;
        }
    }

    if (changed)
    {
        std::cout << "Feature config updated.\n";
    }
}

void FeatureManager::pollConfig()
{
    while (running_)
    {
        std::this_thread::sleep_for(std::chrono::seconds(10));
        fetchConfig(serverUrl_);
    }
}

bool FeatureManager::isFeatureEnabled(const std::string &featureName)
{
    std::lock_guard<std::mutex> lock(featuresMutex_);
    return features.count(featureName) && features[featureName];
}
