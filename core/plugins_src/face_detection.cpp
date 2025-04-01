 
#include <opencv2/opencv.hpp>
#include <opencv2/objdetect.hpp>
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

        // Load Haar Cascade classifier for face detection
        cv::CascadeClassifier faceCascade;
        // Note: You'll need to provide the path to the cascade file
        std::string cascadePath = cv::samples::findFile("haarcascades/haarcascade_frontalface_default.xml");
        if (!faceCascade.load(cascadePath))
        {
            std::cerr << "Error: Could not load face cascade classifier" << std::endl;
            return cv::Mat();
        }

        // Convert to grayscale for detection
        cv::Mat gray;
        cv::cvtColor(inputFrame, gray, cv::COLOR_BGR2GRAY);
        cv::equalizeHist(gray, gray);

        // Detect faces
        std::vector<cv::Rect> faces;
        faceCascade.detectMultiScale(
            gray,
            faces,
            1.1,             // Scale factor
            3,               // Min neighbors
            0,               // Flags
            cv::Size(30, 30) // Min size
        );

        // Draw rectangles around detected faces
        cv::Mat result = inputFrame.clone();
        for (const auto &face : faces)
        {
            cv::rectangle(result,
                          face,
                          cv::Scalar(0, 255, 0),
                          2);
        }

        // Add label
        cv::putText(result,
                    "Face Detection",
                    cv::Point(10, 30),
                    cv::FONT_HERSHEY_SIMPLEX,
                    1,
                    cv::Scalar(0, 255, 0),
                    2);

        return result;
    }
}

// C interface for plugin
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
        else
        {
            std::cerr << "Error: Memory allocation failed in face_detection plugin" << std::endl;
        }
    }

    return result;
}