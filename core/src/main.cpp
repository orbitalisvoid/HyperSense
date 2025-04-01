#include <opencv2/opencv.hpp>
#include <iostream>
#include <unordered_map>
#include "include/feature_manager.h"
#include "include/plugin_loader.h"

#ifdef _WIN32
#define LIB_PREFIX ""
#define LIB_SUFFIX ".dll"
#elif defined(__APPLE__)
#define LIB_PREFIX "lib"
#define LIB_SUFFIX ".dylib"
#else
#define LIB_PREFIX "lib"
#define LIB_SUFFIX ".so"
#endif

// C-compatible struct for plugin results
struct CPluginResult
{
    unsigned char *data;
    int width;
    int height;
    int channels;
    int hasData;
};

std::string getLibraryPath(const std::string &featureName)
{
    return "plugins/" + static_cast<std::string>(LIB_PREFIX) + featureName + LIB_SUFFIX;
}

int main()
{
    std::string serverUrl = "http://localhost:9001/api/get_subscription";
    FeatureManager fm(serverUrl);

    std::unordered_map<std::string, std::string> features = {
        {"kalman_filter", "kalman_filter"},
        {"optical_flow", "optical_flow"},
        {"face_detection", "face_detection"}};

    cv::VideoCapture cap(0);
    if (!cap.isOpened())
    {
        std::cout << "Error: Could not open camera" << std::endl;
        return -1;
    }

    cv::Mat frame;
    bool running = true;

    std::unordered_map<std::string, cv::Mat> results;
    std::unordered_map<std::string, bool> active_features;

    while (running)
    {
        cap >> frame;
        if (frame.empty())
        {
            std::cout << "Error: Empty frame captured" << std::endl;
            break;
        }

        for (const auto &[feature, libName] : features)
        {

            bool is_feature_enabled = fm.isFeatureEnabled(feature);

            if (!is_feature_enabled && active_features[feature])
            {
                cv::destroyWindow(feature + "_window");
                results.erase(feature);
                active_features[feature] = false;
                continue;
            }

            if (is_feature_enabled) //  && !active_features[feature])
            {
                std::string libPath = getLibraryPath(libName);
                PluginLoader loader(libPath);

                auto processFrame =
                    reinterpret_cast<CPluginResult (*)(const unsigned char *, int, int, int)>(loader.getFunction("processFrame"));

                if (processFrame)
                {
                    CPluginResult result = processFrame(frame.data,
                                                        frame.cols,
                                                        frame.rows,
                                                        frame.channels());

                    if (result.hasData && result.data)
                    {
                        cv::Mat processedFrame(result.height,
                                               result.width,
                                               CV_8UC(result.channels),
                                               result.data);
                        results[feature] = processedFrame.clone();
                        free(result.data);
                    }
                }
                else
                {
                    std::cout << "Failed to load " << feature << " feature" << std::endl;
                }
            }
        }

        // Display results
        for (const auto &[feature, result] : results)
        {
            cv::imshow(feature + "_window", result);
        }

        int key = cv::waitKey(1);
        if (key == 27)
        {
            running = false;
        }
    }

    cv::destroyAllWindows();
    cap.release();
    return 0;
}
