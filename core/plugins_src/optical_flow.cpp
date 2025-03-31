
#include <opencv2/opencv.hpp>
#include <iostream>

// C-compatible struct for plugin interface
extern "C" struct CPluginResult
{
    unsigned char *data;
    int width;
    int height;
    int channels;
    int hasData;
};

// Internal C++ implementation
namespace
{
    cv::Mat processFrameImpl(const cv::Mat &inputFrame)
    {
        if (inputFrame.empty())
        {
            return cv::Mat();
        }

        cv::Mat result;
        cv::cvtColor(inputFrame, result, cv::COLOR_BGR2GRAY);
        cv::putText(result,
                    "Optical Flow",
                    cv::Point(60, 140),
                    cv::FONT_HERSHEY_SIMPLEX,
                    1,
                    cv::Scalar(255),
                    2);
        return result;
    }
}
 
extern "C" CPluginResult processFrame(const unsigned char *data, int width, int height, int channels)
{
    CPluginResult result = {nullptr, 0, 0, 0, 0};

    if (!data || width <= 0 || height <= 0 || channels <= 0)
    {
        return result;
    }

    cv::Mat inputFrame(height, width, CV_8UC(channels), const_cast<unsigned char *>(data));
    cv::Mat processed = processFrameImpl(inputFrame);

    if (!processed.empty())
    {
        size_t size = processed.total() * processed.elemSize();
        result.data = static_cast<unsigned char *>(malloc(size));
        if (result.data)
        {
            memcpy(result.data, processed.data, size);
            result.width = processed.cols;
            result.height = processed.rows;
            result.channels = processed.channels();
            result.hasData = 1;
        }
    }

    return result;
}